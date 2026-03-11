"""
Nacos-Py: Python client for Alibaba Nacos

Nacos is a dynamic service discovery, configuration and service management platform.
This package provides a Python client for interacting with Nacos server.

Example:
    >>> from nacos import NacosClient
    >>> client = NacosClient(server_addresses="http://localhost:8848")
    >>> client.register_instance("my-service", "127.0.0.1", 8080)
"""

from .client import NacosClient
from .exceptions import (
    NacosException,
    NacosRequestException,
    NacosResponseException,
    NacosConnectionException,
    NacosTimeoutException,
)

__version__ = "0.1.0"
__all__ = [
    "NacosClient",
    "NacosException",
    "NacosRequestException",
    "NacosResponseException",
    "NacosConnectionException",
    "NacosTimeoutException",
]
