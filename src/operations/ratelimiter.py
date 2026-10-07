import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_concurrent: int = 5, global_rate_limit: float = 0.1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.global_rate_limit = global_rate_limit
        self.last_request: Dict[str, float] = defaultdict(float)
        self.bucket_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        self.global_lock = asyncio.Lock()
        self.last_global_request = 0.0

    async def acquire(self, bucket: str = "global") -> None:
        await self.semaphore.acquire()
        try:
            await self._wait_for_bucket(bucket)
            await self._wait_global()
        except Exception:
            self.semaphore.release()
            raise

    def release(self) -> None:
        self.semaphore.release()

    async def _wait_for_bucket(self, bucket: str) -> None:
        lock = self.bucket_locks[bucket]
        async with lock:
            now = time.monotonic()
            elapsed = now - self.last_request[bucket]
            if elapsed < self.global_rate_limit:
                await asyncio.sleep(self.global_rate_limit - elapsed)
            self.last_request[bucket] = time.monotonic()

    async def _wait_global(self) -> None:
        async with self.global_lock:
            now = time.monotonic()
            elapsed = now - self.last_global_request
            if elapsed < self.global_rate_limit:
                await asyncio.sleep(self.global_rate_limit - elapsed)
            self.last_global_request = time.monotonic()

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


rate_limiter = RateLimiter(max_concurrent=3, global_rate_limit=0.2)
bucket_limiter = BucketRateLimiter()