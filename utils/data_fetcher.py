"""
Data Fetcher for market data
Supports multiple data sources including CCXT for crypto exchanges
"""
import pandas as pd
import ccxt
from datetime import datetime, timedelta
from typing import Optional
import logging
import os


class DataFetcher:
    """
    Fetches market data from various sources
    """
    
    def __init__(self, exchange_name: str = 'binance'):
        """
        Initialize data fetcher
        
        Args:
            exchange_name: Name of the exchange (e.g., 'binance', 'coinbase')
        """
        self.logger = logging.getLogger(__name__)
        self.exchange_name = exchange_name
        
        # Initialize exchange
        try:
            exchange_class = getattr(ccxt, exchange_name)
            self.exchange = exchange_class({
                'enableRateLimit': True,
            })
        except Exception as e:
            self.logger.error(f"Error initializing exchange {exchange_name}: {e}")
            self.exchange = None
    
    def fetch_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1d',
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 1000
    ) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data
        
        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '1m', '5m', '1h', '1d')
            start_date: Start date for historical data
            end_date: End date for historical data
            limit: Maximum number of candles to fetch
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        if not self.exchange:
            self.logger.error("Exchange not initialized")
            return None
        
        try:
            # Set default dates if not provided
            if end_date is None:
                end_date = datetime.now()
            if start_date is None:
                start_date = end_date - timedelta(days=365)
            
            # Convert to timestamps
            since = int(start_date.timestamp() * 1000)
            
            self.logger.info(f"Fetching {symbol} {timeframe} data from {start_date} to {end_date}")
            
            # Fetch OHLCV data
            all_ohlcv = []
            current_since = since
            
            while True:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    since=current_since,
                    limit=limit
                )
                
                if not ohlcv:
                    break
                
                all_ohlcv.extend(ohlcv)
                
                # Check if we've reached the end date
                last_timestamp = ohlcv[-1][0]
                if last_timestamp >= int(end_date.timestamp() * 1000):
                    break
                
                current_since = last_timestamp + 1
                
                # Prevent infinite loop
                if len(all_ohlcv) > limit * 10:
                    break
            
            # Convert to DataFrame
            df = pd.DataFrame(
                all_ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Filter by date range
            df = df[(df.index >= start_date) & (df.index <= end_date)]
            
            self.logger.info(f"Fetched {len(df)} candles")
            
            return df
            
        except Exception as e:
            self.logger.error(f"Error fetching OHLCV data: {e}")
            return None
    
    def fetch_from_csv(self, filepath: str) -> Optional[pd.DataFrame]:
        """
        Load OHLCV data from CSV file
        
        Args:
            filepath: Path to CSV file
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            df = pd.read_csv(filepath, parse_dates=['timestamp'], index_col='timestamp')
            self.logger.info(f"Loaded {len(df)} candles from {filepath}")
            return df
        except Exception as e:
            self.logger.error(f"Error loading CSV: {e}")
            return None
    
    def save_to_csv(self, data: pd.DataFrame, filepath: str) -> bool:
        """
        Save OHLCV data to CSV file
        
        Args:
            data: DataFrame with OHLCV data
            filepath: Path to save CSV file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            data.to_csv(filepath)
            self.logger.info(f"Saved {len(data)} candles to {filepath}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
            return False
