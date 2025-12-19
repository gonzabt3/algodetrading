"""
Base Strategy Class
All trading strategies should inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import pandas as pd


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies
    """
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        Initialize the strategy
        
        Args:
            name: Strategy name
            params: Strategy parameters
        """
        self.name = name
        self.params = params or {}
        self.positions = []
        self.trades = []
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on market data
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with signals column (1 for buy, -1 for sell, 0 for hold)
        """
        pass
    
    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added indicator columns
        """
        pass
    
    def validate_params(self) -> bool:
        """
        Validate strategy parameters
        
        Returns:
            True if parameters are valid
        """
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get strategy information
        
        Returns:
            Dictionary with strategy details
        """
        return {
            'name': self.name,
            'params': self.params,
            'num_trades': len(self.trades)
        }
