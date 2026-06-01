import asyncio
import logging

from collections.abc import Callable, Coroutine
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Task:
    def __init__(self, coro_task: Callable[[], Coroutine], period_sec: int = 60):
        self.coro_task = coro_task
        self.period_sec = period_sec


class Scheduler:
    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    async def _run(self) -> int:
        async with asyncio.TaskGroup() as tg:
            # TODO exception handling
            tasks = [tg.create_task(t.coro_task()) for t in self.tasks]

        for task in tasks:
            logger.info(str(task.result()))

        # TODO make each task run on its own period
        sleep_time = 120
        for task in self.tasks:
            sleep_time = min(sleep_time, task.period_sec)

        return sleep_time

    async def run_tasks(self):
        try:
            while True:
                sleep_time = await self._run()
                await asyncio.sleep(sleep_time)
        except Exception as e:
            logger.exception(f"Exception while running task: {e}")
        finally:
            logger.info("Scheduler got cancellation, terminating")
