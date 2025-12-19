import { useQuery } from '@tanstack/react-query'
import { tradingApi } from '../services/api'

export default function BacktestList() {
  const { data: backtests, isLoading, error } = useQuery({
    queryKey: ['backtests'],
    queryFn: tradingApi.getBacktests,
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  if (isLoading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-center py-8">
          <svg className="animate-spin h-8 w-8 text-blue-500" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <span className="ml-3 text-gray-400">Loading backtests...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6 border border-red-700">
        <p className="text-red-400">❌ Error loading backtests: {error.message}</p>
      </div>
    )
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getReturnColor = (returnPct) => {
    if (returnPct >= 10) return 'text-green-400'
    if (returnPct >= 0) return 'text-green-300'
    if (returnPct >= -10) return 'text-red-300'
    return 'text-red-400'
  }

  const getSharpeColor = (sharpe) => {
    if (sharpe >= 2) return 'text-purple-400'
    if (sharpe >= 1) return 'text-blue-400'
    if (sharpe >= 0) return 'text-gray-400'
    return 'text-red-400'
  }

  return (
    <div className="bg-gray-800 rounded-lg border border-gray-700">
      <div className="p-6 border-b border-gray-700">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <span>📊</span>
          <span>Backtest Results</span>
          <span className="ml-auto text-sm font-normal text-gray-400">
            {backtests?.length || 0} backtests
          </span>
        </h2>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Strategy
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                Return
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                Sharpe
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                Trades
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-400 uppercase tracking-wider">
                Win Rate
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700">
            {backtests && backtests.length > 0 ? (
              backtests.map((backtest) => (
                <tr
                  key={backtest.id}
                  className="hover:bg-gray-750 transition-colors cursor-pointer"
                  onClick={() => window.open(`http://localhost:8000/api/backtests/${backtest.id}`, '_blank')}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-2 h-2 rounded-full bg-blue-500 mr-3" />
                      <span className="text-sm font-medium text-white">
                        {backtest.strategy_name}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-300">{backtest.symbol}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className={`text-sm font-semibold ${getReturnColor(backtest.total_return)}`}>
                      {backtest.total_return >= 0 ? '+' : ''}
                      {backtest.total_return.toFixed(2)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className={`text-sm font-semibold ${getSharpeColor(backtest.sharpe_ratio)}`}>
                      {backtest.sharpe_ratio?.toFixed(2) || 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className="text-sm text-gray-300">{backtest.total_trades}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right">
                    <span className="text-sm text-gray-300">
                      {backtest.win_rate?.toFixed(1)}%
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-xs text-gray-500">
                      {formatDate(backtest.executed_at)}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="7" className="px-6 py-8 text-center">
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-4xl">📭</span>
                    <p className="text-gray-400">No backtests yet</p>
                    <p className="text-sm text-gray-500">
                      Select a strategy and run your first backtest
                    </p>
                  </div>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
