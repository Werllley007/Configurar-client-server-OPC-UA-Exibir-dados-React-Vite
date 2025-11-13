import time
import random
from threading import Thread
from opcua import Server, ua


class NewIndustrialOPCServer:
    """
    Novo Servidor OPC UA rodando na porta 4841 para simular uma linha de produção diferente.
    """
    def __init__(self):
        # O endpoint DEVE ser diferente do opcua_server.py (4840)
        self.server = Server()
        self.server.set_endpoint("opc.tcp://localhost:4841/newserver/opcua/")
        self.server.set_server_name("New Production Line Server")

        # Set up the address space
        self.setup_address_space()

        # Variables for simulation
        self.running = False
        self.simulation_thread = None

    def setup_address_space(self):
        # Obtém o nó de objetos raiz
        objects = self.server.get_objects_node()

        # Cria nosso objeto principal 'Factory' (Namespace 2 é usado por convenção)
        self.factory = objects.add_object("ns=2;i=1", "Factory")

        # Adiciona sensores de temperatura
        self.temp_sensors = self.factory.add_object("ns=2;i=3", "TemperatureSensors")

        # Cria variáveis de sensor de temperatura
        self.temp_sensor_1 = self.temp_sensors.add_variable("ns=2;i=10", "Sensor1_Temperature", 30.0) # Base 30.0
        self.temp_sensor_2 = self.temp_sensors.add_variable("ns=2;i=11", "Sensor2_Temperature", 35.0) # Base 35.0

        # Permite escrita nos sensores (para compatibilidade com o server original)
        self.temp_sensor_1.set_writable()
        self.temp_sensor_2.set_writable()

        # Adiciona informações do sistema
        self.system_info = self.factory.add_object("ns=2;i=5", "SystemInfo")
        self.uptime = self.system_info.add_variable("ns=2;i=30", "Uptime", 0)
        self.total_production = self.system_info.add_variable("ns=2;i=31", "TotalProduction", 0)

    def simulate_industrial_data(self):
        """Simula mudanças de dados industriais."""
        uptime_counter = 0
        production_counter = 500 # Produção inicial maior para diferenciar

        while self.running:
            try:
                # Simula flutuações de temperatura (diferentes do servidor original)
                base_temp_1 = 30.0 + random.uniform(-1, 2)
                base_temp_2 = 35.0 + random.uniform(-0.5, 1.5)
                
                self.temp_sensor_1.set_value(round(base_temp_1, 2))
                self.temp_sensor_2.set_value(round(base_temp_2, 2))

                # Atualiza informações do sistema
                uptime_counter += 1
                production_counter += 5 # Produção maior
                
                self.uptime.set_value(uptime_counter)
                self.total_production.set_value(production_counter)

                time.sleep(2)  # Atualiza a cada 2 segundos

            except Exception as e:
                print(f"Simulation error in new server: {e}")
                break

    def start(self):
        """Inicia o servidor OPC UA"""
        try:
            self.server.start()
            print("NOVO OPC UA Server started at opc.tcp://localhost:4841/newserver/opcua/")
            print("Server is running. Press Ctrl+C to stop.")

            # Inicia o thread de simulação
            self.running = True
            self.simulation_thread = Thread(target=self.simulate_industrial_data)
            self.simulation_thread.daemon = True
            self.simulation_thread.start()

        except Exception as e:
            print(f"Failed to start new server: {e}")

    def stop(self):
        """Para o servidor OPC UA"""
        self.running = False
        if self.simulation_thread:
            self.simulation_thread.join(timeout=5)
        self.server.stop()
        print("New Server stopped.")


if __name__ == "__main__":
    server = NewIndustrialOPCServer()

    try:
        server.start()
        # Mantém o servidor rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down new server...")
        server.stop()
