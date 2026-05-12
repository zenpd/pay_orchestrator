from redis.asyncio import Redis
from shared.config import get_settings

settings = get_settings()
_redis: Redis | None = None


async def get_redis() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis
