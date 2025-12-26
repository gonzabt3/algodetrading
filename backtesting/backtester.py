"""
Backtesting Engine
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from datetime import datetime
import logging

from strategies.base_strategy import BaseStrategy
from utils.results_logger import ResultsLogger


class Backtester:
    """
    Backtesting engine for trading strategies
    """
    
    def __init__(
        self,
        strategy: BaseStrategy,
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        save_results: bool = False
    ):
        """
        Initialize backtester
        
        Args:
            strategy: Trading strategy instance
            initial_capital: Starting capital
            commission: Commission rate (e.g., 0.001 = 0.1%)
            slippage: Slippage rate
            save_results: Si True, guarda resultados automáticamente
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.results = {}
        self.save_results = save_results
        self.results_logger = ResultsLogger() if save_results else None
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def run(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        Run backtest on historical data
        
        Args:
            data: DataFrame with OHLCV data (columns: open, high, low, close, volume)
            
        Returns:
            Dictionary with backtest results
        """
        self.logger.info(f"Starting backtest for {self.strategy.name}")
        
        # Calculate indicators and generate signals
        data = self.strategy.calculate_indicators(data.copy())
        data = self.strategy.generate_signals(data)
        
        # Initialize tracking variables
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        # Simulate trading
        for i in range(len(data)):
            row = data.iloc[i]
            signal = row.get('signal', 0)
            price = float(row['close'])  # Convert to native Python float
            
            # Buy signal
            if signal == 1 and position == 0:
                shares = int(capital / (price * (1 + self.commission + self.slippage)))
                if shares > 0:
                    cost = shares * price * (1 + self.commission + self.slippage)
                    capital -= cost
                    position = shares
                    trades.append({
                        'type': 'BUY',
                        'date': row.name,
                        'price': float(price),
                        'shares': int(shares),
                        'capital': float(capital)
                    })
                    self.logger.info(f"BUY: {shares} shares at {price}")
            
            # Sell signal
            elif signal == -1 and position > 0:
                revenue = position * price * (1 - self.commission - self.slippage)
                capital += revenue
                trades.append({
                    'type': 'SELL',
                    'date': row.name,
                    'price': float(price),
                    'shares': int(position),
                    'capital': float(capital)
                })
                self.logger.info(f"SELL: {position} shares at {price}")
                position = 0
            
            # Calculate current equity
            current_equity = capital + (position * price if position > 0 else 0)
            equity_curve.append(current_equity)
        
        # Close any remaining position
        if position > 0:
            final_price = float(data.iloc[-1]['close'])
            revenue = position * final_price * (1 - self.commission - self.slippage)
            capital += revenue
            trades.append({
                'type': 'SELL',  # Changed from 'SELL (CLOSE)' to fit in DB
                'date': data.index[-1],
                'price': float(final_price),
                'shares': int(position),
                'capital': float(capital)
            })
        
        # Calculate metrics
        self.results = self._calculate_metrics(
            equity_curve,
            trades,
            data
        )
        
        self.logger.info(f"Backtest completed. Final capital: {capital:.2f}")
        return self.results
    
    def _calculate_metrics(
        self,
        equity_curve: list,
        trades: list,
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Calculate performance metrics
        
        Args:
            equity_curve: List of equity values
            trades: List of trades
            data: Original market data
            
        Returns:
            Dictionary with performance metrics
        """
        final_capital = equity_curve[-1] if equity_curve else self.initial_capital
        total_return = (final_capital - self.initial_capital) / self.initial_capital * 100
        
        # Calculate returns
        returns = pd.Series(equity_curve).pct_change().dropna()
        
        # Sharpe ratio (annualized)
        sharpe_ratio = 0
        if len(returns) > 0 and returns.std() != 0:
            sharpe_ratio = np.sqrt(252) * (returns.mean() / returns.std())
        
        # Maximum drawdown
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Win rate
        winning_trades = sum(1 for i in range(0, len(trades) - 1, 2) 
                           if i + 1 < len(trades) and 
                           trades[i+1]['capital'] > trades[i]['capital'])
        total_trade_pairs = len(trades) // 2
        win_rate = (winning_trades / total_trade_pairs * 100) if total_trade_pairs > 0 else 0
        
        # Convert numpy types to native Python types
        def to_python_type(value):
            if isinstance(value, (np.integer, np.floating)):
                return float(value)
            if isinstance(value, np.ndarray):
                return value.tolist()
            return value
        
        # Preparar datos de velas con indicadores para el gráfico
        chart_data = []
        
        # Usar el DataFrame que ya tiene los indicadores calculados
        # Filtrar solo las filas donde las MAs tienen valores válidos (después del período de warm-up)
        display_data = data.dropna(subset=[col for col in data.columns if col not in ['open', 'high', 'low', 'close', 'volume', 'signal']])
        
        # Debug: imprimir columnas disponibles
        print(f"🔍 Columnas en el DataFrame: {list(data.columns)}")
        print(f"🔍 Filas totales: {len(data)}, Filas con indicadores válidos: {len(display_data)}")
        if len(display_data) > 0:
            print(f"🔍 Primera fila con MAs: {display_data.iloc[0].to_dict()}")
        
        for idx, row in display_data.iterrows():
            point = {
                'timestamp': idx.isoformat() if hasattr(idx, 'isoformat') else str(idx),
                'open': float(row['open']) if 'open' in row and not pd.isna(row['open']) else None,
                'high': float(row['high']) if 'high' in row and not pd.isna(row['high']) else None,
                'low': float(row['low']) if 'low' in row and not pd.isna(row['low']) else None,
                'close': float(row['close']) if 'close' in row and not pd.isna(row['close']) else None,
                'volume': float(row['volume']) if 'volume' in row and not pd.isna(row['volume']) else None,
            }
            
            # Agregar indicadores técnicos (ahora todos deberían tener valores)
            for col in row.index:
                if col not in ['open', 'high', 'low', 'close', 'volume', 'signal']:
                    # Ya no filtramos NaN porque dropna() ya lo hizo
                    point[col] = float(row[col])
            
            chart_data.append(point)
        
        return {
            'initial_capital': float(self.initial_capital),
            'final_capital': float(final_capital),
            'total_return': float(total_return),
            'sharpe_ratio': float(sharpe_ratio) if not np.isnan(sharpe_ratio) else 0.0,
            'max_drawdown': float(max_drawdown) if not np.isnan(max_drawdown) else 0.0,
            'total_trades': int(len(trades)),
            'win_rate': float(win_rate),
            'trades': trades,
            'equity_curve': [float(x) for x in equity_curve],
            'chart_data': chart_data  # Nuevos datos para gráfico de velas
        }
        
        # Guardar resultados si está habilitado
        if self.save_results and self.results_logger:
            symbol = getattr(data, 'symbol', 'UNKNOWN')
            self.results_logger.save_backtest(
                strategy_name=self.strategy.name,
                symbol=symbol,
                results=metrics,
                params=self.strategy.params
            )
    
    def print_results(self):
        """Print backtest results"""
        if not self.results:
            print("No results available. Run backtest first.")
            return
        
        print("\n" + "="*50)
        print(f"Backtest Results for {self.strategy.name}")
        print("="*50)
        print(f"Initial Capital: ${self.results['initial_capital']:,.2f}")
        print(f"Final Capital: ${self.results['final_capital']:,.2f}")
        print(f"Total Return: {self.results['total_return']:.2f}%")
        print(f"Sharpe Ratio: {self.results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {self.results['max_drawdown']:.2f}%")
        print(f"Total Trades: {self.results['total_trades']}")
        print(f"Win Rate: {self.results['win_rate']:.2f}%")
        print("="*50 + "\n")
