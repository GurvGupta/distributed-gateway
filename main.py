from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from models import PipelineContext
from factory import TenantConfigFactory
from handlers import RedisRateLimitHandler, DeepPayloadInspectionHandler

app = FastAPI(title="Distributed Guard API Gateway v1")

class GatewayRequest(BaseModel):
    payload: str

@app.post("/v1/proxy", status_code=status.HTTP_200_OK)
async def proxy_request(
    request_data: GatewayRequest, 
    x_tenant_id: str = Header(..., description="Unique ID assigned to the tenant client")
):
    # 1. Gather context details from the Factory
    tenant_meta = TenantConfigFactory.get_metadata(x_tenant_id)
    
    context = PipelineContext(
        tenant_id=x_tenant_id,
        rate_limit_tier=tenant_meta["rate_limit_tier"],
        active_strategies=tenant_meta["strategies"],
        payload=request_data.payload
    )
    
    # 2. Wire up the Chain of Responsibility Pipeline
    rate_limiter = RedisRateLimitHandler()
    payload_inspector = DeepPayloadInspectionHandler()

    rate_limiter.set_next(payload_inspector)
    
    # 3. Execute the chain pipeline
    processed_context = await rate_limiter.handle(context)
    
    # 4. Evaluate execution pipeline outcome
    if processed_context.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Gateway Rejected Request",
                "reason": processed_context.block_reason,
                "metrics": processed_context.scan_results
            }
        )
        
    return {
        "status": "Success",
        "upstream_forwarded": True,
        "scans_performed": [r.strategy_name for r in processed_context.scan_results]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)