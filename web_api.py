# web_api.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import time
from opcua import Client, ua
from threading import Thread, Lock
import asyncio

app = FastAPI()

# Configuração do CORS para permitir que o React se conecte
origins = [
    "http://localhost",
    "http://localhost:5173", # Porta padrão do Vite React
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Variáveis para armazenar os dados do OPC UA e um Lock para thread safety ---
opcua_data = {
    "Sensor1_Temperature": 0.0,
    "Sensor2_Temperature": 0.0,
    "Sensor3_Temperature": 0.0,
    "Uptime": 0,
    "TotalProduction": 0
}
data_lock = Lock()
opcua_client_instance = None
running_opcua_reader = False

class OPCUAReader:
    def __init__(self, server_url="opc.tcp://localhost:4840/freeopcua/server/"):
        self.client = Client(server_url)
        # Não precisamos setar usuário/senha se o servidor for anônimo
        # self.client.set_user("admin")
        # self.client.set_password("admin")
        self.connected = False
        self.nodes = {} # Para armazenar referências aos nós

    def connect(self):
        try:
            self.client.connect()
            print("Conectado ao servidor OPC UA")
            self.connected = True
            self._get_nodes()
            return True
        except Exception as e:
            print(f"Falha ao conectar ao OPC UA: {e}")
            self.connected = False
            return False

    def disconnect(self):
        if self.connected:
            try:
                self.client.disconnect()
                print("Desconectado do servidor OPC UA")
                self.connected = False
            except Exception as e:
                print(f"Erro ao desconectar do OPC UA: {e}")

    def _get_nodes(self):
        # Este método busca os NodeIds uma vez para leitura mais eficiente
        try:
            root_node = self.client.get_root_node()
            objects_node = root_node.get_children()[0]
            
            factory_node = None
            for child in objects_node.get_children():
                if child.get_display_name().Text == "Factory":
                    factory_node = child
                    break
            
            if factory_node:
                for child in factory_node.get_children():
                    node_name = child.get_display_name().Text
                    if node_name == "TemperatureSensors":
                        for sub_child in child.get_children():
                            self.nodes[sub_child.get_display_name().Text] = sub_child
                    elif node_name == "SystemInfo":
                        for sub_child in child.get_children():
                            self.nodes[sub_child.get_display_name().Text] = sub_child
        except Exception as e:
            print(f"Erro ao obter nós OPC UA: {e}")
            self.nodes = {}

    def read_data(self):
        if not self.connected:
            if not self.connect():
                return
        
        with data_lock:
            try:
                if "Sensor1_Temperature" in self.nodes:
                    opcua_data["Sensor1_Temperature"] = round(self.nodes["Sensor1_Temperature"].get_value(), 2)
                if "Sensor2_Temperature" in self.nodes:
                    opcua_data["Sensor2_Temperature"] = round(self.nodes["Sensor2_Temperature"].get_value(), 2)
                if "Sensor3_Temperature" in self.nodes: # Adicionado o terceiro sensor
                    opcua_data["Sensor3_Temperature"] = round(self.nodes["Sensor3_Temperature"].get_value(), 2)
                if "Uptime" in self.nodes:
                    opcua_data["Uptime"] = self.nodes["Uptime"].get_value()
                if "TotalProduction" in self.nodes:
                    opcua_data["TotalProduction"] = self.nodes["TotalProduction"].get_value()
            except Exception as e:
                print(f"Erro ao ler dados OPC UA: {e}")
                self.connected = False # Tentar reconectar na próxima
                self.disconnect() # Desconectar para forçar reconexão

async def run_opcua_reader():
    global opcua_client_instance, running_opcua_reader
    opcua_client_instance = OPCUAReader()
    
    running_opcua_reader = True
    while running_opcua_reader:
        opcua_client_instance.read_data()
        await asyncio.sleep(2) # Lê a cada 2 segundos

@app.on_event("startup")
async def startup_event():
    print("Iniciando leitor OPC UA em thread...")
    # Usa asyncio.create_task para rodar a função assíncrona em background
    asyncio.create_task(run_opcua_reader())

@app.on_event("shutdown")
async def shutdown_event():
    global opcua_client_instance, running_opcua_reader
    print("Encerrando leitor OPC UA...")
    running_opcua_reader = False
    if opcua_client_instance:
        opcua_client_instance.disconnect()

@app.get("/api/opcua_data")
async def get_opcua_data():
    with data_lock:
        # Retorna uma cópia dos dados para evitar modificações externas
        return opcua_data.copy()

if __name__ == "__main__":
    import uvicorn
    # Para rodar o servidor web: uvicorn web_api:app --reload --port 8000
    # --reload (opcional, reinicia o servidor ao detectar mudanças no código)
    uvicorn.run(app, host="0.0.0.0", port=8000)