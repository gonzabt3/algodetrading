import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { RefreshCw, Download, Trash2, Database, TrendingUp, Calendar, Activity, CheckCircle, AlertTriangle, XCircle } from 'lucide-react';

const API_URL = 'http://localhost:8000';

const DataManager = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [fetchForm, setFetchForm] = useState({
    symbol: 'BTC/USDT',
    timeframe: '1d',
    days: 365,
    assetType: 'crypto'
  });
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadDataSources();
  }, []);

  const loadDataSources = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/data/sources`);
      setSources(response.data.sources || []);
    } catch (error) {
      console.error('Error cargando fuentes de datos:', error);
      setMessage({ type: 'error', text: 'Error al cargar fuentes de datos' });
    } finally {
      setLoading(false);
    }
  };

  const handleFetchData = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.post(`${API_URL}/api/data/fetch`, null, {
        params: {
          symbol: fetchForm.symbol,
          timeframe: fetchForm.timeframe,
          days: parseInt(fetchForm.days),
          asset_type: fetchForm.assetType
        }
      });

      setMessage({ type: 'success', text: response.data.message });
      loadDataSources();
    } catch (error) {
      console.error('Error descargando datos:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al descargar datos' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async (symbol) => {
    setLoading(true);
    setMessage(null);

    try {
      const ccxtSymbol = symbol.replace('_', '/');
      const response = await axios.post(`${API_URL}/api/data/${ccxtSymbol}/refresh`, null, {
        params: {
          timeframe: '1d',
          days: 365
        }
      });

      setMessage({ type: 'success', text: response.data.message });
      loadDataSources();
    } catch (error) {
      console.error('Error actualizando datos:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al actualizar datos' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleValidate = async (symbol) => {
    setLoading(true);
    setValidationResult(null);
    setMessage(null);

    try {
      const response = await axios.post(`${API_URL}/api/data/validate/${symbol}`, null, {
        params: { days: 365 }
      });
      setValidationResult(response.data);
      
      if (response.data.is_valid) {
        setMessage({ type: 'success', text: `✅ Datos de ${symbol} son válidos` });
      } else {
        setMessage({ type: 'error', text: `❌ Datos de ${symbol} tienen problemas` });
      }
    } catch (error) {
      console.error('Error validando datos:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al validar datos' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (symbol) => {
    if (!window.confirm(`¿Eliminar todos los datos de ${symbol}?`)) {
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const response = await axios.delete(`${API_URL}/api/data/${symbol}`);
      setMessage({ type: 'success', text: response.data.message });
      loadDataSources();
    } catch (error) {
      console.error('Error eliminando datos:', error);
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error al eliminar datos' 
      });
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString();
  };

  const getAssetTypeColor = (type) => {
    const colors = {
      crypto: 'bg-blue-100 text-blue-800',
      stock: 'bg-green-100 text-green-800',
      forex: 'bg-purple-100 text-purple-800',
      commodity: 'bg-yellow-100 text-yellow-800',
      index: 'bg-red-100 text-red-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-2">
          <Database className="w-8 h-8 text-blue-600" />
          Gestión de Datos de Mercado
        </h1>
        <p className="text-gray-600">
          Administra los datos históricos almacenados en PostgreSQL
        </p>
      </div>

      {/* Message Alert */}
      {message && (
        <div className={`mb-6 p-4 rounded-lg ${
          message.type === 'success' ? 'bg-green-50 text-green-800 border border-green-200' : 'bg-red-50 text-red-800 border border-red-200'
        }`}>
          {message.text}
        </div>
      )}

      {/* Fetch Data Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
          <Download className="w-5 h-5 text-blue-600" />
          Descargar Nuevos Datos
        </h2>
        
        <form onSubmit={handleFetchData} className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Símbolo
            </label>
            <input
              type="text"
              value={fetchForm.symbol}
              onChange={(e) => setFetchForm({ ...fetchForm, symbol: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              placeholder="BTC/USDT"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Temporalidad
            </label>
            <select
              value={fetchForm.timeframe}
              onChange={(e) => setFetchForm({ ...fetchForm, timeframe: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="1d">1 Día</option>
              <option value="4h">4 Horas</option>
              <option value="1h">1 Hora</option>
              <option value="15m">15 Minutos</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Días
            </label>
            <input
              type="number"
              value={fetchForm.days}
              onChange={(e) => setFetchForm({ ...fetchForm, days: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              min="1"
              max="1825"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tipo de Activo
            </label>
            <select
              value={fetchForm.assetType}
              onChange={(e) => setFetchForm({ ...fetchForm, assetType: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="crypto">Crypto</option>
              <option value="stock">Stock</option>
              <option value="forex">Forex</option>
              <option value="commodity">Commodity</option>
              <option value="index">Index</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-md disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  Descargando...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Descargar
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {/* Data Sources Table */}
      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Activity className="w-5 h-5 text-blue-600" />
              Fuentes de Datos Disponibles
            </h2>
            <button
              onClick={loadDataSources}
              disabled={loading}
              className="text-blue-600 hover:text-blue-700 font-medium flex items-center gap-1"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Recargar
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Símbolo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Exchange
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Registros
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Desde - Hasta
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Última Actualización
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {sources.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-6 py-8 text-center text-gray-500">
                    {loading ? 'Cargando...' : 'No hay fuentes de datos disponibles. Descarga algunos datos para comenzar.'}
                  </td>
                </tr>
              ) : (
                sources.map((source) => (
                  <tr key={source.symbol} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="w-4 h-4 text-gray-400" />
                        <span className="font-medium text-gray-900">{source.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getAssetTypeColor(source.asset_type)}`}>
                        {source.asset_type.toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {source.exchange || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                      {source.total_records?.toLocaleString() || '0'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        {formatDate(source.min_date)} - {formatDate(source.max_date)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(source.last_updated)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => handleValidate(source.symbol)}
                          disabled={loading}
                          className="text-green-600 hover:text-green-900 disabled:text-gray-400"
                          title="Validar calidad de datos"
                        >
                          <CheckCircle className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleRefresh(source.symbol)}
                          disabled={loading}
                          className="text-blue-600 hover:text-blue-900 disabled:text-gray-400"
                          title="Actualizar datos"
                        >
                          <RefreshCw className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleDelete(source.symbol)}
                          disabled={loading}
                          className="text-red-600 hover:text-red-900 disabled:text-gray-400"
                          title="Eliminar datos"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Stats */}
      {sources.length > 0 && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-blue-600 text-sm font-medium mb-1">Total Fuentes</div>
            <div className="text-2xl font-bold text-blue-900">{sources.length}</div>
          </div>
          <div className="bg-green-50 rounded-lg p-4 border border-green-200">
            <div className="text-green-600 text-sm font-medium mb-1">Total Registros</div>
            <div className="text-2xl font-bold text-green-900">
              {sources.reduce((sum, s) => sum + (s.total_records || 0), 0).toLocaleString()}
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-purple-600 text-sm font-medium mb-1">Tipos de Activos</div>
            <div className="text-2xl font-bold text-purple-900">
              {new Set(sources.map(s => s.asset_type)).size}
            </div>
          </div>
        </div>
      )}

      {/* Validation Results */}
      {validationResult && (
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            {validationResult.is_valid ? (
              <CheckCircle className="w-5 h-5 text-green-600" />
            ) : (
              <XCircle className="w-5 h-5 text-red-600" />
            )}
            Resultados de Validación: {validationResult.symbol}
          </h3>

          {/* Errors */}
          {validationResult.errors && validationResult.errors.length > 0 && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h4 className="font-semibold text-red-800 mb-2 flex items-center gap-2">
                <XCircle className="w-4 h-4" />
                Errores Críticos
              </h4>
              <ul className="list-disc list-inside space-y-1">
                {validationResult.errors.map((error, idx) => (
                  <li key={idx} className="text-red-700 text-sm">{error}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings */}
          {validationResult.warnings && validationResult.warnings.length > 0 && (
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <h4 className="font-semibold text-yellow-800 mb-2 flex items-center gap-2">
                <AlertTriangle className="w-4 h-4" />
                Advertencias
              </h4>
              <ul className="list-disc list-inside space-y-1">
                {validationResult.warnings.map((warning, idx) => (
                  <li key={idx} className="text-yellow-700 text-sm">{warning}</li>
                ))}
              </ul>
            </div>
          )}

          {/* Stats */}
          {validationResult.stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-700 mb-2">Información General</h4>
                <div className="space-y-1 text-sm">
                  <div><span className="font-medium">Total Registros:</span> {validationResult.stats.total_records?.toLocaleString()}</div>
                  {validationResult.stats.date_range && (
                    <>
                      <div><span className="font-medium">Desde:</span> {new Date(validationResult.stats.date_range.start).toLocaleDateString()}</div>
                      <div><span className="font-medium">Hasta:</span> {new Date(validationResult.stats.date_range.end).toLocaleDateString()}</div>
                    </>
                  )}
                </div>
              </div>

              {validationResult.stats.price_range && (
                <div className="p-4 bg-gray-50 rounded-lg">
                  <h4 className="font-semibold text-gray-700 mb-2">Rango de Precios</h4>
                  <div className="space-y-1 text-sm">
                    <div><span className="font-medium">Mínimo:</span> ${validationResult.stats.price_range.min?.toLocaleString()}</div>
                    <div><span className="font-medium">Máximo:</span> ${validationResult.stats.price_range.max?.toLocaleString()}</div>
                    <div><span className="font-medium">Actual:</span> ${validationResult.stats.price_range.current?.toLocaleString()}</div>
                  </div>
                </div>
              )}
            </div>
          )}

          {validationResult.is_valid && validationResult.errors.length === 0 && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-medium flex items-center gap-2">
                <CheckCircle className="w-5 h-5" />
                ✅ Los datos pasaron todas las validaciones correctamente
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DataManager;
