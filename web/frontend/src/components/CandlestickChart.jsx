import { useState } from 'react';
import { 
  ComposedChart, Line, Bar, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, ReferenceLine 
} from 'recharts';

const CandlestickChart = ({ data, indicators = [] }) => {
  const [showVolume, setShowVolume] = useState(true);
  
  if (!data || data.length === 0) {
    return (
      <div className="text-center p-8 text-gray-500">
        No hay datos de velas disponibles
      </div>
    );
  }

  // Calcular rango de precios incluyendo velas e indicadores
  const allPriceValues = data.flatMap(d => {
    const values = [d.high, d.low, d.open, d.close];
    // Agregar valores de indicadores (MAs, Bollinger Bands, etc)
    Object.keys(d).forEach(key => {
      if (!['timestamp', 'open', 'high', 'low', 'close', 'volume'].includes(key) && typeof d[key] === 'number') {
        values.push(d[key]);
      }
    });
    return values;
  }).filter(p => p != null && !isNaN(p));
  
  const minPrice = Math.min(...allPriceValues);
  const maxPrice = Math.max(...allPriceValues);
  const priceRange = maxPrice - minPrice;

  // Función para renderizar una vela personalizada
  const CustomCandle = (props) => {
    const { x, y, width, height, payload, yAxisId } = props;
    
    if (!payload || payload.open == null || payload.close == null || payload.high == null || payload.low == null) {
      return null;
    }

    const { open, close, high, low } = payload;
    const isGreen = close >= open;
    const color = isGreen ? '#10b981' : '#ef4444';
    
    // Obtener el contexto del gráfico para convertir valores a coordenadas Y
    const chart = props;
    
    // Calcular el rango de precios para esta vela
    const priceMax = Math.max(open, close, high, low);
    const priceMin = Math.min(open, close, high, low);
    const priceRange = maxPrice - minPrice;
    
    // Calcular posiciones Y basadas en el dominio del eje
    const chartHeight = 400 - 50; // Altura del gráfico menos márgenes
    const yScale = (price) => {
      const normalized = (maxPrice - price) / priceRange;
      return 10 + (normalized * chartHeight);
    };
    
    const yHigh = yScale(high);
    const yLow = yScale(low);
    const yOpen = yScale(open);
    const yClose = yScale(close);
    
    const candleTop = Math.min(yOpen, yClose);
    const candleBottom = Math.max(yOpen, yClose);
    const candleHeight = Math.abs(yClose - yOpen) || 1;
    const candleWidth = width * 0.6;
    const candleX = x + (width - candleWidth) / 2;

    return (
      <g>
        {/* Mecha superior */}
        <line
          x1={x + width / 2}
          y1={yHigh}
          x2={x + width / 2}
          y2={candleTop}
          stroke={color}
          strokeWidth={1}
        />
        {/* Cuerpo de la vela */}
        <rect
          x={candleX}
          y={candleTop}
          width={candleWidth}
          height={candleHeight}
          fill={color}
          stroke={color}
          strokeWidth={1}
        />
        {/* Mecha inferior */}
        <line
          x1={x + width / 2}
          y1={candleBottom}
          x2={x + width / 2}
          y2={yLow}
          stroke={color}
          strokeWidth={1}
        />
      </g>
    );
  };

  // Tooltip personalizado
  const CustomTooltip = ({ active, payload, label }) => {
    if (!active || !payload || payload.length === 0) return null;

    const data = payload[0].payload;
    const date = new Date(label).toLocaleDateString('es-AR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });

    const isGreen = data.close >= data.open;

    return (
      <div className="bg-white p-4 rounded-lg shadow-xl border-2 border-gray-200">
        <p className="font-bold text-gray-800 mb-2">{date}</p>
        <div className="space-y-1 text-sm">
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">Open:</span>
            <span className="font-bold">${data.open?.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">High:</span>
            <span className="font-bold text-green-600">${data.high?.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">Low:</span>
            <span className="font-bold text-red-600">${data.low?.toFixed(2)}</span>
          </div>
          <div className="flex justify-between gap-4">
            <span className="text-gray-600">Close:</span>
            <span className={`font-bold ${isGreen ? 'text-green-600' : 'text-red-600'}`}>
              ${data.close?.toFixed(2)}
            </span>
          </div>
          {data.volume && (
            <div className="flex justify-between gap-4 pt-2 border-t">
              <span className="text-gray-600">Volume:</span>
              <span className="font-bold">{(data.volume / 1000000).toFixed(2)}M</span>
            </div>
          )}
          
          {/* Mostrar indicadores técnicos */}
          {Object.keys(data).filter(key => 
            !['timestamp', 'open', 'high', 'low', 'close', 'volume'].includes(key)
          ).map(indicator => (
            <div key={indicator} className="flex justify-between gap-4 text-xs">
              <span className="text-blue-600">{indicator}:</span>
              <span className="font-bold text-blue-800">
                {typeof data[indicator] === 'number' ? data[indicator].toFixed(2) : data[indicator]}
              </span>
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Detectar qué indicadores están en los datos
  const availableIndicators = data.length > 0 
    ? Object.keys(data[0]).filter(key => 
        !['timestamp', 'open', 'high', 'low', 'close', 'volume'].includes(key)
      )
    : [];

  // Separar indicadores por tipo
  const priceIndicators = availableIndicators.filter(ind => 
    ['ma_fast', 'ma_slow', 'sma', 'ema', 'bb_upper', 'bb_middle', 'bb_lower', 'upper_band', 'middle_band', 'lower_band'].includes(ind)
  );
  
  const oscillatorIndicators = availableIndicators.filter(ind => 
    ['rsi', 'macd', 'signal', 'histogram'].includes(ind)
  );

  // Debug: mostrar qué indicadores se detectaron
  console.log('🔍 CandlestickChart - Datos recibidos:', data.length, 'velas');
  console.log('🔍 Primera vela:', data[0]);
  console.log('🔍 Indicadores de precio:', priceIndicators);
  console.log('🔍 Indicadores osciladores:', oscillatorIndicators);

  // Colores para diferentes indicadores
  const indicatorColors = {
    'ma_fast': '#3b82f6',
    'ma_slow': '#ef4444',
    'sma': '#8b5cf6',
    'ema': '#10b981',
    'bb_upper': '#f59e0b',
    'bb_middle': '#6366f1',
    'bb_lower': '#f59e0b',
    'upper_band': '#f59e0b',
    'lower_band': '#f59e0b',
    'middle_band': '#6366f1',
    'rsi': '#ec4899',
    'macd': '#06b6d4',
    'signal': '#f97316',
  };

  return (
    <div className="space-y-4">
      {/* Controles */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-bold text-gray-900">
          📊 Gráfico de Velas con Indicadores
        </h3>
        <button
          onClick={() => setShowVolume(!showVolume)}
          className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors"
        >
          {showVolume ? '📊 Ocultar Volumen' : '📊 Mostrar Volumen'}
        </button>
      </div>

      {/* Leyenda de indicadores de precio */}
      {priceIndicators.length > 0 && (
        <div className="flex flex-wrap gap-3 text-xs">
          <span className="font-semibold text-gray-600">Indicadores de Precio:</span>
          {priceIndicators.map(indicator => (
            <div key={indicator} className="flex items-center gap-1">
              <div 
                className="w-3 h-3 rounded"
                style={{ backgroundColor: indicatorColors[indicator] || '#6b7280' }}
              />
              <span className="text-gray-700 font-medium">{indicator}</span>
            </div>
          ))}
        </div>
      )}

      {/* Gráfico Principal con Velas e Indicadores */}
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="colorVolume" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.05}/>
            </linearGradient>
          </defs>
          
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          
          <XAxis 
            dataKey="timestamp"
            tick={{ fontSize: 11 }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return `${date.getMonth() + 1}/${date.getDate()}`;
            }}
          />
          
          <YAxis 
            yAxisId="price"
            domain={[minPrice * 0.99, maxPrice * 1.01]}
            tick={{ fontSize: 11 }}
            tickFormatter={(value) => `$${value.toFixed(0)}`}
          />
          
          {showVolume && (
            <YAxis 
              yAxisId="volume"
              orientation="right"
              tick={{ fontSize: 11 }}
              tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
            />
          )}
          
          <Tooltip content={<CustomTooltip />} />
          <Legend />

          {/* Volumen como barras de fondo */}
          {showVolume && (
            <Bar 
              yAxisId="volume"
              dataKey="volume" 
              fill="url(#colorVolume)"
              name="Volumen"
              opacity={0.3}
            />
          )}

          {/* Renderizar velas primero (fondo) */}
          <Bar
            yAxisId="price"
            dataKey="close"
            shape={<CustomCandle />}
            name="Precio"
          />

          {/* Líneas de indicadores de precio encima */}
          {priceIndicators.map((indicator, idx) => (
            <Line
              key={indicator}
              yAxisId="price"
              type="monotone"
              dataKey={indicator}
              stroke={indicatorColors[indicator] || `hsl(${idx * 60}, 70%, 50%)`}
              strokeWidth={3}
              dot={false}
              name={indicator}
              connectNulls
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>

      {/* Gráfico de Osciladores (RSI, MACD, etc) */}
      {oscillatorIndicators.length > 0 && (
        <>
          <div className="flex flex-wrap gap-3 text-xs mt-4">
            <span className="font-semibold text-gray-600">Indicadores Osciladores:</span>
            {oscillatorIndicators.map(indicator => (
              <div key={indicator} className="flex items-center gap-1">
                <div 
                  className="w-3 h-3 rounded"
                  style={{ backgroundColor: indicatorColors[indicator] || '#6b7280' }}
                />
                <span className="text-gray-700 font-medium">{indicator}</span>
              </div>
            ))}
          </div>
          
          <ResponsiveContainer width="100%" height={150}>
            <ComposedChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              
              <XAxis 
                dataKey="timestamp"
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              
              <YAxis 
                domain={[0, 100]}
                tick={{ fontSize: 11 }}
                tickFormatter={(value) => value.toFixed(0)}
              />
              
              <Tooltip 
                contentStyle={{ fontSize: '12px' }}
                formatter={(value) => value.toFixed(2)}
              />
              <Legend wrapperStyle={{ fontSize: '11px' }} />

              {/* Líneas de referencia para RSI */}
              {oscillatorIndicators.includes('rsi') && (
                <>
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="3 3" label="Sobrecompra" />
                  <ReferenceLine y={30} stroke="#10b981" strokeDasharray="3 3" label="Sobreventa" />
                  <ReferenceLine y={50} stroke="#6b7280" strokeDasharray="2 2" />
                </>
              )}

              {/* Líneas de osciladores */}
              {oscillatorIndicators.map((indicator, idx) => (
                <Line
                  key={indicator}
                  type="monotone"
                  dataKey={indicator}
                  stroke={indicatorColors[indicator] || `hsl(${idx * 60}, 70%, 50%)`}
                  strokeWidth={2}
                  dot={false}
                  name={indicator}
                  connectNulls
                />
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  );
};

export default CandlestickChart;
