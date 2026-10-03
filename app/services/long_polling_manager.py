import asyncio
from collections import defaultdict


class LongPollingManager:

    def __init__(self):
        self._conditions = defaultdict(asyncio.Condition)
        self._latest_notification_ids = defaultdict(int)

    async def notify(
        self,
        user_id: int,
        notification_id: int,
    ):
        condition = self._conditions[user_id]

        async with condition:

            self._latest_notification_ids[user_id] = (
                notification_id
            )

            condition.notify_all()

    async def wait_for_notification(
        self,
        user_id: int,
        last_notification_id: int,
        timeout: int = 30,
    ):

        condition = self._conditions[user_id]

        async with condition:

            try:

                await asyncio.wait_for(
                    condition.wait_for(
                        lambda:
                        self._latest_notification_ids[user_id]
                        > last_notification_id
                    ),
                    timeout=timeout,
                )

                return (
                    self._latest_notification_ids[user_id]
                )

            except asyncio.TimeoutError:

                return None


long_polling_manager = LongPollingManager()