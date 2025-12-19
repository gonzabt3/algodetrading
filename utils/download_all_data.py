"""
Script maestro para descargar todos los datos históricos
"""
import logging
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Ejecuta todos los descargadores"""
    logger.info("=" * 70)
    logger.info("🚀 DESCARGADOR MAESTRO DE DATOS HISTÓRICOS")
    logger.info("=" * 70)
    logger.info("")
    logger.info("Este script descargará:")
    logger.info("  • 5 criptomonedas principales (2 años, datos diarios)")
    logger.info("  • 10 acciones tech (10 años, datos diarios)")
    logger.info("  • 3 índices principales (10 años, datos diarios)")
    logger.info("")
    logger.info("Tiempo estimado: 2-3 minutos")
    logger.info("=" * 70)
    logger.info("")
    
    # Crear directorios
    os.makedirs('data/crypto', exist_ok=True)
    os.makedirs('data/stocks', exist_ok=True)
    os.makedirs('data/indices', exist_ok=True)
    
    # 1. Descargar criptomonedas
    logger.info("\n" + "🔶" * 35)
    logger.info("PASO 1/2: CRIPTOMONEDAS (CCXT)")
    logger.info("🔶" * 35 + "\n")
    
    try:
        from utils.download_market_data import main as download_crypto
        download_crypto()
    except Exception as e:
        logger.error(f"❌ Error descargando criptomonedas: {e}")
        logger.info("Continuando con acciones...")
    
    # 2. Descargar acciones e índices
    logger.info("\n" + "🔷" * 35)
    logger.info("PASO 2/2: ACCIONES E ÍNDICES (YAHOO FINANCE)")
    logger.info("🔷" * 35 + "\n")
    
    try:
        from utils.download_yahoo_data import main as download_yahoo
        download_yahoo()
    except Exception as e:
        logger.error(f"❌ Error descargando acciones: {e}")
    
    # Resumen final
    logger.info("\n" + "=" * 70)
    logger.info("🎉 DESCARGA COMPLETADA")
    logger.info("=" * 70)
    
    # Contar archivos descargados
    crypto_files = len([f for f in os.listdir('data/crypto') if f.endswith('.csv')]) if os.path.exists('data/crypto') else 0
    stock_files = len([f for f in os.listdir('data/stocks') if f.endswith('.csv')]) if os.path.exists('data/stocks') else 0
    index_files = len([f for f in os.listdir('data/indices') if f.endswith('.csv')]) if os.path.exists('data/indices') else 0
    
    logger.info(f"\n📊 Archivos descargados:")
    logger.info(f"  • Criptomonedas: {crypto_files} archivos en data/crypto/")
    logger.info(f"  • Acciones: {stock_files} archivos en data/stocks/")
    logger.info(f"  • Índices: {index_files} archivos en data/indices/")
    logger.info(f"  • TOTAL: {crypto_files + stock_files + index_files} archivos CSV")
    
    logger.info("\n✅ Todos los datos están listos para backtesting!")
    logger.info("\n💡 Próximos pasos:")
    logger.info("  1. Usa estos datos con use_real_data=True en el dashboard")
    logger.info("  2. Ejecuta: python main.py para backtest desde CLI")
    logger.info("  3. O usa el dashboard en http://localhost:3000")
    logger.info("")


if __name__ == '__main__':
    main()
