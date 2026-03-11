"""
HTTP client for Nacos-Py with retry logic.
"""
import logging
import random
import time
from typing import Dict, Any, Optional, List, Tuple
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    NacosConnectionException,
    NacosTimeoutException,
    NacosRequestException,
    NacosResponseException,
)
from .utils import select_random_server

logger = logging.getLogger(__name__)


class NacosHttpClient:
    """HTTP client for Nacos server communication."""
    
    def __init__(
        self,
        server_addresses: str,
        timeout: int = 5,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ):
        """
        Initialize HTTP client.
        
        Args:
            server_addresses: Comma-separated server addresses (e.g., "http://localhost:8848")
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            backoff_factor: Backoff factor for retries
        """
        self.servers = self._parse_servers(server_addresses)
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self._session = self._create_session()
        self._current_server_index = 0
    
    def _parse_servers(self, addresses: str) -> List[str]:
        """Parse server addresses string."""
        servers = [s.strip() for s in addresses.split(",") if s.strip()]
        if not servers:
            raise NacosRequestException("No valid server addresses provided")
        return servers
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry configuration."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_server(self) -> str:
        """Get current server address."""
        server = self.servers[self._current_server_index]
        self._current_server_index = (self._current_server_index + 1) % len(self.servers)
        return server
    
    def _switch_server(self):
        """Switch to next available server."""
        self._current_server_index = (self._current_server_index + 1) % len(self.servers)
    
    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        server = self._get_server()
        return urljoin(server, endpoint)
    
    def _handle_response(self, response: requests.Response) -> Tuple[int, str]:
        """Handle HTTP response."""
        if response.status_code >= 200 and response.status_code < 300:
            return response.status_code, response.text
        
        if response.status_code == 403:
            raise NacosResponseException(
                f"Access denied: {response.text}",
                code=response.status_code
            )
        elif response.status_code == 404:
            raise NacosResponseException(
                f"Resource not found: {response.text}",
                code=response.status_code
            )
        elif response.status_code >= 500:
            raise NacosResponseException(
                f"Server error: {response.text}",
                code=response.status_code
            )
        else:
            raise NacosResponseException(
                f"Request failed: {response.text}",
                code=response.status_code
            )
    
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str]:
        """
        Send GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            
        Returns:
            Tuple of (status_code, response_text)
        """
        url = self._build_url(endpoint)
        
        try:
            response = self._session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise NacosTimeoutException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NacosConnectionException(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NacosRequestException(f"Request failed: {str(e)}")
    
    def post(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str]:
        """
        Send POST request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json_data: JSON body
            headers: Request headers
            
        Returns:
            Tuple of (status_code, response_text)
        """
        url = self._build_url(endpoint)
        
        try:
            response = self._session.post(
                url,
                params=params,
                data=data,
                json=json_data,
                headers=headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise NacosTimeoutException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NacosConnectionException(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NacosRequestException(f"Request failed: {str(e)}")
    
    def put(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str]:
        """
        Send PUT request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            headers: Request headers
            
        Returns:
            Tuple of (status_code, response_text)
        """
        url = self._build_url(endpoint)
        
        try:
            response = self._session.put(
                url,
                params=params,
                data=data,
                headers=headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise NacosTimeoutException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NacosConnectionException(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NacosRequestException(f"Request failed: {str(e)}")
    
    def delete(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Tuple[int, str]:
        """
        Send DELETE request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Request headers
            
        Returns:
            Tuple of (status_code, response_text)
        """
        url = self._build_url(endpoint)
        
        try:
            response = self._session.delete(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
            )
            return self._handle_response(response)
        except requests.exceptions.Timeout:
            raise NacosTimeoutException(f"Request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError as e:
            raise NacosConnectionException(f"Connection failed: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise NacosRequestException(f"Request failed: {str(e)}")
    
    def close(self):
        """Close the HTTP session."""
        self._session.close()
