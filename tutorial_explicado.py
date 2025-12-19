"""
TUTORIAL: Cómo funciona el Trading Algorítmico
Este archivo explica paso a paso todo el proceso
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("="*70)
print("TUTORIAL DE TRADING ALGORÍTMICO - PASO A PASO")
print("="*70)
print()

# ============================================================================
# PASO 1: ENTENDER LOS DATOS DEL MERCADO
# ============================================================================
print("📊 PASO 1: LOS DATOS DEL MERCADO (OHLCV)")
print("-" * 70)

# Crear datos de ejemplo (simplificados)
fechas = pd.date_range('2024-01-01', periods=10, freq='D')
precios = [100, 102, 98, 105, 110, 108, 112, 115, 113, 118]

datos = pd.DataFrame({
    'fecha': fechas,
    'precio': precios
})

print("\nEjemplo de precios de Bitcoin (simulado):")
print(datos.to_string(index=False))
print()
print("Cada día tiene un precio. En realidad también tendríamos:")
print("  - Precio de apertura (open)")
print("  - Precio máximo (high)")
print("  - Precio mínimo (low)")
print("  - Precio de cierre (close)")
print("  - Volumen negociado")
print()

# ============================================================================
# PASO 2: CALCULAR INDICADORES
# ============================================================================
print("\n" + "="*70)
print("📈 PASO 2: CALCULAR INDICADORES TÉCNICOS")
print("-" * 70)

# Calcular Media Móvil Simple de 3 días (normalmente se usan 20, 50, etc.)
datos['MA_3'] = datos['precio'].rolling(window=3).mean()

print("\nMedia Móvil de 3 días (promedio de últimos 3 precios):")
print(datos[['fecha', 'precio', 'MA_3']].to_string(index=False))
print()
print("Observa cómo la MA_3 es el promedio de los últimos 3 días:")
print("  Día 3: (100 + 102 + 98) / 3 = 100.0")
print("  Día 4: (102 + 98 + 105) / 3 = 101.67")
print("  Y así sucesivamente...")
print()

# ============================================================================
# PASO 3: GENERAR SEÑALES DE TRADING
# ============================================================================
print("\n" + "="*70)
print("🎯 PASO 3: GENERAR SEÑALES DE COMPRA/VENTA")
print("-" * 70)

# Estrategia simple: Comprar cuando precio > MA, vender cuando precio < MA
datos['señal'] = 0  # 0 = no hacer nada

for i in range(1, len(datos)):
    precio_actual = datos.loc[i, 'precio']
    ma_actual = datos.loc[i, 'MA_3']
    precio_anterior = datos.loc[i-1, 'precio']
    ma_anterior = datos.loc[i-1, 'MA_3']
    
    # Si el precio cruza ARRIBA de la MA → COMPRAR
    if precio_anterior <= ma_anterior and precio_actual > ma_actual:
        datos.loc[i, 'señal'] = 1  # Comprar
        datos.loc[i, 'acción'] = 'COMPRAR 💰'
    
    # Si el precio cruza ABAJO de la MA → VENDER
    elif precio_anterior >= ma_anterior and precio_actual < ma_actual:
        datos.loc[i, 'señal'] = -1  # Vender
        datos.loc[i, 'acción'] = 'VENDER 💸'
    else:
        datos.loc[i, 'acción'] = 'ESPERAR ⏳'

print("\nSeñales generadas por la estrategia:")
print(datos[['fecha', 'precio', 'MA_3', 'acción']].to_string(index=False))
print()

# ============================================================================
# PASO 4: SIMULAR TRADING (BACKTESTING)
# ============================================================================
print("\n" + "="*70)
print("💰 PASO 4: SIMULAR OPERACIONES (BACKTESTING)")
print("-" * 70)

capital_inicial = 1000
capital = capital_inicial
acciones = 0
operaciones = []

print(f"\nCapital inicial: ${capital_inicial}")
print("\nSimulando operaciones día por día:")
print("-" * 70)

for i in range(len(datos)):
    precio = datos.loc[i, 'precio']
    señal = datos.loc[i, 'señal']
    fecha = datos.loc[i, 'fecha'].strftime('%Y-%m-%d')
    
    if señal == 1 and acciones == 0:  # COMPRAR
        acciones = capital / precio
        print(f"{fecha} | COMPRAR  | Precio: ${precio:6.2f} | Compro {acciones:.2f} acciones")
        print(f"          | Gasto todo mi capital: ${capital:.2f}")
        capital = 0
        operaciones.append({
            'tipo': 'COMPRA',
            'fecha': fecha,
            'precio': precio,
            'acciones': acciones
        })
    
    elif señal == -1 and acciones > 0:  # VENDER
        capital = acciones * precio
        ganancia = capital - capital_inicial
        print(f"{fecha} | VENDER   | Precio: ${precio:6.2f} | Vendo {acciones:.2f} acciones")
        print(f"          | Recibo: ${capital:.2f} | Ganancia: ${ganancia:.2f} ({ganancia/capital_inicial*100:.1f}%)")
        operaciones.append({
            'tipo': 'VENTA',
            'fecha': fecha,
            'precio': precio,
            'acciones': acciones,
            'capital': capital
        })
        acciones = 0

print()

# ============================================================================
# PASO 5: CALCULAR RESULTADOS
# ============================================================================
print("\n" + "="*70)
print("📊 PASO 5: RESULTADOS FINALES")
print("-" * 70)

# Si todavía tengo acciones, las vendo al último precio
if acciones > 0:
    capital = acciones * datos.loc[len(datos)-1, 'precio']

capital_final = capital
ganancia_total = capital_final - capital_inicial
rendimiento = (ganancia_total / capital_inicial) * 100

print(f"\nCapital inicial:  ${capital_inicial:.2f}")
print(f"Capital final:    ${capital_final:.2f}")
print(f"Ganancia/Pérdida: ${ganancia_total:.2f}")
print(f"Rendimiento:      {rendimiento:.2f}%")
print()

# ============================================================================
# RESUMEN DE CONCEPTOS
# ============================================================================
print("\n" + "="*70)
print("📚 RESUMEN DE CONCEPTOS CLAVE")
print("="*70)
print("""
1. DATOS DEL MERCADO (OHLCV):
   - Son los precios históricos que usamos para decidir
   - Open, High, Low, Close, Volume de cada período

