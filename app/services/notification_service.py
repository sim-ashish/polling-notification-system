from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.services.long_polling_manager import (
    long_polling_manager,
)


def create_notification(
    db: Session,
    *,
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
) -> Notification:

    notification = Notification(
        user_id=user_id,
        notification_type=notification_type,
        title=title,
        message=message,
    )

    db.add(notification)

    db.commit()

    db.refresh(notification)

    return notification


def get_unread_count(
    db: Session,
    *,
    user_id: int,
) -> int:

    statement = (
        select(func.count(Notification.id))
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
    )

    return db.scalar(statement) or 0