from pydantic import BaseModel, Field
from typing import List, Optional

class ScanResult(BaseModel):
    strategy_name: str
    passed: bool
    findings: List[str] = Field(default_factory=list)
    risk_score: float = 0.0

class PipelineContext(BaseModel):
    tenant_id: str
    rate_limit_tier: str
    active_strategies: List[str]
    payload: str
    is_blocked: bool = False
    block_reason: Optional[str] = None
    scan_results: List[ScanResult] = Field(default_factory=list)