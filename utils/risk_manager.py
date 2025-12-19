"""
Risk Management utilities
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np


class RiskManager:
    """
    Risk management for trading strategies
    """
    
    def __init__(
        self,
        max_position_size: float = 1.0,
        max_risk_per_trade: float = 0.02,
        max_drawdown: float = 0.20
    ):
        """
        Initialize risk manager
        
        Args:
            max_position_size: Maximum position size as fraction of capital (0-1)
            max_risk_per_trade: Maximum risk per trade as fraction of capital
            max_drawdown: Maximum allowed drawdown before stopping
        """
        self.max_position_size = max_position_size
        self.max_risk_per_trade = max_risk_per_trade
        self.max_drawdown = max_drawdown
        
    def calculate_position_size(
        self,
        capital: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None
    ) -> int:
        """
        Calculate position size based on risk parameters
        
        Args:
            capital: Available capital
            entry_price: Entry price
            stop_loss_price: Stop loss price (optional)
            
        Returns:
            Number of shares/units to buy
        """
        # Basic position sizing
        max_position_value = capital * self.max_position_size
        position_size = int(max_position_value / entry_price)
        
        # Adjust for stop loss if provided
        if stop_loss_price and stop_loss_price < entry_price:
            risk_per_unit = entry_price - stop_loss_price
            max_risk = capital * self.max_risk_per_trade
            risk_adjusted_size = int(max_risk / risk_per_unit)
            position_size = min(position_size, risk_adjusted_size)
        
        return max(1, position_size)
    
    def calculate_stop_loss(
        self,
        entry_price: float,
        atr: Optional[float] = None,
        atr_multiplier: float = 2.0,
        percentage: float = 0.05
    ) -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price
            atr: Average True Range value (optional)
            atr_multiplier: Multiplier for ATR-based stop loss
            percentage: Stop loss percentage if ATR not provided
            
        Returns:
            Stop loss price
        """
        if atr:
            # ATR-based stop loss
            stop_loss = entry_price - (atr * atr_multiplier)
        else:
            # Percentage-based stop loss
            stop_loss = entry_price * (1 - percentage)
        
        return stop_loss
    
    def calculate_take_profit(
        self,
        entry_price: float,
        stop_loss_price: float,
        risk_reward_ratio: float = 2.0
    ) -> float:
        """
        Calculate take profit price based on risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss_price: Stop loss price
            risk_reward_ratio: Desired risk-reward ratio
            
        Returns:
            Take profit price
        """
        risk = entry_price - stop_loss_price
        reward = risk * risk_reward_ratio
        take_profit = entry_price + reward
        
        return take_profit
    
    def check_drawdown(self, equity_curve: list) -> bool:
        """
        Check if current drawdown exceeds maximum allowed
        
        Args:
            equity_curve: List of equity values
            
        Returns:
            True if drawdown is within limits, False otherwise
        """
        if not equity_curve:
            return True
        
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        current_drawdown = abs(drawdown.iloc[-1])
        
        return current_drawdown < self.max_drawdown
    
    def calculate_kelly_criterion(
        self,
        win_rate: float,
        avg_win: float,
        avg_loss: float
    ) -> float:
        """
        Calculate optimal position size using Kelly Criterion
        
        Args:
            win_rate: Win rate (0-1)
            avg_win: Average winning trade return
            avg_loss: Average losing trade return (positive value)
            
        Returns:
            Optimal position size fraction (0-1)
        """
        if avg_loss == 0:
            return 0
        
        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio
        
        # Use half-Kelly for more conservative sizing
        kelly = max(0, min(kelly * 0.5, self.max_position_size))
        
        return kelly
