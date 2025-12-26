"""
Backtest Service - Single Responsibility Principle
Handles backtest execution logic
"""
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy.orm import Session

from backtesting.backtester import Backtester, MultiSymbolBacktester
from api.services.strategy_registry import registry
from utils.data_fetcher import DataFetcher


class BacktestService:
    """
    Service for executing backtests.
    Follows Dependency Inversion Principle - depends on abstractions (Session, registry)
    """
    
    def __init__(self, db_session: Session, data_fetcher: DataFetcher):
        self.db = db_session
        self.data_fetcher = data_fetcher
    
    def execute_single_symbol_backtest(
        self,
        strategy_id: str,
        symbol: str,
        days: int,
        initial_capital: float,
        commission: float,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute backtest for single-symbol strategy"""
        
        # Get strategy info
        strategy_info = registry.get_strategy_info(strategy_id)
        strategy_class = strategy_info['class']
        
        # Merge params
        strategy_params = {**strategy_info['params'], **(params or {})}
        
        # Fetch data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data = self.data_fetcher.fetch_from_db(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date
        )
        
        if data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        # Create and run strategy
        strategy = strategy_class(params=strategy_params)
        
        backtester = Backtester(
            strategy=strategy,
            initial_capital=initial_capital,
            commission=commission
        )
        
        results = backtester.run(data)
        
        # Transform trades to frontend format
        results['trades'] = self._transform_trades(results.get('trades', []))
        
        return results
    
    def execute_multi_symbol_backtest(
        self,
        strategy_id: str,
        symbols: list,
        days: int,
        initial_capital: float,
        commission: float,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute backtest for multi-symbol strategy"""
        
        # Get strategy info
        strategy_info = registry.get_strategy_info(strategy_id)
        strategy_class = strategy_info['class']
        
        # Merge params
        strategy_params = {**strategy_info['params'], **(params or {})}
        
        # Fetch data for all symbols
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        data_dict = {}
        for symbol in symbols:
            data = self.data_fetcher.fetch_from_db(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date
            )
            if not data.empty:
                data_dict[symbol] = data
        
        if len(data_dict) != len(symbols):
            raise ValueError(f"Could not fetch data for all symbols")
        
        # Align data (inner join on timestamps)
        aligned_data = self._align_dataframes(data_dict)
        
        # Create and run strategy
        strategy = strategy_class(symbols=symbols, params=strategy_params)
        
        backtester = MultiSymbolBacktester(
            strategy=strategy,
            initial_capital=initial_capital,
            commission=commission
        )
        
        results = backtester.run(aligned_data)
        
        # Transform trades to frontend format
        results['trades'] = self._transform_trades(results.get('trades', []))
        
        return results
    
    def _transform_trades(self, trades: list) -> list:
        """Transform backend trade format to frontend format"""
        if not trades:
            return []
        
        # Group trades into entry/exit pairs
        formatted_trades = []
        
        # Separate by symbol
        trades_by_symbol = {}
        for trade in trades:
            symbol = trade.get('symbol', 'UNKNOWN')
            if symbol not in trades_by_symbol:
                trades_by_symbol[symbol] = []
            trades_by_symbol[symbol].append(trade)
        
        # Process each symbol's trades
        for symbol, symbol_trades in trades_by_symbol.items():
            i = 0
            while i < len(symbol_trades) - 1:
                entry = symbol_trades[i]
                exit_trade = symbol_trades[i + 1]
                
                # Calculate return
                entry_price = entry.get('price', 0)
                exit_price = exit_trade.get('price', 0)
                
                if entry.get('type') in ['BUY', 'LONG']:
                    return_pct = ((exit_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
                    trade_type = 'LONG'
                else:  # SHORT
                    return_pct = ((entry_price - exit_price) / entry_price * 100) if entry_price > 0 else 0
                    trade_type = 'SHORT'
                
                formatted_trades.append({
                    'symbol': symbol,
                    'trade_type': trade_type,
                    'entry_date': entry.get('date'),
                    'exit_date': exit_trade.get('date'),
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'return_pct': return_pct,
                    'shares': entry.get('shares', 0)
                })
                
                i += 2
        
        return formatted_trades
    
    def _align_dataframes(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Align multiple dataframes on timestamp"""
        if not data_dict:
            return {}
        
        # Get common timestamps
        common_index = None
        for df in data_dict.values():
            if common_index is None:
                common_index = df.index
            else:
                common_index = common_index.intersection(df.index)
        
        # Filter all dataframes to common timestamps
        return {
            symbol: df.loc[common_index]
            for symbol, df in data_dict.items()
        }
