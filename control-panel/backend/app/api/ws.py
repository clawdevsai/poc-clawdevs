# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import asyncio
import json
import logging
from typing import Dict, List
from urllib.parse import urlparse
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.auth import decode_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_CHANNELS = {"dashboard", "agents", "approvals", "cluster", "crons", "context-mode-metrics"}


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    def register(self, channel: str, websocket: WebSocket):
        self.active.setdefault(channel, []).append(websocket)
        logger.info(
            f"WS connected: channel={channel}, total={len(self.active[channel])}"
        )

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self.active:
            try:
                self.active[channel].remove(websocket)
            except ValueError:
                pass

    async def broadcast(self, channel: str, data: dict):
        dead = []
        for ws in self.active.get(channel, []):
            try:
                await ws.send_json(data)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(channel, ws)


manager = ConnectionManager()


@router.websocket("/ws/{channel}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel: str,
):
    settings = get_settings()

    if channel not in ALLOWED_CHANNELS:
        await websocket.close(code=4000)
        return

    # Validate Origin header — CORSMiddleware does not protect WebSocket connections.
    origin = websocket.headers.get("origin", "")
    parsed = urlparse(origin) if origin else None
    origin_host = parsed.hostname if parsed else None
    is_local_browser = origin_host in {"127.0.0.1", "localhost"}
    if origin not in settings.allowed_origins and not is_local_browser:
        logger.warning(
            f"WS rejected invalid origin: origin={origin!r}, channel={channel}"
        )
        await websocket.close(code=4003)
        return

    await websocket.accept()

    # Authenticate via first frame instead of query parameter.
    # Tokens in URLs are logged by proxies, servers, and stored in browser history.
    try:
        raw = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
        frame = json.loads(raw)
        token = (
            frame.get("token", "")
            if isinstance(frame, dict) and frame.get("type") == "auth"
            else ""
        )
    except (asyncio.TimeoutError, json.JSONDecodeError, Exception):
        await websocket.close(code=4001)
        return

    payload = decode_token(token) if token else None
    if payload is None:
        logger.warning(
            f"WS rejected unauthenticated connection: channel={channel}, ip={websocket.client}"
        )
        await websocket.close(code=4001)
        return

    manager.register(channel, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(channel, websocket)
