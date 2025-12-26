"""
Base class for multi-symbol trading strategies.

Extends BaseStrategy to support portfolios with multiple assets traded simultaneously.
Used for strategies like pair trading, statistical arbitrage, and basket trading.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from strategies.base_strategy import BaseStrategy


class MultiSymbolStrategy(BaseStrategy):
    """
    Abstract base class for strategies that trade multiple symbols simultaneously.
    
    Unlike single-symbol strategies, multi-symbol strategies:
    - Receive data for multiple symbols
    - Generate signals for each symbol independently
    - Support long/short positions across different assets
    - Track portfolio-level metrics
    """
    
    def __init__(self, name: str, symbols: List[str], params: Optional[Dict[str, Any]] = None):
        """
        Initialize multi-symbol strategy.
        
        Args:
            name: Strategy name
            symbols: List of symbols to trade (e.g., ['BTC/USDT', 'ETH/USDT'])
            params: Strategy parameters
        """
        super().__init__(name=name, params=params)
        self.symbols = symbols
        self.positions_by_symbol = {symbol: 0 for symbol in symbols}
        
    @abstractmethod
    def fetch_multi_symbol_data(
        self, 
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        timeframe: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch and align data for multiple symbols.
        
        Args:
            symbols: List of symbol identifiers
            start_date: Start date for historical data
            end_date: End date for historical data
            timeframe: Timeframe (e.g., '1d', '1h')
            
        Returns:
            Dictionary mapping symbol -> DataFrame with aligned timestamps
        """
        pass
    
    @abstractmethod
    def calculate_multi_symbol_indicators(
        self, 
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Calculate indicators across multiple symbols.
        
        This method should add indicator columns to each DataFrame and may
        also calculate cross-asset indicators (correlations, spreads, etc.).
        
        Args:
            data_dict: Dictionary of symbol -> DataFrame
            
        Returns:
            Updated dictionary with indicator columns added
        """
        pass
    
    @abstractmethod
    def generate_multi_symbol_signals(
        self, 
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate trading signals for each symbol.
        
        Signals are added as 'signal' column to each DataFrame:
        - 1: Buy/Long signal
        - -1: Sell/Short signal
        - 0: Hold/No action
        
        Args:
            data_dict: Dictionary of symbol -> DataFrame with indicators
            
        Returns:
            Updated dictionary with 'signal' column added to each DataFrame
        """
        pass
    
    # Override single-symbol methods to raise errors
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Not used for multi-symbol strategies."""
        raise NotImplementedError(
            "Multi-symbol strategies should use calculate_multi_symbol_indicators()"
        )
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Not used for multi-symbol strategies."""
        raise NotImplementedError(
            "Multi-symbol strategies should use generate_multi_symbol_signals()"
        )
    
    def get_position_summary(self) -> Dict[str, Any]:
        """
        Get current portfolio position summary.
        
        Returns:
            Dictionary with position information for each symbol
        """
        return {
            'symbols': self.symbols,
            'positions': self.positions_by_symbol.copy(),
            'num_positions': sum(1 for pos in self.positions_by_symbol.values() if pos != 0)
        }
    
    def validate_params(self) -> bool:
        """
        Validate strategy parameters.
        
        Returns:
            True if parameters are valid
        """
        if not self.symbols or len(self.symbols) < 2:
            raise ValueError("Multi-symbol strategy requires at least 2 symbols")
        
        return super().validate_params()
