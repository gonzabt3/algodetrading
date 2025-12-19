"""
Comparador de Estrategias
Ejecuta todas las estrategias y compara resultados
"""
import pandas as pd
from datetime import datetime, timedelta

from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.multi_indicator import MultiIndicatorStrategy
from backtesting.backtester import Backtester
from utils.data_fetcher import DataFetcher


def generate_sample_data(days=365):
    """Genera datos de muestra para testing"""
    import numpy as np
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    base_price = 100
    trend = np.linspace(0, 50, days)
    noise = np.random.randn(days) * 5
    close = base_price + trend + noise
    
    data = pd.DataFrame({
        'open': close + np.random.randn(days) * 2,
        'high': close + abs(np.random.randn(days) * 3),
        'low': close - abs(np.random.randn(days) * 3),
        'close': close,
        'volume': np.random.randint(1000, 10000, days)
    }, index=dates)
    
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    return data


def compare_strategies():
    """Compara todas las estrategias disponibles"""
    
    print("=" * 80)
    print("COMPARACIÓN DE ESTRATEGIAS DE TRADING")
    print("=" * 80)
    print()
    
    # Generar datos
    print("Generando datos de mercado...")
    data = generate_sample_data(days=365)
    print(f"✓ {len(data)} días de datos generados\n")
    
    # Definir estrategias a comparar
    strategies = [
        MovingAverageCrossover(params={'fast_period': 20, 'slow_period': 50}),
        RSIStrategy(params={'period': 14, 'oversold': 30, 'overbought': 70}),
        MACDStrategy(params={'fast': 12, 'slow': 26, 'signal': 9}),
        BollingerBandsStrategy(params={'period': 20, 'std_dev': 2.0}),
        MeanReversionStrategy(params={'lookback_period': 20, 'entry_threshold': 2.0}),
        MultiIndicatorStrategy(params={})
    ]
    
    # Ejecutar backtests
    results = []
    
    print("Ejecutando backtests...")
    print("-" * 80)
    
    for strategy in strategies:
        print(f"\n📊 Testing: {strategy.name}...")
        
        backtester = Backtester(
            strategy=strategy,
            initial_capital=10000.0,
            commission=0.001
        )
        
        try:
            result = backtester.run(data.copy())
            results.append({
                'Estrategia': strategy.name,
                'Retorno (%)': result['total_return'],
                'Capital Final': result['final_capital'],
                'Sharpe Ratio': result['sharpe_ratio'],
                'Max Drawdown (%)': result['max_drawdown'],
                'Total Trades': result['total_trades'],
                'Win Rate (%)': result['win_rate']
            })
            print(f"   ✓ Completado: {result['total_return']:.2f}% retorno")
        
        except Exception as e:
            print(f"   ✗ Error: {e}")
            results.append({
                'Estrategia': strategy.name,
                'Retorno (%)': 0,
                'Capital Final': 10000,
                'Sharpe Ratio': 0,
                'Max Drawdown (%)': 0,
                'Total Trades': 0,
                'Win Rate (%)': 0
            })
    
    # Crear tabla de resultados
    print("\n" + "=" * 80)
    print("RESULTADOS COMPARATIVOS")
    print("=" * 80)
    print()
    
    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values('Retorno (%)', ascending=False)
    
    # Formatear tabla
    print(df_results.to_string(index=False))
    print()
    
    # Análisis y recomendaciones
    print("=" * 80)
    print("ANÁLISIS Y RECOMENDACIONES")
    print("=" * 80)
    print()
    
    best_return = df_results.iloc[0]
    best_sharpe = df_results.loc[df_results['Sharpe Ratio'].idxmax()]
    best_winrate = df_results.loc[df_results['Win Rate (%)'].idxmax()]
    lowest_drawdown = df_results.loc[df_results['Max Drawdown (%)'].idxmax()]  # Menos negativo
    
    print(f"🏆 MEJOR RETORNO:")
    print(f"   {best_return['Estrategia']}: {best_return['Retorno (%)']:.2f}%")
    print()
    
    print(f"📊 MEJOR SHARPE RATIO (Riesgo/Beneficio):")
    print(f"   {best_sharpe['Estrategia']}: {best_sharpe['Sharpe Ratio']:.2f}")
    print()
    
    print(f"🎯 MEJOR WIN RATE:")
    print(f"   {best_winrate['Estrategia']}: {best_winrate['Win Rate (%)']:.2f}%")
    print()
    
    print(f"🛡️  MENOR DRAWDOWN (Más segura):")
    print(f"   {lowest_drawdown['Estrategia']}: {lowest_drawdown['Max Drawdown (%)']:.2f}%")
    print()
    
    print("💡 RECOMENDACIONES:")
    print()
    
    # Recomendación basada en perfil
    if best_sharpe['Sharpe Ratio'] > 1.0:
        print("   ✓ Para traders conservadores:")
        print(f"     → {best_sharpe['Estrategia']} (Mejor Sharpe: {best_sharpe['Sharpe Ratio']:.2f})")
    
    if best_return['Retorno (%)'] > 20:
        print("   ✓ Para traders agresivos:")
        print(f"     → {best_return['Estrategia']} (Retorno: {best_return['Retorno (%)']:.2f}%)")
    
    if best_winrate['Win Rate (%)'] > 60:
        print("   ✓ Para traders que buscan consistencia:")
        print(f"     → {best_winrate['Estrategia']} (Win Rate: {best_winrate['Win Rate (%)']:.2f}%)")
    
    print()
    print("⚠️  NOTA IMPORTANTE:")
    print("   Estos resultados son con datos SINTÉTICOS.")
    print("   Prueba con datos REALES usando:")
    print("   python3 main.py --strategy NOMBRE --symbol BTC/USDT --days 365")
    print()
    
    # Guardar resultados
    df_results.to_csv('data/strategy_comparison.csv', index=False)
    print(f"✓ Resultados guardados en: data/strategy_comparison.csv")
    print()


if __name__ == '__main__':
    compare_strategies()
