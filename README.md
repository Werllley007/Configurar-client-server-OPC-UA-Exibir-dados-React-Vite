# Configurar client/server OPC UA & Exibir dados em uma aplicação front-end em React com Vite

Neste projeto é criada uma **aplicação front-end em React com Vite** para exibir os dados do **cliente OPC UA** que recebe esses dados do **server OPC UA**.

Para isso, adiciona-se uma **camada intermediária**: um pequeno servidor Web em Python (Flask ou FastAPI). Isso porque o React (que roda no navegador) não consegue se conectar diretamente a um servidor OPC UA. Ele precisa de uma API HTTP para solicitar os dados.

### 1. Instalação do Node.js

### 2. Um servidor Web em Python (que chamaremos de web_api.py) irá:

  - Conectar-se ao seu opcua_server.py como um cliente OPC UA.

  - Ler os dados do OPC UA.

  - Expor um endpoint HTTP (ex: /api/data) que o front-end React pode consumir.

### 3. A aplicação React (vite-opcua-dashboard) irá:

  - Fazer requisições HTTP para o web_api.py.

  - Exibir os dados recebidos em uma interface amigável.

### 4. Execute a Aplicação React


## 1. Instalação do Node.js

Para começar com o React, você precisa ter o Node.js instalado. Ele é necessário para o React e para o comando npx.

**Baixe o Instalador**: Vá para o site oficial do Node.js:

```bash
https://nodejs.org/
```

**Recomendação**: Baixe a versão LTS (Long-Term Support - Suporte de Longo Prazo), que é a mais estável e recomendada para a maioria dos usuários.

**Instalação**: Execute o instalador baixado. Mantenha as configurações padrão. É crucial que a opção "Add to PATH" esteja marcada, mas geralmente ela já vem marcada por padrão.

### 1.1 Verificação da Instalação
Após a instalação, abra um novo terminal (ou Prompt de Comando/PowerShell) e execute os seguintes comandos para verificar se tudo está funcionando:

```bash
node -v
npm -v
```

### 1.2 Criando o Projeto React
Agora que o npx está disponível, você pode tentar criar o projeto novamente.

Volte para a pasta C:\Users\Desktop no seu terminal e execute:

```bash
npx create-react-app meu-projeto-opcua-web
```

Quando terminar, entre na pasta do projeto e inicie o servidor de desenvolvimento:

```bash
cd meu-projeto-opcua-web
npm start
```

### 1.3 Como usar o VS Code

Depois que o Node.js estiver instalado, você pode usar o Terminal Integrado do VS Code, que é a maneira mais prática de criar e gerenciar seu projeto.

Abra o VS Code.

