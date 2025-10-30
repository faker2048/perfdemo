"""所有演示函数"""

from __future__ import annotations

import asyncio
import os
import time
from concurrent.futures import ProcessPoolExecutor

from numba import set_num_threads

from perfdemo.async_utils import bounded_map
from perfdemo.rate_limiter import RateLimiter
from perfdemo.tasks import heavy_compute, heavy_compute_numba, io_task, order_task

try:
    import compute_ext

    HAS_CPP_EXT = True
except ImportError:
    print("未找到 compute_ext C++ 扩展，跳过相关演示")
    HAS_CPP_EXT = False


async def demo1_io() -> None:
    """Demo 1: 高并发 I/O 任务测试"""
    N = 10000
    t0 = time.perf_counter()
    res = await bounded_map(range(N), io_task, concurrency=256, retries=2, timeout=0.05)
    dt = time.perf_counter() - t0
    lat = sorted(lat for _, lat in res)
    p50 = lat[int(0.50 * len(lat))] * 1e3 if lat else 0.0
    p95 = lat[int(0.95 * len(lat))] * 1e3 if lat else 0.0
    p99 = lat[int(0.99 * len(lat))] * 1e3 if lat else 0.0
    print(
        f"完成 {len(res)} 条任务，耗时 {dt:.3f}s  吞吐≈{len(res) / dt:.0f}/s  "
        f"p50={p50:.1f}ms  p95={p95:.1f}ms  p99={p99:.1f}ms"
    )


async def demo2_order_with_qps() -> None:
    """Demo 2: 下单任务限流测试"""
    N2 = 1000
    limiter = RateLimiter(
        rate=200.0, burst=200.0, init_tokens=0
    )  # 每秒最多 200 个，支持 200 的瞬时突发
    t0 = time.perf_counter()

    async def rate_limited_order(i: int) -> int:
        await limiter.acquire(1.0)  # 每单消耗一个令牌
        return await order_task(i)

    # 高并发提交任务，实际速率由限流器控制
    _ = await bounded_map(
        range(N2), rate_limited_order, concurrency=2000, retries=0, timeout=None
    )
    dt2 = time.perf_counter() - t0
    print(f"共 {N2} 单完成，用时 {dt2:.3f}s  实际QPS≈{N2 / dt2:.1f} (目标≈200 QPS)")


async def demo3_heavy_compute_with_processpool() -> None:
    """Demo 3: Python 多进程池并行计算"""
    TOTAL_ITERS = 4_000_000_000
    num_workers = max(2, (os.cpu_count() or 2))
    loop = asyncio.get_running_loop()

    # ---- 预热：让每个进程各自编译一次（不计入统计）----
    with ProcessPoolExecutor(max_workers=num_workers) as pool:
        warmups = [
            loop.run_in_executor(pool, heavy_compute, 10_000)
            for _ in range(num_workers)
        ]
        await asyncio.gather(*warmups)

    # ---- 按进程数把 TOTAL_ITERS 均分（尽量平均，处理余数）----
    base = TOTAL_ITERS // num_workers
    rem = TOTAL_ITERS % num_workers
    parts = [base + (1 if i < rem else 0) for i in range(num_workers)]

    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=num_workers) as pool:
        tasks = [loop.run_in_executor(pool, heavy_compute, n) for n in parts]
        results = await asyncio.gather(*tasks)
    dt = time.perf_counter() - t0

    total = sum(results)
    print(
        f"进程池并行：{num_workers} 个工作进程，总 {TOTAL_ITERS:,} 次循环，用时 {dt:.3f}s，"
        f"吞吐≈{TOTAL_ITERS/dt/1e6:.2f} M it/s，校验和={total:.3e}"
    )


async def demo4_heavy_compute_with_numba_parallel() -> None:
    """Demo 4: Numba JIT 并行计算"""
    TOTAL_ITERS = 4_000_000_000
    threads = os.cpu_count() or 8
    set_num_threads(threads)

    # 预热：触发 JIT 编译（不计入统计）
    _ = heavy_compute_numba(10_000)

    t0 = time.perf_counter()
    total = heavy_compute_numba(TOTAL_ITERS)  # 与 demo3 相同总量
    dt = time.perf_counter() - t0

    print(
        f"Numba 并行：{threads} 线程，总 {TOTAL_ITERS:,} 次循环，用时 {dt:.3f}s，"
        f"吞吐≈{TOTAL_ITERS/dt/1e6:.2f} M it/s，校验和={total:.3e}"
    )


async def demo5_heavy_compute_with_cpp_openmp() -> None:
    """Demo 5: C++ OpenMP 并行计算"""
    if not HAS_CPP_EXT:
        print("跳过 demo5：C++ 扩展未编译")
        return

    TOTAL_ITERS = 4_000_000_000
    threads = os.cpu_count() or 8

    # 预热：确保代码缓存已加载
    _ = compute_ext.heavy_compute_cpp_parallel(10_000, threads)

    t0 = time.perf_counter()
    total = compute_ext.heavy_compute_cpp_parallel(TOTAL_ITERS, threads)
    dt = time.perf_counter() - t0

    print(
        f"C++ OpenMP：{threads} 线程，总 {TOTAL_ITERS:,} 次循环，用时 {dt:.3f}s，"
        f"吞吐≈{TOTAL_ITERS/dt/1e6:.2f} M it/s，校验和={total:.3e}"
    )


async def run_all_demos() -> None:
    """运行所有演示"""
    # demo 1：高并发 I/O 测试
    print("=== Demo 1：高并发 I/O 测试 ===")
    await demo1_io()

    # demo 2：下单任务限流测试（200 QPS）
    print("\n=== Demo 2：下单任务限流测试（200 QPS） ===")
    await demo2_order_with_qps()

    # demo 3：重计算任务 - 进程池并行
    print("\n=== Demo 3：重计算任务 - Python 进程池并行 ===")
    await demo3_heavy_compute_with_processpool()

    # demo 4：重计算任务 - Numba 并行
    print("\n=== Demo 4：重计算任务 - Numba JIT 并行 ===")
    await demo4_heavy_compute_with_numba_parallel()

    # demo 5：重计算任务 - C++ OpenMP 并行
    if HAS_CPP_EXT:
        print("\n=== Demo 5：重计算任务 - C++ OpenMP 并行 ===")
        await demo5_heavy_compute_with_cpp_openmp()
    else:
        print(
            "\n=== Demo 5：C++ 扩展未编译，已跳过 ==="
            "\n提示：运行 'python setup.py build_ext --inplace' 编译 C++ 扩展"
        )
