import logging
from collections.abc import Callable

from src.model import Publication
from src.sciencedirect import Parser

from .tasks import Task, TaskQueue


class CrawlerWorker:
    def __init__(
        self,
        tasks: TaskQueue,
        parser: Parser,
        process: Callable[[Publication], bool],
    ) -> None:
        self._parser = parser
        self._task_queue = tasks
        self._process = process

    async def run(self):
        while True:
            task = await self._task_queue.pop()

            logging.info(f"crawl target {task.target}")

            page = await self._parser.parse_record(task.target)

            self._process(page)

            await self._push_targets(page)

            await self._task_queue.ack()

    async def _push_targets(self, page: Publication):

        logging.info(f"references {page.references}")

        logging.info(f"spawn new {len(page.references)} targets")

        for link in page.references:
            target = link.url

            if target is None:
                continue

            await self._task_queue.push(Task(**{
                "target": target,
            }))
