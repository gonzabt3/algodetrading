"""
RSI (Relative Strength Index) Strategy
Generates buy signals when RSI is oversold
Generates sell signals when RSI is overbought
"""
import pandas as pd
from typing import Dict, Any
from strategies.base_strategy import BaseStrategy


class RSIStrategy(BaseStrategy):
    """
    RSI Trading Strategy
    """
    
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize RSI strategy
        
        Args:
            params: Dictionary with 'period', 'oversold', and 'overbought'
        """
        default_params = {
            'period': 14,
            'oversold': 30,
            'overbought': 70
        }
        if params:
            default_params.update(params)
        
        super().__init__(name="RSI Strategy", params=default_params)
        
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate RSI indicator
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            DataFrame with RSI column added
        """
        period = self.params['period']
        
        # Calculate price changes
        delta = data['close'].diff()
        
        # Separate gains and losses
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gain / avg_loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        return data
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals based on RSI
        
        Args:
            data: DataFrame with RSI indicator
            
        Returns:
            DataFrame with signals column
        """
        oversold = self.params['oversold']
        overbought = self.params['overbought']
        
        data['signal'] = 0
        
        # Buy signal: RSI crosses above oversold level
        data.loc[
            (data['rsi'] > oversold) &
            (data['rsi'].shift(1) <= oversold),
            'signal'
        ] = 1
        
        # Sell signal: RSI crosses below overbought level
        data.loc[
            (data['rsi'] < overbought) &
            (data['rsi'].shift(1) >= overbought),
            'signal'
        ] = -1
        
        return data
    
    def validate_params(self) -> bool:
        """
        Validate strategy parameters
        
        Returns:
            True if parameters are valid
        """
        period = self.params.get('period', 0)
        oversold = self.params.get('oversold', 0)
        overbought = self.params.get('overbought', 0)
        
        if period <= 0:
            return False
        
        if oversold <= 0 or oversold >= 50:
            return False
        
        if overbought <= 50 or overbought >= 100:
            return False
        
        if oversold >= overbought:
            return False
        
        return True
