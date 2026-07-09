from handlers import BaseHandler # Assuming BaseHandler is still in handlers.py
from models import PipelineContext
from redis_client import get_redis_client

class RedisRateLimitHandler(BaseHandler):
    def __init__(self):
        self.redis = get_redis_client()
        
        # Define limits per tier (Requests per minute)
        self.tier_limits = {
            "premium": 1000,
            "free": 10
        }
        self.window_seconds = 60

    async def handle(self, context: PipelineContext) -> PipelineContext:
        # Determine the limit based on the tenant's tier
        limit = self.tier_limits.get(context.rate_limit_tier, 10)
        
        # Create a unique Redis key for this tenant
        redis_key = f"rate_limit:{context.tenant_id}"
        
        # Atomically increment the counter in Redis
        current_requests = await self.redis.incr(redis_key)
        
        # If this is the first request in the window, set the expiration timer
        if current_requests == 1:
            await self.redis.expire(redis_key, self.window_seconds)
            
        # Check if they breached the limit
        if current_requests > limit:
            context.is_blocked = True
            context.block_reason = f"Redis Rate Limit Exceeded: {limit} requests per {self.window_seconds}s allowed."
            return context  # Short-circuit the chain
            
        return await super().handle(context)