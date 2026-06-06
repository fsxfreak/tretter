import argparse
import asyncio
import logging

from dotenv import load_dotenv

from collections.abc import Callable, Coroutine
from connectors.HkoConnector import HkoConnector
from connectors.NwsConnector import NwsConnector
from connectors.types import Connector
from scheduler.Scheduler import Scheduler, Task
from storage.DbAccessor import DbAccessor

logger = logging.getLogger(__name__)


# TODO come up with a better way of linking these two together - lots of coupling between the interfaces here
# not sure if I want to do a callback style, or enqueue the results in memory to be written out later...
def observe_and_insert(connector: Connector, db: DbAccessor) -> Callable[[], Coroutine]:
    async def task_func() -> None:
        observations = await connector.observe()
        await db.persist_observation(observations)

    return task_func


async def main(args):
    connectors = [
        HkoConnector(),
        NwsConnector(),
    ]
    db = await DbAccessor.connect(args.database)
    scheduler = Scheduler()
    for connector in connectors:
        task = observe_and_insert(connector, db)
        scheduler.add_task(Task(task, 15))

    await scheduler.run_tasks()


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
