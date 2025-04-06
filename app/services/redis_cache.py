import json
import logging
import os

import redis.asyncio as redis

logger = logging.getLogger(__name__)

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


async def set_cache(key: str, value: str, ttl: int = 3600):
    try:
        if isinstance(value, (dict, list)):
            value = json.dumps(value, default=str)
        await redis_client.setex(key, ttl, value)
    except Exception as e:
        logger.warning(f"Redis error: {e}")


async def get_cache(key: str) -> str:
    try:
        return await redis_client.get(key)
    except Exception as e:
        logger.warning(f"Redis error: {e}")
        return None
