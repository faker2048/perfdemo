from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


async def _retry(
    fn: Callable[[], Awaitable[R]],
    *,
    retries: int = 2,
    base_delay: float = 0.05,
    timeout: float | None = 1.0,
) -> R:
    """执行异步函数，带重试与超时机制。

    Args:
        fn: 要执行的异步函数（不带参数的可调用对象）。
        retries: 最大重试次数。
        base_delay: 基础延迟时间（秒），用于计算退避间隔。
        timeout: 每次执行的超时时间（秒）；若为 None 则不设超时。

    Returns:
        异步函数成功执行后的返回值。

    """
    attempt = 0
    while True:
        try:
            if timeout is None:
                return await fn()
            return await asyncio.wait_for(fn(), timeout=timeout)
        except (asyncio.TimeoutError, OSError, RuntimeError) as exc:
            if attempt >= retries:
                raise exc
            # 指数退避 + 随机抖动
            await asyncio.sleep(base_delay * (2**attempt) + random.random() * base_delay)
            attempt += 1


async def bounded_map(
    items: Iterable[T],
    worker: Callable[[T], Awaitable[R]],
    *,
    concurrency: int = 256,
    retries: int = 1,
    timeout: float | None = 0.2,
) -> list[R]:
    """在高并发场景下执行异步任务，带并发限制与重试机制。

    Args:
        items: 输入元素的可迭代对象。
        worker: 对每个元素执行的异步处理函数。
        concurrency: 最大并发任务数量。
        retries: 每个任务的最大重试次数。
        timeout: 每个任务的超时时间（秒）；若为 None 则不设超时。

    Returns:
        所有成功任务的结果列表（失败任务被自动跳过）。
    """
    sem = asyncio.Semaphore(concurrency)
    seq = list(items)
    out: list[R | None] = [None] * len(seq)

    async def run_one(i: int, x: T) -> None:
        async with sem:
            out[i] = await _retry(lambda: worker(x), retries=retries, timeout=timeout)

    async with asyncio.TaskGroup() as tg:
        for i, x in enumerate(seq):
            tg.create_task(run_one(i, x))
    return [r for r in out if r is not None]
