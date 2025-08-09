import socketio
from fastapi import FastAPI

sio = socketio.AsyncServer(cors_allowed_origins="*")
ws_app = FastAPI()
ws_app.mount("/ws", socketio.ASGIApp(sio, socketio_path="socket.io"))

@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
def slide_progress(sid, data):
    # Example: emit progress update
    sio.emit("slide:progress", data, to=sid)

@sio.event
def slide_completed(sid, data):
    # Example: emit completion event
    sio.emit("slide:completed", data, to=sid)

@sio.event
def error(sid, data):
    sio.emit("error", data, to=sid) 