"""
Demostración Visual de Diferencias entre Estrategias
Ejecuta esto para ver cómo cada estrategia toma decisiones diferentes
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.multi_indicator import MultiIndicatorStrategy


def create_scenario_data():
    """Crea datos con escenarios específicos"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    # Escenario: Precio lateral con picos
    base = 100
    lateral = np.ones(50) * base
    spike_up = np.linspace(100, 120, 25)  # Pico hacia arriba
    spike_down = np.linspace(120, 95, 25)  # Caída
    
    prices = np.concatenate([lateral, spike_up, spike_down])
    prices += np.random.randn(100) * 2  # Ruido
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices + 2,
        'low': prices - 2,
        'close': prices,
        'volume': np.random.randint(1000, 3000, 100)
    }, index=dates)
    
    return data


def compare_decisions():
    """Compara cómo cada estrategia decide en los mismos momentos"""
    
    print("=" * 80)
    print("COMPARACIÓN DE DECISIONES - ESTRATEGIAS")
    print("=" * 80)
    print("\nGenerando escenario de mercado...")
    print("Situación: Precio lateral ($100) con pico a $120 y caída a $95\n")
    
    data = create_scenario_data()
    
    # Crear estrategias
    bollinger = BollingerBandsStrategy()
    mean_rev = MeanReversionStrategy()
    multi = MultiIndicatorStrategy()
    
    # Calcular indicadores y señales para cada una
    data_bb = bollinger.generate_signals(bollinger.calculate_indicators(data.copy()))
    data_mr = mean_rev.generate_signals(mean_rev.calculate_indicators(data.copy()))
    data_mi = multi.generate_signals(multi.calculate_indicators(data.copy()))
    
    # Momentos clave para analizar
    key_moments = [
        (60, "Inicio del pico alcista"),
        (75, "Precio en $120 (máximo)"),
        (90, "Precio cayendo a $95 (mínimo)")
    ]
    
    print("-" * 80)
    print("ANÁLISIS DE MOMENTOS CLAVE")
    print("-" * 80)
    
    for idx, description in key_moments:
        if idx >= len(data):
            continue
            
        print(f"\n📅 DÍA {idx}: {description}")
        print(f"   Precio: ${data.iloc[idx]['close']:.2f}")
        print()
        
        # Bollinger Bands
        bb_signal = data_bb.iloc[idx]['signal']
        bb_action = "COMPRAR" if bb_signal == 1 else ("VENDER" if bb_signal == -1 else "ESPERAR")
        print(f"   🔵 Bollinger Bands: {bb_action}")
        if hasattr(data_bb.iloc[idx], 'bb_upper'):
            print(f"      Banda Superior: ${data_bb.iloc[idx]['bb_upper']:.2f}")
            print(f"      Banda Inferior: ${data_bb.iloc[idx]['bb_lower']:.2f}")
        
        # Mean Reversion
        mr_signal = data_mr.iloc[idx]['signal']
        mr_action = "COMPRAR" if mr_signal == 1 else ("VENDER" if mr_signal == -1 else "ESPERAR")
        print(f"   🟢 Mean Reversion: {mr_action}")
        if 'z_score' in data_mr.columns:
            print(f"      Z-Score: {data_mr.iloc[idx]['z_score']:.2f}")
        
        # Multi-Indicator
        mi_signal = data_mi.iloc[idx]['signal']
        mi_action = "COMPRAR" if mi_signal == 1 else ("VENDER" if mi_signal == -1 else "ESPERAR")
        print(f"   🔴 Multi-Indicator: {mi_action}")
        if 'rsi' in data_mi.columns:
            print(f"      RSI: {data_mi.iloc[idx]['rsi']:.2f}")
        
        print()
    
    # Contar operaciones de cada estrategia
    print("-" * 80)
    print("ESTADÍSTICAS GENERALES")
    print("-" * 80)
    print()
    
    bb_trades = len(data_bb[data_bb['signal'] != 0])
    mr_trades = len(data_mr[data_mr['signal'] != 0])
    mi_trades = len(data_mi[data_mi['signal'] != 0])
    
    print(f"📊 Número de señales generadas:")
    print(f"   Bollinger Bands:   {bb_trades} señales")
    print(f"   Mean Reversion:    {mr_trades} señales")
    print(f"   Multi-Indicator:   {mi_trades} señales")
    print()
    
    print("💡 INTERPRETACIÓN:")
    print()
    print("   MÁS señales = Más operaciones (más comisiones, más activo)")
    print("   MENOS señales = Más selectivo (menos comisiones, más conservador)")
    print()
    
    print("🎯 RECOMENDACIONES POR PERFIL:")
    print()
    print("   Trader ACTIVO (diario):")
    print(f"      → Bollinger Bands ({bb_trades} operaciones)")
    print()
    print("   Trader CONSERVADOR (semanal):")
    print(f"      → Multi-Indicator ({mi_trades} operaciones)")
    print()
    print("   Trader MEDIO (swing):")
    print(f"      → Mean Reversion ({mr_trades} operaciones)")
    print()


if __name__ == '__main__':
    compare_decisions()
