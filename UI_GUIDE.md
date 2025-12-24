# 🎨 Trading Strategy Runner - Interfaz Gráfica

## 🚀 ¿Qué es esto?

Una interfaz gráfica moderna y fácil de usar para:
- ✅ Ejecutar backtests de diferentes estrategias de trading
- ✅ Visualizar resultados con gráficos interactivos
- ✅ Comparar el rendimiento de tus estrategias
- ✅ Ver historial de ejecuciones

---

## 📋 Requisitos Previos

1. **Backend (API) corriendo** en `http://localhost:8000`
2. **Frontend corriendo** en `http://localhost:3000` (puerto 5173 con Vite)
3. Base de datos PostgreSQL activa

---

## 🎯 Cómo Usar

### 1️⃣ Iniciar los Servicios

#### Opción A: Usando el script automático

```bash
# En una terminal
cd /home/gonza/Develop/algodetraiding
./start_dashboard.sh
```

#### Opción B: Manual

```bash
# Terminal 1: Iniciar Backend
cd /home/gonza/Develop/algodetraiding
source venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Iniciar Frontend
cd /home/gonza/Develop/algodetraiding/web/frontend
npm run dev
```

### 2️⃣ Abrir la UI

Abre tu navegador en: **http://localhost:3000** (o el puerto que muestre Vite)

---

## 🎨 Características de la UI

### Panel de Control (Izquierda)

#### 📊 Selección de Estrategia
- **MA Crossover** 📊 - Cruces de medias móviles (Principiantes)
- **RSI** 📈 - Relative Strength Index (Intermedio)
- **MACD** 🎯 - Moving Average Convergence Divergence (Intermedio)
- **Bollinger Bands** 🎪 - Bandas de volatilidad (Intermedio) ⬅️ **NUEVO!**
- **Mean Reversion** ↩️ - Reversión a la media (Avanzado)
- **Multi-Indicator** 🔮 - Combinación de indicadores (Avanzado)

#### 🪙 Selección de Símbolo
**Criptomonedas:**
- BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT, ADA/USDT

**Acciones:**
- AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA

#### ⏰ Período de Tiempo
- Slider: 30 a 365 días
- Valores recomendados: 90, 180, 365 días

#### 💰 Capital Inicial
- Mínimo: $1,000
- Por defecto: $10,000
- Incrementos: $1,000

### Panel de Resultados (Derecha)

#### 📊 Tarjetas de Métricas
```
┌──────────────────┬──────────────────┐
│ Retorno Total    │ Capital Final    │
│ +15.50%          │ $11,550.00       │
├──────────────────┼──────────────────┤
│ Sharpe Ratio     │ Max Drawdown     │
│ 1.25             │ -8.30%           │
└──────────────────┴──────────────────┘
```

#### 📈 Estadísticas Detalladas
- Total de operaciones
- Win Rate (% ganadas)
- Ganancia/Pérdida neta
- Estrategia utilizada
- Símbolo operado

#### 💰 Curva de Capital
Gráfico interactivo que muestra:
- Evolución del capital a lo largo del tiempo
- Identificación visual de ganancias y pérdidas
- Tooltips con información detallada al pasar el mouse

#### 📋 Historial de Operaciones
Tabla con todas las operaciones:
- Tipo (LONG/SHORT)
- Fecha de entrada y salida
- Precios de entrada y salida
- Retorno porcentual de cada operación

#### 📚 Historial de Backtests
Tarjetas con los últimos 10 backtests ejecutados:
- Estrategia utilizada
- Símbolo
- Retorno obtenido
- Número de operaciones
- Fecha de ejecución

---

## 🎨 Código de Colores

### 📊 Retornos
- 🟢 **Verde**: Retorno positivo (ganancia)
- 🔴 **Rojo**: Retorno negativo (pérdida)
- ⚫ **Gris**: Retorno neutro (0%)

### 📈 Sharpe Ratio
- 🟢 **> 1.0**: Excelente (buena relación riesgo/recompensa)
- 🟡 **0.5-1.0**: Bueno
- 🟠 **< 0.5**: Mediocre
- 🔴 **< 0**: Malo (pérdida)

