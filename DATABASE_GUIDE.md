# 🗄️ Guía: ¿Cuándo Necesitas una Base de Datos?

## 📌 RESPUESTA RÁPIDA

**AHORA: NO necesitas una base de datos**

Tu proyecto actual usa:
- ✅ Archivos JSON para resultados
- ✅ Archivos CSV para datos históricos
- ✅ Diccionarios Python en memoria

**Esto es SUFICIENTE para:**
- Aprender trading algorítmico
- Hacer backtests ocasionales
- Probar estrategias
- Primeros 6-12 meses de desarrollo

---

## 🚦 SEMÁFORO: ¿Necesito una DB?

### 🟢 VERDE - NO NECESITAS DB (TÚ ESTÁS AQUÍ)

```
Situación:
- Estás aprendiendo
- Haces 1-10 backtests por día
- Datos de 1-5 activos
- Históricos de 1-2 años
- Dataset < 100 MB
- 1 persona en el proyecto

Solución actual:
✅ Archivos JSON (utils/results_logger.py)
✅ Archivos CSV para precios
✅ Carpeta data/ con todo organizado

Tiempo estimado: 6-12 meses
```

### 🟡 AMARILLO - CONSIDERA SQLite

```
Situación:
- Haces 50-100 backtests por día
- Optimización de parámetros (probar 100+ combinaciones)
- Datos de 10-20 activos
- Históricos de 5+ años
- Dataset 100 MB - 1 GB
- Quieres queries más complejas

Solución:
→ SQLite (base de datos en 1 archivo)
  - No requiere servidor
  - Fácil de migrar desde JSON/CSV
  - Integración con pandas
  - Suficiente para millones de registros

Implementación: 1-2 días
```

### 🔴 ROJO - NECESITAS DB REAL

```
Situación:
- Haces 1000+ backtests por día
- Trading en vivo 24/7
- Datos de 100+ activos
- Tick-by-tick data (millones de registros)
- Dataset > 1 GB
- Equipo de 2+ personas
- Necesitas dashboards en tiempo real

Solución:
→ PostgreSQL + TimescaleDB
  - Optimizada para series de tiempo
  - Soporta consultas complejas
  - Replicación y respaldos
  - Múltiples usuarios concurrentes

Implementación: 1-2 semanas
```

---

## 📊 COMPARACIÓN TÉCNICA

| Característica | JSON/CSV | SQLite | PostgreSQL |
|---|---|---|---|
| **Configuración** | ✅ Cero | ⚠️ Mínima | ❌ Compleja |
| **Velocidad (pequeño)** | ✅ Rápido | ✅ Rápido | ⚠️ Medio |
| **Velocidad (grande)** | ❌ Lento | ✅ Rápido | ✅ Muy rápido |
| **Queries complejas** | ❌ Manual | ✅ SQL | ✅ SQL avanzado |
| **Múltiples usuarios** | ❌ No | ⚠️ Limitado | ✅ Sí |
| **Respaldos** | ⚠️ Manual | ⚠️ Copiar archivo | ✅ Automático |
| **Tamaño máximo** | ~100 MB | ~1 GB | Ilimitado |
| **Debuggear** | ✅ Muy fácil | ⚠️ Medio | ⚠️ Medio |
| **Portable** | ✅ Copiar/pegar | ✅ 1 archivo | ❌ Complejo |

---

## 💡 TU SISTEMA ACTUAL (JSON/CSV)

### ✅ VENTAJAS

```python
# 1. SIMPLE DE ENTENDER
with open('results.json') as f:
    data = json.load(f)  # ¡Eso es todo!

# 2. FÁCIL DE DEBUGGEAR
# Abre el JSON con cualquier editor de texto
# No necesitas herramientas especiales

# 3. PORTABLE
# Copia la carpeta data/ y listo
# No necesitas exportar/importar

# 4. INTEGRACIÓN CON PANDAS
df = pd.read_csv('data/BTC_USDT.csv')  # Directo a DataFrame

# 5. VERSIONABLE CON GIT
# Los archivos JSON/CSV se pueden commitear
# (bases de datos NO se pueden versionar)
```

