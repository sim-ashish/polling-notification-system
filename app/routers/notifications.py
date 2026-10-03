from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    UnreadCountResponse,
)
from app.services.notification_service import (
    create_notification,
    get_unread_count,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"],
)


@router.post(
    "",
    response_model=NotificationResponse,
)
def create(
    payload: NotificationCreate,
    db: Session = Depends(get_db),
):
    return create_notification(
        db,
        user_id=payload.user_id,
        notification_type=payload.notification_type,
        title=payload.title,
        message=payload.message,
    )


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