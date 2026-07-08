from abc import ABC, abstractmethod
from models import PipelineContext
from factory import TenantConfigFactory
import time

class IHandler(ABC):
    @abstractmethod
    def set_next(self, handler: 'IHandler') -> 'IHandler':
        pass

    @abstractmethod
    async def handle(self, context: PipelineContext) -> PipelineContext:
        pass

class BaseHandler(IHandler):
    _next_handler: IHandler = None

    def set_next(self, handler: 'IHandler') -> 'IHandler':
        self._next_handler = handler
        return handler

    async def handle(self, context: PipelineContext) -> PipelineContext:
        if self._next_handler:
            return await self._next_handler.handle(context)
        return context

class RateLimitHandler(BaseHandler):
    async def handle(self, context: PipelineContext) -> PipelineContext:
        # Simple simulated rate limiting constraint
        # In V2, you would connect this to a Redis distributed token bucket
        if context.rate_limit_tier == "free" and "block_me" in context.payload.lower():
            context.is_blocked = True
            context.block_reason = "Rate limit exceeded for Free Tier profile."
            return context  # Short-circuit the chain
            
        return await super().handle(context)

class DeepPayloadInspectionHandler(BaseHandler):
    async def handle(self, context: PipelineContext) -> PipelineContext:
        # Dynamically fetch the scanning strategies via the Factory pattern
        strategies = TenantConfigFactory.get_strategies_for_tenant(context.tenant_id)
        
        for strategy in strategies:
            result = strategy.scan(context.payload)
            context.scan_results.append(result)
            
            # Block request immediately if a high-severity strategy violation occurs
            if not result.passed and result.risk_score >= 0.8:
                context.is_blocked = True
                context.block_reason = f"Security Policy Violation flagged by: {strategy.name}"
                return context  # Short-circuit the chain
                
        return await super().handle(context)