### 📉 Drawdown
- 🟢 **0-10%**: Bajo riesgo
- 🟡 **10-20%**: Riesgo moderado
- 🟠 **20-30%**: Alto riesgo
- 🔴 **> 30%**: Muy alto riesgo

---

## 🔧 Flujo de Trabajo Recomendado

### Para Principiantes

1. **Comenzar Simple**
   ```
   Estrategia: MA Crossover
   Símbolo: BTC/USDT
   Período: 180 días
   Capital: $10,000
   ```

2. **Observar Resultados**
   - ¿El retorno es positivo?
   - ¿El Sharpe Ratio es > 0.5?
   - ¿El Max Drawdown es < 20%?

3. **Experimentar**
   - Cambia el período (90, 180, 365 días)
   - Prueba diferentes símbolos
   - Compara estrategias

### Para Intermedios

1. **Probar Múltiples Estrategias**
   ```bash
   # Ejecuta cada estrategia con el mismo símbolo y período
   1. MA Crossover
   2. RSI
   3. MACD
   4. Bollinger Bands
   ```

2. **Comparar Métricas**
   - Observa el historial en la parte inferior
   - Identifica la estrategia con mejor Sharpe Ratio
   - Considera el balance entre retorno y drawdown

3. **Optimizar**
   - Usa la estrategia ganadora
   - Prueba diferentes símbolos
   - Ajusta el capital según riesgo

### Para Avanzados

1. **Análisis Profundo**
   - Examina la curva de capital buscando patrones
   - Revisa el historial de operaciones
   - Identifica operaciones ganadoras vs perdedoras

2. **Diversificación**
   - Prueba la misma estrategia en múltiples activos
   - Combina criptos y acciones
   - Busca correlaciones

3. **Gestión de Riesgo**
   - Ajusta capital según volatilidad del activo
   - Considera drawdowns históricos
   - Planifica diversificación de cartera

---

## 📱 Características de la Interfaz

### ✨ Diseño Responsivo
- ✅ Funciona en desktop, tablet y móvil
- ✅ Panel sticky en pantallas grandes
- ✅ Layout adaptativo

### 🎨 Animaciones
- ✅ Transiciones suaves
- ✅ Hover effects en tarjetas
- ✅ Loading spinner durante ejecución

### 📊 Gráficos Interactivos
- ✅ Zoom y pan
- ✅ Tooltips informativos
- ✅ Gradientes visuales

### 🎯 UX Optimizada
- ✅ Feedback visual inmediato
- ✅ Mensajes de error claros
- ✅ Estados de carga visibles

---

## 🐛 Solución de Problemas

### La UI no carga

```bash
# Verifica que el frontend esté corriendo
cd /home/gonza/Develop/algodetraiding/web/frontend
npm run dev

# Debería mostrar: VITE ready at http://localhost:3000
```

### Error: "No se pudieron cargar las estrategias"

```bash
# Verifica que el backend esté corriendo
curl http://localhost:8000/api/strategies

# Debería retornar JSON con las estrategias
```

### Error: "Error al ejecutar el backtest"

**Causas comunes:**
1. El símbolo no tiene datos disponibles
2. El período es muy corto (<30 días)
3. Problema de red con exchanges

**Solución:**
```bash
# Prueba con datos sintéticos primero
# Cambia use_real_data a false en el código
```

### Base de datos no conecta

```bash
# Verifica que Docker esté corriendo
sudo docker ps

# Debería mostrar contenedores postgres y redis

# Si no están corriendo:
sudo docker-compose up -d postgres redis
```

---

## 🎓 Ejemplos de Uso

### Ejemplo 1: Primer Backtest

```
1. Selecciona "MA Crossover"
2. Símbolo: BTC/USDT
3. Período: 180 días
4. Capital: $10,000
5. Click "🚀 Ejecutar Backtest"
6. Espera 5-10 segundos
7. Observa los resultados
```

