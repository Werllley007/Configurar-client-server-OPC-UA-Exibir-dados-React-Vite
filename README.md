# Configurar client/server OPC UA & Exibir dados em uma aplicação front-end em React com Vite

Neste projeto é criada uma **aplicação front-end em React com Vite** para exibir os dados do **cliente OPC UA** que recebe esses dados do **server OPC UA**.

Para isso, adiciona-se uma **camada intermediária**: um pequeno servidor Web em Python (Flask ou FastAPI). Isso porque o React (que roda no navegador) não consegue se conectar diretamente a um servidor OPC UA. Ele precisa de uma API HTTP para solicitar os dados.

### 1. Um servidor Web em Python (que chamaremos de web_api.py) irá:

  - Conectar-se ao seu opcua_server.py como um cliente OPC UA.

  - Ler os dados do OPC UA.

  - Expor um endpoint HTTP (ex: /api/data) que o front-end React pode consumir.

### 2. A aplicação React (vite-opcua-dashboard) irá:

  - Fazer requisições HTTP para o web_api.py.

  - Exibir os dados recebidos em uma interface amigável.

### 3. Execute a Aplicação React


## 1. Crie o Servidor Web (Python FastAPI)
Vamos usar FastAPI por ser moderno e fácil de usar.

Crie um novo arquivo chamado **web_api.py**:

```bash
# web_api.py
```

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




## 2. Crie a Aplicação React (Vite)

### Abra um novo terminal e execute:

```bash
npm create vite@latest vite-opcua-dashboard -- --template react

cd vite-opcua-dashboard

npm install
```

### Edite src/App.jsx:
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


## 3. Execute a Aplicação React
No terminal do projeto vite-opcua-dashboard, execute:

```bash
npm run dev
```

O Vite iniciará o servidor de desenvolvimento e te dará um link (geralmente **http://localhost:5173**). Abra este link no seu navegador.

### Como Rodar Tudo

**Terminal 1**: Execute o servidor OPC UA (corrigido).

```bash
python opcua_server.py
```

**Terminal 2**: Execute o servidor Web FastAPI.

```bash
uvicorn web_api:app --reload --port 8000
```

**Terminal 3**: No diretório vite-opcua-dashboard, execute a aplicação React.

```bash
npm run dev
```

Abra o navegador no endereço fornecido pelo Vite (ex: **http://localhost:5173**).

Você deverá ver um dashboard simples em React exibindo os valores dos sensores de temperatura, tempo de atividade e produção total, atualizando-se a cada 3 segundos.







