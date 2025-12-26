"""
Strategy Registry Service - Single Responsibility Principle
Manages strategy registration and retrieval
"""
from typing import Dict, Type, Any, Optional
from strategies.base_strategy import BaseStrategy
from strategies.base_multi_symbol_strategy import MultiSymbolStrategy


class StrategyRegistry:
    """
    Centralized registry for trading strategies.
    Follows Open/Closed Principle - extend by registration, not modification.
    """
    
    def __init__(self):
        self._strategies: Dict[str, Dict[str, Any]] = {}
    
    def register(
        self,
        strategy_id: str,
        strategy_class: Type[BaseStrategy],
        name: str,
        description: str,
        default_params: Dict[str, Any],
        strategy_type: str = 'single_symbol',
        default_symbols: Optional[list] = None
    ) -> None:
        """
        Register a new strategy.
        
        Args:
            strategy_id: Unique identifier
            strategy_class: Strategy class (must inherit from BaseStrategy)
            name: Display name
            description: Strategy description
            default_params: Default parameter values
            strategy_type: 'single_symbol' or 'multi_symbol'
            default_symbols: Default symbols for multi-symbol strategies
        """
        if not issubclass(strategy_class, BaseStrategy):
            raise ValueError(f"{strategy_class} must inherit from BaseStrategy")
        
        self._strategies[strategy_id] = {
            'class': strategy_class,
            'name': name,
            'description': description,
            'params': default_params,
            'type': strategy_type,
            'default_symbols': default_symbols or []
        }
    
    def get_strategy_info(self, strategy_id: str) -> Dict[str, Any]:
        """Get strategy metadata"""
        if strategy_id not in self._strategies:
            raise KeyError(f"Strategy '{strategy_id}' not found")
        return self._strategies[strategy_id].copy()
    
    def get_strategy_class(self, strategy_id: str) -> Type[BaseStrategy]:
        """Get strategy class"""
        return self.get_strategy_info(strategy_id)['class']
    
    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all registered strategies"""
        return {
            strategy_id: {k: v for k, v in info.items() if k != 'class'}
            for strategy_id, info in self._strategies.items()
        }
    
    def exists(self, strategy_id: str) -> bool:
        """Check if strategy exists"""
        return strategy_id in self._strategies


# Global registry instance
registry = StrategyRegistry()


def register_default_strategies():
    """Register all default strategies - called at startup"""
    from strategies.ma_crossover import MovingAverageCrossover
    from strategies.rsi_strategy import RSIStrategy
    from strategies.macd_strategy import MACDStrategy
    from strategies.bollinger_bands import BollingerBandsStrategy
    from strategies.mean_reversion import MeanReversionStrategy
    from strategies.multi_indicator import MultiIndicatorStrategy
    from strategies.pair_trading import PairTradingStrategy
    
    registry.register(
        'ma_crossover',
        MovingAverageCrossover,
        'MA Crossover',
        'Moving Average Crossover - Buy when fast MA crosses above slow MA',
        {'fast_period': 20, 'slow_period': 50}
    )
    
    registry.register(
        'rsi',
        RSIStrategy,
        'RSI Strategy',
        'RSI-based mean reversion - Buy oversold, sell overbought',
        {'period': 14, 'oversold': 30, 'overbought': 70}
    )
    
    registry.register(
        'macd',
        MACDStrategy,
        'MACD Strategy',
        'MACD momentum strategy - Buy on bullish crossover',
        {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
    )
    
    registry.register(
        'bollinger_bands',
        BollingerBandsStrategy,
        'Bollinger Bands',
        'Volatility-based strategy - Buy at lower band, sell at upper',
        {'period': 20, 'std_dev': 2}
    )
    
    registry.register(
        'mean_reversion',
        MeanReversionStrategy,
        'Mean Reversion',
        'Z-score based mean reversion',
        {'period': 20, 'entry_threshold': 2, 'exit_threshold': 0}
    )
    
    registry.register(
        'multi_indicator',
        MultiIndicatorStrategy,
        'Multi-Indicator',
        'Combines RSI + MACD + Volume for confirmation',
        {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_period': 20
        }
    )
    
    registry.register(
        'pair_trading',
        PairTradingStrategy,
        'Pair Trading',
        'Statistical arbitrage between two correlated assets',
        {
            'window': 20,
            'entry_threshold': 2.0,
            'exit_threshold': 0.5,
            'hedge_ratio': 1.0,
            'use_dynamic_hedge': False
        },
        strategy_type='multi_symbol',
        default_symbols=['BTC/USDT', 'ETH/USDT']
    )