2. INDICADORES TÉCNICOS:
   - Medias Móviles (MA): Promedios que suavizan el ruido
   - RSI: Mide si está sobrecomprado/sobrevendido
   - MACD: Compara tendencias de diferentes períodos

3. ESTRATEGIA:
   - Conjunto de REGLAS que dicen cuándo comprar/vender
   - Ejemplo: "Compra cuando MA rápida > MA lenta"

4. SEÑALES:
   - 1 = COMPRAR
   - -1 = VENDER  
   - 0 = ESPERAR

5. BACKTESTING:
   - Probar la estrategia con datos históricos
   - Ver si hubiera funcionado en el pasado
   - NO GARANTIZA éxito futuro, pero da confianza

6. MÉTRICAS DE RENDIMIENTO:
   - Total Return: % de ganancia/pérdida
   - Sharpe Ratio: Ganancia ajustada por riesgo
   - Max Drawdown: Peor caída desde un pico
   - Win Rate: % de operaciones ganadoras

7. GESTIÓN DE RIESGO:
   - NUNCA invertir todo el capital en una sola operación
   - Usar stop-loss (límite de pérdida)
   - Diversificar

⚠️  ADVERTENCIA IMPORTANTE:
   El trading tiene riesgos. Los resultados pasados NO garantizan
   resultados futuros. Solo invierte dinero que puedas perder.
""")

print("="*70)
print("FIN DEL TUTORIAL")
print("="*70)
print("\nAhora ejecuta 'python3 example.py' para ver un ejemplo real!")
print()