### ❌ LIMITACIONES

```python
# 1. QUERIES COMPLEJAS SON MANUALES
# SQL:     SELECT * FROM trades WHERE return > 10 AND strategy = 'RSI'
# Python:  df[(df['return'] > 10) & (df['strategy'] == 'RSI')]
#          ↑ Más código, menos legible

# 2. PERFORMANCE CON DATASETS GRANDES
# 10 MB:    ✅ Rápido
# 100 MB:   ⚠️ Empieza a ralentizarse
# 1 GB:     ❌ Muy lento

# 3. CONCURRENCIA
# Si 2 procesos escriben al mismo archivo → PROBLEMA
# (No es tu caso ahora, pero puede serlo después)

# 4. INTEGRIDAD DE DATOS
# No hay validación automática
# Puedes guardar datos inconsistentes sin darte cuenta
```

---

## 🔄 MIGRACIÓN FUTURA (Cuando la necesites)

### Paso 1: De JSON a SQLite (Fácil)

```python
import sqlite3
import json
import pandas as pd

# Crear base de datos
conn = sqlite3.connect('data/backtests.db')

# Cargar todos los JSON
for filename in os.listdir('data/backtest_results/'):
    with open(f'data/backtest_results/{filename}') as f:
        data = json.load(f)
    
    # Convertir a DataFrame
    df = pd.DataFrame([data])
    
    # Guardar en SQLite
    df.to_sql('backtests', conn, if_exists='append', index=False)

# ¡Listo! Ahora puedes hacer queries SQL
results = pd.read_sql("""
    SELECT strategy, symbol, AVG(total_return) as avg_return
    FROM backtests
    GROUP BY strategy, symbol
    ORDER BY avg_return DESC
""", conn)
```

### Paso 2: De SQLite a PostgreSQL (Medio)

```bash
# 1. Instalar PostgreSQL
sudo apt install postgresql

# 2. Exportar de SQLite
sqlite3 backtests.db .dump > backup.sql

# 3. Importar a PostgreSQL
psql -U postgres -d trading < backup.sql

# 4. Instalar TimescaleDB (para series de tiempo)
sudo apt install timescaledb-postgresql
```

---

## 🎯 RECOMENDACIÓN PARA TI

### AHORA (Semanas 1-8)

```
✅ USA: JSON/CSV (lo que ya tienes)
✅ SCRIPT: utils/results_logger.py
✅ COMANDO: python3 ver_resultados.py

NO HAGAS NADA MÁS
```

### FUTURO CERCANO (Mes 2-3)

```
SI empiezas a hacer optimización de parámetros:

1. Instala SQLite:
   pip install sqlalchemy

2. Modifica results_logger.py para guardar en SQLite
   (en vez de JSON)

3. Sigue usando pandas para leer
   df = pd.read_sql('SELECT * FROM backtests', conn)

Beneficio: Queries más rápidas, mismo workflow
Costo: 1 día de migración
```

### FUTURO MEDIO (Mes 4-6)

```
SI vas a trading en vivo o tienes datasets gigantes:

1. Monta PostgreSQL + TimescaleDB
2. Migra datos de SQLite a PostgreSQL
3. Configura respaldos automáticos
4. Considera herramientas como:
   - Grafana (dashboards)
   - pgAdmin (gestión de DB)
   - Airflow (automatización)

Beneficio: Sistema profesional escalable
Costo: 1-2 semanas de setup
```

---

## 📈 EJEMPLO PRÁCTICO: Optimización de Parámetros

### Con tu sistema actual (JSON):

```python
# Probar 100 combinaciones de parámetros
results = []

for fast in range(5, 30, 5):      # 5 valores
    for slow in range(20, 100, 10):  # 8 valores
        # 5 x 8 = 40 combinaciones
        strategy = MACrossover(fast, slow)
        backtester = Backtester(strategy, save_results=True)
        result = backtester.run(data)
        results.append(result)

# Ver resultados
python3 ver_resultados.py  # Muestra todos los 40 backtests
```

