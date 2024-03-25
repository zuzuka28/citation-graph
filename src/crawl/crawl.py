import asyncio
from collections.abc import Callable

from src.crawl.worker import CrawlerWorker
from src.model import Publication
from src.sciencedirect import Browser, Parser

from .tasks import Task, TaskQueue


class Crawler:
    def __init__(
        self,
        workers: int,
        ddir: str,
    ):
        self._task_queue = TaskQueue()
        self._workers_count = workers

        self._ddir = ddir
        self._parser = NotImplemented

    async def setup(self, start: Task):
        browser = Browser()
        await browser.setup()

        self._parser = Parser(
            browser,
            self._ddir
        )

        await self._task_queue.push(start)

    async def run(self, process: Callable[[Publication], bool]):
        tasks = []
        for _ in range(self._workers_count):
            worker = CrawlerWorker(
                self._task_queue,
                self._parser,
                process
            )
            task = asyncio.create_task(worker.run())
            tasks.append(task)

        await self._task_queue.join()

        await asyncio.gather(*tasks, return_exceptions=True)