Vá em **Terminal** no menu superior e clique em **Novo Terminal** (ou use o atalho: Ctrl + ' no Windows).

Neste terminal que se abrirá dentro do VS Code, você pode finalmente executar os comandos para **criar seu projeto React/Vite**, pois ele reconhecerá o npm que você instalou:

### 1.3.1. Verifique se o Node/npm está funcionando no terminal do VS Code
```bash
node -v
npm -v
```
### 1.3.2. Crie seu projeto React usando Vite

O Vite se tornou a maneira mais rápida e moderna de iniciar um projeto React. Ele oferece uma experiência de desenvolvimento super-rápida, utilizando a capacidade nativa de módulos ES do navegador.

Abra seu terminal e execute o seguinte comando:

```bash
npm create vite@latest
```
Ou pode usar o comando abaixo para inserir o nome do projeto e o tipo de template usado que no caso é o REACT

```bash
npm create vite@latest meu-projeto-opcua-web -- --template react
```
### 1.3.3. Entre na pasta do projeto
```bash
cd meu-projeto-opcua-web
```
### 1.3.4. Instale as dependências (as bibliotecas necessárias)
```bash
npm install
```
### 1.3.5. Inicie o servidor de desenvolvimento
```bash
npm run dev
```



# 1. Verifique que abaixo tem para UM e DOIS SERVIDOR OPC-UA 

Sugestão de fazer primeiro para um servidor e depois para dois servidores.

## 2. Crie o Servidor Web (Python FastAPI)

Vamos usar FastAPI por ser moderno e fácil de usar.


### Para UM SERVIDOR OPC-UA 

Crie um novo arquivo chamado **web_api.py**:

```bash
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

```
-----------------------------


### Para DOIS SERVIDOR OPC-UA 

Crie um novo arquivo chamado **web_api_new.py**:

```bash
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

```





----------------------------

### Criar e Ativar o Ambiente Virtual

```bash
# 1. Crie o ambiente virtual (chame-o de 'venv')
python -m venv venv

# 2. Ative o ambiente virtual (no PowerShell)
.\venv\Scripts\Activate
```

Após a ativação, você verá (venv) no início da sua linha de comando, indicando que está no ambiente isolado

### Instalar as dependências do web_api.py:
Com o **ambiente virtual ativo**, instale as dependências. Isso garantirá que o **uvicorn** e os outros pacotes sejam instalados no local correto, onde o ambiente virtual os encontra facilmente.

```bash
pip install fastapi uvicorn freeopcua
```

### Para executar o web_api.py:

```bash
uvicorn web_api:app --reload --port 8000
```




## 3. Crie a Aplicação React (Vite)

### Abra um novo terminal e execute:

```bash
npm create vite@latest vite-opcua-dashboard -- --template react

cd vite-opcua-dashboard

npm install
```


------------------------------------------------------------

### Caso seja com UM SERVIDOR OPC-UA Edite src/App.jsx:

Substitua o conteúdo de src/App.jsx pelo seguinte:

```bash
// src/App.jsx

import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [opcUaData, setOpcUaData] = useState({
    Sensor1_Temperature: 'N/A',
    Sensor2_Temperature: 'N/A',
    Sensor3_Temperature: 'N/A', // Adicionado o terceiro sensor
    Uptime: 'N/A',
    TotalProduction: 'N/A',
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/opcua_data');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setOpcUaData(data);
        setError(null);
      } catch (e) {
        console.error("Erro ao buscar dados OPC UA:", e);
        setError("Não foi possível conectar ao servidor de dados. Verifique se a API Python está rodando.");
      } finally {
        setLoading(false);
      }
    };

    // Busca os dados inicialmente
    fetchData();

    // Configura o intervalo para buscar dados a cada 3 segundos
    const intervalId = setInterval(fetchData, 3000); // Ajuste conforme a frequência de atualização desejada

    // Limpa o intervalo quando o componente for desmontado
    return () => clearInterval(intervalId);
  }, []); // O array vazio garante que o useEffect rode apenas uma vez na montagem

  return (
    <div className="App">
      <header className="App-header">
        <h1>Dashboard OPC UA Industrial</h1>
      </header>
      <main>
        {loading && <p>Carregando dados...</p>}
        {error && <p className="error-message">{error}</p>}
        {!loading && !error && (
          <div className="data-grid">
            <div className="card">
              <h2>Sensores de Temperatura</h2>
              <p>Sensor 1: <span>{opcUaData.Sensor1_Temperature} °C</span></p>
              <p>Sensor 2: <span>{opcUaData.Sensor2_Temperature} °C</span></p>
              <p>Sensor 3: <span>{opcUaData.Sensor3_Temperature} °C</span></p> {/* Exibindo o terceiro sensor */}
            </div>
            <div className="card">
              <h2>Informações do Sistema</h2>
              <p>Tempo de Atividade: <span>{opcUaData.Uptime} segundos</span></p>
              <p>Produção Total: <span>{opcUaData.TotalProduction} unidades</span></p>
            </div>
          </div>
        )}
      </main>
      <footer>
        <p>Dados atualizados do Servidor OPC UA via API Python.</p>
      </footer>
    </div>
  );
}

export default App;
```

------------------------------------------------------------

### Caso seja com DOIS SERVIDOR OPC-UA Edite src/App.jsx:

Substitua o conteúdo de src/App.jsx pelo seguinte (em anexo tem opcua_server_new.py):

```bash
import React, { useState, useEffect } from 'react';

// URL da API FastAPI
const API_URL = 'http://localhost:8000/api/opcua_data';
// Constantes para os nomes dos servidores (chaves esperadas)
const SERVER_KEYS = ["Server_4840", "Server_4841"];

// Componente para exibir um único painel de servidor
const ServerCard = ({ serverKey, data }) => {
  // Use um objeto de fallback se os dados estiverem ausentes
  const fallbackData = {
    Sensor1_Temperature: 'N/A',
    Sensor2_Temperature: 'N/A',
    Uptime: 'N/A',
    TotalProduction: 'N/A',
  };
  const serverData = data || fallbackData;

  // Determina se o servidor está ativo (assumindo que 0.0 é o valor inicial de falha de conexão)
  const isConnected = serverData.Uptime !== 0 && serverData.Uptime !== 'N/A';
  const statusColor = isConnected ? 'bg-green-500' : 'bg-red-500';
  const statusText = isConnected ? 'Online' : 'Offline / Desconectado';

  return (
    <div className="bg-white shadow-xl rounded-xl p-6 mb-8 w-full md:w-[48%] transform transition duration-300 hover:shadow-2xl border border-gray-100">
      <div className="flex justify-between items-center pb-4 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-800 flex items-center">
          <span className="text-blue-600 mr-3">🏭</span> {/* Ícone Factory substituído por Emoji */}
          {serverKey.replace('_', ' ')}
        </h2>
        <div className={`px-3 py-1 text-sm font-semibold rounded-full text-white ${statusColor}`}>
          {statusText}
        </div>
      </div>

      <div className="mt-6 space-y-4">
        {/* Bloco de Temperaturas */}
        <h3 className="text-lg font-semibold text-gray-700 border-l-4 border-blue-500 pl-3">Sensores de Temperatura</h3>
        <DataPoint label="Sensor 1" value={`${serverData.Sensor1_Temperature} °C`} icon="🌡️" />
        <DataPoint label="Sensor 2" value={`${serverData.Sensor2_Temperature} °C`} icon="🌡️" />

        {/* Bloco de Sistema */}
        <h3 className="text-lg font-semibold text-gray-700 border-l-4 border-blue-500 pl-3 pt-4">Informações do Sistema</h3>
        <DataPoint label="Tempo de Atividade" value={`${serverData.Uptime} segundos`} icon="⏱️" />
        <DataPoint label="Produção Total" value={`${serverData.TotalProduction} unidades`} icon="⚙️" />
      </div>
    </div>
  );
};

// Componente auxiliar para um ponto de dado
const DataPoint = ({ icon, label, value }) => (
  <div className="flex items-center justify-between bg-gray-50 p-3 rounded-lg">
    <div className="flex items-center">
      <span className="w-5 h-5 text-blue-500 mr-3">{icon}</span> {/* Ícone substituído por Emoji */}
      <span className="text-gray-600 font-medium">{label}:</span>
    </div>
    <span className="text-lg font-bold text-gray-900">{value}</span>
  </div>
);


const App = () => {
  // O estado agora é um objeto que armazena dados por chave de servidor (ex: { "Server_4840": {...} })
  const [opcUaData, setOpcUaData] = useState({}); 
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(API_URL);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        // Verifica se a API retornou todas as chaves esperadas
        const receivedKeys = Object.keys(data);
        if (SERVER_KEYS.every(key => receivedKeys.includes(key))) {
            setOpcUaData(data);
            setError(null);
        } else {
             setError("Dados recebidos da API incompletos ou no formato errado.");
        }
      } catch (e) {
        console.error("Erro ao buscar dados OPC UA:", e);
        // Garante que a mensagem de erro seja clara sobre o problema de conexão
        setError(`Não foi possível conectar à API. Verifique se o FastAPI está rodando em ${API_URL}.`);
      } finally {
        setLoading(false);
      }
    };

    // Busca os dados inicialmente e configura o intervalo
    fetchData();
    const intervalId = setInterval(fetchData, 2000); // Atualiza a cada 2 segundos

    return () => clearInterval(intervalId);
  }, []); 

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-8 font-['Inter']">
      <header className="text-center mb-10">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-gray-900 mb-2">
          Dashboard Multi-Servidor OPC UA
        </h1>
        <p className="text-xl text-gray-600">Monitoramento em tempo real de múltiplas linhas de produção</p>
        
        {error && (
            <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg flex items-center justify-center">
                <span className="mr-2">⚠️</span> {/* Alerta substituído por Emoji */}
                <span className="font-medium">{error}</span>
            </div>
        )}
      </header>
      
      <main className="max-w-7xl mx-auto">
        {loading ? (
          <div className="flex justify-center items-center h-64">
             <div className="w-12 h-12 border-4 border-blue-400 border-t-transparent border-solid rounded-full animate-spin"></div>
             <p className="ml-4 text-gray-600">Conectando aos servidores...</p>
          </div>
        ) : (
          <div className="flex flex-wrap justify-around gap-y-8">
            {/* Mapeia sobre as chaves esperadas e renderiza um cartão para cada servidor */}
            {SERVER_KEYS.map(key => (
              <ServerCard key={key} serverKey={key} data={opcUaData[key]} />
            ))}
          </div>
        )}
      </main>
      
      <footer className="text-center mt-10 p-4 border-t border-gray-200">
        <p className="text-sm text-gray-500">
          Dados consumidos via FastAPI ({API_URL}) e atualizados a cada 2 segundos.
        </p>
      </footer>
    </div>
  );
};

export default App;
```


###  Edite src/App.css:

Substitua o conteúdo de src/App.css pelo seguinte para um estilo básico:

```bash
/* src/App.css */

#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.App {
  font-family: Arial, sans-serif;
  color: #333;
  background-color: #f4f7f6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.App-header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  border-radius: 8px;
  margin-bottom: 20px;
}

h1 {
  margin: 0;
  font-size: 2.5em;
}

main {
  flex-grow: 1;
  padding: 20px 0;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  justify-content: center;
  margin-top: 20px;
}

.card {
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  text-align: left;
}

.card h2 {
  color: #007bff;
  margin-top: 0;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

.card p {
  font-size: 1.1em;
  margin: 10px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card p span {
  font-weight: bold;
  color: #555;
  background-color: #f0f0f0;
  padding: 5px 10px;
  border-radius: 4px;
}

.error-message {
  color: red;
  font-weight: bold;
  margin-top: 20px;
}

footer {
  margin-top: 40px;
  padding: 20px;
  border-top: 1px solid #eee;
  color: #666;
  font-size: 0.9em;
}
```


## 4. Execute a Aplicação React

No terminal do projeto vite-opcua-dashboard, execute:

**Terminal 1**: Execute o servidor OPC UA (corrigido).

Windows:
```bash
python.exe opcua_server.py
```

Linux:
```bash
python opcua_server.py
```

**Terminal 2**: Execute o servidor Web FastAPI para **um Servidor**.

Windows:
```bash
python.exe -m venv venv

.\venv\Scripts\Activate

uvicorn web_api:app --reload --port 8000
```

Linux:
```bash
python -m venv venv

source venv/bin/activate

uvicorn web_api:app --reload --port 8000
```

**Terminal 2**: Execute o servidor Web FastAPI para **dois Servidor**.

Windows:
```bash
python.exe -m venv venv

.\venv\Scripts\Activate

uvicorn web_api_new:app --reload --port 8000
```

Linux:
```bash
python -m venv venv

source venv/bin/activate

uvicorn web_api_new:app --reload --port 8000

**Terminal 3**: No diretório vite-opcua-dashboard, execute a aplicação React.

Dentro da pasta (Windows ou Linux):

```bash
cd vite-opcua-dashboard

npm run dev
```

O Vite iniciará o servidor de desenvolvimento e te dará um link (geralmente **http://localhost:5173**). Abra este link no seu navegador.

Você deverá ver um dashboard simples em React exibindo os valores dos sensores de temperatura, tempo de atividade e produção total, atualizando-se a cada 3 segundos.







