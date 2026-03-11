"""
Main Nacos client for service discovery and configuration management.
"""
import logging
from typing import Dict, Any, List, Optional, Callable

from .http import NacosHttpClient
from .service import ServiceManager
from .config import ConfigManager
from .exceptions import NacosAuthException, NacosRequestException

logger = logging.getLogger(__name__)


class NacosClient:
    """
    Main client for interacting with Nacos server.
    
    This client provides unified access to Nacos service discovery and
    configuration management capabilities.
    
    Example:
        >>> client = NacosClient(
        ...     server_addresses="http://localhost:8848",
        ...     namespace="public",
        ...     username="nacos",
        ...     password="nacos"
        ... )
        >>> client.register_instance("my-service", "127.0.0.1", 8080)
    """
    
    def __init__(
        self,
        server_addresses: str,
        namespace: str = "public",
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout: int = 5,
        max_retries: int = 3,
    ):
        """
        Initialize Nacos client.
        
        Args:
            server_addresses: Nacos server addresses (comma-separated for multiple)
                Example: "http://localhost:8848" or "http://host1:8848,http://host2:8848"
            namespace: Namespace ID, default is "public"
            username: Username for authentication (optional)
            password: Password for authentication (optional)
            timeout: Request timeout in seconds, default is 5
            max_retries: Maximum retry attempts, default is 3
        """
        self.server_addresses = server_addresses
        self.namespace = namespace
        self.username = username
        self.password = password
        
        # Initialize HTTP client
        self._http_client = NacosHttpClient(
            server_addresses=server_addresses,
            timeout=timeout,
            max_retries=max_retries,
        )
        
        # Initialize managers
        self._service_manager = ServiceManager(
            http_client=self._http_client,
            namespace=namespace,
        )
        self._config_manager = ConfigManager(
            http_client=self._http_client,
            namespace=namespace,
        )
        
        # Authenticate if credentials provided
        if username and password:
            self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Nacos server."""
        try:
            params = {
                "username": self.username,
                "password": self.password,
            }
            status, response = self._http_client.post(
                "/nacos/v1/auth/login",
                params=params,
            )
            
            if status == 200:
                logger.info("Successfully authenticated with Nacos server")
            else:
                raise NacosAuthException(f"Authentication failed: {response}")
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise NacosAuthException(f"Authentication failed: {str(e)}")
    
    # ==================== Service Methods ====================
    
    def register_instance(
        self,
        service_name: str,
        ip: str,
        port: int,
        group: Optional[str] = None,
        cluster_name: Optional[str] = None,
        weight: float = 1.0,
        enabled: bool = True,
        healthy: bool = True,
        metadata: Optional[Dict[str, str]] = None,
        ephemeral: bool = True,
    ) -> bool:
        """
        Register a service instance.
        
        Args:
            service_name: Service name
            ip: Instance IP address
            port: Instance port
            group: Service group (default: DEFAULT_GROUP)
            cluster_name: Cluster name
            weight: Instance weight for load balancing (0.0-1.0)
            enabled: Whether instance is enabled
            healthy: Whether instance is healthy
            metadata: Instance metadata as key-value pairs
            ephemeral: Whether instance is ephemeral (auto-removed on disconnect)
            
        Returns:
            True if registration successful
        """
        return self._service_manager.register_instance(
            service_name=service_name,
            ip=ip,
            port=port,
            group=group,
            cluster_name=cluster_name,
            weight=weight,
            enabled=enabled,
            healthy=healthy,
            metadata=metadata,
            ephemeral=ephemeral,
        )
    
    def deregister_instance(
        self,
        service_name: str,
        ip: str,
        port: int,
        group: Optional[str] = None,
        cluster_name: Optional[str] = None,
        ephemeral: bool = True,
    ) -> bool:
        """
        Deregister a service instance.
        
        Args:
            service_name: Service name
            ip: Instance IP address
            port: Instance port
            group: Service group (default: DEFAULT_GROUP)
            cluster_name: Cluster name
            ephemeral: Whether instance is ephemeral
            
        Returns:
            True if deregistration successful
        """
        return self._service_manager.deregister_instance(
            service_name=service_name,
            ip=ip,
            port=port,
            group=group,
            cluster_name=cluster_name,
            ephemeral=ephemeral,
        )
    
    def get_service(
        self,
        service_name: str,
        group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get service information.
        
        Args:
            service_name: Service name
            group: Service group (default: DEFAULT_GROUP)
            
        Returns:
            Service information dictionary
        """
        return self._service_manager.get_service(
            service_name=service_name,
            group=group,
        )
    
    def select_all_instances(
        self,
        service_name: str,
        group: Optional[str] = None,
        clusters: Optional[str] = None,
        healthy_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Select all instances of a service.
        
        Args:
            service_name: Service name
            group: Service group (default: DEFAULT_GROUP)
            clusters: Cluster names (comma-separated)
            healthy_only: Return only healthy instances
            
        Returns:
            List of instance dictionaries
        """
        return self._service_manager.select_all_instances(
            service_name=service_name,
            group=group,
            clusters=clusters,
            healthy_only=healthy_only,
        )
    
    def select_one_healthy_instance(
        self,
        service_name: str,
        group: Optional[str] = None,
        clusters: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Select one healthy instance using weighted random algorithm.
        
        Args:
            service_name: Service name
            group: Service group (default: DEFAULT_GROUP)
            clusters: Cluster names (comma-separated)
            
        Returns:
            Selected instance dictionary or None if no healthy instance found
        """
        return self._service_manager.select_one_healthy_instance(
            service_name=service_name,
            group=group,
            clusters=clusters,
        )
    
    # ==================== Config Methods ====================
    
    def get_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        timeout: int = 5000,
    ) -> Optional[str]:
        """
        Get configuration content.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group (default: DEFAULT_GROUP)
            timeout: Request timeout in milliseconds
            
        Returns:
            Configuration content or None if not found
        """
        return self._config_manager.get_config(
            data_id=data_id,
            group=group,
            timeout=timeout,
        )
    
    def publish_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        content: str = "",
        config_type: str = "text",
        tag: Optional[str] = None,
        app_name: Optional[str] = None,
    ) -> bool:
        """
        Publish configuration.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group (default: DEFAULT_GROUP)
            content: Configuration content
            config_type: Configuration type (text, json, yaml, properties, etc.)
            tag: Configuration tag
            app_name: Application name
            
        Returns:
            True if publish successful
        """
        return self._config_manager.publish_config(
            data_id=data_id,
            group=group,
            content=content,
            config_type=config_type,
            tag=tag,
            app_name=app_name,
        )
    
    def remove_config(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        tag: Optional[str] = None,
    ) -> bool:
        """
        Remove configuration.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group (default: DEFAULT_GROUP)
            tag: Configuration tag
            
        Returns:
            True if removal successful
        """
        return self._config_manager.remove_config(
            data_id=data_id,
            group=group,
            tag=tag,
        )
    
    def add_listener(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        callback: Callable[[str], None] = None,
    ) -> bool:
        """
        Add a listener for configuration changes.
        
        Uses long-polling mechanism for real-time updates.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group (default: DEFAULT_GROUP)
            callback: Callback function that receives new config content
            
        Returns:
            True if listener added successfully
        """
        return self._config_manager.add_listener(
            data_id=data_id,
            group=group,
            callback=callback,
        )
    
    def remove_listener(
        self,
        data_id: str,
        group: str = "DEFAULT_GROUP",
        callback: Optional[Callable[[str], None]] = None,
    ) -> bool:
        """
        Remove a listener for configuration changes.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group (default: DEFAULT_GROUP)
            callback: Specific callback to remove, or None to remove all
            
        Returns:
            True if listener removed successfully
        """
        return self._config_manager.remove_listener(
            data_id=data_id,
            group=group,
            callback=callback,
        )
    
    # ==================== Lifecycle Methods ====================
    
    def close(self):
        """
        Close the client and release resources.
        
        This method stops all background threads (heartbeats, listeners)
        and closes the HTTP session.
        """
        try:
            # Stop all service heartbeats
            self._service_manager.stop_all_heartbeats()
            
            # Stop all config listeners
            self._config_manager.stop_all_listeners()
            
            # Close HTTP session
            self._http_client.close()
            
            logger.info("Nacos client closed successfully")
        except Exception as e:
            logger.error(f"Error closing client: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
