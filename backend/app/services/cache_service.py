"""
Redis-based caching service for Gemini API responses
Reduces latency by caching expensive API calls
"""

import redis
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
from app.config import get_settings

settings = get_settings()

# Global Redis client (lazy-loaded)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create Redis client with connection pooling"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
    return _redis_client


def generate_cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate a unique cache key from function arguments
    Uses SHA256 hash of serialized arguments
    """
    # Create a deterministic representation of arguments
    key_data = {
        "args": args,
        "kwargs": kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True)
    key_hash = hashlib.sha256(key_string.encode()).hexdigest()
    return f"hirehub:{prefix}:{key_hash}"


def get_cached(key: str) -> Optional[Any]:
    """
    Retrieve cached value from Redis
    Returns None if key doesn't exist or on error
    """
    try:
        client = get_redis_client()
        cached_value = client.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except redis.RedisError as e:
        print(f"⚠️  Redis get error: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"⚠️  Cache decode error: {e}")
        return None


def set_cached(key: str, value: Any, ttl: Optional[int] = None) -> bool:
    """
    Store value in Redis cache with TTL
    Returns True if successful, False otherwise
    """
    try:
        client = get_redis_client()
        ttl = ttl or settings.CACHE_TTL
        serialized_value = json.dumps(value)
        client.setex(key, ttl, serialized_value)
        return True
    except redis.RedisError as e:
        print(f"⚠️  Redis set error: {e}")
        return False
    except (TypeError, ValueError) as e:
        print(f"⚠️  Cache serialization error: {e}")
        return False


def delete_cached(key: str) -> bool:
    """Delete a specific cache key"""
    try:
        client = get_redis_client()
        client.delete(key)
        return True
    except redis.RedisError as e:
        print(f"⚠️  Redis delete error: {e}")
        return False


def clear_cache_pattern(pattern: str = "hirehub:*") -> int:
    """
    Clear all cache keys matching a pattern
    Returns number of keys deleted
    """
    try:
        client = get_redis_client()
        keys = list(client.scan_iter(match=pattern))
        if keys:
            return client.delete(*keys)
        return 0
    except redis.RedisError as e:
        print(f"⚠️  Redis clear error: {e}")
        return 0


def cached(prefix: str, ttl: Optional[int] = None):
    """
    Decorator for caching function results in Redis

    Usage:
        @cached("cv_parse")
        def parse_cv(text: str) -> dict:
            # Expensive operation
            return result
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = generate_cache_key(prefix, *args, **kwargs)

            # Try to get cached result
            cached_result = get_cached(cache_key)
            if cached_result is not None:
                print(f"✅ Cache hit: {prefix}")
                return cached_result

            # Execute function if cache miss
            print(f"⚠️  Cache miss: {prefix}")
            result = func(*args, **kwargs)

            # Store result in cache
            set_cached(cache_key, result, ttl)

            return result

        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """Get Redis cache statistics"""
    try:
        client = get_redis_client()
        info = client.info("stats")
        return {
            "total_connections": info.get("total_connections_received", 0),
            "total_commands": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": round(
                info.get("keyspace_hits", 0) /
                max(info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1) * 100,
                2
            )
        }
    except redis.RedisError as e:
        print(f"⚠️  Redis stats error: {e}")
        return {}


def is_redis_available() -> bool:
    """Check if Redis is available"""
    try:
        client = get_redis_client()
        client.ping()
        return True
    except redis.RedisError:
        return False
