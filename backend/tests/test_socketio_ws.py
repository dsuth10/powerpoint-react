import pytest
import socketio
import asyncio
import threading
from app.main import app
import uvicorn

@pytest.mark.asyncio
async def test_socketio_slide_progress(tmp_path):
    # Start the server in a background thread
    config = uvicorn.Config(app, host="127.0.0.1", port=9001, log_level="error")
    server = uvicorn.Server(config)
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    await asyncio.sleep(1)  # Wait for server to start

    sio = socketio.AsyncClient()
    received = {}

    @sio.on("slide:progress")
    def on_progress(data):
        received["progress"] = data

    await sio.connect("http://127.0.0.1:9001", socketio_path="/ws/socket.io")
    await sio.emit("slide_progress", {"step": 1})
    await asyncio.sleep(1)
    await sio.disconnect()
    assert "progress" in received
    assert received["progress"]["step"] == 1 