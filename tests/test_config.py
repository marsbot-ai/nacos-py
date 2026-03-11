"""
Unit tests for ConfigManager.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock

from nacos.config import ConfigManager
from nacos.exceptions import NacosConfigException


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_http = Mock()
        self.manager = ConfigManager(
            http_client=self.mock_http,
            namespace="public",
        )
    
    def test_get_config_success(self):
        """Test successful config retrieval."""
        self.mock_http.get.return_value = (200, "key=value")
        
        result = self.manager.get_config("test-data", "DEFAULT_GROUP")
        
        self.assertEqual(result, "key=value")
        self.mock_http.get.assert_called_once()
    
    def test_get_config_not_found(self):
        """Test config not found."""
        self.mock_http.get.return_value = (404, "config not found")
        
        result = self.manager.get_config("test-data", "DEFAULT_GROUP")
        
        self.assertIsNone(result)
    
    def test_get_config_failure(self):
        """Test failed config retrieval."""
        self.mock_http.get.return_value = (500, "server error")
        
        with self.assertRaises(NacosConfigException):
            self.manager.get_config("test-data", "DEFAULT_GROUP")
    
    def test_publish_config_success(self):
        """Test successful config publish."""
        self.mock_http.post.return_value = (200, "true")
        
        result = self.manager.publish_config(
            data_id="test-data",
            group="DEFAULT_GROUP",
            content="key=value",
        )
        
        self.assertTrue(result)
        self.mock_http.post.assert_called_once()
    
    def test_publish_config_failure(self):
        """Test failed config publish."""
        self.mock_http.post.return_value = (200, "false")
        
        with self.assertRaises(NacosConfigException):
            self.manager.publish_config(
                data_id="test-data",
                group="DEFAULT_GROUP",
                content="key=value",
            )
    
    def test_remove_config_success(self):
        """Test successful config removal."""
        self.mock_http.delete.return_value = (200, "true")
        
        result = self.manager.remove_config("test-data", "DEFAULT_GROUP")
        
        self.assertTrue(result)
        self.mock_http.delete.assert_called_once()
    
    def test_remove_config_failure(self):
        """Test failed config removal."""
        self.mock_http.delete.return_value = (200, "false")
        
        with self.assertRaises(NacosConfigException):
            self.manager.remove_config("test-data", "DEFAULT_GROUP")
    
    def test_add_listener(self):
        """Test adding config listener."""
        callback = Mock()
        
        result = self.manager.add_listener(
            data_id="test-data",
            group="DEFAULT_GROUP",
            callback=callback,
        )
        
        self.assertTrue(result)
        
        # Cleanup
        self.manager.remove_listener("test-data", "DEFAULT_GROUP")
    
    def test_remove_listener(self):
        """Test removing config listener."""
        callback = Mock()
        
        # Add listener first
        self.manager.add_listener(
            data_id="test-data",
            group="DEFAULT_GROUP",
            callback=callback,
        )
        
        # Then remove it
        result = self.manager.remove_listener(
            data_id="test-data",
            group="DEFAULT_GROUP",
            callback=callback,
        )
        
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
