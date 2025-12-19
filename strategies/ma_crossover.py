"""
Moving Average Crossover Strategy
Generates buy signals when fast MA crosses above slow MA
Generates sell signals when fast MA crosses below slow MA
"""
import pandas as pd
from typing import Dict, Any
from strategies.base_strategy import BaseStrategy


class MovingAverageCrossover(BaseStrategy):
    """
    Moving Average Crossover Strategy
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize MA Crossover strategy
        
        Args:
            params: Dictionary with 'fast_period' and 'slow_period'
        """
        default_params = {
            'fast_period': 20,
            'slow_period': 50
        }
        if params:
            default_params.update(params)
        
        super().__init__(name="MA Crossover", params=default_params)
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate moving averages
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with MA columns added
        """
        fast_period = self.params['fast_period']
        slow_period = self.params['slow_period']
        
        data['ma_fast'] = data['close'].rolling(window=fast_period).mean()
        data['ma_slow'] = data['close'].rolling(window=slow_period).mean()
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on MA crossover
        
        Args:
            data: DataFrame with MA indicators
            
        Returns:
            DataFrame with signals column
        """
        data['signal'] = 0
        
        # Buy signal: fast MA crosses above slow MA
        data.loc[
            (data['ma_fast'] > data['ma_slow']) &
            (data['ma_fast'].shift(1) <= data['ma_slow'].shift(1)),
            'signal'
        ] = 1
        
        # Sell signal: fast MA crosses below slow MA
        data.loc[
            (data['ma_fast'] < data['ma_slow']) &
            (data['ma_fast'].shift(1) >= data['ma_slow'].shift(1)),
            'signal'
        ] = -1
        
        return data
    
    def validate_params(self) -> bool:
        """
        Validate strategy parameters
        
        Returns:
            True if parameters are valid
        """
        fast = self.params.get('fast_period', 0)
        slow = self.params.get('slow_period', 0)
        
        if fast <= 0 or slow <= 0:
            return False
        
        if fast >= slow:
            return False
        
        return True
