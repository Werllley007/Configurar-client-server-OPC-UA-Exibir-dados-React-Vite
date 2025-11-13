import time
from opcua import Client, ua


class IndustrialOPCClient:
    def __init__(self, server_url="opc.tcp://localhost:4840/freeopcua/server/"):
        self.client = Client(server_url)
        self.client.set_user("admin")
        self.client.set_password("admin")

    def connect(self):
        """Connect to the OPC UA server"""
        try:
            self.client.connect()
            print("Connected to OPC UA server")
            return True
        except Exception as e:
            print(f"Failed to connect: {e}")
            return False

    def disconnect(self):
        """Disconnect from the OPC UA server"""
        try:
            self.client.disconnect()
            print("Disconnected from server")
        except Exception as e:
            print(f"Error during disconnection: {e}")

    def browse_specific_factory_nodes(self):
        """Browse and print specific nodes within the 'Factory' object"""
        try:
            root_node = self.client.get_root_node()
            objects_node = root_node.get_children()[0]  # Objects node is usually the first child of the root

            # Find the "Factory" object
            factory_node = None
            for child in objects_node.get_children():
                if child.get_display_name().Text == "Factory":
                    factory_node = child
                    break

            if factory_node:
                print("\n" + "=" * 50)
                print("SERVER OBJECTS (Factory and its variables)")
                print("=" * 50)
                print(f"Object: {factory_node.get_display_name().Text} | NodeId: {factory_node.nodeid}")

                # Browse the children of "Factory"
                factory_children = factory_node.get_children()
                for child in factory_children:
                    node_name = child.get_display_name().Text
                    node_class = child.get_node_class()

                    if node_class == ua.NodeClass.Object:
                        print(f"  Object: {node_name}")

                        # Browse children of 'SystemInfo' or 'TemperatureSensors'
                        sub_children = child.get_children()
                        for sub_child in sub_children:
                            sub_node_name = sub_child.get_display_name().Text
                            sub_node_value = sub_child.get_value()
                            print(f"    Variable: {sub_node_name} | Value: {sub_node_value}")

        except Exception as e:
            print(f"Error reading data: {e}")

    def monitor_continuous(self, duration=30):
        """Monitor factory data continuously"""
        print(f"\nStarting continuous monitoring for {duration} seconds...")
        start_time = time.time()
        while time.time() - start_time < duration:
            self.browse_specific_factory_nodes()
            time.sleep(5)  # Read every 5 seconds
        print("\nMonitoring completed.")


def main():
    client = IndustrialOPCClient()
    if not client.connect():
        return

    try:
        print("\n1. Browsing server address space:")
        client.monitor_continuous(duration=30)

    except KeyboardInterrupt:
        print("\nClient stopped by user")
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()