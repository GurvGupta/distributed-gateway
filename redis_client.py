import redis.asyncio as redis

# In a real project, pull these from environment variables
REDIS_HOST = "localhost"
REDIS_PORT = 6379

# Create a robust connection pool
redis_pool = redis.ConnectionPool.from_url(
    f"redis://{REDIS_HOST}:{REDIS_PORT}", 
    decode_responses=True
)

def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=redis_pool)