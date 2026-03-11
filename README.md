# Nacos-Py

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

**⚠️ This is a CLIENT library, NOT a server implementation.**

Python client for [Alibaba Nacos](https://github.com/alibaba/nacos) - a dynamic service discovery, configuration and service management platform.

> **Note:** This library allows your Python applications to connect to a Nacos server. You need to deploy the [Nacos server](https://github.com/alibaba/nacos) separately. The server is written in Java and is not included in this package.

## Features

- **Service Discovery**: Register, deregister, and discover services
- **Configuration Management**: Get, publish, and listen to configuration changes
- **Health Checking**: Automatic heartbeat and health checks
- **Namespace Support**: Multi-tenant isolation support
- **Long Polling**: Real-time configuration updates
- **Retry Logic**: Built-in retry mechanism for resilience
- **Type Hints**: Full type annotation support

## Prerequisites

Before using this client library, you need to deploy a **Nacos server**. This package does NOT include the server.

### Quick Start with Nacos Server

**Option 1: Docker (Recommended)**
```bash
docker run --name nacos-server \
  -e MODE=standalone \
  -p 8848:8848 \
  -p 9848:9848 \
  nacos/nacos-server:v2.3.0
```

**Option 2: Download Binary**
```bash
wget https://github.com/alibaba/nacos/releases/download/2.3.0/nacos-server-2.3.0.tar.gz
tar -xzf nacos-server-2.3.0.tar.gz
cd nacos/bin
sh startup.sh -m standalone
```

Once the server is running, access the console at: http://localhost:8848/nacos (default login: nacos/nacos)

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

> **Note:** The examples below assume you have a Nacos server running at `http://localhost:8848`. See [Prerequisites](#prerequisites) for setup instructions.

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

## Architecture

```
┌─────────────────┐         HTTP API          ┌─────────────────┐
│   Your Python   │  ═══════════════════════► │   Nacos Server  │
│   Application   │  ◄═══════════════════════ │   (Java)        │
│   (nacos-py)    │    Service Registry       │                 │
│                 │    Config Management      │                 │
└─────────────────┘                           └─────────────────┘
       Client                                          Server
```

**This package is the CLIENT only.** The Nacos server (written in Java) must be deployed separately.

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

## FAQ

### Is this a Nacos server implementation?

**No.** This is a Python client library that connects to an existing Nacos server. The server is written in Java by Alibaba and must be deployed separately.

### Where can I get the Nacos server?

Download the official Nacos server from: https://github.com/alibaba/nacos/releases

Or use Docker:
```bash
docker run -e MODE=standalone -p 8848:8848 nacos/nacos-server:v2.3.0
```

### Can I run Nacos server in Python?

No. The official Nacos server is implemented in Java. This library only provides client functionality for Python applications.

## Acknowledgments

This project is inspired by the official [Nacos Java Client](https://github.com/alibaba/nacos).

This is a **client-only** library. For the server implementation, see [alibaba/nacos](https://github.com/alibaba/nacos).
