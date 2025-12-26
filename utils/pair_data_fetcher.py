"""
Data fetcher for pair trading strategies.

Fetches and aligns market data for multiple symbols to support
pair trading, statistical arbitrage, and other multi-symbol strategies.
"""

from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
from utils.data_fetcher import DataFetcher


class PairDataFetcher:
    """
    Fetches and aligns data for multiple symbols.
    
    Handles:
    - Fetching data from multiple sources
    - Timestamp alignment (inner join to ensure matching data points)
    - Missing data handling
    - Hedge ratio calculation
    """
    
    def __init__(self):
        self.data_fetcher = DataFetcher()
    
    def fetch_pair_data(
        self,
        symbol_a: str,
        symbol_b: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timeframe: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch aligned data for a pair of symbols.
        
        Args:
            symbol_a: First symbol (e.g., 'BTC/USDT')
            symbol_b: Second symbol (e.g., 'ETH/USDT')
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Timeframe (e.g., '1d', '1h', '15m')
            
        Returns:
            Dictionary with keys 'symbol_a' and 'symbol_b', each containing
            a DataFrame with aligned timestamps
            
        Raises:
            ValueError: If symbols are identical or data cannot be fetched
        """
        if symbol_a == symbol_b:
            raise ValueError("Symbols must be different for pair trading")
        
        # Fetch data for both symbols
        data_a = self.data_fetcher.fetch_from_db(
            symbol=symbol_a,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
        
        data_b = self.data_fetcher.fetch_from_db(
            symbol=symbol_b,
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
        
        if data_a.empty:
            raise ValueError(f"No data found for symbol: {symbol_a}")
        if data_b.empty:
            raise ValueError(f"No data found for symbol: {symbol_b}")
        
        # Align timestamps using inner join (only keep matching timestamps)
        data_a, data_b = self._align_dataframes(data_a, data_b)
        
        if data_a.empty or data_b.empty:
            raise ValueError(
                f"No overlapping timestamps found between {symbol_a} and {symbol_b}"
            )
        
        return {
            symbol_a: data_a,
            symbol_b: data_b
        }
    
    def fetch_multiple_symbols(
        self,
        symbols: List[str],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timeframe: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch aligned data for multiple symbols.
        
        Args:
            symbols: List of symbols to fetch
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Timeframe (e.g., '1d', '1h', '15m')
            
        Returns:
            Dictionary mapping symbol -> DataFrame with aligned timestamps
        """
        if len(symbols) < 2:
            raise ValueError("At least 2 symbols required")
        
        # Fetch all data
        data_dict = {}
        for symbol in symbols:
            data = self.data_fetcher.fetch_from_db(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe
            )
            if data.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            data_dict[symbol] = data
        
        # Align all dataframes
        aligned_dict = self._align_multiple_dataframes(data_dict)
        
        return aligned_dict
    
    def _align_dataframes(
        self,
        df_a: pd.DataFrame,
        df_b: pd.DataFrame
    ) -> tuple:
        """
        Align two dataframes on their timestamp index.
        
        Uses inner join to keep only matching timestamps.
        
        Args:
            df_a: First dataframe
            df_b: Second dataframe
            
        Returns:
            Tuple of (aligned_df_a, aligned_df_b)
        """
        # Ensure both have datetime index
        if not isinstance(df_a.index, pd.DatetimeIndex):
            df_a = df_a.set_index('timestamp')
        if not isinstance(df_b.index, pd.DatetimeIndex):
            df_b = df_b.set_index('timestamp')
        
        # Find common timestamps (inner join)
        common_index = df_a.index.intersection(df_b.index)
        
        # Filter both dataframes to common timestamps
        df_a_aligned = df_a.loc[common_index].copy()
        df_b_aligned = df_b.loc[common_index].copy()
        
        return df_a_aligned, df_b_aligned
    
    def _align_multiple_dataframes(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Align multiple dataframes on their timestamp index.
        
        Args:
            data_dict: Dictionary of symbol -> DataFrame
            
        Returns:
            Dictionary with aligned DataFrames
        """
        # Ensure all have datetime index
        for symbol, df in data_dict.items():
            if not isinstance(df.index, pd.DatetimeIndex):
                data_dict[symbol] = df.set_index('timestamp')
        
        # Find common timestamps across all dataframes
        common_index = None
        for df in data_dict.values():
            if common_index is None:
                common_index = df.index
            else:
                common_index = common_index.intersection(df.index)
        
        # Filter all dataframes to common timestamps
        aligned_dict = {}
        for symbol, df in data_dict.items():
            aligned_dict[symbol] = df.loc[common_index].copy()
        
        return aligned_dict
    
    def calculate_hedge_ratio(
        self,
        data_a: pd.DataFrame,
        data_b: pd.DataFrame,
        window: Optional[int] = None
    ) -> float:
        """
        Calculate hedge ratio using linear regression.
        
        Hedge ratio determines how many units of symbol_b to trade
        for each unit of symbol_a to create a market-neutral position.
        
        Args:
            data_a: DataFrame for first symbol
            data_b: DataFrame for second symbol
            window: Rolling window size (None = use all data)
            
        Returns:
            Hedge ratio (beta coefficient from regression)
        """
        import numpy as np
        from sklearn.linear_model import LinearRegression
        
        # Use closing prices
        prices_a = data_a['close'].values.reshape(-1, 1)
        prices_b = data_b['close'].values
        
        if window is not None:
            # Use only recent data
            prices_a = prices_a[-window:]
            prices_b = prices_b[-window:]
        
        # Fit linear regression: price_b = beta * price_a + alpha
        model = LinearRegression()
        model.fit(prices_a, prices_b)
        
        hedge_ratio = model.coef_[0]
        
        return hedge_ratio
    
    def calculate_correlation(
        self,
        data_a: pd.DataFrame,
        data_b: pd.DataFrame,
        window: Optional[int] = None
    ) -> float:
        """
        Calculate correlation between two symbols.
        
        Args:
            data_a: DataFrame for first symbol
            data_b: DataFrame for second symbol
            window: Rolling window size (None = use all data)
            
        Returns:
            Correlation coefficient (-1 to 1)
        """
        returns_a = data_a['close'].pct_change()
        returns_b = data_b['close'].pct_change()
        
        if window is not None:
            returns_a = returns_a.iloc[-window:]
            returns_b = returns_b.iloc[-window:]
        
        correlation = returns_a.corr(returns_b)
        
        return correlation
