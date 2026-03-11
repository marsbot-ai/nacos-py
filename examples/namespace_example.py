"""
Example: Working with Namespaces in Nacos

This example demonstrates how to:
1. Use different namespaces for isolation
2. Register services in different namespaces
3. Manage configurations per namespace
"""
import time
from nacos import NacosClient

# Configuration
NACOS_SERVER = "http://localhost:8848"

# Define namespaces
NAMESPACES = {
    "dev": "dev-namespace-id",
    "test": "test-namespace-id",
    "prod": "prod-namespace-id",
}

def main():
    """Main example function."""
    
    # ============================================
    # Example 1: Create clients for different namespaces
    # ============================================
    print("=== Creating clients for different namespaces ===")
    
    clients = {}
    for env, namespace_id in NAMESPACES.items():
        client = NacosClient(
            server_addresses=NACOS_SERVER,
            namespace=namespace_id,
        )
        clients[env] = client
        print(f"Created client for {env} environment (namespace: {namespace_id})")
    
    try:
        # ============================================
        # Example 2: Register services in each namespace
        # ============================================
        print("\n=== Registering services in each namespace ===")
        
        for env, client in clients.items():
            port = 8080 + list(NAMESPACES.keys()).index(env)
            result = client.register_instance(
                service_name="my-service",
                ip=f"127.0.0.{list(NAMESPACES.keys()).index(env) + 1}",
                port=port,
                metadata={"env": env},
            )
            print(f"[{env}] Registered my-service on port {port}: {result}")
        
        time.sleep(1)
        
        # ============================================
        # Example 3: Show namespace isolation
        # ============================================
        print("\n=== Demonstrating namespace isolation ===")
        
        for env, client in clients.items():
            instances = client.select_all_instances("my-service")
            print(f"[{env}] Found {len(instances)} instance(s):")
            for inst in instances:
                print(f"    - {inst['ip']}:{inst['port']}")
        
        # ============================================
        # Example 4: Publish configs to each namespace
        # ============================================
        print("\n=== Publishing configurations to each namespace ===")
        
        for env, client in clients.items():
            config = f"""
# Configuration for {env} environment
database:
  url: jdbc:mysql://{env}-db:3306/mydb
  pool_size: {5 if env == "prod" else 2}

logging:
  level: {"INFO" if env == "prod" else "DEBUG"}
"""
            result = client.publish_config(
                data_id="app-config",
                group="DEFAULT_GROUP",
                content=config,
                config_type="yaml",
            )
            print(f"[{env}] Published config: {result}")
        
        # ============================================
        # Example 5: Read configs from each namespace
        # ============================================
        print("\n=== Reading configurations from each namespace ===")
        
        for env, client in clients.items():
            config = client.get_config(data_id="app-config")
            print(f"[{env}] Config:\n{config}")
        
        # ============================================
        # Example 6: Verify isolation
        # ============================================
        print("\n=== Verifying namespace isolation ===")
        print("Services and configs in different namespaces are completely isolated.")
        print("A client in 'dev' namespace cannot see services in 'prod' namespace.")
        
    finally:
        # ============================================
        # Cleanup
        # ============================================
        print("\n=== Cleaning up ===")
        
        for env, client in clients.items():
            port = 8080 + list(NAMESPACES.keys()).index(env)
            ip = f"127.0.0.{list(NAMESPACES.keys()).index(env) + 1}"
            
            # Deregister service
            client.deregister_instance("my-service", ip, port)
            print(f"[{env}] Deregistered my-service")
            
            # Remove config
            client.remove_config("app-config")
            print(f"[{env}] Removed config")
            
            # Close client
            client.close()
        
        print("All clients closed")


if __name__ == "__main__":
    main()
