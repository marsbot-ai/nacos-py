"""
Custom exceptions for Nacos-Py client.
"""


class NacosException(Exception):
    """Base exception for Nacos client."""
    
    def __init__(self, message: str = "", code: int = None):
        super().__init__(message)
        self.message = message
        self.code = code
    
    def __str__(self) -> str:
        if self.code:
            return f"[Error {self.code}] {self.message}"
        return self.message


class NacosRequestException(NacosException):
    """Exception raised when request fails."""
    pass


class NacosResponseException(NacosException):
    """Exception raised when response is invalid or contains error."""
    pass


class NacosConnectionException(NacosException):
    """Exception raised when connection to Nacos server fails."""
    pass


class NacosTimeoutException(NacosException):
    """Exception raised when request times out."""
    pass


class NacosConfigException(NacosException):
    """Exception raised when configuration operation fails."""
    pass


class NacosServiceException(NacosException):
    """Exception raised when service operation fails."""
    pass


class NacosAuthException(NacosException):
    """Exception raised when authentication fails."""
    pass
