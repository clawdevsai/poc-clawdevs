import asyncio
import json
import logging
from typing import Dict, List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active: Dict[str, List[WebSocket]] = {}

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        self.active.setdefault(channel, []).append(websocket)
        logger.info(f"WS connected: channel={channel}, total={len(self.active[channel])}")

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
async def websocket_endpoint(websocket: WebSocket, channel: str):
    ALLOWED_CHANNELS = {"dashboard", "agents", "approvals", "cluster", "crons"}
    if channel not in ALLOWED_CHANNELS:
        await websocket.close(code=4000)
        return

    await manager.connect(channel, websocket)
    try:
        while True:
            # Keep alive — client can send pings
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(channel, websocket)
