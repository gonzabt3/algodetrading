# 📊 Guía de Datos Históricos

## ✅ ¿Qué tienes ahora?

Los datos se descargaron exitosamente en **archivos CSV**:

```
data/
├── crypto/          ← 5 criptomonedas (2 años)
│   ├── binance_BTC_USDT_1d.csv
│   ├── binance_ETH_USDT_1d.csv
│   ├── binance_BNB_USDT_1d.csv
│   ├── binance_SOL_USDT_1d.csv
│   └── binance_ADA_USDT_1d.csv
├── stocks/          ← 10 acciones tech (10 años) 
└── indices/         ← 3 índices (10 años)
```

## 🤔 ¿Guardar en PostgreSQL?

### **Opción A: Solo CSV** (Actual) ⭐ RECOMENDADO PARA EMPEZAR

**Ventajas:**
- ✅ Simple y directo
- ✅ No llena la base de datos
- ✅ Fácil de respaldar/compartir
- ✅ Ya funciona con tus backtests

**Cómo usar:**
```python
# En el dashboard o CLI, marca:
use_real_data = True

# O desde CLI:
python main.py
# Selecciona: "Use real market data" → YES
```

### **Opción B: CSV + PostgreSQL** 🚀 PARA PRODUCCIÓN

**Ventajas:**
- ✅ Queries SQL más rápidas
- ✅ Búsquedas por fecha/símbolo eficientes
- ✅ Cache automático
- ✅ Ideal para muchos backtests repetidos

**Desventajas:**
- ⚠️ Usa más espacio en DB (~200MB para todos los datos)
- ⚠️ Requiere mantener sincronización CSV ↔ DB

**Cómo importar a PostgreSQL:**

```bash
# Importar TODOS los CSV a la base de datos
python utils/import_csv_to_db.py

# O importar un archivo específico
python utils/import_csv_to_db.py --file data/crypto/binance_BTC_USDT_1d.csv --symbol BTC/USDT --type crypto
```

## 📋 Comandos Útiles

### Descargar datos nuevos
```bash
# Todas las fuentes (crypto + stocks + indices)
python utils/download_all_data.py

# Solo criptomonedas
python utils/download_market_data.py

# Solo acciones e índices
python utils/download_yahoo_data.py
```

### Importar a PostgreSQL (opcional)
```bash
# Importar todo
python utils/import_csv_to_db.py

# Ver estadísticas de la DB
python -c "from api.database import SessionLocal; from api.models import MarketData; db = SessionLocal(); print(f'Registros en DB: {db.query(MarketData).count():,}'); db.close()"
```

### Actualizar datos
```bash
# Re-descargar (sobrescribe CSV existentes)
python utils/download_all_data.py

# Re-importar a DB (omite duplicados)
python utils/import_csv_to_db.py
```

## 🎯 Mi Recomendación

**Para ti ahora:** Usa **Opción A (solo CSV)**

¿Por qué?
1. Ya tienes los datos descargados ✅
2. Funciona perfectamente con backtests
3. Más simple de mantener
4. Puedes migrar a PostgreSQL después si necesitas

**Cuándo usar PostgreSQL:**
- Cuando ejecutes 100+ backtests por día
- Si necesitas queries complejas (ej: "dame todas las acciones que subieron >5% en 2023")
- Para dashboard con gráficos en tiempo real
- Si múltiples usuarios hacen backtests simultáneos

## 📖 Uso en Backtests

### Dashboard (http://localhost:3000)
1. Selecciona estrategia
2. Elige símbolo: `BTC/USDT` o `AAPL`
3. **Marca "Use Real Market Data"** ✅
4. Run Backtest

### CLI
```bash
python main.py
# Opciones:
# - Symbol: BTC/USDT (debe coincidir con archivo CSV)
# - Use real data: YES
```

### Programático
```python
from backtesting.backtester import Backtester
from strategies.ma_crossover import MovingAverageCrossover

backtester = Backtester(
    strategy_class=MovingAverageCrossover,
    symbol='BTC/USDT',
    use_real_data=True,  # ← Usa CSV
    days=365
)
results = backtester.run()
```

## 🗂️ Estructura de CSV

Todos los archivos tienen el formato estándar:

```csv
timestamp,open,high,low,close,volume
2023-01-01 00:00:00,16500.0,16600.0,16450.0,16550.0,1234567.0
2023-01-02 00:00:00,16550.0,16700.0,16500.0,16680.0,2345678.0
...
```

Compatible con pandas, backtrader, y cualquier librería de backtesting.

## ❓ FAQ

**Q: ¿Los datos se actualizan automáticamente?**
A: No. Ejecuta `python utils/download_all_data.py` cuando quieras actualizar.

**Q: ¿Puedo agregar más símbolos?**
A: Sí! Edita `utils/download_market_data.py` o `utils/download_yahoo_data.py` y agrega a la lista.

**Q: ¿Los datos son gratis?**
A: Sí, CCXT (Binance) y Yahoo Finance son 100% gratuitos.

**Q: ¿Qué timeframes soporta?**
A: Actual: 1d (diario). Puedes cambiar a '1h', '4h', etc. en los scripts.

**Q: ¿Necesito API keys?**
A: No para CCXT/Binance ni Yahoo Finance. Solo si usas Alpha Vantage.
