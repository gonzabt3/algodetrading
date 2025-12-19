"""
MACD (Moving Average Convergence Divergence) Strategy
Generates buy signals when MACD crosses above signal line
Generates sell signals when MACD crosses below signal line
"""
import pandas as pd
from typing import Dict, Any
from strategies.base_strategy import BaseStrategy


class MACDStrategy(BaseStrategy):
    """
    MACD Trading Strategy
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize MACD strategy
        
        Args:
            params: Dictionary with 'fast', 'slow', and 'signal' periods
        """
        default_params = {
            'fast': 12,
            'slow': 26,
            'signal': 9
        }
        if params:
            default_params.update(params)
        
        super().__init__(name="MACD Strategy", params=default_params)
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD indicator
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with MACD columns added
        """
        fast = self.params['fast']
        slow = self.params['slow']
        signal = self.params['signal']
        
        # Calculate EMAs
        ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
        ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
        
        # Calculate MACD line
        data['macd'] = ema_fast - ema_slow
        
        # Calculate signal line
        data['macd_signal'] = data['macd'].ewm(span=signal, adjust=False).mean()
        
        # Calculate histogram
        data['macd_histogram'] = data['macd'] - data['macd_signal']
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on MACD
        
        Args:
            data: DataFrame with MACD indicators
            
        Returns:
            DataFrame with signals column
        """
        data['signal'] = 0
        
        # Buy signal: MACD crosses above signal line
        data.loc[
            (data['macd'] > data['macd_signal']) &
            (data['macd'].shift(1) <= data['macd_signal'].shift(1)),
            'signal'
        ] = 1
        
        # Sell signal: MACD crosses below signal line
        data.loc[
            (data['macd'] < data['macd_signal']) &
            (data['macd'].shift(1) >= data['macd_signal'].shift(1)),
            'signal'
        ] = -1
        
        return data
    
    def validate_params(self) -> bool:
        """
        Validate strategy parameters
        
        Returns:
            True if parameters are valid
        """
        fast = self.params.get('fast', 0)
        slow = self.params.get('slow', 0)
        signal = self.params.get('signal', 0)
        
        if fast <= 0 or slow <= 0 or signal <= 0:
            return False
        
        if fast >= slow:
            return False
        
        return True
