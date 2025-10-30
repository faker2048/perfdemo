from __future__ import annotations

import asyncio
import random
import time

from numba import njit, prange


async def io_task(n: int) -> tuple[int, float]:
    """模拟 I/O 操作：p50≈3ms，p95≈20ms，约 1% 的随机错误。"""
    t0 = time.perf_counter()
    await asyncio.sleep(random.expovariate(1 / 0.003) + random.random() * 0.002)
    if random.random() < 0.01:
        raise OSError("随机错误")
    return n, time.perf_counter() - t0


async def order_task(n: int) -> int:
    """模拟下单任务"""
    # 实际场景可替换为真实下单 API
    await asyncio.sleep(0.001)
    return n


@njit(fastmath=True, parallel=False, cache=False)
def heavy_compute(n: int) -> float:
    total = 0.0
    for i in range(n):
        x = i * 0.001
        total += x * x
    return total


@njit(fastmath=True, parallel=True, cache=False)
def heavy_compute_numba(n: int) -> float:
    total = 0.0
    # prange 让循环并行
    for i in prange(n):
        x = i * 0.001
        total += x * x
    return total
