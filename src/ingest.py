import argparse
import asyncio
import logging
from collections.abc import Callable, Coroutine

from dotenv import load_dotenv

from connectors.HkoConnector import HkoConnector
from connectors.NwsConnector import NwsConnector
from connectors.types import Connector
from scheduler.Scheduler import Scheduler, Task
from storage.DbAccessor import DbAccessor

logger = logging.getLogger(__name__)


async def observe_and_enqueue(connector: Connector, queue: asyncio.Queue):
    """Observesto fetch data and enqueue it."""
    while True:
        observations = await connector.observe()
        await queue.put(observations)


async def persist_observations(queue: asyncio.Queue, db: DbAccessor):
    """Consumes observations from the queue and persists them to the DB."""
    while True:
        observations = await queue.get()
        await db.persist_observation(observations)
        queue.task_done()


async def main(args):
    connectors = [
        HkoConnector(),
        NwsConnector(),
    ]
    db = await DbAccessor.connect(args.database)

    # Initialize the queue to decouple observation and persistence
    observation_queue = asyncio.Queue()

    # Start the persistence task
    persistence_task = asyncio.create_task(persist_observations(observation_queue, db))

    # Create and start observation tasks for each connector
    observation_tasks = []
    for connector in connectors:
        task = asyncio.create_task(observe_and_enqueue(connector, observation_queue))
        observation_tasks.append(task)

    # Run all tasks concurrently. This loop runs indefinitely until interrupted (e.g., Ctrl+C).
    await asyncio.gather(*observation_tasks, persistence_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    load_dotenv()
    parser = argparse.ArgumentParser(description="Continuously fetch data")
    parser.add_argument(
        "-d",
        "--database",
        type=str,
        default="out/data.db",  # The fallback filename if none is specified
        help="Specify the database filename (default: data.db)",
    )

    args = parser.parse_args()
    asyncio.run(main(args))
