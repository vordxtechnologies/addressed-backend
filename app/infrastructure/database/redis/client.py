import redis

redis_client = redis.StrictRedis.from_url("redis://localhost:6379/0")

def cache_data(key, value, expiration=3600):
    redis_client.setex(key, expiration, value)

def get_cached_data(key):
    return redis_client.get(key)