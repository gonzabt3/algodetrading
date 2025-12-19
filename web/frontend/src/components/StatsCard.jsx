const colorClasses = {
  blue: 'from-blue-500 to-blue-600',
  purple: 'from-purple-500 to-purple-600',
  green: 'from-green-500 to-green-600',
  orange: 'from-orange-500 to-orange-600',
}

export default function StatsCard({ title, value, icon, color = 'blue' }) {
  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-gray-600 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-gray-400 text-sm font-medium">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <p className={`text-3xl font-bold bg-gradient-to-r ${colorClasses[color]} text-transparent bg-clip-text`}>
        {value}
      </p>
    </div>
  )
}
