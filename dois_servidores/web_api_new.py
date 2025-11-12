import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opcua import Client, ua
from threading import Lock
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

# --- Configuração dos Servidores a Monitorar ---
SERVER_CONFIGS = {
    "Server_4840": "opc.tcp://localhost:4840/freeopcua/server/", # Servidor Original
    "Server_4841": "opc.tcp://localhost:4841/newserver/opcua/"    # Novo Servidor
}

# --- Variáveis para armazenar os dados e o Lock ---
# Estrutura de dados para armazenar as leituras de todos os servidores
# Ex: { "Server_4840": { "Sensor1_Temperature": 0.0, ... }, "Server_4841": { ... } }
opcua_data = {} 

# Estrutura para armazenar as instâncias do cliente OPC UA
opcua_clients = {} 

data_lock = Lock()
running_opcua_reader = False

# Nomes de nós esperados (comuns a ambos os servidores)
EXPECTED_NODES = [
    "Sensor1_Temperature",
    "Sensor2_Temperature",
    "Uptime",
    "TotalProduction"
]

class OPCUAReader:
    def __init__(self, server_key, server_url):
        self.server_key = server_key
        self.client = Client(server_url)
        self.connected = False
        self.nodes = {} 

    def connect(self):
        try:
            print(f"[{self.server_key}] Tentando conectar a {self.client.server_url}...")
            self.client.connect()
            print(f"[{self.server_key}] SUCESSO: Conectado!")
            self.connected = True
            # Inicializa o bloco de dados para este servidor
            with data_lock:
                 opcua_data[self.server_key] = {node: 0.0 for node in EXPECTED_NODES}
            self._get_nodes()
            return True
        except Exception as e:
            print(f"[{self.server_key}] FALHA: Conexão recusada ou erro de rede. Erro: {e}")
            self.connected = False
            self.nodes = {}
            # Garante que os dados fiquem em 0 se a conexão falhar
            with data_lock:
                 opcua_data[self.server_key] = {node: 0.0 for node in EXPECTED_NODES}
            return False

    def disconnect(self):
        if self.connected:
            try:
                self.client.disconnect()
                print(f"[{self.server_key}] Desconectado.")
                self.connected = False
            except Exception as e:
                print(f"[{self.server_key}] Erro ao desconectar: {e}")

    def _get_nodes(self):
        self.nodes = {}
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
                    if node_name == "TemperatureSensors" or node_name == "SystemInfo":
                        for sub_child in child.get_children():
                            display_name = sub_child.get_display_name().Text
                            if display_name in EXPECTED_NODES:
                                self.nodes[display_name] = sub_child
            
            # Alerta se algum nó importante não foi encontrado
            missing_nodes = [node for node in EXPECTED_NODES if node not in self.nodes]
            if missing_nodes:
                print(f"[{self.server_key}] ALERTA: Nós ausentes: {missing_nodes}")
            else:
                 print(f"[{self.server_key}] DEBUG: Todos os nós encontrados com sucesso.")
                 
        except Exception as e:
            print(f"[{self.server_key}] ERRO CRÍTICO ao obter nós OPC UA: {e}")
            self.nodes = {}

    def read_data(self):
        if not self.connected:
            if not self.connect():
                return
        
        # Tenta buscar os nós novamente se a lista estiver vazia
        if not self.nodes:
             self._get_nodes()
             if not self.nodes:
                 return # Não há nós para ler, sai

        current_data = {}
        try:
            # Leitura de todos os nós configurados
            for node_name, node_ref in self.nodes.items():
                value = node_ref.get_value()
                # Aplica arredondamento apenas para temperaturas (presumindo float)
                if 'Temperature' in node_name:
                    current_data[node_name] = round(value, 2)
                else:
                    current_data[node_name] = value

            # Atualiza o dicionário global em um bloco lock
            with data_lock:
                opcua_data[self.server_key] = current_data
                
        except Exception as e:
            print(f"[{self.server_key}] ERRO ao ler dados. Forçando reconexão. Erro: {e}")
            self.connected = False 
            self.disconnect()
            # Garante que os dados fiquem em 0
            with data_lock:
                 opcua_data[self.server_key] = {node: 0.0 for node in EXPECTED_NODES}

async def run_opcua_reader():
    global running_opcua_reader, opcua_clients
    
    # Cria uma instância de leitor para cada servidor configurado
    for key, url in SERVER_CONFIGS.items():
        opcua_clients[key] = OPCUAReader(key, url)
        # Inicializa o bloco de dados no global dict, caso não conecte de primeira
        opcua_data[key] = {node: 0.0 for node in EXPECTED_NODES}
    
    running_opcua_reader = True
    print(f"Iniciando leitores para {list(opcua_clients.keys())}...")

    while running_opcua_reader:
        # Itera e lê dados de todos os clientes
        for client_key in opcua_clients:
            opcua_clients[client_key].read_data()
        
        await asyncio.sleep(2) # Lê a cada 2 segundos

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_opcua_reader())

@app.on_event("shutdown")
async def shutdown_event():
    global running_opcua_reader
    print("Encerrando leitores OPC UA...")
    running_opcua_reader = False
    # Desconecta todos os clientes
    for client_key in opcua_clients:
        opcua_clients[client_key].disconnect()

@app.get("/api/opcua_data")
async def get_opcua_data():
    """
    Retorna os dados de todos os servidores.
    Exemplo: 
    {
      "Server_4840": { "Sensor1_Temperature": 21.5, ... },
      "Server_4841": { "Sensor1_Temperature": 32.1, ... }
    }
    """
    with data_lock:
        return opcua_data.copy()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
