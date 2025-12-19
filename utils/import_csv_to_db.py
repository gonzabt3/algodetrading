"""
Script para importar datos CSV a PostgreSQL
"""
import pandas as pd
import os
import sys
from pathlib import Path
import logging
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import MarketData
from sqlalchemy import and_

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_csv_to_db(csv_path: str, symbol: str, asset_type: str = 'crypto') -> int:
    """
    Importa un archivo CSV a la tabla market_data
    
    Args:
        csv_path: Ruta al archivo CSV
        symbol: Símbolo del activo (ej: BTC/USDT)
        asset_type: Tipo de activo (crypto, stock, index)
        
    Returns:
        Número de registros importados
    """
    logger.info(f"📥 Importando {csv_path}...")
    
    # Leer CSV
    try:
        df = pd.read_csv(csv_path, index_col=0, parse_dates=True)
    except Exception as e:
        logger.error(f"❌ Error leyendo CSV: {e}")
        return 0
    
    # Verificar columnas requeridas
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    if not all(col in df.columns for col in required_cols):
        logger.error(f"❌ CSV no tiene las columnas requeridas: {required_cols}")
        return 0
    
    db = SessionLocal()
    imported_count = 0
    skipped_count = 0
    
    try:
        # Procesar en chunks para no saturar memoria
        chunk_size = 1000
        total_rows = len(df)
        
        for start_idx in range(0, total_rows, chunk_size):
            end_idx = min(start_idx + chunk_size, total_rows)
            chunk = df.iloc[start_idx:end_idx]
            
            for timestamp, row in chunk.iterrows():
                # Verificar si ya existe
                existing = db.query(MarketData).filter(
                    and_(
                        MarketData.symbol == symbol,
                        MarketData.timestamp == timestamp
                    )
                ).first()
                
                if existing:
                    skipped_count += 1
                    continue
                
                # Crear registro
                market_data = MarketData(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=float(row['open']),
                    high=float(row['high']),
                    low=float(row['low']),
                    close=float(row['close']),
                    volume=float(row['volume']),
                    asset_type=asset_type
                )
                db.add(market_data)
                imported_count += 1
            
            # Commit cada chunk
            db.commit()
            logger.info(f"  ↳ Procesados {end_idx}/{total_rows} registros...")
        
        logger.info(f"✅ Importados: {imported_count}, Omitidos (duplicados): {skipped_count}")
        return imported_count
        
    except Exception as e:
        logger.error(f"❌ Error importando: {e}")
        db.rollback()
        return 0
    finally:
        db.close()


def import_all_csv_files():
    """Importa todos los archivos CSV a la base de datos"""
    
    logger.info("=" * 70)
    logger.info("📦 IMPORTADOR DE DATOS CSV → PostgreSQL")
    logger.info("=" * 70)
    logger.info("")
    
    total_imported = 0
    
    # Directorios a procesar
    directories = {
        'data/crypto': 'crypto',
        'data/stocks': 'stock',
        'data/indices': 'index'
    }
    
    for directory, asset_type in directories.items():
        if not os.path.exists(directory):
            logger.warning(f"⚠️  Directorio {directory} no existe, saltando...")
            continue
        
        csv_files = [f for f in os.listdir(directory) if f.endswith('.csv')]
        
        if not csv_files:
            logger.warning(f"⚠️  No hay archivos CSV en {directory}")
            continue
        
        logger.info(f"\n{'='*70}")
        logger.info(f"📂 Procesando {directory} ({len(csv_files)} archivos)")
        logger.info(f"{'='*70}\n")
        
        for i, csv_file in enumerate(csv_files, 1):
            logger.info(f"[{i}/{len(csv_files)}] {csv_file}")
            
            # Extraer símbolo del nombre del archivo
            # Formato: exchange_SYMBOL_timeframe.csv o yahoo_SYMBOL_interval_period.csv
            parts = csv_file.replace('.csv', '').split('_')
            
            if asset_type == 'crypto':
                # Formato: binance_BTC_USDT_1d.csv
                if len(parts) >= 3:
                    symbol = f"{parts[1]}/{parts[2]}"  # BTC/USDT
                else:
                    logger.warning(f"⚠️  No se pudo extraer símbolo de {csv_file}")
                    continue
            else:
                # Formato: yahoo_AAPL_1d_10y.csv
                if len(parts) >= 2:
                    symbol = parts[1]  # AAPL
                else:
                    logger.warning(f"⚠️  No se pudo extraer símbolo de {csv_file}")
                    continue
            
            csv_path = os.path.join(directory, csv_file)
            imported = import_csv_to_db(csv_path, symbol, asset_type)
            total_imported += imported
    
    # Resumen final
    logger.info("\n" + "=" * 70)
    logger.info("🎉 IMPORTACIÓN COMPLETADA")
    logger.info("=" * 70)
    logger.info(f"\n📊 Total registros importados: {total_imported:,}")
    
    # Estadísticas de la DB
    db = SessionLocal()
    try:
        total_records = db.query(MarketData).count()
        crypto_count = db.query(MarketData).filter(MarketData.asset_type == 'crypto').count()
        stock_count = db.query(MarketData).filter(MarketData.asset_type == 'stock').count()
        index_count = db.query(MarketData).filter(MarketData.asset_type == 'index').count()
        
        logger.info(f"\n📈 Datos en PostgreSQL:")
        logger.info(f"  • Criptomonedas: {crypto_count:,} registros")
        logger.info(f"  • Acciones: {stock_count:,} registros")
        logger.info(f"  • Índices: {index_count:,} registros")
        logger.info(f"  • TOTAL: {total_records:,} registros")
        
    finally:
        db.close()
    
    logger.info("\n✅ Los backtests ahora pueden usar datos desde PostgreSQL!")
    logger.info("")


def main():
    """Punto de entrada principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Importar datos CSV a PostgreSQL')
    parser.add_argument(
        '--file',
        help='Importar un archivo CSV específico (requiere --symbol)',
        type=str
    )
    parser.add_argument(
        '--symbol',
        help='Símbolo del activo (ej: BTC/USDT)',
        type=str
    )
    parser.add_argument(
        '--type',
        help='Tipo de activo (crypto, stock, index)',
        default='crypto',
        choices=['crypto', 'stock', 'index']
    )
    
    args = parser.parse_args()
    
    if args.file:
        # Importar archivo específico
        if not args.symbol:
            logger.error("❌ Debes especificar --symbol cuando usas --file")
            return
        
        import_csv_to_db(args.file, args.symbol, args.type)
    else:
        # Importar todos los archivos
        import_all_csv_files()


if __name__ == '__main__':
    main()
