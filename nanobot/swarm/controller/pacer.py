# Pacer for iteration control
import asyncio
from datetime import datetime


class Pacer:
    def __init__(self, max_concurrent: int = 3, delay_between_seconds: float = 5.0):
        self.max_concurrent = max_concurrent
        self.delay = delay_between_seconds
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._last_run = None

    async def __aenter__(self):
        await self._semaphore.acquire()
        if self._last_run:
            elapsed = (datetime.utcnow() - self._last_run).total_seconds()
            if elapsed < self.delay:
                await asyncio.sleep(self.delay - elapsed)
        self._last_run = datetime.utcnow()
        return self

    async def __aexit__(self, *args):
        self._semaphore.release()
