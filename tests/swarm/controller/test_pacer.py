# Test pacer
import pytest
import asyncio
from nanobot.swarm.controller.pacer import Pacer


@pytest.mark.asyncio
async def test_pacer_concurrency():
    pacer = Pacer(max_concurrent=2, delay_between_seconds=0.01)

    results = []

    async def task(i):
        async with pacer:
            results.append(i)
            await asyncio.sleep(0.01)

    await asyncio.gather(*[task(i) for i in range(4)])
    # First 2 should start before any complete
    assert len(results) == 4


@pytest.mark.asyncio
async def test_pacer_sequential():
    pacer = Pacer(max_concurrent=1, delay_between_seconds=0.01)

    results = []

    async def task(i):
        async with pacer:
            results.append(i)

    await asyncio.gather(*[task(i) for i in range(3)])
    assert len(results) == 3
