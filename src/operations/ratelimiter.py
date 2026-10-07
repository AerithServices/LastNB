import asyncio
import logging
import time
from typing import Dict, Optional, Callable, Any
from collections import defaultdict


logging.getLogger("discord.http").setLevel(logging.ERROR)


class RateLimiter:
    def __init__(self, requests_per_second: float = 45.0, max_burst: int = 50):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.max_burst = max_burst
        self.tokens = float(max_burst)
        self.last_update = time.monotonic()
        self.lock = asyncio.Lock()
        self.bucket_reset_times: Dict[str, float] = {}
        self.global_semaphore = asyncio.Semaphore(max_burst)

    async def acquire(self, bucket: str = "global") -> None:
        await self.global_semaphore.acquire()
        async with self.lock:
            now = time.monotonic()
            
            if bucket in self.bucket_reset_times:
                reset_time = self.bucket_reset_times[bucket]
                if now < reset_time:
                    await asyncio.sleep(reset_time - now)
            
            elapsed = now - self.last_update
            self.tokens = min(self.max_burst, self.tokens + elapsed * self.requests_per_second)
            
            if self.tokens >= 1.0:
                self.tokens -= 1.0
                self.last_update = now
            else:
                wait_time = (1.0 - self.tokens) / self.requests_per_second
                self.tokens = 0.0
                self.last_update = now + wait_time
                await asyncio.sleep(wait_time)

    def release(self) -> None:
        self.global_semaphore.release()

    def handle_rate_limit(self, bucket: str, retry_after: float) -> None:
        self.bucket_reset_times[bucket] = time.monotonic() + retry_after

    async def execute_with_retry(
        self,
        bucket: str,
        func: Callable[..., Any],
        *args,
        max_retries: int = 3,
        **kwargs
    ) -> Any:
        for attempt in range(max_retries):
            await self.acquire(bucket)
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                if hasattr(e, 'status') and e.status == 429:
                    retry_after = getattr(e, 'retry_after', 1.0)
                    self.handle_rate_limit(bucket, retry_after)
                    await asyncio.sleep(retry_after)
                    print(f"rate limit hit for bucket {bucket}, retrying after {retry_after} seconds (attempt {attempt + 1}/{max_retries})")
                else:
                    raise
            finally:
                self.release()
        raise Exception(f"Max retries exceeded for bucket {bucket}")

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, *args):
        self.release()


class BucketRateLimiter:
    def __init__(self):
        self.buckets: Dict[str, asyncio.Semaphore] = {}
        self.bucket_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.global_semaphore = asyncio.Semaphore(10)
        self.global_lock = asyncio.Lock()

    def _get_bucket(self, key: str, limit: int) -> asyncio.Semaphore:
        if key not in self.buckets:
            self.buckets[key] = asyncio.Semaphore(limit)
        return self.buckets[key]

    async def acquire(self, bucket_key: str, limit: int = 5) -> None:
        await self.global_semaphore.acquire()
        bucket = self._get_bucket(bucket_key, limit)
        await bucket.acquire()

    def release(self, bucket_key: str) -> None:
        if bucket_key in self.buckets:
            self.buckets[bucket_key].release()
        self.global_semaphore.release()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


rate_limiter = RateLimiter(requests_per_second=45.0, max_burst=50)
bucket_limiter = BucketRateLimiter()