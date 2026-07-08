from typing import Dict, Any, List
from strategies import IScanningStrategy, SecretScanningStrategy, PiiScanningStrategy
from cache import ThreadSafeLRUCache
import time

class TenantConfigFactory:
    # Initialize the LRU Cache with a capacity of 1000 tenant records
    _metadata_cache = ThreadSafeLRUCache(capacity=1000)

    # Simulating a slow database
    _database_mock: Dict[str, Dict[str, Any]] = {
        "tenant_alpha": {"rate_limit_tier": "premium", "strategies": ["SecretDetector"]},
        "tenant_beta": {"rate_limit_tier": "free", "strategies": ["SecretDetector", "PiiDetector"]}
    }

    @classmethod
    def get_metadata(cls, tenant_id: str) -> Dict[str, Any]:
        # 1. Cache HIT: Return instantly
        cached_config = cls._metadata_cache.get(tenant_id)
        if cached_config:
            print(f"[CACHE HIT] Loaded config for {tenant_id}")
            return cached_config

        # 2. Cache MISS: Simulate a slow database query (e.g., 50ms network hop)
        print(f"[CACHE MISS] Querying database for {tenant_id}...")
        time.sleep(0.05) 
        
        db_config = cls._database_mock.get(tenant_id, {"rate_limit_tier": "free", "strategies": []})
        
        # 3. Store the result in the LRU cache for subsequent requests
        cls._metadata_cache.put(tenant_id, db_config)
        
        return db_config

    @classmethod
    def get_strategies_for_tenant(cls, tenant_id: str) -> List[IScanningStrategy]:
        config = cls.get_metadata(tenant_id)
        strategies = []
        for name in config.get("strategies", []):
            if name == "SecretDetector":
                strategies.append(SecretScanningStrategy())
            elif name == "PiiDetector":
                strategies.append(PiiScanningStrategy())
        return strategies if strategies else [SecretScanningStrategy()]