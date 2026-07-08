from collections import OrderedDict
import threading
from typing import Any, Optional

class ThreadSafeLRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.lock = threading.Lock()

    def get(self, key: str) -> Optional[Any]:
        with self.lock:
            if key not in self.cache:
                return None
            # Move the accessed item to the end (marking it as most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        with self.lock:
            if key in self.cache:
                # Update existing value and mark as recently used
                self.cache.move_to_end(key)
            self.cache[key] = value
            
            # Evict the Least Recently Used item if capacity is exceeded
            if len(self.cache) > self.capacity:
                # popitem(last=False) removes the first item added (the oldest)
                self.cache.popitem(last=False)