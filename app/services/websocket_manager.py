from collections import defaultdict

from fastapi import WebSocket


class WebSocketManager:

    def __init__(self):
        self._connections = defaultdict(set)

    async def connect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        await websocket.accept()

        self._connections[user_id].add(
            websocket
        )

    def disconnect(
        self,
        user_id: int,
        websocket: WebSocket,
    ):
        connections = self._connections.get(
            user_id
        )

        if not connections:
            return

        connections.discard(websocket)

        if not connections:
            del self._connections[user_id]

    async def send_to_user(
        self,
        user_id: int,
        message: dict,
    ):
        connections = self._connections.get(
            user_id,
            set(),
        )

        disconnected = []

        for websocket in connections:

            try:

                await websocket.send_json(
                    message
                )

            except Exception:

                disconnected.append(
                    websocket
                )

        for websocket in disconnected:

            self.disconnect(
                user_id,
                websocket,
            )


websocket_manager = WebSocketManager()