"""
Pair Trading Strategy

Statistical arbitrage strategy that trades two correlated assets.
Takes long/short positions when the price spread deviates from its mean,
betting on mean reversion.

Theory:
- Two assets with high correlation should maintain a stable price relationship
- When spread widens: short the expensive asset, long the cheap one
- When spread narrows: close positions for profit
"""

from typing import Dict, List, Optional, Any
import pandas as pd
import numpy as np
from datetime import datetime
from strategies.base_multi_symbol_strategy import MultiSymbolStrategy
from utils.pair_data_fetcher import PairDataFetcher


class PairTradingStrategy(MultiSymbolStrategy):
    """
    Pair trading strategy using z-score of price spread.
    
    Default Parameters:
        - window: 20 (lookback period for calculating mean and std of spread)
        - entry_threshold: 2.0 (z-score threshold to enter positions)
        - exit_threshold: 0.5 (z-score threshold to exit positions)
        - hedge_ratio: 1.0 (units of symbol_b per unit of symbol_a)
        - use_dynamic_hedge: False (calculate hedge ratio dynamically)
    
    Signals:
        - symbol_a = 1, symbol_b = -1: Buy A, Sell B (spread too low)
        - symbol_a = -1, symbol_b = 1: Sell A, Buy B (spread too high)
        - Both = 0: Exit positions (spread normalized)
    """
    
    def __init__(self, symbols: List[str], params: Optional[Dict[str, Any]] = None):
        """
        Initialize pair trading strategy.
        
        Args:
            symbols: List of exactly 2 symbols [symbol_a, symbol_b]
            params: Strategy parameters
        """
        if len(symbols) != 2:
            raise ValueError("Pair trading requires exactly 2 symbols")
        
        super().__init__(name="Pair Trading", symbols=symbols, params=params)
        
        # Set default parameters
        self.params.setdefault('window', 20)
        self.params.setdefault('entry_threshold', 2.0)
        self.params.setdefault('exit_threshold', 0.5)
        self.params.setdefault('hedge_ratio', 1.0)
        self.params.setdefault('use_dynamic_hedge', False)
        
        self.pair_fetcher = PairDataFetcher()
        self.symbol_a = symbols[0]
        self.symbol_b = symbols[1]
    
    def fetch_multi_symbol_data(
        self,
        symbols: List[str],
        start_date: Optional[str] = None,
        end_date: Optional[datetime] = None,
        timeframe: str = '1d'
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch and align data for the pair.
        
        Returns:
            Dictionary with symbol_a and symbol_b DataFrames
        """
        return self.pair_fetcher.fetch_pair_data(
            symbol_a=symbols[0],
            symbol_b=symbols[1],
            start_date=start_date,
            end_date=end_date,
            timeframe=timeframe
        )
    
    def calculate_multi_symbol_indicators(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Calculate spread and z-score indicators.
        
        Adds columns to both DataFrames:
        - spread: Price difference (price_a - hedge_ratio * price_b)
        - spread_mean: Rolling mean of spread
        - spread_std: Rolling standard deviation of spread
        - z_score: Standardized spread deviation
        """
        data_a = data_dict[self.symbol_a].copy()
        data_b = data_dict[self.symbol_b].copy()
        
        window = self.params['window']
        hedge_ratio = self.params['hedge_ratio']
        
        # Calculate dynamic hedge ratio if enabled
        if self.params['use_dynamic_hedge']:
            hedge_ratio = self.pair_fetcher.calculate_hedge_ratio(
                data_a, data_b, window=window
            )
            print(f"📊 Dynamic hedge ratio calculated: {hedge_ratio:.4f}")
        
        # Calculate spread (price difference adjusted by hedge ratio)
        spread = data_a['close'] - (hedge_ratio * data_b['close'])
        
        # Calculate rolling statistics of spread
        spread_mean = spread.rolling(window=window).mean()
        spread_std = spread.rolling(window=window).std()
        
        # Calculate z-score (how many standard deviations from mean)
        z_score = (spread - spread_mean) / spread_std
        
        # Add indicators to both dataframes (they share the same spread)
        for symbol in [self.symbol_a, self.symbol_b]:
            data_dict[symbol]['spread'] = spread
            data_dict[symbol]['spread_mean'] = spread_mean
            data_dict[symbol]['spread_std'] = spread_std
            data_dict[symbol]['z_score'] = z_score
            data_dict[symbol]['hedge_ratio'] = hedge_ratio
        
        return data_dict
    
    def generate_multi_symbol_signals(
        self,
        data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, pd.DataFrame]:
        """
        Generate trading signals based on z-score.
        
        Entry logic:
        - z_score < -entry_threshold: Spread too LOW → Buy A, Sell B
        - z_score > entry_threshold: Spread too HIGH → Sell A, Buy B
        
        Exit logic:
        - abs(z_score) < exit_threshold: Spread normalized → Close positions
        
        Returns signals for both symbols:
        - symbol_a: 1 (long), -1 (short), 0 (hold)
        - symbol_b: -1 (short), 1 (long), 0 (hold) [opposite of symbol_a]
        """
        data_a = data_dict[self.symbol_a].copy()
        data_b = data_dict[self.symbol_b].copy()
        
        entry_threshold = self.params['entry_threshold']
        exit_threshold = self.params['exit_threshold']
        
        # Initialize signal columns
        data_a['signal'] = 0
        data_b['signal'] = 0
        
        # Track current position state
        position_state = 0  # 0 = flat, 1 = long spread, -1 = short spread
        
        for i in range(len(data_a)):
            z_score = data_a['z_score'].iloc[i]
            
            # Skip if z_score is NaN (not enough data yet)
            if pd.isna(z_score):
                continue
            
            # Entry signals (when flat)
            if position_state == 0:
                # Spread too low: buy spread (long A, short B)
                if z_score < -entry_threshold:
                    data_a.iloc[i, data_a.columns.get_loc('signal')] = 1
                    data_b.iloc[i, data_b.columns.get_loc('signal')] = -1
                    position_state = 1
                
                # Spread too high: short spread (short A, long B)
                elif z_score > entry_threshold:
                    data_a.iloc[i, data_a.columns.get_loc('signal')] = -1
                    data_b.iloc[i, data_b.columns.get_loc('signal')] = 1
                    position_state = -1
            
            # Exit signals (when in position)
            else:
                # Spread normalized: close positions
                if abs(z_score) < exit_threshold:
                    # Close long spread position
                    if position_state == 1:
                        data_a.iloc[i, data_a.columns.get_loc('signal')] = -1
                        data_b.iloc[i, data_b.columns.get_loc('signal')] = 1
                    # Close short spread position
                    elif position_state == -1:
                        data_a.iloc[i, data_a.columns.get_loc('signal')] = 1
                        data_b.iloc[i, data_b.columns.get_loc('signal')] = -1
                    
                    position_state = 0
        
        data_dict[self.symbol_a] = data_a
        data_dict[self.symbol_b] = data_b
        
        return data_dict
    
    def validate_params(self) -> bool:
        """Validate pair trading parameters."""
        if not super().validate_params():
            return False
        
        window = self.params.get('window', 0)
        if window < 5:
            raise ValueError("window must be at least 5")
        
        entry_threshold = self.params.get('entry_threshold', 0)
        if entry_threshold <= 0:
            raise ValueError("entry_threshold must be positive")
        
        exit_threshold = self.params.get('exit_threshold', 0)
        if exit_threshold < 0:
            raise ValueError("exit_threshold must be non-negative")
        
        if exit_threshold >= entry_threshold:
            raise ValueError("exit_threshold must be less than entry_threshold")
        
        hedge_ratio = self.params.get('hedge_ratio', 0)
        if hedge_ratio <= 0:
            raise ValueError("hedge_ratio must be positive")
        
        return True
    
    def get_strategy_info(self) -> Dict[str, Any]:
        """Get strategy information and current state."""
        return {
            'name': self.name,
            'type': 'pair_trading',
            'symbols': self.symbols,
            'symbol_a': self.symbol_a,
            'symbol_b': self.symbol_b,
            'params': self.params,
            'positions': self.positions_by_symbol,
            'description': f"Pair trading between {self.symbol_a} and {self.symbol_b}"
        }
