"""
Script para ver y analizar resultados guardados
"""
from utils.results_logger import ResultsLogger
import pandas as pd


def main():
    logger = ResultsLogger()
    
    print("=" * 80)
    print("📊 VISOR DE RESULTADOS DE BACKTESTS")
    print("=" * 80)
    print()
    
    # Mostrar resumen
    df = logger.create_summary_report()
    
    if df.empty:
        print("❌ No hay resultados guardados todavía.")
        print()
        print("💡 CONSEJO: Ejecuta backtests con save_results=True para guardarlos:")
        print("   backtester = Backtester(strategy, save_results=True)")
        return
    
    print(f"📁 Total de backtests guardados: {len(df)}")
    print()
    
    # Mostrar tabla completa
    print("📋 TODOS LOS RESULTADOS:")
    print("-" * 80)
    print(df.to_string(index=False))
    print()
    
    # Estadísticas
    print("=" * 80)
    print("📈 ESTADÍSTICAS:")
    print("=" * 80)
    print()
    
    # Mejor retorno
    mejor_retorno = logger.get_best_result('total_return')
    print("🏆 MEJOR RETORNO:")
    print(f"   {mejor_retorno['strategy']} - {mejor_retorno['symbol']}")
    print(f"   {mejor_retorno['results']['total_return']:.2f}%")
    print(f"   ({mejor_retorno['timestamp'][:10]})")
    print()
    
    # Mejor Sharpe
    mejor_sharpe = logger.get_best_result('sharpe_ratio')
    print("⚡ MEJOR SHARPE RATIO:")
    print(f"   {mejor_sharpe['strategy']} - {mejor_sharpe['symbol']}")
    print(f"   {mejor_sharpe['results']['sharpe_ratio']:.2f}")
    print()
    
    # Mejor Win Rate
    mejor_wr = logger.get_best_result('win_rate')
    print("🎯 MEJOR WIN RATE:")
    print(f"   {mejor_wr['strategy']} - {mejor_wr['symbol']}")
    print(f"   {mejor_wr['results']['win_rate']:.2f}%")
    print()
    
    # Comparación por estrategia
    print("=" * 80)
    print("📊 PROMEDIO POR ESTRATEGIA:")
    print("=" * 80)
    print()
    
    estrategia_stats = df.groupby('Estrategia').agg({
        'Retorno (%)': 'mean',
        'Sharpe': 'mean',
        'Win Rate (%)': 'mean',
        'Trades': 'sum'
    }).round(2)
    
    print(estrategia_stats.to_string())
    print()
    
    # Comparación por símbolo
    print("=" * 80)
    print("💰 PROMEDIO POR SÍMBOLO:")
    print("=" * 80)
    print()
    
    simbolo_stats = df.groupby('Símbolo').agg({
        'Retorno (%)': 'mean',
        'Sharpe': 'mean',
        'Win Rate (%)': 'mean',
        'Trades': 'sum'
    }).round(2)
    
    print(simbolo_stats.to_string())
    print()
    
    print("=" * 80)
    print("✅ Para ver detalles de un backtest específico:")
    print(f"   logger.load_backtest('{df.iloc[0]['Archivo']}')")
    print("=" * 80)


if __name__ == '__main__':
    main()
