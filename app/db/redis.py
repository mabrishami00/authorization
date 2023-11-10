import redis.asyncio as redis
from core.config import settings

async def get_redis():
    pool = redis.ConnectionPool.from_url(settings.REDIS_URL)
    try:
        client = redis.Redis.from_pool(pool)
        yield client
    finally:
        await client.close()

async def get_redis_email():
    pool = redis.ConnectionPool.from_url(settings.REDIS_EMIL_URL)
    try:
        client = redis.Redis.from_pool(pool)
        yield client
    finally:
        await client.close()