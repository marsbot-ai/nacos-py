"""
Utility functions for Nacos-Py client.
"""
import hashlib
import json
import random
import time
from typing import Dict, Any, Optional, List


def get_current_time_millis() -> int:
    """Get current time in milliseconds."""
    return int(time.time() * 1000)


def get_current_time_secs() -> int:
    """Get current time in seconds."""
    return int(time.time())


def generate_nonce(length: int = 6) -> str:
    """Generate a random nonce string."""
    return ''.join(random.choices('0123456789', k=length))


def md5_hash(content: str) -> str:
    """Calculate MD5 hash of content."""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def encode_param(param: Any) -> str:
    """Encode parameter to string."""
    if param is None:
        return ""
    return str(param)


def build_query_string(params: Dict[str, Any]) -> str:
    """Build URL query string from parameters."""
    if not params:
        return ""
    
    query_parts = []
    for key, value in params.items():
        if value is not None:
            from urllib.parse import quote
            query_parts.append(f"{key}={quote(encode_param(value))}")
    
    return "&".join(query_parts)


def parse_json_response(content: str) -> Optional[Dict[str, Any]]:
    """Parse JSON response content."""
    if not content:
        return None
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def is_valid_ip(ip: str) -> bool:
    """Check if IP address is valid."""
    import re
    pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return bool(re.match(pattern, ip))


def is_valid_port(port: int) -> bool:
    """Check if port number is valid."""
    return isinstance(port, int) and 1 <= port <= 65535


def select_random_server(servers: List[str]) -> str:
    """Randomly select a server from the list."""
    return random.choice(servers)


class LRUCache:
    """Simple LRU Cache implementation."""
    
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.cache: Dict[str, Any] = {}
        self.keys: List[str] = []
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            # Move to end (most recently used)
            self.keys.remove(key)
            self.keys.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any):
        if key in self.cache:
            self.keys.remove(key)
        elif len(self.cache) >= self.capacity:
            # Remove least recently used
            oldest = self.keys.pop(0)
            del self.cache[oldest]
        
        self.cache[key] = value
        self.keys.append(key)
    
    def remove(self, key: str):
        if key in self.cache:
            self.keys.remove(key)
            del self.cache[key]
    
    def clear(self):
        self.cache.clear()
        self.keys.clear()


def weighted_random_choice(choices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Select an instance based on weighted random algorithm.
    
    Args:
        choices: List of instances with 'weight' key
        
    Returns:
        Selected instance or None if list is empty
    """
    if not choices:
        return None
    
    total_weight = sum(c.get('weight', 1) for c in choices)
    if total_weight <= 0:
        return random.choice(choices)
    
    random_weight = random.uniform(0, total_weight)
    current_weight = 0
    
    for choice in choices:
        current_weight += choice.get('weight', 1)
        if current_weight >= random_weight:
            return choice
    
    return choices[-1]
