from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse


router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post(
    "",
    response_model=UserResponse,
)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
):
    user = User(
        username=payload.username,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user