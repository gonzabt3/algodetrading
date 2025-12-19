# Algorithmic Trading System

Un sistema completo de trading algorítmico en Python para desarrollar, probar y ejecutar estrategias de trading.

## 🚀 Características

- **Múltiples Estrategias**: Incluye estrategias de ejemplo como Moving Average Crossover, RSI y MACD
- **Motor de Backtesting**: Framework robusto para probar estrategias con datos históricos
- **Gestión de Riesgo**: Herramientas para controlar el riesgo y el tamaño de las posiciones
- **Integración con Exchanges**: Soporte para exchanges de criptomonedas mediante CCXT
- **Visualización**: Gráficos detallados de resultados y métricas de rendimiento
- **Extensible**: Arquitectura modular para agregar nuevas estrategias fácilmente

## 📋 Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## 🔧 Instalación

1. Clona el repositorio o descarga el proyecto

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

## 📁 Estructura del Proyecto

```
algodetrading/
├── strategies/          # Implementaciones de estrategias de trading
│   ├── base_strategy.py      # Clase base para todas las estrategias
│   ├── ma_crossover.py       # Estrategia de cruce de medias móviles
│   ├── rsi_strategy.py       # Estrategia basada en RSI
│   └── macd_strategy.py      # Estrategia basada en MACD
├── backtesting/         # Motor de backtesting
│   └── backtester.py         # Clase principal de backtesting
├── utils/               # Utilidades
│   ├── data_fetcher.py       # Obtención de datos de mercado
│   ├── risk_manager.py       # Gestión de riesgo
│   └── visualizer.py         # Visualización de resultados
├── config/              # Archivos de configuración
│   ├── settings.py           # Configuración general
│   └── strategies.json       # Parámetros de estrategias
├── data/                # Almacenamiento de datos históricos
├── logs/                # Logs de la aplicación
├── tests/               # Tests unitarios
└── main.py              # Punto de entrada principal
```

## 🎯 Uso Rápido

### Ejecutar un Backtest Básico

```bash
# Estrategia de Moving Average Crossover
python main.py --strategy ma_crossover --symbol BTC/USDT --days 365

# Estrategia RSI
python main.py --strategy rsi --symbol BTC/USDT --days 180

# Estrategia MACD
python main.py --strategy macd --symbol ETH/USDT --days 365
```

### Opciones de Línea de Comandos

```bash
python main.py [opciones]

Opciones:
  --strategy {ma_crossover,rsi,macd}  Estrategia a utilizar
  --symbol SYMBOL                     Par de trading (ej: BTC/USDT)
  --timeframe TIMEFRAME               Marco temporal (1m, 5m, 1h, 1d)
  --days DAYS                         Días de datos históricos
  --capital CAPITAL                   Capital inicial
  --plot                              Mostrar gráficos de resultados
```

### Ejemplo con Visualización

```bash
python main.py --strategy ma_crossover --symbol BTC/USDT --days 365 --capital 10000 --plot
```

## 📊 Estrategias Incluidas

### 1. Moving Average Crossover
Genera señales de compra cuando la media móvil rápida cruza por encima de la lenta, y señales de venta cuando cruza por debajo.

**Parámetros:**
- `fast_period`: Período de la MA rápida (default: 20)
- `slow_period`: Período de la MA lenta (default: 50)

### 2. RSI Strategy
Basada en el Índice de Fuerza Relativa. Compra cuando el RSI está en sobreventa y vende cuando está en sobrecompra.

**Parámetros:**
- `period`: Período del RSI (default: 14)
- `oversold`: Nivel de sobreventa (default: 30)
- `overbought`: Nivel de sobrecompra (default: 70)

### 3. MACD Strategy
Utiliza el indicador MACD para generar señales cuando la línea MACD cruza la línea de señal.

**Parámetros:**
- `fast`: Período EMA rápido (default: 12)
- `slow`: Período EMA lento (default: 26)
- `signal`: Período de la línea de señal (default: 9)

## 🔨 Crear una Estrategia Personalizada

```python
from strategies.base_strategy import BaseStrategy
import pandas as pd

class MiEstrategia(BaseStrategy):
    def __init__(self, params=None):
        super().__init__(name="Mi Estrategia", params=params)
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        # Calcula tus indicadores aquí
        data['mi_indicador'] = data['close'].rolling(20).mean()
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        # Genera señales de trading
        data['signal'] = 0
        # 1 = compra, -1 = venta, 0 = mantener
        data.loc[condicion_compra, 'signal'] = 1
        data.loc[condicion_venta, 'signal'] = -1
        return data
```

## 📈 Métricas de Rendimiento

El sistema calcula automáticamente:

- **Retorno Total**: Ganancia/pérdida porcentual total
- **Ratio de Sharpe**: Retorno ajustado por riesgo
- **Drawdown Máximo**: Mayor caída desde un pico
- **Tasa de Acierto**: Porcentaje de operaciones ganadoras
- **Número de Operaciones**: Total de operaciones ejecutadas
- **Curva de Equity**: Evolución del capital en el tiempo

## ⚠️ Configuración de API

Para usar exchanges reales, configura tus claves API en `config/settings.py`:

```python
API_KEY = "tu_clave_api"
API_SECRET = "tu_secreto_api"
```

**⚠️ IMPORTANTE**: 
- Nunca compartas tus claves API
- Usa el archivo `.gitignore` para evitar subir credenciales
- Para trading real, comienza con pequeñas cantidades

## 🧪 Testing

```bash
# Ejecutar tests
pytest tests/

# Ejecutar tests con cobertura
pytest --cov=. tests/
```

## 📝 Gestión de Riesgo

El sistema incluye herramientas de gestión de riesgo:

- **Tamaño de Posición**: Control del tamaño máximo de posición
- **Stop Loss**: Cálculo automático de stop loss
- **Take Profit**: Cálculo basado en ratio riesgo-beneficio
- **Kelly Criterion**: Optimización del tamaño de posición
- **Control de Drawdown**: Detención automática si se excede el drawdown máximo

## 📚 Recursos Adicionales

- [Documentación de CCXT](https://docs.ccxt.com/)
- [Documentación de Pandas](https://pandas.pydata.org/docs/)
- [Análisis Técnico](https://www.investopedia.com/technical-analysis-4689657)

## ⚖️ Disclaimer

Este software es solo para fines educativos y de investigación. El trading conlleva riesgos significativos de pérdida. Los desarrolladores no se hacen responsables de pérdidas financieras derivadas del uso de este software.

**⚠️ Trading de Criptomonedas**: Altamente volátil. Solo invierte lo que puedas permitirte perder.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/nueva-estrategia`)
3. Commit tus cambios (`git commit -am 'Agrega nueva estrategia'`)
4. Push a la rama (`git push origin feature/nueva-estrategia`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## 💬 Soporte

Para preguntas, sugerencias o reportar bugs, por favor abre un issue en el repositorio.

---

**¡Feliz Trading! 📈🚀**
