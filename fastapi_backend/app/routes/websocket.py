from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect
)

from app.websocket.manager import manager


router = APIRouter(
    tags=["WebSocket"]
)


@router.websocket("/ws/notifications/{user_id}")
async def notification_websocket(
    websocket: WebSocket,
    user_id: int
):

    await manager.connect(
        user_id,
        websocket
    )

    try:

        while True:

            await websocket.receive_text()

    except WebSocketDisconnect:

        manager.disconnect(
            user_id,
            websocket
        )

    except Exception:

        manager.disconnect(
            user_id,
            websocket
        )