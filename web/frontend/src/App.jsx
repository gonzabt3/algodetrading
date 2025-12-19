import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { tradingApi } from './services/api'
import StrategySelector from './components/StrategySelector'
import BacktestForm from './components/BacktestForm'
import BacktestList from './components/BacktestList'
import StatsCard from './components/StatsCard'

function App() {
  const [selectedStrategy, setSelectedStrategy] = useState(null)

  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: () => tradingApi.getStats().then(res => res.data),
    refetchInterval: 5000, // Refresh every 5 seconds
  })

  const { data: strategies } = useQuery({
    queryKey: ['strategies'],
    queryFn: () => tradingApi.getStrategies().then(res => res.data),
  })

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-500">
            📊 Trading Dashboard
          </h1>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <StatsCard
            title="Total Backtests"
            value={stats?.total_backtests || 0}
            icon="📈"
            color="blue"
          />
          <StatsCard
            title="Strategies Tested"
            value={stats?.strategies_tested || 0}
            icon="🎯"
            color="purple"
          />
          <StatsCard
            title="Avg Return"
            value={`${stats?.avg_return?.toFixed(2) || 0}%`}
            icon="💰"
            color="green"
          />
          <StatsCard
            title="Total Trades"
            value={stats?.total_trades || 0}
            icon="🔄"
            color="orange"
          />
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Strategy & Form */}
          <div className="lg:col-span-1 space-y-6">
            <StrategySelector
              strategies={strategies || []}
              selectedStrategy={selectedStrategy}
              onSelect={setSelectedStrategy}
            />
            
            {selectedStrategy && (
              <BacktestForm strategy={selectedStrategy} />
            )}
          </div>

          {/* Right Column - Results */}
          <div className="lg:col-span-2">
            <BacktestList />
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
