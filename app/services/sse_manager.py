import asyncio
from collections import defaultdict


class SSEManager:

    def __init__(self):
        self._connections = defaultdict(set)

    async def connect(
        self,
        user_id: int,
    ) -> asyncio.Queue:

        queue = asyncio.Queue()

        self._connections[user_id].add(queue)

        return queue

    async def disconnect(
        self,
        user_id: int,
        queue: asyncio.Queue,
    ):

        self._connections[user_id].discard(queue)

        if not self._connections[user_id]:
            del self._connections[user_id]

    async def publish(
        self,
        user_id: int,
        event: dict,
    ):

        queues = self._connections.get(
            user_id,
            set(),
        )

        for queue in queues:
            await queue.put(event)


sse_manager = SSEManager()