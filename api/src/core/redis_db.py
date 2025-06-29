import redis

from src.core.config import settings

redis_client = redis.Redis(host="localhost", port=settings.REDIS_PORT, db=0, decode_responses=True)
