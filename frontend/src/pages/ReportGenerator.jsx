import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import ReactMarkdown from 'react-markdown';
import { generateReport } from '../api/report'; // Assuming this function exists for non-streaming

const ReportGenerator = () => {
  const { user, token } = useContext(AuthContext);
  const [query, setQuery] = useState('');
  const [report, setReport] = useState('');
  const [streamedReasonings, setStreamedReasonings] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // State for API Keys and Model Configuration
  const [analystModelName, setAnalystModelName] = useState('gemini-2.5-flash');
  const [analystTemperature, setAnalystTemperature] = useState(0.7);
  const [analystApiKey, setAnalystApiKey] = useState('');

  const [querierModelName, setQuerierModelName] = useState('gemini-2.0-flash');
  const [querierTemperature, setQuerierTemperature] = useState(0.5);
  const [querierApiKey, setQuerierApiKey] = useState('');

  const [haltingModelName, setHaltingModelName] = useState('gemini-2.0-flash');
  const [haltingTemperature, setHaltingTemperature] = useState(0.3);
  const [haltingApiKey, setHaltingApiKey] = useState('');


  const handleGenerateReport = async (e) => {
    e.preventDefault();
    setLoading(true);
    setReport('');
    setStreamedReasonings([]);
    setError('');

    if (!token || !user || !user.user_id) { // Changed user.id to user.user_id to match backend
      setError('No hay token o información de usuario (ID). Por favor, inicie sesión.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/edubot/analyze/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          user_id: user.user_id, // Ensure user.user_id is used
          model_analyst: { client: "google", model: analystModelName, temperature: analystTemperature, api_key: analystApiKey },
          model_querier: { client: "google", model: querierModelName, temperature: querierTemperature, api_key: querierApiKey },
          model_halting: { client: "google", model: haltingModelName, temperature: haltingTemperature, api_key: haltingApiKey },
          query: query,
          top_n: 5,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Error al iniciar el stream.');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let partialData = '';
      let finalReportContent = '';

      // eslint-disable-next-line no-constant-condition
      while (true) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }
        partialData += decoder.decode(value, { stream: true });

        const lines = partialData.split('\n');
        partialData = lines.pop();

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const jsonString = line.substring(6);
            try {
              const eventData = JSON.parse(jsonString);
              if (eventData.type === 'reasoning') {
                setStreamedReasonings(prev => [...prev, eventData.content]);
              } else if (eventData.type === 'report_chunk') {
                setReport(prev => prev + eventData.content);
                finalReportContent += eventData.content;
              } else if (eventData.type === 'final_report') {
                setReport(eventData.content);
                finalReportContent = eventData.content;
              }
            } catch (parseError) {
              console.error('Error parsing SSE data:', parseError, jsonString);
            }
          }
        }
      }
      setReport(finalReportContent);

    } catch (err) {
      console.error('Report generation error:', err);
      setError(err.message || 'Error al generar el informe.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-3xl font-bold text-center mb-6">Generador de Informes EduBot</h2>
        {user && <p className="text-center text-gray-700 mb-4">Bienvenido, {user.name} ({user.email})</p>}

        <form onSubmit={handleGenerateReport} className="mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Analyst Model (Google)</label>
              <input type="text" value={analystModelName} onChange={(e) => setAnalystModelName(e.target.value)} placeholder="Model Name" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="number" step="0.1" value={analystTemperature} onChange={(e) => setAnalystTemperature(parseFloat(e.target.value))} placeholder="Temperature" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="text" value={analystApiKey} onChange={(e) => setAnalystApiKey(e.target.value)} placeholder="API Key (Analyst)" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Querier Model (Google)</label>
              <input type="text" value={querierModelName} onChange={(e) => setQuerierModelName(e.target.value)} placeholder="Model Name" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="number" step="0.1" value={querierTemperature} onChange={(e) => setQuerierTemperature(parseFloat(e.target.value))} placeholder="Temperature" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="text" value={querierApiKey} onChange={(e) => setQuerierApiKey(e.target.value)} placeholder="API Key (Querier)" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Halting Model (Google)</label>
              <input type="text" value={haltingModelName} onChange={(e) => setHaltingModelName(e.target.value)} placeholder="Model Name" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="number" step="0.1" value={haltingTemperature} onChange={(e) => setHaltingTemperature(parseFloat(e.target.value))} placeholder="Temperature" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
              <input type="text" value={haltingApiKey} onChange={(e) => setHaltingApiKey(e.target.value)} placeholder="API Key (Halting)" className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm" />
            </div>
          </div>
          <textarea
            className="w-full p-3 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-600 resize-y mb-4"
            rows="5"
            placeholder="Introduce tu consulta para generar un informe..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            required
            disabled={loading}
          ></textarea>
          {error && <p className="text-red-500 text-sm mt-2 mb-4">{error}</p>}
          <button
            type="submit"
            className="w-full px-6 py-3 text-white bg-blue-600 rounded-lg hover:bg-blue-900 font-semibold"
            disabled={loading}
          >
            {loading ? 'Generando...' : 'Generar Informe'}
          </button>
        </form>

        {streamedReasonings.length > 0 && (
          <div className="mb-6 p-4 border border-gray-300 rounded-md bg-gray-50">
            <h4 className="text-xl font-semibold mb-3">Razonamientos del Agente:</h4>
            {streamedReasonings.map((reasoning, index) => (
              <ReactMarkdown key={index} className="prose max-w-none mb-2">
                {reasoning}
              </ReactMarkdown>
            ))}
          </div>
        )}

        {report && (
          <div className="p-4 border border-gray-300 rounded-md bg-white">
            <h4 className="text-xl font-semibold mb-3">Informe Final:</h4>
            <ReactMarkdown className="prose max-w-none">
              {report}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportGenerator;
