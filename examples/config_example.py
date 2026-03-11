"""
Example: Configuration Management with Nacos

This example demonstrates how to:
1. Publish configuration
2. Get configuration
3. Listen for configuration changes
4. Remove configuration
"""
import time
from nacos import NacosClient

# Configuration
NACOS_SERVER = "http://localhost:8848"
NAMESPACE = "public"
DATA_ID = "example-config"
GROUP = "DEFAULT_GROUP"

def on_config_change(content: str):
    """Callback function for config changes."""
    print(f"\n*** Configuration changed! ***")
    print(f"New content:\n{content}")
    print("*** End of update ***\n")

def main():
    """Main example function."""
    # Initialize Nacos client
    client = NacosClient(
        server_addresses=NACOS_SERVER,
        namespace=NAMESPACE,
    )
    
    try:
        # ============================================
        # Example 1: Publish configuration
        # ============================================
        print("=== Publishing configuration ===")
        
        config_content = """
# Application Configuration
app:
  name: Example App
  version: 1.0.0
  debug: false

database:
  host: localhost
  port: 3306
  username: root
  password: secret

cache:
  enabled: true
  ttl: 3600
"""
        result = client.publish_config(
            data_id=DATA_ID,
            group=GROUP,
            content=config_content,
            config_type="yaml",
        )
        print(f"Publish result: {result}")
        
        # ============================================
        # Example 2: Get configuration
        # ============================================
        print("\n=== Getting configuration ===")
        config = client.get_config(data_id=DATA_ID, group=GROUP)
        print(f"Config content:\n{config}")
        
        # ============================================
        # Example 3: Add config listener
        # ============================================
        print("\n=== Adding configuration listener ===")
        print("The listener will watch for changes using long-polling...")
        
        client.add_listener(
            data_id=DATA_ID,
            group=GROUP,
            callback=on_config_change,
        )
        
        # Keep the script running to receive updates
        print("\nWaiting for configuration changes...")
        print("You can manually update the config in Nacos console to see the callback in action.")
        print("Press Ctrl+C to stop\n")
        
        try:
            counter = 0
            while True:
                time.sleep(5)
                counter += 1
                # Periodically show we're still listening
                if counter % 6 == 0:  # Every 30 seconds
                    print(f"Still listening... (run for {counter * 5} seconds)")
        except KeyboardInterrupt:
            print("\nStopping listener...")
        
        # ============================================
        # Example 4: Remove listener
        # ============================================
        print("\n=== Removing configuration listener ===")
        client.remove_listener(
            data_id=DATA_ID,
            group=GROUP,
            callback=on_config_change,
        )
        print("Listener removed")
        
        # ============================================
        # Example 5: Update configuration
        # ============================================
        print("\n=== Updating configuration ===")
        updated_content = """
# Updated Configuration
app:
  name: Example App
  version: 1.1.0
  debug: true

database:
  host: prod.db.example.com
  port: 3306
  username: app_user
  password: encrypted_password

cache:
  enabled: true
  ttl: 7200

new_feature:
  enabled: true
"""
        result = client.publish_config(
            data_id=DATA_ID,
            group=GROUP,
            content=updated_content,
            config_type="yaml",
        )
        print(f"Update result: {result}")
        
        # Get updated config
        updated = client.get_config(data_id=DATA_ID, group=GROUP)
        print(f"\nUpdated content:\n{updated}")
        
    finally:
        # ============================================
        # Cleanup: Remove configuration
        # ============================================
        print("\n=== Removing configuration ===")
        result = client.remove_config(data_id=DATA_ID, group=GROUP)
        print(f"Remove result: {result}")
        
        # Close client
        client.close()
        print("Client closed")


if __name__ == "__main__":
    main()
