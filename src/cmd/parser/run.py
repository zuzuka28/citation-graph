import asyncio
import logging
import os

from src.crawl.crawl import Crawler
from src.crawl.tasks import Task
from src.process.sciencedirect import SciencedirectProcessor

# def save_content(data: str | bytes):
#     filename = str(uuid.uuid4()) + ".txt"
#     with open(filename, "w") as f:
#         f.write(str(data))


async def main():
    logging.basicConfig(
        format='%(threadName)s %(name)s %(levelname)s: %(message)s',
        level=logging.DEBUG)

    processor = SciencedirectProcessor(
        "graph.csv"
    )

    crawler = Crawler(
        3,
        os.getcwd() + "/" + "data",
    )

    await crawler.setup(
        Task(
            "https://www.sciencedirect.com/science/article/abs/pii/S0196064409005319",
        ),
    )

    await asyncio.create_task(crawler.run(processor.process))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
