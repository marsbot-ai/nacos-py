"""
Unit tests for ServiceManager.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock

from nacos.service import ServiceManager
from nacos.exceptions import NacosServiceException


class TestServiceManager(unittest.TestCase):
    """Test cases for ServiceManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_http = Mock()
        self.manager = ServiceManager(
            http_client=self.mock_http,
            namespace="public",
            group="DEFAULT_GROUP",
        )
    
    def test_register_instance_success(self):
        """Test successful instance registration."""
        self.mock_http.post.return_value = (200, "ok")
        
        result = self.manager.register_instance(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertTrue(result)
        self.mock_http.post.assert_called_once()
    
    def test_register_instance_failure(self):
        """Test failed instance registration."""
        self.mock_http.post.return_value = (500, "error")
        
        with self.assertRaises(NacosServiceException):
            self.manager.register_instance(
                service_name="test-service",
                ip="127.0.0.1",
                port=8080,
            )
    
    def test_deregister_instance_success(self):
        """Test successful instance deregistration."""
        self.mock_http.delete.return_value = (200, "ok")
        
        result = self.manager.deregister_instance(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertTrue(result)
        self.mock_http.delete.assert_called_once()
    
    def test_get_service(self):
        """Test getting service information."""
        service_data = {
            "name": "test-service",
            "groupName": "DEFAULT_GROUP",
            "metadata": {},
        }
        import json
        self.mock_http.get.return_value = (200, json.dumps(service_data))
        
        result = self.manager.get_service("test-service")
        
        self.assertEqual(result["name"], "test-service")
        self.mock_http.get.assert_called_once()
    
    def test_select_all_instances(self):
        """Test selecting all instances."""
        instances_data = {
            "hosts": [
                {"ip": "127.0.0.1", "port": 8080, "healthy": True},
                {"ip": "127.0.0.1", "port": 8081, "healthy": True},
            ]
        }
        import json
        self.mock_http.get.return_value = (200, json.dumps(instances_data))
        
        result = self.manager.select_all_instances("test-service")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["port"], 8080)
    
    def test_select_one_healthy_instance(self):
        """Test selecting one healthy instance."""
        instances_data = {
            "hosts": [
                {"ip": "127.0.0.1", "port": 8080, "healthy": True, "weight": 1.0},
                {"ip": "127.0.0.1", "port": 8081, "healthy": True, "weight": 1.0},
            ]
        }
        import json
        self.mock_http.get.return_value = (200, json.dumps(instances_data))
        
        result = self.manager.select_one_healthy_instance("test-service")
        
        self.assertIsNotNone(result)
        self.assertIn(result["port"], [8080, 8081])
    
    def test_select_one_healthy_instance_empty(self):
        """Test selecting instance when no healthy instances exist."""
        instances_data = {"hosts": []}
        import json
        self.mock_http.get.return_value = (200, json.dumps(instances_data))
        
        result = self.manager.select_one_healthy_instance("test-service")
        
        self.assertIsNone(result)
    
    def test_send_beat_success(self):
        """Test successful heartbeat."""
        self.mock_http.put.return_value = (200, "ok")
        
        result = self.manager.send_beat(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertTrue(result)
    
    def test_send_beat_failure(self):
        """Test failed heartbeat."""
        self.mock_http.put.return_value = (500, "error")
        
        result = self.manager.send_beat(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
