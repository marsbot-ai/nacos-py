"""
Configuration management for Nacos-Py.
"""
import json
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable

from .http import NacosHttpClient
from .utils import md5_hash
from .exceptions import NacosConfigException

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manager for configuration operations."""
    
    # API endpoints
    GET_CONFIG = "/nacos/v1/cs/configs"
    PUBLISH_CONFIG = "/nacos/v1/cs/configs"
    REMOVE_CONFIG = "/nacos/v1/cs/configs"
    LISTEN_CONFIG = "/nacos/v1/cs/configs/listener"
    
    def __init__(
        self,
        http_client: NacosHttpClient,
        namespace: str = "public",
    ):
        """
        Initialize config manager.
        
        Args:
            http_client: HTTP client instance
            namespace: Namespace ID
        """
        self.http_client = http_client
        self.namespace = namespace
        self._listeners: Dict[str, List[Callable]] = {}
        self._listener_threads: Dict[str, threading.Thread] = {}
        self._listener_stop_events: Dict[str, threading.Event] = {}
        self._config_md5_cache: Dict[str, str] = {}
        self._lock = threading.Lock()
    
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
            group: Configuration group
            timeout: Request timeout in milliseconds
            
        Returns:
            Configuration content or None if not found
        """
        params = {
            "dataId": data_id,
            "group": group,
            "namespaceId": self.namespace,
            "timeout": timeout,
        }
        
        try:
            status, response = self.http_client.get(self.GET_CONFIG, params=params)
            if status == 200:
                return response
            elif status == 404:
                return None
            else:
                raise NacosConfigException(f"Failed to get config: {response}")
        except Exception as e:
            logger.error(f"Failed to get config: {e}")
            raise NacosConfigException(f"Get config failed: {str(e)}")
    
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
            group: Configuration group
            content: Configuration content
            config_type: Configuration type (text, json, yaml, properties, etc.)
            tag: Configuration tag
            app_name: Application name
            
        Returns:
            True if publish successful
        """
        params = {
            "dataId": data_id,
            "group": group,
            "namespaceId": self.namespace,
            "content": content,
            "type": config_type,
        }
        
        if tag:
            params["tag"] = tag
        if app_name:
            params["appName"] = app_name
        
        try:
            status, response = self.http_client.post(self.PUBLISH_CONFIG, params=params)
            if status == 200 and response == "true":
                logger.info(f"Published config {data_id}/{group}")
                return True
            else:
                raise NacosConfigException(f"Failed to publish config: {response}")
        except Exception as e:
            logger.error(f"Failed to publish config: {e}")
            raise NacosConfigException(f"Publish config failed: {str(e)}")
    
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
            group: Configuration group
            tag: Configuration tag
            
        Returns:
            True if removal successful
        """
        params = {
            "dataId": data_id,
            "group": group,
            "namespaceId": self.namespace,
        }
        
        if tag:
            params["tag"] = tag
        
        try:
            status, response = self.http_client.delete(self.REMOVE_CONFIG, params=params)
            if status == 200 and response == "true":
                logger.info(f"Removed config {data_id}/{group}")
                return True
            else:
                raise NacosConfigException(f"Failed to remove config: {response}")
        except Exception as e:
            logger.error(f"Failed to remove config: {e}")
            raise NacosConfigException(f"Remove config failed: {str(e)}")
    
    def add_listener(
        self,
        data_id: str,
        callback: Callable[[str], None],
        group: str = "DEFAULT_GROUP",
    ) -> bool:
        """
        Add a listener for configuration changes.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group
            callback: Callback function that receives new config content
            
        Returns:
            True if listener added successfully
        """
        config_key = f"{data_id}#{group}"
        
        with self._lock:
            if config_key not in self._listeners:
                self._listeners[config_key] = []
                # Start listening thread
                self._start_listening(data_id, group)
            
            if callback not in self._listeners[config_key]:
                self._listeners[config_key].append(callback)
                logger.info(f"Added listener for {config_key}")
        
        return True
    
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
            group: Configuration group
            callback: Specific callback to remove, or None to remove all
            
        Returns:
            True if listener removed successfully
        """
        config_key = f"{data_id}#{group}"
        
        with self._lock:
            if config_key not in self._listeners:
                return True
            
            if callback is None:
                # Remove all listeners
                self._listeners[config_key].clear()
                self._stop_listening(config_key)
            else:
                # Remove specific callback
                if callback in self._listeners[config_key]:
                    self._listeners[config_key].remove(callback)
                
                # Stop if no more listeners
                if not self._listeners[config_key]:
                    self._stop_listening(config_key)
        
        return True
    
    def _start_listening(self, data_id: str, group: str):
        """Start long-polling thread for config changes."""
        config_key = f"{data_id}#{group}"
        
        stop_event = threading.Event()
        self._listener_stop_events[config_key] = stop_event
        
        def listen_loop():
            # Initial config fetch
            content = self.get_config(data_id, group)
            self._config_md5_cache[config_key] = md5_hash(content or "")
            
            while not stop_event.is_set():
                try:
                    # Long polling request
                    content = self._do_long_polling(data_id, group)
                    
                    if content is not None:
                        # Config changed
                        new_md5 = md5_hash(content)
                        old_md5 = self._config_md5_cache.get(config_key, "")
                        
                        if new_md5 != old_md5:
                            self._config_md5_cache[config_key] = new_md5
                            self._notify_listeners(config_key, content)
                    
                except Exception as e:
                    logger.warning(f"Config listening error: {e}")
                    stop_event.wait(1)  # Wait before retry
        
        thread = threading.Thread(
            target=listen_loop,
            name=f"ConfigListener-{config_key}",
            daemon=True,
        )
        thread.start()
        self._listener_threads[config_key] = thread
        logger.debug(f"Started config listener for {config_key}")
    
    def _stop_listening(self, config_key: str):
        """Stop long-polling thread for config changes."""
        if config_key in self._listener_stop_events:
            self._listener_stop_events[config_key].set()
            del self._listener_stop_events[config_key]
        
        if config_key in self._listener_threads:
            del self._listener_threads[config_key]
        
        if config_key in self._config_md5_cache:
            del self._config_md5_cache[config_key]
        
        if config_key in self._listeners:
            del self._listeners[config_key]
        
        logger.debug(f"Stopped config listener for {config_key}")
    
    def _do_long_polling(self, data_id: str, group: str, timeout: int = 30000) -> Optional[str]:
        """
        Perform long polling request.
        
        Args:
            data_id: Configuration data ID
            group: Configuration group
            timeout: Long polling timeout in milliseconds
            
        Returns:
            New config content or None if not changed
        """
        config_key = f"{data_id}#{group}"
        current_md5 = self._config_md5_cache.get(config_key, "")
        
        # Build probe modification string
        probe = f"{data_id}{chr(2)}{group}{chr(2)}{current_md5}{chr(2)}{self.namespace}"
        
        params = {
            "Listening-Configs": probe,
        }
        
        try:
            status, response = self.http_client.post(
                self.LISTEN_CONFIG,
                params=params,
                headers={"Long-Pulling-Timeout": str(timeout)},
            )
            
            if status == 200:
                if response and response.strip():
                    # Config changed, fetch new content
                    return self.get_config(data_id, group)
                else:
                    # No change
                    return None
            else:
                return None
        except Exception as e:
            logger.warning(f"Long polling failed: {e}")
            return None
    
    def _notify_listeners(self, config_key: str, content: str):
        """Notify all listeners of config change."""
        listeners = self._listeners.get(config_key, [])
        for callback in listeners:
            try:
                callback(content)
            except Exception as e:
                logger.error(f"Listener callback error: {e}")
    
    def stop_all_listeners(self):
        """Stop all config listeners."""
        with self._lock:
            for key in list(self._listener_stop_events.keys()):
                self._listener_stop_events[key].set()
            
            self._listener_stop_events.clear()
            self._listener_threads.clear()
            self._config_md5_cache.clear()
            self._listeners.clear()
            logger.info("Stopped all config listeners")
