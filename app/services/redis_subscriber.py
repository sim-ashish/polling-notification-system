import asyncio
import json

from app.services.redis_manager import (
    redis_manager,
    NOTIFICATION_CHANNEL,
)

from app.services.websocket_manager import websocket_manager


async def subscribe_to_notifications():

    if not redis_manager.redis:
        raise RuntimeError("Redis is not connected")

    pubsub = redis_manager.redis.pubsub()

    redis_manager.pubsub = pubsub

    await pubsub.subscribe(NOTIFICATION_CHANNEL)

    print(
        f"Subscribed to Redis channel: {NOTIFICATION_CHANNEL}"
    )

    try:
        async for message in pubsub.listen():

            if message["type"] != "message":
                continue

            payload = json.loads(message["data"])

            user_id = payload["user_id"]
            notification = payload["message"]

            print(
                f"Redis event received for user {user_id}"
            )

            await websocket_manager.send_to_user(
                user_id=user_id,
                message=notification,
            )

    except asyncio.CancelledError:
        print("Redis subscriber stopped.")
        raise

    finally:
        await pubsub.unsubscribe(NOTIFICATION_CHANNEL)
        await pubsub.close()