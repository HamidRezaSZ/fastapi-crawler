import json
import os

import redis.asyncio as redis

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True
)


async def set_cache(key: str, value: str, ttl: int = 3600):
    if isinstance(value, (dict, list)):
        value = json.dumps(value, default=str)
    await redis_client.setex(key, ttl, value)


async def get_cache(key: str) -> str:
    return await redis_client.get(key)
