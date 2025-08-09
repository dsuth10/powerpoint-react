from fastapi import Request, HTTPException, status, Depends
from limits import RateLimitItemPerMinute, parse
from limits.storage import MemoryStorage
from limits.strategies import FixedWindowRateLimiter
import time

RATE_LIMIT = "100 per 15 minutes"
storage = MemoryStorage()
limiter = FixedWindowRateLimiter(storage)
rate = parse(RATE_LIMIT)

async def rate_limit_dependency(request: Request):
    ip = request.headers.get("x-forwarded-for", request.client.host)
    key = f"rl:{ip}"
    if not limiter.hit(rate, key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded") 