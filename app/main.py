import asyncio

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine

from app.routers import users
from app.routers import notifications
from app.routers import websocket

from app.services.redis_manager import redis_manager
from app.services.redis_subscriber import subscribe_to_notifications


subscriber_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):

    global subscriber_task

    print("Starting application...")

    Base.metadata.create_all(bind=engine)

    await redis_manager.connect()

    print("Redis connected.")

    subscriber_task = asyncio.create_task(
        subscribe_to_notifications()
    )

    print("Redis subscriber started.")

    yield

    print("Shutting down application...")

    if subscriber_task:
        subscriber_task.cancel()

        try:
            await subscriber_task
        except asyncio.CancelledError:
            pass

    await redis_manager.close()

    print("Redis connection closed.")


app = FastAPI(
    title="Real-Time Notification System",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(notifications.router)
app.include_router(websocket.router)


@app.get("/health")
def health():
    return {"status": "ok"}