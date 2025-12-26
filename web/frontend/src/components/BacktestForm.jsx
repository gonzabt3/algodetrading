import { useState } from 'react'
import { useMutation, useQueryClient } from '@tantml/react-query'
import { tradingApi } from '../services/api'
import PairChart from './PairChart'

export default function BacktestForm({ strategy }) {
  const queryClient = useQueryClient()
  const isPairTrading = strategy.id === 'pair_trading'
  
  const [formData, setFormData] = useState({
    symbol: 'BTC/USDT',
    symbol_a: 'VIST',  // VISTA por defecto
    symbol_b: 'YPF',   // YPF por defecto (ticker correcto)
    days: 365,
    initial_capital: 10000,
    commission: 0.001,
    use_real_data: false,
  })
  
  // Calcular fechas para el gráfico de pair trading
  const getDateRange = () => {
    const endDate = new Date()
    const startDate = new Date()
    startDate.setDate(startDate.getDate() - formData.days)
    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0]
    }
  }
  
  const mutation = useMutation({
    mutationFn: (data) => tradingApi.runBacktest(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['backtests'])
      queryClient.invalidateQueries(['stats'])
      alert('Backtest completed successfully!')
    },
    onError: (error) => {
      alert(`Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    
    // Validate pair trading symbols
    if (isPairTrading && formData.symbol_a === formData.symbol_b) {
      alert('Please select different symbols for pair trading')
      return
    }
    
    const backtestData = {
      strategy_id: strategy.id,
      ...formData,
      params: strategy.default_params,
    }
    
    // For pair trading, remove single symbol field
    if (isPairTrading) {
      delete backtestData.symbol
    } else {
      // For single-symbol, remove pair fields
      delete backtestData.symbol_a
      delete backtestData.symbol_b
    }
    
    mutation.mutate(backtestData)
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : (type === 'number' ? parseFloat(value) : value)
    }))
  }

  const dateRange = getDateRange()

  return (
    <div className="space-y-6">
      {/* Mostrar gráfico de análisis solo para pair trading */}
      {isPairTrading && formData.symbol_a && formData.symbol_b && (
        <PairChart
          symbolA={formData.symbol_a}
          symbolB={formData.symbol_b}
          startDate={dateRange.start}
          endDate={dateRange.end}
        />
      )}

      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span>⚙️</span>
        <span>Backtest Configuration</span>
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Symbol Selection - Different for Pair Trading */}
        {isPairTrading ? (
          <>
            {/* Symbol A */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Symbol A (First Asset)
              </label>
              <select
                name="symbol_a"
                value={formData.symbol_a}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white"
              >
                <optgroup label="Criptomonedas">
                  <option value="BTC/USDT">BTC/USDT</option>
                  <option value="ETH/USDT">ETH/USDT</option>
                  <option value="SOL/USDT">SOL/USDT</option>
                </optgroup>
                <optgroup label="Acciones Argentinas">
                  <option value="VIST">VISTA (VIST)</option>
                  <option value="YPF">YPF (YPF)</option>
                  <option value="GGAL">Galicia (GGAL)</option>
                  <option value="BMA">Macro (BMA)</option>
                  <option value="SUPV">Supervielle (SUPV)</option>
                  <option value="PAM">Pampa (PAM)</option>
                </optgroup>
              </select>
            </div>

            {/* Symbol B */}
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Symbol B (Second Asset)
              </label>
              <select
                name="symbol_b"
                value={formData.symbol_b}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white"
              >
                <optgroup label="Criptomonedas">
                  <option value="BTC/USDT">BTC/USDT</option>
                  <option value="ETH/USDT">ETH/USDT</option>
                  <option value="SOL/USDT">SOL/USDT</option>
                </optgroup>
                <optgroup label="Acciones Argentinas">
                  <option value="VIST">VISTA (VIST)</option>
                  <option value="YPF">YPF (YPF)</option>
                  <option value="GGAL">Galicia (GGAL)</option>
                  <option value="BMA">Macro (BMA)</option>
                  <option value="SUPV">Supervielle (SUPV)</option>
                  <option value="PAM">Pampa (PAM)</option>
                </optgroup>
              </select>
                <option value="DOT/USDT">DOT/USDT</option>
                <option value="LINK/USDT">LINK/USDT</option>
              </select>
            </div>

            {/* Pair Info */}
            {formData.symbol_a === formData.symbol_b && (
              <div className="bg-yellow-900/30 border border-yellow-700 rounded-lg p-3">
                <p className="text-yellow-300 text-sm">
                  ⚠️ Warning: Both symbols are the same. Please select different assets for pair trading.
                </p>
              </div>
            )}
          </>
        ) : (
          /* Single Symbol */
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Symbol
            </label>
            <input
              type="text"
              name="symbol"
              value={formData.symbol}
              onChange={handleChange}
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white"
            />
          </div>
        )}

        {/* Days */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Days: {formData.days}
          </label>
          <input
            type="range"
            name="days"
            min="30"
            max="3650"
            value={formData.days}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-gray-500">
            <span>30 days</span>
            <span>10 years</span>
          </div>
        </div>

        {/* Initial Capital */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Initial Capital ($)
          </label>
          <input
            type="number"
            name="initial_capital"
            value={formData.initial_capital}
            onChange={handleChange}
            step="100"
            min="100"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white"
          />
        </div>

        {/* Commission */}
        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Commission ({(formData.commission * 100).toFixed(2)}%)
          </label>
          <input
            type="number"
            name="commission"
            value={formData.commission}
            onChange={handleChange}
            step="0.0001"
            min="0"
            max="0.1"
            className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none text-white"
          />
        </div>

        {/* Use Real Data */}
        <div className="flex items-center">
          <input
            type="checkbox"
            name="use_real_data"
            id="use_real_data"
            checked={formData.use_real_data}
            onChange={handleChange}
            className="w-4 h-4 text-blue-600 bg-gray-700 border-gray-600 rounded focus:ring-blue-500"
          />
          <label htmlFor="use_real_data" className="ml-2 text-sm font-medium text-gray-300">
            Use Real Market Data
          </label>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={mutation.isPending}
          className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {mutation.isPending ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Running Backtest...
            </span>
          ) : (
            '🚀 Run Backtest'
          )}
        </button>
      </form>

      {/* Strategy Parameters */}
      <div className="mt-6 pt-6 border-t border-gray-700">
        <h3 className="text-sm font-semibold text-gray-400 mb-2">Strategy Parameters:</h3>
        <pre className="text-xs bg-gray-900 p-3 rounded-lg overflow-auto text-gray-300">
          {JSON.stringify(strategy.default_params, null, 2)}
        </pre>
      </div>
    </div>
    </div>
  )
}
