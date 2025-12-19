"""
Script para descargar datos de Yahoo Finance (acciones, índices, ETFs)
"""
import pandas as pd
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class YahooDataDownloader:
    """Descarga datos de Yahoo Finance"""
    
    @staticmethod
    def download_stock(
        ticker: str,
        period: str = '10y',
        interval: str = '1d',
        save_csv: bool = True
    ) -> pd.DataFrame:
        """
        Descarga datos de una acción usando pandas_datareader
        
        Args:
            ticker: Símbolo (ej: 'AAPL', 'MSFT', 'TSLA')
            period: Período en años
            interval: Intervalo ('1d')
            save_csv: Guardar CSV
            
        Returns:
            DataFrame con OHLCV
        """
        logger.info(f"📊 Descargando {ticker} período {period}...")
        
        try:
            import yfinance as yf
        except ImportError:
            logger.error("❌ yfinance no instalado. Instalando...")
            import subprocess
            subprocess.check_call(['pip', 'install', 'yfinance'])
            import yfinance as yf
        
        try:
            # Descargar datos
            stock = yf.Ticker(ticker)
            data = stock.history(period=period, interval=interval)
            
            if data.empty:
                logger.error(f"❌ No se encontraron datos para {ticker}")
                return None
            
            # Renombrar columnas para consistencia (ya vienen en minúsculas con .history())
            data.columns = [col.lower().replace(' ', '_') for col in data.columns]
            
            logger.info(f"✅ Descargados {len(data)} registros")
            logger.info(f"  ↳ Rango: {data.index[0].date()} a {data.index[-1].date()}")
            
            # Guardar CSV
            if save_csv:
                # Crear directorio si no existe
                if ticker.startswith('^'):
                    os.makedirs('data/indices', exist_ok=True)
                    filename = f"data/indices/yahoo_{ticker.replace('^', '')}_{interval}_{period}.csv"
                else:
                    os.makedirs('data/stocks', exist_ok=True)
                    filename = f"data/stocks/yahoo_{ticker}_{interval}_{period}.csv"
                
                data.to_csv(filename)
                logger.info(f"💾 Guardado en: {filename}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Error descargando {ticker}: {e}")
            return None
    
    @staticmethod
    def download_multiple_stocks(
        tickers: list,
        period: str = '10y',
        interval: str = '1d'
    ) -> dict:
        """
        Descarga múltiples acciones
        
        Args:
            tickers: Lista de símbolos
            period: Período
            interval: Intervalo
            
        Returns:
            Diccionario {ticker: DataFrame}
        """
        data = {}
        
        for i, ticker in enumerate(tickers, 1):
            logger.info(f"\n[{i}/{len(tickers)}] Procesando {ticker}")
            try:
                df = YahooDataDownloader.download_stock(ticker, period, interval)
                if df is not None:
                    data[ticker] = df
            except Exception as e:
                logger.error(f"❌ Error con {ticker}: {e}")
        
        return data


def main():
    """Descarga datos de acciones e índices"""
    logger.info("=" * 60)
    logger.info("🚀 DESCARGA DE DATOS DE YAHOO FINANCE")
    logger.info("=" * 60)
    
    downloader = YahooDataDownloader()
    
    # Acciones tech principales
    logger.info("\n📈 Descargando ACCIONES...")
    stocks = [
        'AAPL',   # Apple
        'MSFT',   # Microsoft
        'GOOGL',  # Google
        'AMZN',   # Amazon
        'TSLA',   # Tesla
        'NVDA',   # NVIDIA
        'META',   # Meta (Facebook)
        'NFLX',   # Netflix
        'AMD',    # AMD
        'INTC',   # Intel
    ]
    
    stock_data = downloader.download_multiple_stocks(stocks, period='10y')
    
    # Índices principales
    logger.info("\n📊 Descargando ÍNDICES...")
    indices = [
        '^GSPC',  # S&P 500
        '^DJI',   # Dow Jones
        '^IXIC',  # NASDAQ
    ]
    
    index_data = downloader.download_multiple_stocks(indices, period='10y')
    
    # Resumen
    logger.info("\n" + "=" * 60)
    logger.info(f"✅ DESCARGA COMPLETADA")
    logger.info("=" * 60)
    logger.info(f"  • Acciones: {len(stock_data)}/{len(stocks)} descargadas")
    logger.info(f"  • Índices: {len(index_data)}/{len(indices)} descargados")
    
    logger.info("\n📁 Archivos guardados en:")
    logger.info("  • data/stocks/")
    logger.info("  • data/indices/")


if __name__ == '__main__':
    main()
