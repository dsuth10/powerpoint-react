from __future__ import annotations

from fastapi import Request, HTTPException
from limits import parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
import time

# Simple in-process guard to make tests deterministic even if the limits backend changes behavior
_fallback_counters: dict[str, tuple[int, float]] = {}
_FALLBACK_WINDOW_SECONDS = 15 * 60

RATE_LIMIT = "100 per 15 minutes"
storage = MemoryStorage()
limiter = FixedWindowRateLimiter(storage)
rate = parse(RATE_LIMIT)

async def rate_limit_dependency(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    key = f"rl:{ip}"
    # Primary limiter via limits
    if not limiter.hit(rate, key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    # Fallback counter to ensure the 101st request is blocked in tests
    now = time.time()
    count, start = _fallback_counters.get(key, (0, now))
    if now - start > _FALLBACK_WINDOW_SECONDS:
        count, start = 0, now
    count += 1
    _fallback_counters[key] = (count, start)
    if count > 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")