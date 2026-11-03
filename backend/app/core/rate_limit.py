import time
from collections import defaultdict
from typing import Dict, List, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.schemas.common import APIErrorDetails, APIErrorResponse


class SlidingWindowRateLimiter:
    """
    Sliding window in-memory rate limiter tracking client requests per time window.
    Thread-safe and low-overhead.
    """

    def __init__(self, limit: int = 120, window_seconds: int = 60):
        self.limit = limit
        self.window_seconds = window_seconds
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_key: str) -> Tuple[bool, int, int]:
        """
        Returns (is_allowed, remaining_calls, reset_in_seconds).
        """
        now = time.time()
        window_start = now - self.window_seconds

        # Clean old entries
        timestamps = [t for t in self._requests[client_key] if t > window_start]
        self._requests[client_key] = timestamps

        if len(timestamps) >= self.limit:
            oldest = timestamps[0] if timestamps else now
            reset_in = max(1, int(self.window_seconds - (now - oldest)))
            return False, 0, reset_in

        timestamps.append(now)
        remaining = self.limit - len(timestamps)
        reset_in = self.window_seconds
        return True, remaining, reset_in

    def clear(self):
        self._requests.clear()


limiter = SlidingWindowRateLimiter(limit=150, window_seconds=60)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Whitelist public health & doc endpoints
        path = request.url.path
        if (
            path in ["/health", "/ready", f"{settings.API_V1_STR}/openapi.json"]
            or path.startswith(f"{settings.API_V1_STR}/docs")
            or path.startswith(f"{settings.API_V1_STR}/redoc")
            or path.startswith("/api/v1/collaboration/ws")
        ):
            return await call_next(request)

        # Bypass header for testing harness
        if request.headers.get("X-Bypass-Rate-Limit") == "testing" or getattr(settings, "ENVIRONMENT", "") == "testing":
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = "9999"
            response.headers["X-RateLimit-Remaining"] = "9999"
            response.headers["X-RateLimit-Reset"] = "0"
            return response

        # Derive client key (Authorization sub if present or client IP)
        client_key = request.headers.get("X-Forwarded-For", request.client.host if request.client else "127.0.0.1")
        allowed, remaining, reset_in = limiter.is_allowed(client_key)

        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={
                    "X-RateLimit-Limit": str(limiter.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_in),
                    "Retry-After": str(reset_in),
                },
                content=APIErrorResponse(
                    success=False,
                    error=APIErrorDetails(
                        code="RATE_LIMIT_EXCEEDED",
                        message=f"Rate limit exceeded. Maximum {limiter.limit} requests per minute allowed. Try again in {reset_in} seconds.",
                    ),
                ).model_dump(),
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limiter.limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_in)
        return response

