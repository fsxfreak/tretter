import asyncio
import logging

from dotenv import load_dotenv

from connectors.types import Connector, Observation
from collections.abc import Sequence

from connectors.HkoConnector import HkoConnector
from connectors.NwsConnector import NwsConnector
from scheduler.Scheduler import Scheduler, Task

logger = logging.getLogger(__name__)


async def ingest(connectors: Sequence[Connector]) -> Sequence[Observation]:
    tasks = []
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(connector.observe()) for connector in connectors]

    observations = []
    for task in tasks:
        obs = task.result()
        observations.extend(obs)

    return observations


async def main():
    connectors = [
        HkoConnector(),
        NwsConnector(),
    ]
    scheduler = Scheduler()
    for connector in connectors:
        scheduler.add_task(Task(connector.observe, 15))
    await scheduler.run_tasks()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    asyncio.run(main())
