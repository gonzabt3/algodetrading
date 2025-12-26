import { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, Area, AreaChart 
} from 'recharts';
import CandlestickChart from './CandlestickChart';
import PairChart from './PairChart';

const API_URL = 'http://localhost:8000';

const StrategyRunner = () => {
  // Estado
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState('');
  const [symbol, setSymbol] = useState('BTC/USDT');
  const [symbolA, setSymbolA] = useState('VIST');
  const [symbolB, setSymbolB] = useState('YPF');
  const [days, setDays] = useState(180);
  const [capital, setCapital] = useState(10000);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [dataHealth, setDataHealth] = useState(null);

  // Símbolos populares
  const symbols = [
    'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT',
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA'
  ];

  // Acciones argentinas
  const argentineStocks = [
    { value: 'VIST', label: 'VISTA (VIST)' },
    { value: 'YPF', label: 'YPF (YPF)' },
    { value: 'GGAL', label: 'Galicia (GGAL)' },
    { value: 'BMA', label: 'Macro (BMA)' },
    { value: 'SUPV', label: 'Supervielle (SUPV)' },
    { value: 'PAM', label: 'Pampa (PAM)' },
  ];

  // Verificar si la estrategia seleccionada es pair trading
  const isPairTrading = selectedStrategy === 'pair_trading';

  // Cargar estrategias al montar
  useEffect(() => {
    loadStrategies();
    loadHistory();
  }, []);

  // Verificar salud de datos cuando cambia el símbolo
  useEffect(() => {
    checkDataHealth();
  }, [symbol]);

  const checkDataHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/data-health/${symbol}`);
      setDataHealth(response.data);
    } catch (err) {
      console.error('Error checking data health:', err);
      setDataHealth(null);
    }
  };

  const loadStrategies = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/strategies`);
      setStrategies(response.data);
      if (response.data.length > 0) {
        setSelectedStrategy(response.data[0].id);
      }
    } catch (err) {
      console.error('Error loading strategies:', err);
      setError('No se pudieron cargar las estrategias');
    }
  };

  const loadHistory = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/backtests?limit=10`);
      setHistory(response.data);
    } catch (err) {
      console.error('Error loading history:', err);
    }
  };

  const runBacktest = async () => {
    if (!selectedStrategy) {
      setError('Selecciona una estrategia');
      return;
    }

    // Validar símbolos para pair trading
    if (isPairTrading && symbolA === symbolB) {
      setError('Por favor selecciona símbolos diferentes para pair trading');
      return;
    }

    setLoading(true);
    setError(null);
    setResults(null);

    try {
      // Construir payload según el tipo de estrategia
      const payload = {
        strategy_id: selectedStrategy,
        days: days,
        initial_capital: capital,
        commission: 0.001
      };

      // Agregar símbolos según el tipo de estrategia
      if (isPairTrading) {
        payload.symbol_a = symbolA;
        payload.symbol_b = symbolB;
      } else {
        payload.symbol = symbol;
      }

      const response = await axios.post(`${API_URL}/api/backtest`, payload);

      // El response.data contiene el BacktestResponse del backend
      if (response.data.success && response.data.results) {
        // Asegurar que los valores numéricos sean válidos
        const results = response.data.results;
        const sanitizedResults = {
          ...results,
          total_return: results.total_return ?? 0,
          sharpe_ratio: results.sharpe_ratio ?? 0,
          max_drawdown: results.max_drawdown ?? 0,
          win_rate: results.win_rate ?? 0,
          total_trades: results.total_trades ?? 0,
          initial_capital: results.initial_capital ?? capital,
          final_capital: results.final_capital ?? capital,
          equity_curve: results.equity_curve ?? [],
          trades: results.trades ?? [],
          chart_data: results.chart_data ?? []  // Datos de velas con indicadores
        };
        setResults(sanitizedResults);
      } else {
        setError(response.data.message || 'Error al ejecutar el backtest');
      }
      
      loadHistory(); // Recargar historial
    } catch (err) {
      console.error('Error running backtest:', err);
      setError(err.response?.data?.detail || 'Error al ejecutar el backtest');
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercent = (value) => {
    if (value === null || value === undefined || isNaN(value)) return '0.00%';
    return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;
  };

  const getReturnColor = (value) => {
    if (value > 0) return 'text-green-600';
    if (value < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getStrategyEmoji = (strategyId) => {
    const emojis = {
      'ma_crossover': '📊',
      'rsi': '📈',
      'macd': '🎯',
      'bollinger_bands': '🎪',
      'mean_reversion': '↩️',
      'multi_indicator': '🔮'
    };
    return emojis[strategyId] || '💹';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            🚀 Laboratorio de Estrategias
          </h1>
          <p className="text-gray-600">
            Ejecuta backtests de diferentes estrategias y visualiza los resultados
          </p>
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-lg p-6 sticky top-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                ⚙️ Configuración
              </h2>

              {/* Strategy Selection */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Estrategia
                </label>
                <select
                  value={selectedStrategy}
                  onChange={(e) => setSelectedStrategy(e.target.value)}
                  className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                >
                  {strategies.map((strategy) => (
                    <option key={strategy.id} value={strategy.id}>
                      {getStrategyEmoji(strategy.id)} {strategy.name}
                    </option>
                  ))}
                </select>
                {selectedStrategy && (
                  <p className="text-xs text-gray-500 mt-2">
                    {strategies.find(s => s.id === selectedStrategy)?.description}
                  </p>
                )}
                
                {/* MA Crossover Configuration Info */}
                {selectedStrategy === 'ma_crossover' && (
                  <div className="mt-4 p-4 bg-blue-50 border-2 border-blue-200 rounded-xl">
                    <h3 className="text-sm font-bold text-blue-900 mb-2 flex items-center">
                      <span className="mr-2">📊</span>
                      Configuración de Medias Móviles
                    </h3>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between items-center">
                        <span className="text-blue-700 font-medium">Media Rápida:</span>
                        <span className="text-blue-900 font-bold">20 períodos</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-blue-700 font-medium">Media Lenta:</span>
                        <span className="text-blue-900 font-bold">50 períodos</span>
                      </div>
                      <div className="mt-3 pt-3 border-t border-blue-300">
                        <p className="text-xs text-blue-800">
                          <span className="font-semibold">Señal de Compra:</span> MA rápida cruza por encima de MA lenta
                        </p>
                        <p className="text-xs text-blue-800 mt-1">
                          <span className="font-semibold">Señal de Venta:</span> MA rápida cruza por debajo de MA lenta
                        </p>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Symbol Selection */}
              {isPairTrading ? (
                /* Pair Trading: Dos selectores */
                <>
                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Símbolo A (Primera Acción)
                    </label>
                    <select
                      value={symbolA}
                      onChange={(e) => setSymbolA(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                    >
                      <optgroup label="🪙 Criptomonedas">
                        <option value="BTC/USDT">BTC/USDT</option>
                        <option value="ETH/USDT">ETH/USDT</option>
                        <option value="SOL/USDT">SOL/USDT</option>
                      </optgroup>
                      <optgroup label="📈 Acciones Argentinas">
                        {argentineStocks.map((stock) => (
                          <option key={stock.value} value={stock.value}>{stock.label}</option>
                        ))}
                      </optgroup>
                    </select>
                  </div>

                  <div className="mb-6">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Símbolo B (Segunda Acción)
                    </label>
                    <select
                      value={symbolB}
                      onChange={(e) => setSymbolB(e.target.value)}
                      className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                    >
                      <optgroup label="🪙 Criptomonedas">
                        <option value="BTC/USDT">BTC/USDT</option>
                        <option value="ETH/USDT">ETH/USDT</option>
                        <option value="SOL/USDT">SOL/USDT</option>
                      </optgroup>
                      <optgroup label="📈 Acciones Argentinas">
                        {argentineStocks.map((stock) => (
                          <option key={stock.value} value={stock.value}>{stock.label}</option>
                        ))}
                      </optgroup>
                    </select>
                  </div>

                  {/* Advertencia si son iguales */}
                  {symbolA === symbolB && (
                    <div className="mb-6 bg-yellow-50 border-2 border-yellow-300 rounded-xl p-4">
                      <p className="text-yellow-800 text-sm font-medium">
                        ⚠️ Advertencia: Ambos símbolos son iguales. Por favor selecciona activos diferentes para pair trading.
                      </p>
                    </div>
                  )}
                </>
              ) : (
                /* Estrategias de un solo símbolo */
                <div className="mb-6">
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Símbolo
                  </label>
                  <select
                    value={symbol}
                    onChange={(e) => setSymbol(e.target.value)}
                    className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                  >
                    <optgroup label="🪙 Criptomonedas">
                      {symbols.slice(0, 5).map((sym) => (
                        <option key={sym} value={sym}>{sym}</option>
                      ))}
                    </optgroup>
                    <optgroup label="📈 Acciones">
                      {symbols.slice(5).map((sym) => (
                        <option key={sym} value={sym}>{sym}</option>
                      ))}
                    </optgroup>
                  </select>
                  
                  {/* Data Health Check */}
                  {dataHealth && (
                    <div className={`mt-3 p-3 rounded-lg text-xs ${
                      dataHealth.status === 'ok' 
                        ? 'bg-green-50 border border-green-200' 
                        : 'bg-red-50 border border-red-200'
                    }`}>
                      {dataHealth.status === 'ok' ? (
                        <>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-bold text-green-800">✅ Datos Reales</span>
                            <span className="text-green-700">{dataHealth.total_records} registros</span>
                          </div>
                          <div className="space-y-1 text-green-700">
                            <div className="flex justify-between">
                              <span>Máximo histórico:</span>
                              <span className="font-bold">${dataHealth.price_stats.max_high.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Precio actual:</span>
                              <span className="font-bold">${dataHealth.price_stats.current_price.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Rango de fechas:</span>
                              <span className="font-semibold">{dataHealth.date_range.days} días</span>
                            </div>
                          </div>
                          {dataHealth.verification && (
                            <div className="mt-2 pt-2 border-t border-green-300 text-green-800">
                              {dataHealth.verification}
                            </div>
                          )}
                          {dataHealth.warning && (
                            <div className="mt-2 pt-2 border-t border-yellow-300 text-yellow-800">
                              {dataHealth.warning}
                            </div>
                          )}
                        </>
                      ) : (
                        <div className="text-red-800">
                          <div className="font-bold mb-1">❌ Sin datos reales</div>
                          <div>Se usarán datos sintéticos</div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Days Selection */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Período: {days} días
                </label>
                <input
                  type="range"
                  min="30"
                  max="365"
                  step="30"
                  value={days}
                  onChange={(e) => setDays(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>30d</span>
                  <span>180d</span>
                  <span>365d</span>
                </div>
              </div>

              {/* Capital Input */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Capital Inicial
                </label>
                <div className="relative">
                  <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 font-medium">
                    $
                  </span>
                  <input
                    type="number"
                    value={capital}
                    onChange={(e) => setCapital(parseFloat(e.target.value))}
                    className="w-full pl-8 pr-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-colors"
                    min="1000"
                    step="1000"
                  />
                </div>
              </div>

              {/* Run Button */}
              <button
                onClick={runBacktest}
                disabled={loading}
                className={`w-full py-4 px-6 rounded-xl font-bold text-white text-lg transition-all transform hover:scale-105 shadow-lg ${
                  loading
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700'
                }`}
              >
                {loading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Ejecutando...
                  </span>
                ) : (
                  '🚀 Ejecutar Backtest'
                )}
              </button>

              {/* Error Message */}
              {error && (
                <div className="mt-4 p-4 bg-red-50 border-2 border-red-200 rounded-xl">
                  <p className="text-sm text-red-800 font-medium">❌ {error}</p>
                </div>
              )}
            </div>
          </div>

          {/* Results Panel */}
          <div className="lg:col-span-2">
            {!results && !loading && (
              <div className="bg-white rounded-2xl shadow-lg p-12 text-center">
                <div className="text-6xl mb-4">📊</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Listo para comenzar
                </h3>
                <p className="text-gray-600">
                  Configura los parámetros y ejecuta tu primer backtest
                </p>
              </div>
            )}

            {results && (
              <div className="space-y-6">
                {/* Pair Trading Chart - Solo para pair trading */}
                {isPairTrading && (
                  <PairChart
                    symbolA={symbolA}
                    symbolB={symbolB}
                    startDate={new Date(Date.now() - days * 24 * 60 * 60 * 1000).toISOString().split('T')[0]}
                    endDate={new Date().toISOString().split('T')[0]}
                  />
                )}

                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="bg-white rounded-xl shadow-lg p-4">
                    <div className="text-xs text-gray-500 mb-1">Retorno Total</div>
                    <div className={`text-2xl font-bold ${getReturnColor(results.total_return || 0)}`}>
                      {formatPercent(results.total_return || 0)}
                    </div>
                  </div>
                  <div className="bg-white rounded-xl shadow-lg p-4">
                    <div className="text-xs text-gray-500 mb-1">Capital Final</div>
                    <div className="text-2xl font-bold text-gray-900">
                      {formatCurrency(results.final_capital || 0)}
                    </div>
                  </div>
                  <div className="bg-white rounded-xl shadow-lg p-4">
                    <div className="text-xs text-gray-500 mb-1">Sharpe Ratio</div>
                    <div className="text-2xl font-bold text-blue-600">
                      {results.sharpe_ratio != null ? results.sharpe_ratio.toFixed(2) : '0.00'}
                    </div>
                  </div>
                  <div className="bg-white rounded-xl shadow-lg p-4">
                    <div className="text-xs text-gray-500 mb-1">Max Drawdown</div>
                    <div className="text-2xl font-bold text-red-600">
                      {formatPercent(results.max_drawdown || 0)}
                    </div>
                  </div>
                </div>

                {/* Detailed Stats */}
                <div className="bg-white rounded-2xl shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">
                    📈 Estadísticas Detalladas
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Total Operaciones</div>
                      <div className="text-lg font-bold text-gray-900">{results.total_trades || 0}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Win Rate</div>
                      <div className="text-lg font-bold text-green-600">
                        {results.win_rate != null ? results.win_rate.toFixed(1) : '0.0'}%
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Capital Inicial</div>
                      <div className="text-lg font-bold text-gray-900">
                        {formatCurrency(results.initial_capital || 0)}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Ganancia/Pérdida</div>
                      <div className={`text-lg font-bold ${getReturnColor((results.final_capital || 0) - (results.initial_capital || 0))}`}>
                        {formatCurrency((results.final_capital || 0) - (results.initial_capital || 0))}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Estrategia</div>
                      <div className="text-lg font-bold text-gray-900">
                        {getStrategyEmoji(results.strategy_type || selectedStrategy)} {results.strategy_name || 'N/A'}
                      </div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Símbolo</div>
                      <div className="text-lg font-bold text-gray-900">
                        {isPairTrading ? `${symbolA} / ${symbolB}` : (results.symbol || symbol)}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Candlestick Chart with Indicators - NUEVO */}
                {results.chart_data && results.chart_data.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-lg p-6">
                    <CandlestickChart data={results.chart_data} />
                  </div>
                )}

                {/* Equity Curve Chart */}
                {results.equity_curve && results.equity_curve.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-4">
                      💰 Curva de Capital
                    </h3>
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={results.equity_curve}>
                        <defs>
                          <linearGradient id="colorEquity" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                        <XAxis 
                          dataKey="timestamp" 
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => {
                            const date = new Date(value);
                            return `${date.getMonth() + 1}/${date.getDate()}`;
                          }}
                        />
                        <YAxis 
                          tick={{ fontSize: 12 }}
                          tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                        />
                        <Tooltip 
                          formatter={(value) => formatCurrency(value)}
                          labelFormatter={(label) => new Date(label).toLocaleDateString()}
                        />
                        <Area 
                          type="monotone" 
                          dataKey="equity" 
                          stroke="#3b82f6" 
                          fillOpacity={1} 
                          fill="url(#colorEquity)" 
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                )}

                {/* Trades Table */}
                {results.trades && Array.isArray(results.trades) && results.trades.length > 0 && (
                  <div className="bg-white rounded-2xl shadow-lg p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-2">
                      📋 Historial de Operaciones {isPairTrading ? '(Ambas Acciones)' : ''}
                    </h3>
                    {isPairTrading && (
                      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
                        <p className="text-blue-800">
                          <strong>💡 Pair Trading:</strong> Opera ambas acciones simultáneamente con posiciones opuestas.
                          <span className="ml-2">
                            <span className="inline-block bg-green-100 text-green-700 px-2 py-0.5 rounded text-xs font-bold mr-1">LONG</span>
                            = Compra barato, vende caro (ganas si sube ↗)
                          </span>
                          <span className="ml-2">
                            <span className="inline-block bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-bold mr-1">SHORT</span>
                            = Vende caro, compra barato (ganas si baja ↘)
                          </span>
                        </p>
                      </div>
                    )}
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b-2 border-gray-200">
                            {isPairTrading && <th className="text-left py-3 px-2 text-xs font-semibold text-gray-700">Símbolo</th>}
                            <th className="text-left py-3 px-2 text-xs font-semibold text-gray-700">Tipo</th>
                            <th className="text-left py-3 px-2 text-xs font-semibold text-gray-700">Entrada</th>
                            <th className="text-left py-3 px-2 text-xs font-semibold text-gray-700">Salida</th>
                            <th className="text-right py-3 px-2 text-xs font-semibold text-gray-700">Retorno</th>
                          </tr>
                        </thead>
                        <tbody>
                          {results.trades.slice(0, 20).map((trade, idx) => (
                            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                              {isPairTrading && (
                                <td className="py-2 px-2">
                                  <span className="font-mono text-xs font-semibold text-blue-600">
                                    {trade.symbol}
                                  </span>
                                </td>
                              )}
                              <td className="py-2 px-2">
                                <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                                  trade.trade_type === 'LONG' 
                                    ? 'bg-green-100 text-green-700' 
                                    : 'bg-red-100 text-red-700'
                                }`}>
                                  {trade.trade_type || 'LONG'}
                                </span>
                              </td>
                              <td className="py-2 px-2">
                                <div className="text-xs font-medium">
                                  {trade.entry_date ? new Date(trade.entry_date).toLocaleDateString('es-AR', { month: 'short', day: 'numeric' }) : '-'}
                                </div>
                                <div className="text-xs text-gray-500">
                                  ${(trade.entry_price || 0).toFixed(2)}
                                </div>
                              </td>
                              <td className="py-2 px-2">
                                <div className="text-xs font-medium">
                                  {trade.exit_date ? new Date(trade.exit_date).toLocaleDateString('es-AR', { month: 'short', day: 'numeric' }) : '-'}
                                </div>
                                <div className="text-xs text-gray-500">
                                  ${(trade.exit_price || 0).toFixed(2)}
                                </div>
                              </td>
                              <td className={`py-2 px-2 text-right font-bold text-sm ${getReturnColor(trade.return_pct || 0)}`}>
                                {formatPercent(trade.return_pct || 0)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                      {results.trades.length > 20 && (
                        <div className="mt-4 text-center text-sm text-gray-500">
                          Mostrando 20 de {results.trades.length} operaciones
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* History Section */}
        {history.length > 0 && (
          <div className="mt-8 bg-white rounded-2xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              📚 Historial de Backtests
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {history.map((item) => (
                <div 
                  key={item.id} 
                  className="border-2 border-gray-200 rounded-xl p-4 hover:border-blue-500 transition-colors cursor-pointer"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-lg font-bold">
                      {getStrategyEmoji(item.strategy_name)} {item.strategy_name}
                    </span>
                    <span className={`text-sm font-bold ${getReturnColor(item.total_return)}`}>
                      {formatPercent(item.total_return)}
                    </span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {item.symbol} • {item.total_trades} trades
                  </div>
                  <div className="text-xs text-gray-400 mt-2">
                    {new Date(item.executed_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategyRunner;
