import asyncio
import json

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Notification
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.long_polling_manager import (
    long_polling_manager,
)
from app.services.notification_service import (
    create_notification,
    get_unread_count,
)
from app.services.redis_manager import redis_manager
from app.services.sse_manager import (
    sse_manager,
)
from app.services.websocket_manager import (
    websocket_manager,
)



router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
)
async def create(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
):

    notification = create_notification(
        db,
        user_id=payload.user_id,
        notification_type=
            payload.notification_type,
        title=payload.title,
        message=payload.message,
    )


    await redis_manager.publish_notification(
    user_id=notification.user_id,
    message={
        "type": "notification",
        "data": {
                "id": notification.id,
                "user_id": notification.user_id,
                "notification_type": notification.notification_type,
                "title": notification.title,
                "message": notification.message,
                "is_read": notification.is_read,
                "created_at": notification.created_at.isoformat(),
            },
        },
    )


    return notification


@router.get(
    "/unread-count",
    response_model=UnreadCountResponse,
)
def unread_count(
    user_id: int,
    db: Session = Depends(get_db),
):
    count = get_unread_count(
        db,
        user_id=user_id,
    )

    return {
        "unread_count": count,
    }

@router.get("/long-poll")
async def long_poll(
    user_id: int,
    last_notification_id: int = Query(
        default=0,
    ),
    db: Session = Depends(get_db),
):

    # -------------------------------------------------
    # 1. Check whether a notification already exists
    # -------------------------------------------------

    statement = (
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.id > last_notification_id,
        )
        .order_by(Notification.id.asc())
    )

    existing_notification = db.scalars(
        statement
    ).first()

    if existing_notification:

        return {
            "notification_available": True,
            "notification": existing_notification,
        }

    # -------------------------------------------------
    # 2. Nothing exists.
    #    Wait for a notification.
    # -------------------------------------------------

    latest_id = await (
        long_polling_manager.wait_for_notification(
            user_id=user_id,
            last_notification_id=last_notification_id,
            timeout=30,
        )
    )

    # -------------------------------------------------
    # 3. Timeout
    # -------------------------------------------------

    if latest_id is None:

        return {
            "notification_available": False,
            "notification": None,
        }

    # -------------------------------------------------
    # 4. Notification arrived.
    #    Fetch it from DB.
    # -------------------------------------------------

    statement = (
        select(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.id > last_notification_id,
        )
        .order_by(Notification.id.asc())
    )

    new_notification = db.scalars(
        statement
    ).first()

    return {
        "notification_available": True,
        "notification": new_notification,
    }

async def notification_event_generator(
    user_id: int,
):

    queue = await sse_manager.connect(
        user_id
    )

    try:

        while True:

            try:

                event = await asyncio.wait_for(
                    queue.get(),
                    timeout=15,
                )

                yield (
                    f"event: {event['type']}\n"
                    f"data: "
                    f"{json.dumps(event['data'])}\n\n"
                )
            # Some proxies/load balancers may consider an idle connection inactive.
            # We can periodically send an SSE comment
            # SSE comments aren't dispatched as events to the application, but they keep the connection active.
            except asyncio.TimeoutError:

                yield ": heartbeat\n\n"

    finally:

        await sse_manager.disconnect(
            user_id,
            queue,
        )

@router.get("/stream")
async def notification_stream(
    user_id: int,
):

    return StreamingResponse(
        notification_event_generator(
            user_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )