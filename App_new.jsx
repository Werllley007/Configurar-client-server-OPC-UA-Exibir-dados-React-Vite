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

