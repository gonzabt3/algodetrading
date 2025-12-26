"""
Script para descargar datos de acciones argentinas (ADRs) desde Yahoo Finance.

Las acciones argentinas que cotizan en NYSE tienen tickers especiales:
- VIST (Vista Oil & Gas)
- YPFD (YPF)
- GGAL (Grupo Financiero Galicia)
- BMA (Banco Macro)
- SUPV (Grupo Supervielle)
- PAM (Pampa Energía)
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.database import SessionLocal
from api import crud


# Símbolos de acciones argentinas (ADRs en NYSE)
ARGENTINE_STOCKS = {
    'VIST': 'Vista Oil & Gas',
    'YPF': 'YPF',  # Ticker correcto es YPF, no YPFD
    'GGAL': 'Grupo Financiero Galicia',
    'BMA': 'Banco Macro',
    'SUPV': 'Grupo Supervielle',
    'PAM': 'Pampa Energía',
    'TEO': 'Telecom Argentina',
    'CEPU': 'Central Puerto',
    'TGS': 'Transportadora de Gas del Sur',
    'LOMA': 'Loma Negra'
}


def download_stock_data(symbol: str, period: str = '2y') -> pd.DataFrame:
    """
    Descargar datos históricos de una acción desde Yahoo Finance.
    
    Args:
        symbol: Ticker de la acción
        period: Periodo de datos ('1y', '2y', '5y', etc.)
        
    Returns:
        DataFrame con datos OHLCV
    """
    print(f"📥 Descargando {symbol}...")
    
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if data.empty:
            print(f"❌ {symbol}: No se encontraron datos")
            return None
        
        # Renombrar columnas al formato esperado
        data = data.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        
        # Seleccionar solo columnas necesarias
        data = data[['open', 'high', 'low', 'close', 'volume']]
        
        # Reset index para tener timestamp como columna
        data = data.reset_index()
        data = data.rename(columns={'Date': 'timestamp'})
        
        print(f"✅ {symbol}: {len(data)} registros descargados")
        print(f"   Rango: {data['timestamp'].min().date()} a {data['timestamp'].max().date()}")
        
        return data
    
    except Exception as e:
        print(f"❌ Error descargando {symbol}: {str(e)}")
        return None


def save_to_database(symbol: str, data: pd.DataFrame, db: Session):
    """
    Guardar datos en la base de datos.
    
    Args:
        symbol: Ticker de la acción
        data: DataFrame con datos OHLCV
        db: Sesión de base de datos
    """
    if data is None or data.empty:
        return
    
    print(f"💾 Guardando {symbol} en base de datos...")
    
    try:
        # Preparar datos para inserción
        records = []
        for _, row in data.iterrows():
            records.append({
                'symbol': symbol,
                'asset_type': 'stock',
                'timestamp': row['timestamp'],
                'timeframe': '1d',
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume'])
            })
        
        # Insertar en bulk
        crud.bulk_insert_market_data(db, records)
        
        print(f"✅ {symbol}: {len(records)} registros guardados")
        
    except Exception as e:
        print(f"❌ Error guardando {symbol}: {str(e)}")
        db.rollback()


def main():
    """Función principal para descargar y guardar datos."""
    print("🇦🇷 Descargando datos de acciones argentinas...\n")
    
    db = SessionLocal()
    
    try:
        for symbol, name in ARGENTINE_STOCKS.items():
            print(f"\n{'='*60}")
            print(f"📊 {name} ({symbol})")
            print('='*60)
            
            # Descargar datos
            data = download_stock_data(symbol, period='2y')
            
            if data is not None:
                # Guardar en base de datos
                save_to_database(symbol, data, db)
        
        print(f"\n{'='*60}")
        print("✅ Descarga completada!")
        print('='*60)
        
    finally:
        db.close()


if __name__ == '__main__':
    main()
