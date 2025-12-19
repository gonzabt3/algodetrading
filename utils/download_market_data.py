"""
Script para descargar datos históricos usando CCXT
"""
import ccxt
import pandas as pd
from datetime import datetime, timedelta
import time
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CryptoDataDownloader:
    """Descarga datos históricos de exchanges de criptomonedas"""
    
    def __init__(self, exchange_name: str = 'binance'):
        """
        Inicializa el descargador
        
        Args:
            exchange_name: Nombre del exchange (binance, coinbase, kraken, etc.)
        """
        try:
            self.exchange = getattr(ccxt, exchange_name)()
            self.exchange_name = exchange_name
            logger.info(f"✅ Exchange {exchange_name} inicializado")
        except Exception as e:
            logger.error(f"❌ Error inicializando exchange {exchange_name}: {e}")
            raise
        
    def download_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1d',
        days: int = 730,
        save_csv: bool = True
    ) -> pd.DataFrame:
        """
        Descarga datos OHLCV
        
        Args:
            symbol: Par de trading (ej: 'BTC/USDT')
            timeframe: Timeframe ('1m', '5m', '1h', '1d', '1w')
            days: Días hacia atrás
            save_csv: Si True, guarda en CSV
            
        Returns:
            DataFrame con columnas: timestamp, open, high, low, close, volume
        """
        logger.info(f"📊 Descargando {symbol} {timeframe} últimos {days} días...")
        
        # Calcular timestamp de inicio
        since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        
        all_data = []
        retries = 0
        max_retries = 3
        
        while retries < max_retries:
            try:
                # Descargar chunk de datos
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    since=since,
                    limit=1000  # Máximo por request
                )
                
                if not ohlcv:
                    break
                    
                all_data.extend(ohlcv)
                
                # Actualizar 'since' al último timestamp
                since = ohlcv[-1][0] + 1
                
                # Evitar rate limits
                time.sleep(self.exchange.rateLimit / 1000)
                
                logger.info(f"  ↳ Descargados {len(all_data)} registros...")
                
                # Si ya tenemos suficientes datos, salir
                if len(ohlcv) < 1000:
                    break
                    
            except Exception as e:
                retries += 1
                logger.warning(f"⚠️  Intento {retries}/{max_retries} falló: {e}")
                if retries < max_retries:
                    time.sleep(5)
                else:
                    logger.error(f"❌ Error descargando {symbol} después de {max_retries} intentos")
                    return None
        
        if not all_data:
            logger.error(f"❌ No se pudo descargar datos para {symbol}")
            return None
        
        # Convertir a DataFrame
        df = pd.DataFrame(
            all_data,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )
        
        # Convertir timestamp a datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        # Eliminar duplicados
        df = df[~df.index.duplicated(keep='first')]
        
        logger.info(f"✅ Total descargado: {len(df)} registros")
        logger.info(f"  ↳ Rango: {df.index[0]} a {df.index[-1]}")
        
        # Guardar CSV
        if save_csv:
            # Crear directorio si no existe
            os.makedirs('data/crypto', exist_ok=True)
            
            filename = f"data/crypto/{self.exchange_name}_{symbol.replace('/', '_')}_{timeframe}.csv"
            df.to_csv(filename)
            logger.info(f"💾 Guardado en: {filename}")
        
        return df
    
    def download_multiple_symbols(
        self,
        symbols: list,
        timeframe: str = '1d',
        days: int = 730
    ) -> dict:
        """
        Descarga múltiples símbolos
        
        Args:
            symbols: Lista de símbolos
            timeframe: Timeframe
            days: Días
            
        Returns:
            Diccionario {symbol: DataFrame}
        """
        data = {}
        
        for i, symbol in enumerate(symbols, 1):
            logger.info(f"\n[{i}/{len(symbols)}] Procesando {symbol}")
            try:
                df = self.download_ohlcv(symbol, timeframe, days)
                if df is not None:
                    data[symbol] = df
                time.sleep(1)  # Pausa entre símbolos
            except Exception as e:
                logger.error(f"❌ Error con {symbol}: {e}")
        
        return data


def main():
    """Descarga datos de criptomonedas"""
    logger.info("=" * 60)
    logger.info("🚀 DESCARGA DE DATOS DE CRIPTOMONEDAS")
    logger.info("=" * 60)
    
    downloader = CryptoDataDownloader('binance')
    
    # Lista de criptomonedas principales
    symbols = [
        'BTC/USDT',   # Bitcoin
        'ETH/USDT',   # Ethereum
        'BNB/USDT',   # Binance Coin
        'SOL/USDT',   # Solana
        'ADA/USDT',   # Cardano
    ]
    
    # Descargar todas
    all_data = downloader.download_multiple_symbols(symbols, timeframe='1d', days=730)
    
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ DESCARGA COMPLETADA: {len(all_data)}/{len(symbols)} símbolos")
    logger.info("=" * 60)
    
    for symbol, df in all_data.items():
        logger.info(f"  • {symbol}: {len(df)} registros ({df.index[0].date()} a {df.index[-1].date()})")


if __name__ == '__main__':
    main()
