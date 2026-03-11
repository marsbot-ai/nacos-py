"""
Example: Service Registration and Discovery with Nacos

This example demonstrates how to:
1. Register a service instance
2. Discover services
3. Select healthy instances
4. Handle service deregistration
"""
import time
from nacos import NacosClient

# Configuration
NACOS_SERVER = "http://localhost:8848"
NAMESPACE = "public"
SERVICE_NAME = "example-service"
GROUP = "DEFAULT_GROUP"

def main():
    """Main example function."""
    # Initialize Nacos client
    client = NacosClient(
        server_addresses=NACOS_SERVER,
        namespace=NAMESPACE,
        # username="nacos",  # Uncomment if authentication is required
        # password="nacos",
    )
    
    try:
        # ============================================
        # Example 1: Register a service instance
        # ============================================
        print("=== Registering service instance ===")
        
        # Register this application as a service
        result = client.register_instance(
            service_name=SERVICE_NAME,
            ip="127.0.0.1",
            port=8080,
            group=GROUP,
            weight=1.0,
            metadata={
                "version": "1.0.0",
                "region": "cn-beijing",
                "env": "production",
            },
            ephemeral=True,  # Will be auto-removed if client disconnects
        )
        print(f"Registration result: {result}")
        
        # Wait a moment for registration to propagate
        time.sleep(1)
        
        # ============================================
        # Example 2: Get service information
        # ============================================
        print("\n=== Getting service information ===")
        service_info = client.get_service(SERVICE_NAME, group=GROUP)
        print(f"Service info: {service_info}")
        
        # ============================================
        # Example 3: Select all instances
        # ============================================
        print("\n=== Selecting all instances ===")
        all_instances = client.select_all_instances(
            service_name=SERVICE_NAME,
            group=GROUP,
        )
        print(f"Total instances: {len(all_instances)}")
        for instance in all_instances:
            print(f"  - {instance['ip']}:{instance['port']} (healthy: {instance.get('healthy', True)}, weight: {instance.get('weight', 1)})")
        
        # ============================================
        # Example 4: Select one healthy instance
        # ============================================
        print("\n=== Selecting one healthy instance (weighted random) ===")
        for i in range(5):
            instance = client.select_one_healthy_instance(
                service_name=SERVICE_NAME,
                group=GROUP,
            )
            if instance:
                print(f"  Selected: {instance['ip']}:{instance['port']}")
            else:
                print("  No healthy instance found")
        
        # ============================================
        # Example 5: Keep service alive for demo
        # ============================================
        print("\n=== Keeping service registered (press Ctrl+C to stop) ===")
        print("Service will auto-send heartbeats every 5 seconds")
        
        try:
            while True:
                time.sleep(10)
                # Re-query to show it's still registered
                instances = client.select_all_instances(SERVICE_NAME, group=GROUP)
                print(f"Service still registered with {len(instances)} instance(s)")
        except KeyboardInterrupt:
            print("\nStopping...")
        
    finally:
        # ============================================
        # Cleanup: Deregister service
        # ============================================
        print("\n=== Deregistering service ===")
        result = client.deregister_instance(
            service_name=SERVICE_NAME,
            ip="127.0.0.1",
            port=8080,
            group=GROUP,
        )
        print(f"Deregistration result: {result}")
        
        # Close client
        client.close()
        print("Client closed")


if __name__ == "__main__":
    main()