**Interpretación:**
- Si Retorno > 0% → La estrategia ganó dinero
- Si Sharpe > 1.0 → Buena relación riesgo/recompensa
- Si Drawdown < 15% → Riesgo controlado

### Ejemplo 2: Comparar Estrategias

```
# Ejecuta secuencialmente:
1. MA Crossover + BTC/USDT + 180 días → Anota retorno
2. RSI + BTC/USDT + 180 días → Anota retorno
3. Bollinger Bands + BTC/USDT + 180 días → Anota retorno

# Compara en el historial (parte inferior)
# Identifica la mejor estrategia para BTC
```

### Ejemplo 3: Probar Múltiples Activos

```
# Con la mejor estrategia:
1. Prueba BTC/USDT
2. Prueba ETH/USDT
3. Prueba AAPL
4. Prueba MSFT

# Identifica en qué activos funciona mejor tu estrategia
```

---

## 📖 Documentación Adicional

### API Endpoints

```bash
# Listar estrategias disponibles
GET http://localhost:8000/api/strategies

# Ejecutar backtest
POST http://localhost:8000/api/backtest
{
  "strategy_type": "bollinger_bands",
  "symbol": "BTC/USDT",
  "days": 180,
  "initial_capital": 10000
}

# Ver historial
GET http://localhost:8000/api/backtests?limit=10

# Ver detalles de un backtest
GET http://localhost:8000/api/backtests/{id}
```

### Estructura de Respuesta

```json
{
  "success": true,
  "backtest_id": 123,
  "results": {
    "strategy_name": "Bollinger Bands",
    "strategy_type": "bollinger_bands",
    "symbol": "BTC/USDT",
    "initial_capital": 10000,
    "final_capital": 11550,
    "total_return": 15.5,
    "sharpe_ratio": 1.25,
    "max_drawdown": -8.3,
    "total_trades": 12,
    "win_rate": 75.0,
    "equity_curve": [...],
    "trades": [...]
  }
}
```

---

## 🎯 Próximos Pasos

Una vez que domines la UI:

1. **Explora el código** en `/web/frontend/src/components/StrategyRunner.jsx`
2. **Personaliza estrategias** en `/strategies/`
3. **Añade nuevos símbolos** editando el array `symbols`
4. **Crea estrategias personalizadas** siguiendo el patrón de las existentes
5. **Integra con brokers reales** (¡con precaución!)

---

## ⚠️ Advertencias Importantes

### 🚨 NUNCA operar con dinero real sin:
- ✅ Entender completamente la estrategia
- ✅ Probar exhaustivamente en backtest
- ✅ Practicar en cuenta demo
- ✅ Gestionar el riesgo apropiadamente
- ✅ Tener un plan de salida

### 📊 Limitaciones del Backtesting:
- ❌ Resultados pasados no garantizan resultados futuros
- ❌ No considera slippage ni latencia real
- ❌ Puede sufrir de overfitting
- ❌ Condiciones de mercado cambian constantemente

### 💡 Mejores Prácticas:
- ✅ Prueba con múltiples períodos (in-sample y out-of-sample)
- ✅ Compara múltiples estrategias
- ✅ Considera comisiones y costos
- ✅ Mantén expectativas realistas
- ✅ Diversifica siempre

---

## 🤝 Soporte y Contribuciones

¿Encontraste un bug? ¿Tienes una idea? 
- Revisa los archivos en `/web/frontend/src/`
- Consulta la documentación en `/EMPEZAR_AQUI.md`
- Experimenta y aprende!

---

## 📝 Changelog

### v1.0.0 (2025-12-23)
- ✅ Interfaz gráfica completa
- ✅ 6 estrategias disponibles
- ✅ Gráficos interactivos con Recharts
- ✅ Historial de backtests
- ✅ Diseño responsivo
- ✅ Integración con API FastAPI

---

**¡Feliz Trading! 📈🚀**

*Recuerda: El mejor trader no es el que más gana, sino el que mejor gestiona el riesgo.*
