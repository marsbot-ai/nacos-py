"""
Service discovery and registration for Nacos-Py.
"""
import json
import logging
import threading
import time
from typing import Dict, Any, List, Optional, Callable

from .http import NacosHttpClient
from .utils import get_current_time_millis, weighted_random_choice
from .exceptions import NacosServiceException

logger = logging.getLogger(__name__)


class ServiceManager:
    """Manager for service registration and discovery."""
    
    # API endpoints
    REGISTER_INSTANCE = "/nacos/v1/ns/instance"
    DEREGISTER_INSTANCE = "/nacos/v1/ns/instance"
    GET_SERVICE = "/nacos/v1/ns/service"
    LIST_SERVICES = "/nacos/v1/ns/service/list"
    GET_INSTANCE = "/nacos/v1/ns/instance"
    LIST_INSTANCES = "/nacos/v1/ns/instance/list"
    SEND_BEAT = "/nacos/v1/ns/instance/beat"
    
    def __init__(
        self,
        http_client: NacosHttpClient,
        namespace: str = "public",
        group: str = "DEFAULT_GROUP",
    ):
        """
        Initialize service manager.
        
        Args:
            http_client: HTTP client instance
            namespace: Namespace ID
            group: Default service group
        """
        self.http_client = http_client
        self.namespace = namespace
        self.group = group
        self._heartbeat_threads: Dict[str, threading.Thread] = {}
        self._heartbeat_stop_events: Dict[str, threading.Event] = {}
        self._lock = threading.Lock()
    
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
            group: Service group
            cluster_name: Cluster name
            weight: Instance weight (0.0-1.0)
            enabled: Whether instance is enabled
            healthy: Whether instance is healthy
            metadata: Instance metadata
            ephemeral: Whether instance is ephemeral
            
        Returns:
            True if registration successful
        """
        params = {
            "serviceName": service_name,
            "ip": ip,
            "port": port,
            "namespaceId": self.namespace,
            "groupName": group or self.group,
            "weight": weight,
            "enabled": str(enabled).lower(),
            "healthy": str(healthy).lower(),
            "ephemeral": str(ephemeral).lower(),
        }
        
        if cluster_name:
            params["clusterName"] = cluster_name
        if metadata:
            params["metadata"] = json.dumps(metadata, ensure_ascii=False)
        
        try:
            status, response = self.http_client.post(self.REGISTER_INSTANCE, params=params)
            if status == 200 and response == "ok":
                logger.info(f"Registered instance {ip}:{port} for service {service_name}")
                
                # Start heartbeat for ephemeral instances
                if ephemeral:
                    self._start_heartbeat(service_name, ip, port, group, cluster_name)
                
                return True
            else:
                raise NacosServiceException(f"Failed to register instance: {response}")
        except Exception as e:
            logger.error(f"Failed to register instance: {e}")
            raise NacosServiceException(f"Registration failed: {str(e)}")
    
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
            group: Service group
            cluster_name: Cluster name
            ephemeral: Whether instance is ephemeral
            
        Returns:
            True if deregistration successful
        """
        # Stop heartbeat first
        instance_key = f"{service_name}#{ip}#{port}"
        self._stop_heartbeat(instance_key)
        
        params = {
            "serviceName": service_name,
            "ip": ip,
            "port": port,
            "namespaceId": self.namespace,
            "groupName": group or self.group,
            "ephemeral": str(ephemeral).lower(),
        }
        
        if cluster_name:
            params["clusterName"] = cluster_name
        
        try:
            status, response = self.http_client.delete(self.DEREGISTER_INSTANCE, params=params)
            if status == 200 and response == "ok":
                logger.info(f"Deregistered instance {ip}:{port} for service {service_name}")
                return True
            else:
                raise NacosServiceException(f"Failed to deregister instance: {response}")
        except Exception as e:
            logger.error(f"Failed to deregister instance: {e}")
            raise NacosServiceException(f"Deregistration failed: {str(e)}")
    
    def get_service(
        self,
        service_name: str,
        group: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get service information.
        
        Args:
            service_name: Service name
            group: Service group
            
        Returns:
            Service information dictionary
        """
        params = {
            "serviceName": service_name,
            "namespaceId": self.namespace,
            "groupName": group or self.group,
        }
        
        try:
            status, response = self.http_client.get(self.GET_SERVICE, params=params)
            if status == 200:
                return json.loads(response)
            else:
                raise NacosServiceException(f"Failed to get service: {response}")
        except Exception as e:
            logger.error(f"Failed to get service: {e}")
            raise NacosServiceException(f"Get service failed: {str(e)}")
    
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
            group: Service group
            clusters: Cluster names (comma-separated)
            healthy_only: Return only healthy instances
            
        Returns:
            List of instance dictionaries
        """
        params = {
            "serviceName": service_name,
            "namespaceId": self.namespace,
            "groupName": group or self.group,
            "healthyOnly": str(healthy_only).lower(),
        }
        
        if clusters:
            params["clusters"] = clusters
        
        try:
            status, response = self.http_client.get(self.LIST_INSTANCES, params=params)
            if status == 200:
                data = json.loads(response)
                return data.get("hosts", [])
            else:
                raise NacosServiceException(f"Failed to list instances: {response}")
        except Exception as e:
            logger.error(f"Failed to list instances: {e}")
            raise NacosServiceException(f"List instances failed: {str(e)}")
    
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
            group: Service group
            clusters: Cluster names (comma-separated)
            
        Returns:
            Selected instance dictionary or None
        """
        instances = self.select_all_instances(
            service_name,
            group=group,
            clusters=clusters,
            healthy_only=True,
        )
        
        if not instances:
            return None
        
        return weighted_random_choice(instances)
    
    def send_beat(
        self,
        service_name: str,
        ip: str,
        port: int,
        group: Optional[str] = None,
        cluster_name: Optional[str] = None,
    ) -> bool:
        """
        Send heartbeat to keep instance alive.
        
        Args:
            service_name: Service name
            ip: Instance IP address
            port: Instance port
            group: Service group
            cluster_name: Cluster name
            
        Returns:
            True if heartbeat successful
        """
        beat_info = {
            "serviceName": service_name,
            "ip": ip,
            "port": port,
            "cluster": cluster_name or "",
        }
        
        params = {
            "serviceName": service_name,
            "beat": json.dumps(beat_info),
            "namespaceId": self.namespace,
            "groupName": group or self.group,
        }
        
        try:
            status, response = self.http_client.put(self.SEND_BEAT, params=params)
            return status == 200
        except Exception as e:
            logger.warning(f"Heartbeat failed: {e}")
            return False
    
    def _start_heartbeat(
        self,
        service_name: str,
        ip: str,
        port: int,
        group: Optional[str] = None,
        cluster_name: Optional[str] = None,
        interval: int = 5,
    ):
        """Start heartbeat thread for an instance."""
        instance_key = f"{service_name}#{ip}#{port}"
        
        with self._lock:
            if instance_key in self._heartbeat_threads:
                return
            
            stop_event = threading.Event()
            self._heartbeat_stop_events[instance_key] = stop_event
            
            def heartbeat_loop():
                while not stop_event.is_set():
                    try:
                        self.send_beat(service_name, ip, port, group, cluster_name)
                    except Exception as e:
                        logger.warning(f"Heartbeat error: {e}")
                    
                    stop_event.wait(interval)
            
            thread = threading.Thread(
                target=heartbeat_loop,
                name=f"Heartbeat-{instance_key}",
                daemon=True,
            )
            thread.start()
            self._heartbeat_threads[instance_key] = thread
            logger.debug(f"Started heartbeat for {instance_key}")
    
    def _stop_heartbeat(self, instance_key: str):
        """Stop heartbeat thread for an instance."""
        with self._lock:
            if instance_key in self._heartbeat_stop_events:
                self._heartbeat_stop_events[instance_key].set()
                del self._heartbeat_stop_events[instance_key]
            
            if instance_key in self._heartbeat_threads:
                del self._heartbeat_threads[instance_key]
            
            logger.debug(f"Stopped heartbeat for {instance_key}")
    
    def stop_all_heartbeats(self):
        """Stop all heartbeat threads."""
        with self._lock:
            for key in list(self._heartbeat_stop_events.keys()):
                self._heartbeat_stop_events[key].set()
            
            self._heartbeat_stop_events.clear()
            self._heartbeat_threads.clear()
            logger.info("Stopped all heartbeats")