**Tiempo:** ~5 minutos para 40 backtests ✅

---

### Si tuvieras 10,000 combinaciones:

```python
# Con JSON/CSV: ❌ 20+ minutos, archivos desorganizados
# Con SQLite:   ✅ 5 minutos, queries instantáneas
# Con PostgreSQL: ✅ 2 minutos, dashboards en tiempo real
```

**Conclusión:** Para tu escala actual, JSON es PERFECTO

---

## 🛠️ HERRAMIENTAS ACTUALES

### Lo que tienes AHORA:

```bash
# 1. Guardar resultados automáticamente
python3 main.py --strategy ma_crossover --symbol BTC/USDT

# 2. Ver todos los resultados
python3 ver_resultados.py

# 3. Comparar estrategias
python3 compare_strategies.py

# 4. Explorar archivos
cat data/backtest_results/MA_Crossover_BTC_USDT_*.json | jq .
```

### Lo que tendrías con SQLite:

```bash
# 1. Queries complejas
sqlite3 backtests.db "SELECT * FROM backtests WHERE total_return > 20"

# 2. Agregaciones
sqlite3 backtests.db "SELECT strategy, AVG(total_return) FROM backtests GROUP BY strategy"

# 3. Todo lo demás IGUAL (pandas, scripts, workflow)
```

---

## ❓ FAQ

### **¿Cuánto ocupan mis datos ahora?**

```bash
du -sh data/
# Probablemente: < 10 MB

# Cuando llegues a 100+ MB, considera SQLite
# Cuando llegues a 1+ GB, considera PostgreSQL
```

### **¿Puedo mezclar JSON y SQL?**

```python
# ✅ SÍ - Puedes tener:
data/
  ├── market_data/        # CSV (precios históricos)
  ├── backtest_results/   # SQLite (resultados)
  └── configs/            # JSON (configuraciones)

# Cada formato para lo que mejor hace
```

### **¿Y si quiero aprender SQL?**

```python
# Perfecto! Empieza con SQLite:

# 1. Instala
pip install sqlalchemy

# 2. Practica con tus datos
conn = sqlite3.connect('practice.db')
df.to_sql('trades', conn)
results = pd.read_sql('SELECT * FROM trades WHERE ...', conn)

# 3. No afectes tu workflow actual
# (mantén el sistema JSON funcionando)
```

---

## 🎓 CONCLUSIÓN

```
┌─────────────────────────────────────────┐
│  PREGUNTA: ¿Debería usar una DB?        │
├─────────────────────────────────────────┤
│  RESPUESTA: NO (todavía)                │
│                                         │
│  TU SISTEMA JSON/CSV ES:                │
│  ✅ Suficiente para aprender            │
│  ✅ Simple de entender                  │
│  ✅ Fácil de debuggear                  │
│  ✅ Rápido para tu escala               │
│                                         │
│  MIGRA A DB CUANDO:                     │
│  • Hagas 100+ backtests/día             │
│  • Datasets > 100 MB                    │
│  • Necesites queries complejas          │
│  • Trading en vivo 24/7                 │
│                                         │
│  TIEMPO ESTIMADO: 6-12 meses            │
└─────────────────────────────────────────┘
```

---

## 📚 RECURSOS ADICIONALES

### Si decides migrar a SQLite:
- [SQLite con Python](https://docs.python.org/3/library/sqlite3.html)
- [Pandas + SQL](https://pandas.pydata.org/docs/reference/api/pandas.read_sql.html)

### Si decides usar PostgreSQL:
- [TimescaleDB para trading](https://docs.timescale.com/)
- [PostgreSQL Tutorial](https://www.postgresqltutorial.com/)

### Alternativas modernas:
- **DuckDB**: SQLite con esteroides para analytics
- **ClickHouse**: DB columnar para big data
- **Arctic** (de Man Group): Optimizada para trading

**PERO RECUERDA:** Todo esto es para DESPUÉS. Ahora, enfócate en aprender estrategias, no bases de datos.

---

**Última actualización:** Diciembre 2025
