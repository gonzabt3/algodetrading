import { useState } from 'react'
import StrategyRunner from './components/StrategyRunner'
import DataManager from './components/DataManager'
import { Activity, Database } from 'lucide-react'

function App() {
  const [activeTab, setActiveTab] = useState('backtest')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Tab Navigation */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto">
          <div className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('backtest')}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'backtest'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Activity className="w-5 h-5" />
              Backtesting
            </button>
            <button
              onClick={() => setActiveTab('data')}
              className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'data'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <Database className="w-5 h-5" />
              Gestión de Datos
            </button>
          </div>
        </div>
      </div>

      {/* Tab Content */}
      <div>
        {activeTab === 'backtest' && <StrategyRunner />}
        {activeTab === 'data' && <DataManager />}
      </div>
    </div>
  )
}

export default App

