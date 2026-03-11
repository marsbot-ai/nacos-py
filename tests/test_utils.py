"""
Unit tests for utility functions.
"""
import unittest

from nacos.utils import (
    md5_hash,
    is_valid_ip,
    is_valid_port,
    weighted_random_choice,
    LRUCache,
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_md5_hash(self):
        """Test MD5 hash calculation."""
        result = md5_hash("test")
        self.assertEqual(len(result), 32)
        self.assertEqual(result, "098f6bcd4621d373cade4e832627b4f6")
    
    def test_is_valid_ip(self):
        """Test IP validation."""
        # Valid IPs
        self.assertTrue(is_valid_ip("127.0.0.1"))
        self.assertTrue(is_valid_ip("192.168.1.1"))
        self.assertTrue(is_valid_ip("255.255.255.255"))
        self.assertTrue(is_valid_ip("0.0.0.0"))
        
        # Invalid IPs
        self.assertFalse(is_valid_ip("256.1.1.1"))
        self.assertFalse(is_valid_ip("192.168.1"))
        self.assertFalse(is_valid_ip("192.168.1.1.1"))
        self.assertFalse(is_valid_ip("not-an-ip"))
        self.assertFalse(is_valid_ip(""))
    
    def test_is_valid_port(self):
        """Test port validation."""
        # Valid ports
        self.assertTrue(is_valid_port(1))
        self.assertTrue(is_valid_port(8080))
        self.assertTrue(is_valid_port(65535))
        
        # Invalid ports
        self.assertFalse(is_valid_port(0))
        self.assertFalse(is_valid_port(65536))
        self.assertFalse(is_valid_port(-1))
        self.assertFalse(is_valid_port("8080"))  # String, not int
    
    def test_weighted_random_choice(self):
        """Test weighted random selection."""
        choices = [
            {"name": "a", "weight": 1},
            {"name": "b", "weight": 2},
            {"name": "c", "weight": 3},
        ]
        
        # Test multiple selections
        results = []
        for _ in range(100):
            result = weighted_random_choice(choices)
            self.assertIn(result, choices)
            results.append(result["name"])
        
        # Higher weight items should appear more often (probabilistic)
        count_c = results.count("c")
        count_a = results.count("a")
        self.assertGreater(count_c, count_a)
    
    def test_weighted_random_choice_empty(self):
        """Test weighted random with empty list."""
        result = weighted_random_choice([])
        self.assertIsNone(result)
    
    def test_lru_cache_basic(self):
        """Test LRU cache basic operations."""
        cache = LRUCache(capacity=3)
        
        # Put items
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)
        
        # Get items
        self.assertEqual(cache.get("a"), 1)
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)
    
    def test_lru_cache_eviction(self):
        """Test LRU cache eviction."""
        cache = LRUCache(capacity=2)
        
        # Put items beyond capacity
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict "a"
        
        # "a" should be evicted
        self.assertIsNone(cache.get("a"))
        
        # "b" and "c" should still exist
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)
    
    def test_lru_cache_update(self):
        """Test LRU cache update."""
        cache = LRUCache(capacity=2)
        
        cache.put("a", 1)
        cache.put("a", 2)  # Update
        
        self.assertEqual(cache.get("a"), 2)
    
    def test_lru_cache_remove(self):
        """Test LRU cache remove."""
        cache = LRUCache(capacity=2)
        
        cache.put("a", 1)
        cache.remove("a")
        
        self.assertIsNone(cache.get("a"))
    
    def test_lru_cache_clear(self):
        """Test LRU cache clear."""
        cache = LRUCache(capacity=2)
        
        cache.put("a", 1)
        cache.put("b", 2)
        cache.clear()
        
        self.assertIsNone(cache.get("a"))
        self.assertIsNone(cache.get("b"))


if __name__ == "__main__":
    unittest.main()
