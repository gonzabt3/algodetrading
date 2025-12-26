import { useState, useEffect } from 'react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts'

const PairChart = ({ symbolA, symbolB, startDate, endDate }) => {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [viewMode, setViewMode] = useState('normalized') // 'normalized', 'spread', 'zscore'

  useEffect(() => {
    if (symbolA && symbolB && startDate && endDate) {
      fetchData()
    }
  }, [symbolA, symbolB, startDate, endDate])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/pair-data?symbol_a=${symbolA}&symbol_b=${symbolB}&start_date=${startDate}&end_date=${endDate}`
      )
      
      if (!response.ok) {
        throw new Error('Error al cargar datos del par')
      }
      
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex justify-center items-center h-96">
          <div className="text-gray-600">Cargando análisis del par...</div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p className="text-red-600">Error: {error}</p>
      </div>
    )
  }

  if (!data) {
    return null
  }

  // Preparar datos para el gráfico
  const chartData = data.timestamps.map((timestamp, idx) => ({
    timestamp,
    [data.symbol_a.name]: data.symbol_a.prices_normalized[idx],
    [data.symbol_b.name]: data.symbol_b.prices_normalized[idx],
    spread: data.spread[idx],
    z_score: data.z_score[idx],
    spread_ma: data.spread_ma[idx]
  }))

  // Calcular correlación
  const calculateCorrelation = (x, y) => {
    const n = x.length
    const sum_x = x.reduce((a, b) => a + b, 0)
    const sum_y = y.reduce((a, b) => a + b, 0)
    const sum_xy = x.reduce((acc, val, i) => acc + val * y[i], 0)
    const sum_x2 = x.reduce((acc, val) => acc + val * val, 0)
    const sum_y2 = y.reduce((acc, val) => acc + val * val, 0)
    
    const numerator = n * sum_xy - sum_x * sum_y
    const denominator = Math.sqrt((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y))
    
    return numerator / denominator
  }

  const correlation = calculateCorrelation(data.symbol_a.prices, data.symbol_b.prices)
  const currentSpread = data.spread[data.spread.length - 1]
  const currentZScore = data.z_score[data.z_score.length - 1]

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-800">
          Análisis de Pair Trading: {data.symbol_a.name} vs {data.symbol_b.name}
        </h2>
        
        <div className="flex gap-2">
          <button
            onClick={() => setViewMode('normalized')}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              viewMode === 'normalized'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Precios Normalizados
          </button>
          <button
            onClick={() => setViewMode('spread')}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              viewMode === 'spread'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Spread
          </button>
          <button
            onClick={() => setViewMode('zscore')}
            className={`px-4 py-2 rounded text-sm font-medium transition-colors ${
              viewMode === 'zscore'
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            }`}
          >
            Z-Score
          </button>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="timestamp"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis />
          <Tooltip />
          <Legend />

          {viewMode === 'normalized' && (
            <>
              <Line
                type="monotone"
                dataKey={data.symbol_a.name}
                stroke="#3b82f6"
                strokeWidth={2}
                dot={false}
                name={`${data.symbol_a.name} (Base 100)`}
              />
              <Line
                type="monotone"
                dataKey={data.symbol_b.name}
                stroke="#ef4444"
                strokeWidth={2}
                dot={false}
                name={`${data.symbol_b.name} (Base 100)`}
              />
            </>
          )}

          {viewMode === 'spread' && (
            <>
              <Line
                type="monotone"
                dataKey="spread"
                stroke="#8b5cf6"
                strokeWidth={2}
                dot={false}
                name="Spread"
              />
              <Line
                type="monotone"
                dataKey="spread_ma"
                stroke="#f59e0b"
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Media Móvil (20)"
              />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            </>
          )}

          {viewMode === 'zscore' && (
            <>
              <Line
                type="monotone"
                dataKey="z_score"
                stroke="#10b981"
                strokeWidth={2}
                dot={false}
                name="Z-Score"
              />
              <ReferenceLine y={2} stroke="#ef4444" strokeDasharray="3 3" label="Entry (+2σ)" />
              <ReferenceLine y={-2} stroke="#ef4444" strokeDasharray="3 3" label="Entry (-2σ)" />
              <ReferenceLine y={0.5} stroke="#f59e0b" strokeDasharray="3 3" label="Exit (+0.5σ)" />
              <ReferenceLine y={-0.5} stroke="#f59e0b" strokeDasharray="3 3" label="Exit (-0.5σ)" />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
            </>
          )}
        </LineChart>
      </ResponsiveContainer>

      <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
        <div className="bg-blue-50 p-3 rounded">
          <div className="text-gray-600 font-medium">Correlación</div>
          <div className={`text-xl font-bold ${correlation > 0.7 ? 'text-green-600' : correlation > 0.5 ? 'text-yellow-600' : 'text-red-600'}`}>
            {(correlation * 100).toFixed(2)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {correlation > 0.7 ? 'Alta correlación ✓' : correlation > 0.5 ? 'Correlación moderada' : 'Baja correlación ⚠️'}
          </div>
        </div>
        <div className="bg-purple-50 p-3 rounded">
          <div className="text-gray-600 font-medium">Spread Actual</div>
          <div className="text-xl font-bold text-purple-600">
            {currentSpread.toFixed(4)}
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Diferencia normalizada
          </div>
        </div>
        <div className="bg-green-50 p-3 rounded">
          <div className="text-gray-600 font-medium">Z-Score Actual</div>
          <div className={`text-xl font-bold ${Math.abs(currentZScore) > 2 ? 'text-red-600' : Math.abs(currentZScore) > 1 ? 'text-yellow-600' : 'text-green-600'}`}>
            {currentZScore.toFixed(2)}σ
          </div>
          <div className="text-xs text-gray-500 mt-1">
            {Math.abs(currentZScore) > 2 ? 'Oportunidad de entrada' : Math.abs(currentZScore) < 0.5 ? 'Cerca de la media' : 'Rango normal'}
          </div>
        </div>
      </div>
    </div>
  )
}

export default PairChart
