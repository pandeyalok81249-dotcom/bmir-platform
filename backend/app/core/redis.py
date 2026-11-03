import asyncio
import json
import logging
from typing import Any, Dict, Optional
import redis.asyncio as aioredis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis pool and connection state tracking
_redis_client: Optional[aioredis.Redis] = None
_redis_last_check: float = 0.0
_redis_failed: bool = False


async def get_redis() -> Optional[aioredis.Redis]:
    """
    Returns an active async Redis connection client.
    Returns None if Redis is unreachable or unconfigured.
    Caches connection failures to prevent blocking event loop on repeated timeouts.
    """
    global _redis_client, _redis_last_check, _redis_failed
    if _redis_client is not None:
        return _redis_client

    try:
        now = asyncio.get_running_loop().time()
    except RuntimeError:
        now = 0.0

    # If recent connection attempt failed, avoid repeating synchronous socket timeouts
    if _redis_failed and (now - _redis_last_check < 15.0):
        return None

    _redis_last_check = now
    try:
        timeout = 0.3 if settings.ENVIRONMENT in ["development", "testing"] else 2.0
        client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=timeout,
        )
        await client.ping()
        _redis_client = client
        _redis_failed = False
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis is unavailable at {settings.REDIS_URL}: {str(e)}")
        _redis_client = None
        _redis_failed = True
        return None


class JobQueueManager:
    """
    Asynchronous task and state manager for resume intelligence analysis jobs.
    Uses Redis when available, with in-process state coordination fallback.
    """
    _in_memory_jobs: Dict[str, Dict[str, Any]] = {}
    _in_memory_tasks: Dict[str, asyncio.Task] = {}

    @classmethod
    async def set_job_status(
        cls,
        job_id: str,
        status: str,  # queued, reading_document, extracting_evidence, reasoning_evaluation, completed, failed, cancelled
        stage_description: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
    ) -> None:
        payload = {
            "job_id": job_id,
            "status": status,
            "stage_description": stage_description,
            "result": result,
            "error": error,
        }
        r = await get_redis()
        if r:
            try:
                await r.set(f"job:{job_id}", json.dumps(payload), ex=3600)
                return
            except Exception as e:
                logger.warning(f"Failed to persist job status to Redis: {e}")

        # Fallback in-memory
        cls._in_memory_jobs[job_id] = payload

    @classmethod
    async def get_job_status(cls, job_id: str) -> Optional[Dict[str, Any]]:
        r = await get_redis()
        if r:
            try:
                raw = await r.get(f"job:{job_id}")
                if raw:
                    return json.loads(raw)
            except Exception as e:
                logger.warning(f"Failed to retrieve job status from Redis: {e}")

        return cls._in_memory_jobs.get(job_id)

    @classmethod
    def register_async_task(cls, job_id: str, task: asyncio.Task) -> None:
        cls._in_memory_tasks[job_id] = task

    @classmethod
    async def cancel_job(cls, job_id: str) -> bool:
        if job_id in cls._in_memory_tasks:
            task = cls._in_memory_tasks[job_id]
            if not task.done():
                task.cancel()
                await cls.set_job_status(
                    job_id=job_id,
                    status="cancelled",
                    stage_description="Analysis cancelled by user.",
                )
                return True
        return False

