"""
Script para poblar la base de datos con datos iniciales de criptomonedas
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_fetcher import DataFetcher

def main():
    print("=" * 60)
    print("POBLACIÓN INICIAL DE LA BASE DE DATOS")
    print("=" * 60)
    print()
    
    fetcher = DataFetcher()
    
    # Lista de símbolos a descargar
    symbols = [
        ('BTC/USDT', 'Bitcoin'),
        ('ETH/USDT', 'Ethereum'),
        ('BNB/USDT', 'Binance Coin'),
        ('SOL/USDT', 'Solana'),
        ('ADA/USDT', 'Cardano')
    ]
    
    print(f"📥 Descargando datos para {len(symbols)} criptomonedas...")
    print()
    
    success_count = 0
    error_count = 0
    
    for symbol, name in symbols:
        print(f"🔄 Procesando {name} ({symbol})...")
        
        result = fetcher.fetch_and_store_binance_data(
            symbol=symbol,
            timeframe='1d',
            days=365,  # 1 año de datos
            asset_type='crypto'
        )
        
        if result['success']:
            success_count += 1
            print(f"   ✅ {result['records_saved']} registros guardados")
            print(f"   📅 Desde {result['min_date']} hasta {result['max_date']}")
        else:
            error_count += 1
            print(f"   ❌ Error: {result.get('error', 'Desconocido')}")
        
        print()
    
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    print(f"✅ Exitosos: {success_count}")
    print(f"❌ Errores: {error_count}")
    print()
    
    if success_count > 0:
        print("🎉 Base de datos poblada exitosamente!")
        print("   Ahora puedes usar el frontend para ver y gestionar los datos.")
    else:
        print("⚠️  No se pudo descargar ningún dato.")
        print("   Verifica tu conexión a internet y las credenciales de Binance.")

if __name__ == '__main__':
    main()
