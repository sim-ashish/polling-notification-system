import json

from redis.asyncio import Redis

from app.config import settings


NOTIFICATION_CHANNEL = "notifications"


class RedisManager:

    def __init__(self):
        self.redis: Redis | None = None
        self.pubsub = None

    async def connect(self):
        self.redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )

    async def close(self):
        if self.pubsub:
            await self.pubsub.close()

        if self.redis:
            await self.redis.close()

    async def publish_notification(
        self,
        user_id: int,
        message: dict,
    ):
        if not self.redis:
            raise RuntimeError("Redis is not connected")

        payload = {
            "user_id": user_id,
            "message": message,
        }

        await self.redis.publish(
            NOTIFICATION_CHANNEL,
            json.dumps(payload),
        )


redis_manager = RedisManager()