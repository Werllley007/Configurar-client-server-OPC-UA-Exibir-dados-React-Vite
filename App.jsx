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
