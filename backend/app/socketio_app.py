import socketio
from uuid import UUID
from typing import Any, Dict, List

from app.core.auth import verify_token
from app.core.config import settings

# Async Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins="*")

# Mountable ASGI app at a base path; main mounts it under "/ws"
ws_app = socketio.ASGIApp(sio, socketio_path="socket.io")

# Simple in-memory buffer of recent events per session
_recent_events: Dict[str, List[Dict[str, Any]]] = {}


@sio.event
async def connect(sid, environ, auth=None):
    # Optional auth: accept either JWT or sessionId; enforce API key if configured
    try:
        user_ok = False
        session_ok = False
        api_key_ok = False

        # Header-based JWT (Authorization: Bearer <token>)
        auth_header = environ.get("HTTP_AUTHORIZATION")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            verify_token(token, token_type="access")
            user_ok = True

        # API key header
        api_key = environ.get("HTTP_X_API_KEY")
        if api_key and api_key in (settings.API_KEYS or []):
            api_key_ok = True

        # auth payload or querystring sessionId
        session_id = None
        if isinstance(auth, dict):
            session_id = auth.get("sessionId") or auth.get("session_id")
        if not session_id:
            # Parse QUERY_STRING for sessionId=...
            qs = environ.get("QUERY_STRING", "")
            for part in qs.split("&"):
                if part.startswith("sessionId="):
                    session_id = part.split("=", 1)[1]
                    break
        if session_id:
            try:
                # Validate UUID shape
                UUID(str(session_id))
                session_ok = True
                await sio.enter_room(sid, str(session_id))
            except Exception:
                session_ok = False

        # Enforce API key only if required by settings
        if settings.REQUIRE_API_KEY:
            if not (api_key_ok or user_ok):
                return False

        # In development mode, be more permissive
        if settings.PROJECT_ENV == "development":
            # Allow connections if any auth method is present, or allow anonymous connections
            if user_ok or session_ok or api_key_ok:
                return True
            # For development, allow anonymous connections
            return True

        # Otherwise, allow if any of JWT or sessionId present (or in dev allow anon)
        if not (user_ok or session_ok) and settings.PROJECT_ENV == "production":
            # In prod, require at least a session or JWT if API key not required
            return False

        return True

    except Exception as e:
        # In development, log the error but allow the connection
        if settings.PROJECT_ENV == "development":
            print(f"Socket.IO auth error (allowing in dev): {e}")
            return True
        return False


@sio.event
async def disconnect(sid):
    # Room cleanup handled by server; nothing to do here
    return


@sio.event
async def slide_progress(sid, data):
    # Emit to sender and buffer to session room if present
    await sio.emit("slide:progress", data, to=sid)


@sio.event
async def slide_completed(sid, data):
    await sio.emit("slide:completed", data, to=sid)


@sio.event
async def error(sid, data):
    await sio.emit("error", data, to=sid)


async def emit_progress(session_id: str, data: Dict[str, Any]) -> None:
    """Emit a progress update to a session room and store it for replay."""
    try:
        UUID(str(session_id))
    except Exception:
        return
    _recent_events.setdefault(session_id, []).append({"type": "progress", "data": data})
    await sio.emit("slide:progress", data, room=session_id)


async def emit_completed(session_id: str, data: Dict[str, Any]) -> None:
    """Emit a completion event to a session room and store it for replay."""
    try:
        UUID(str(session_id))
    except Exception:
        return
    _recent_events.setdefault(session_id, []).append({"type": "completed", "data": data})
    await sio.emit("slide:completed", data, room=session_id)


@sio.event
async def resume(sid, data):
    """Client can request missed events by providing a sessionId and optional fromIndex."""
    session_id = str(data.get("sessionId", ""))
    from_index = int(data.get("fromIndex", 0))
    buf = _recent_events.get(session_id, [])
    for evt in buf[from_index:]:
        await sio.emit(f"slide:{evt['type']}", evt["data"], to=sid)