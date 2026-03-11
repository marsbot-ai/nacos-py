# Nacos-Py

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

Python client for [Alibaba Nacos](https://github.com/alibaba/nacos) - a dynamic service discovery, configuration and service management platform.

## Features

- **Service Discovery**: Register, deregister, and discover services
- **Configuration Management**: Get, publish, and listen to configuration changes
- **Health Checking**: Automatic heartbeat and health checks
- **Namespace Support**: Multi-tenant isolation support
- **Long Polling**: Real-time configuration updates
- **Retry Logic**: Built-in retry mechanism for resilience
- **Type Hints**: Full type annotation support

## Installation

```bash
pip install nacos-py
```

Or install from source:

```bash
git clone https://github.com/marsbot-ai/nacos-py.git
cd nacos-py
pip install -e .
```

## Quick Start

### Service Registration & Discovery

```python
from nacos import NacosClient

# Initialize client
client = NacosClient(
    server_addresses="http://localhost:8848",
    namespace="public",
    username="nacos",
    password="nacos"
)

# Register a service instance
client.register_instance(
    service_name="my-service",
    ip="127.0.0.1",
    port=8080,
    group="DEFAULT_GROUP"
)

# Discover services
instances = client.select_all_instances("my-service")
print(instances)

# Deregister
client.deregister_instance(
    service_name="my-service",
    ip="127.0.0.1",
    port=8080
)
```

### Configuration Management

```python
from nacos import NacosClient

client = NacosClient(server_addresses="http://localhost:8848")

# Get configuration
config = client.get_config(data_id="example", group="DEFAULT_GROUP")
print(config)

# Publish configuration
client.publish_config(
    data_id="example",
    group="DEFAULT_GROUP",
    content="key=value"
)

# Listen for configuration changes
def on_config_change(config):
    print(f"Config updated: {config}")

client.add_listener(
    data_id="example",
    group="DEFAULT_GROUP",
    callback=on_config_change
)
```

## API Reference

### NacosClient

Main client class for interacting with Nacos server.

#### Constructor Parameters

- `server_addresses` (str): Nacos server addresses, comma-separated for multiple servers
- `namespace` (str, optional): Namespace ID, default is "public"
- `username` (str, optional): Username for authentication
- `password` (str, optional): Password for authentication
- `timeout` (int, optional): Request timeout in seconds, default is 5
- `retry` (int, optional): Retry times, default is 3

#### Service Methods

- `register_instance(service_name, ip, port, **kwargs)`: Register a service instance
- `deregister_instance(service_name, ip, port, **kwargs)`: Deregister a service instance
- `get_service(service_name, **kwargs)`: Get service information
- `select_one_healthy_instance(service_name, **kwargs)`: Select one healthy instance
- `select_all_instances(service_name, **kwargs)`: Select all instances
- `subscribe(service_name, callback, **kwargs)`: Subscribe to service changes

#### Config Methods

- `get_config(data_id, group, **kwargs)`: Get configuration
- `publish_config(data_id, group, content, **kwargs)`: Publish configuration
- `remove_config(data_id, group, **kwargs)`: Remove configuration
- `add_listener(data_id, group, callback, **kwargs)`: Add config listener
- `remove_listener(data_id, group, callback, **kwargs)`: Remove config listener

## Examples

See the [examples/](examples/) directory for more usage examples.

## Testing

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Acknowledgments

This project is inspired by the official [Nacos Java Client](https://github.com/alibaba/nacos).
