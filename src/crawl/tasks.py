from asyncio import Queue
from dataclasses import dataclass


@dataclass
class Task:
    target: str


class TaskQueue:
    def __init__(self) -> None:
        self._queue = Queue()
        self._uniq = {}

    async def push(self, item: Task):
        if self._uniq.get(item.target, None) is not None:
            return

        self._uniq[item.target] = item

        await self._queue.put(item)

    async def pop(self) -> Task:
        return await self._queue.get()

    def is_empty(self) -> bool:
        return self._queue.empty()

    async def ack(self):
        self._queue.task_done()

    async def join(self):
        await self._queue.join()
