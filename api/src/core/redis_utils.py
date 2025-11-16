import json
from collections.abc import Mapping, Sequence
from datetime import datetime
from typing import TypeVar

from redis.exceptions import ConnectionError

from src.core.config import Errors
from src.core.redis_db import redis_client
from src.exceptions.external import ExternalServiceError

T = TypeVar("T")

RedisEncodable = str | int | float | bool | None | datetime | Mapping[str, object] | Sequence[object] | object


def serialize_for_redis(value: RedisEncodable) -> str:
    """
    Safely serialize any Python object into a Redis-compatible string.
    Converts Pydantic models, dataclasses, datetime, or arbitrary objects to JSON.
    """
    if value is None:
        return ""

    if isinstance(value, str | int | float | bool):
        return str(value)

    if isinstance(value, datetime):
        return value.isoformat()

    if hasattr(value, "model_dump"):
        return json.dumps(value.model_dump(), default=str)

    if hasattr(value, "__dataclass_fields__"):
        from dataclasses import asdict

        return json.dumps(asdict(value), default=str)

    try:
        return json.dumps(value, default=str)
    except Exception:
        return str(value)


def redis_set(key: str, value: RedisEncodable, ex: int | None = None) -> None:
    """
    Wrapper around redis.set that serializes data before saving.
    ex = expiry in seconds (optional)
    """
    try:
        serialized_value = serialize_for_redis(value)
        redis_client.set(key, serialized_value, ex=ex)
    except ConnectionError as e:
        raise ExternalServiceError(Errors.REDIS_CONNECTION_ERROR.value, details={"error": str(e)}) from e
    except Exception as e:
        raise ExternalServiceError(details={"error": str(e)}) from e


def redis_get(key: str, model: type[T] | None = None) -> T | str | None:
    """
    Wrapper around redis.get that optionally deserializes into a model.
    """
    try:
        raw_value = redis_client.get(key)
        if not raw_value:
            return None

        if model:
            data = json.loads(raw_value)
            return model(**data)
        return raw_value
    except ConnectionError as e:
        raise ExternalServiceError(Errors.REDIS_CONNECTION_ERROR.value, details={"error": str(e)}) from e
    except json.JSONDecodeError:
        return raw_value
    except Exception as e:
        raise ExternalServiceError(details={"error": str(e)}) from e
