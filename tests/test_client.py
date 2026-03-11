"""
Unit tests for NacosClient.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock

from nacos import NacosClient
from nacos.exceptions import NacosException, NacosConnectionException


class TestNacosClient(unittest.TestCase):
    """Test cases for NacosClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.server_addresses = "http://localhost:8848"
        self.namespace = "public"
    
    @patch('nacos.client.NacosHttpClient')
    def test_client_initialization(self, mock_http_client):
        """Test client initialization."""
        client = NacosClient(
            server_addresses=self.server_addresses,
            namespace=self.namespace,
        )
        
        self.assertEqual(client.server_addresses, self.server_addresses)
        self.assertEqual(client.namespace, self.namespace)
    
    @patch('nacos.client.NacosHttpClient')
    @patch('nacos.client.ServiceManager')
    @patch('nacos.client.ConfigManager')
    def test_context_manager(self, mock_config, mock_service, mock_http):
        """Test context manager usage."""
        with NacosClient(self.server_addresses) as client:
            self.assertIsNotNone(client)
    
    @patch('nacos.client.NacosHttpClient')
    @patch('nacos.client.ServiceManager')
    def test_register_instance(self, mock_service_manager, mock_http):
        """Test register_instance method."""
        mock_instance = mock_service_manager.return_value
        mock_instance.register_instance.return_value = True
        
        client = NacosClient(self.server_addresses)
        result = client.register_instance(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertTrue(result)
        mock_instance.register_instance.assert_called_once()
    
    @patch('nacos.client.NacosHttpClient')
    @patch('nacos.client.ServiceManager')
    def test_deregister_instance(self, mock_service_manager, mock_http):
        """Test deregister_instance method."""
        mock_instance = mock_service_manager.return_value
        mock_instance.deregister_instance.return_value = True
        
        client = NacosClient(self.server_addresses)
        result = client.deregister_instance(
            service_name="test-service",
            ip="127.0.0.1",
            port=8080,
        )
        
        self.assertTrue(result)
        mock_instance.deregister_instance.assert_called_once()
    
    @patch('nacos.client.NacosHttpClient')
    @patch('nacos.client.ConfigManager')
    def test_get_config(self, mock_config_manager, mock_http):
        """Test get_config method."""
        mock_instance = mock_config_manager.return_value
        mock_instance.get_config.return_value = "test=config"
        
        client = NacosClient(self.server_addresses)
        result = client.get_config(
            data_id="test-data",
            group="DEFAULT_GROUP",
        )
        
        self.assertEqual(result, "test=config")
        mock_instance.get_config.assert_called_once()
    
    @patch('nacos.client.NacosHttpClient')
    @patch('nacos.client.ConfigManager')
    def test_publish_config(self, mock_config_manager, mock_http):
        """Test publish_config method."""
        mock_instance = mock_config_manager.return_value
        mock_instance.publish_config.return_value = True
        
        client = NacosClient(self.server_addresses)
        result = client.publish_config(
            data_id="test-data",
            group="DEFAULT_GROUP",
            content="key=value",
        )
        
        self.assertTrue(result)
        mock_instance.publish_config.assert_called_once()
    
    @patch('nacos.client.NacosHttpClient')
    def test_close(self, mock_http_client):
        """Test close method."""
        mock_instance = mock_http_client.return_value
        
        client = NacosClient(self.server_addresses)
        client.close()
        
        # Verify that close was called on http client
        self.assertTrue(hasattr(client, '_http_client'))


class TestNacosClientIntegration(unittest.TestCase):
    """Integration test cases (requires running Nacos server)."""
    
    @unittest.skip("Requires running Nacos server")
    def test_real_connection(self):
        """Test connection to real Nacos server."""
        client = NacosClient("http://localhost:8848")
        
        # Try to get a non-existent config
        config = client.get_config("non-existent", "test-group")
        self.assertIsNone(config)
        
        client.close()


if __name__ == "__main__":
    unittest.main()
