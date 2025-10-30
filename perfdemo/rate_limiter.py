from __future__ import annotations

import asyncio
import time


class RateLimiter:
    """Token Bucket 算法的异步速率限制器

    Args:
        rate: 每秒产生的令牌数（例如 200 表示 200 QPS）。
        burst: 桶的最大容量，若为 None 则默认为 rate。
        init_tokens: 初始令牌数，若为 None 则默认为最大容量。
    """

    def __init__(
        self, rate: float, burst: float | None = None, init_tokens: float | None = None
    ) -> None:
        self._rate = float(rate)
        self._cap = float(burst if burst is not None else rate)
        self._tokens = float(init_tokens if init_tokens is not None else self._cap)
        self._tokens = min(self._tokens, self._cap)
        self._t_last = time.perf_counter()
        self._lock = asyncio.Lock()

    async def acquire(self, n: float = 1.0) -> None:
        """获取 n 个令牌（不足时自动等待）。"""
        if not (n <= self._cap):
            raise AssertionError(
                f"requested tokens exceed bucket capacity, n={n}, cap={self._cap}"
            )
        while True:
            async with self._lock:
                now = time.perf_counter()
                # 根据时间差补充令牌（elapsed * rate），并限制不超过最大容量
                elapsed = now - self._t_last
                self._t_last = now
                self._tokens = min(self._cap, self._tokens + elapsed * self._rate)
                if self._tokens >= n:
                    self._tokens -= n
                    return
                # 计算需要等待的时间
                need = n - self._tokens
                wait = need / self._rate
            await asyncio.sleep(wait)
