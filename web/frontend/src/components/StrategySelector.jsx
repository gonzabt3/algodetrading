export default function StrategySelector({ strategies, selectedStrategy, onSelect }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
        <span>🎯</span>
        <span>Select Strategy</span>
      </h2>
      
      <div className="space-y-2">
        {strategies.map((strategy) => (
          <button
            key={strategy.id}
            onClick={() => onSelect(strategy)}
            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
              selectedStrategy?.id === strategy.id
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 hover:border-gray-600 bg-gray-700/30'
            }`}
          >
            <div className="font-semibold text-white">{strategy.name}</div>
            <div className="text-sm text-gray-400 mt-1">{strategy.description}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
