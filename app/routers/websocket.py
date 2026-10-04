from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)

from app.services.websocket_manager import (
    websocket_manager,
)


router = APIRouter(
    tags=["WebSocket"],
)


@router.websocket(
    "/ws/notifications/{user_id}"
)
async def notification_websocket(
    websocket: WebSocket,
    user_id: int,
):

    await websocket_manager.connect(
        user_id,
        websocket,
    )

    try:

        while True:

            message = await websocket.receive_json()

            print(
                f"Received from user {user_id}:",
                message,
            )

    except WebSocketDisconnect:

        websocket_manager.disconnect(
            user_id,
            websocket,
        )