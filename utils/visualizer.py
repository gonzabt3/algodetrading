"""
Visualization utilities for backtesting results
"""
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any
import numpy as np


def plot_results(data: pd.DataFrame, strategy, results: Dict[str, Any]):
    """
    Plot backtesting results
    
    Args:
        data: DataFrame with market data and indicators
        strategy: Strategy instance
        results: Dictionary with backtest results
    """
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    
    # Plot 1: Price and indicators
    ax1 = axes[0]
    ax1.plot(data.index, data['close'], label='Close Price', linewidth=1)
    
    # Plot strategy-specific indicators
    if hasattr(strategy, 'params'):
        if strategy.name == 'MA Crossover':
            ax1.plot(data.index, data['ma_fast'], label=f"MA {strategy.params['fast_period']}", alpha=0.7)
            ax1.plot(data.index, data['ma_slow'], label=f"MA {strategy.params['slow_period']}", alpha=0.7)
        elif strategy.name == 'MACD Strategy':
            # MACD will be plotted in a separate panel
            pass
    
    # Plot buy/sell signals
    buy_signals = data[data['signal'] == 1]
    sell_signals = data[data['signal'] == -1]
    
    ax1.scatter(buy_signals.index, buy_signals['close'], 
               marker='^', color='green', s=100, label='Buy', zorder=5)
    ax1.scatter(sell_signals.index, sell_signals['close'], 
               marker='v', color='red', s=100, label='Sell', zorder=5)
    
    ax1.set_ylabel('Price')
    ax1.set_title(f'{strategy.name} - Backtest Results')
    ax1.legend(loc='best')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Strategy-specific indicator
    ax2 = axes[1]
    
    if strategy.name == 'RSI Strategy':
        ax2.plot(data.index, data['rsi'], label='RSI', color='purple')
        ax2.axhline(y=strategy.params['overbought'], color='r', linestyle='--', alpha=0.5, label='Overbought')
        ax2.axhline(y=strategy.params['oversold'], color='g', linestyle='--', alpha=0.5, label='Oversold')
        ax2.axhline(y=50, color='gray', linestyle='-', alpha=0.3)
        ax2.set_ylabel('RSI')
        ax2.set_ylim([0, 100])
    elif strategy.name == 'MACD Strategy':
        ax2.plot(data.index, data['macd'], label='MACD', color='blue')
        ax2.plot(data.index, data['macd_signal'], label='Signal', color='red')
        ax2.bar(data.index, data['macd_histogram'], label='Histogram', alpha=0.3)
        ax2.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        ax2.set_ylabel('MACD')
    else:
        # For MA Crossover, show volume
        ax2.bar(data.index, data['volume'], label='Volume', alpha=0.3)
        ax2.set_ylabel('Volume')
    
    ax2.legend(loc='best')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Equity curve
    ax3 = axes[2]
    equity_curve = results.get('equity_curve', [])
    if equity_curve:
        ax3.plot(data.index[:len(equity_curve)], equity_curve, 
                label='Equity', color='green', linewidth=2)
        ax3.axhline(y=results['initial_capital'], color='gray', 
                   linestyle='--', alpha=0.5, label='Initial Capital')
        ax3.set_ylabel('Equity ($)')
        ax3.legend(loc='best')
        ax3.grid(True, alpha=0.3)
    
    ax3.set_xlabel('Date')
    
    plt.tight_layout()
    
    # Add performance metrics text
    metrics_text = f"""
    Total Return: {results['total_return']:.2f}%
    Sharpe Ratio: {results['sharpe_ratio']:.2f}
    Max Drawdown: {results['max_drawdown']:.2f}%
    Win Rate: {results['win_rate']:.2f}%
    Total Trades: {results['total_trades']}
    """
    
    fig.text(0.02, 0.98, metrics_text, transform=fig.transFigure,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.show()


def plot_equity_curve(equity_curve: list, initial_capital: float):
    """
    Plot equity curve separately
    
    Args:
        equity_curve: List of equity values
        initial_capital: Initial capital value
    """
    plt.figure(figsize=(12, 6))
    plt.plot(equity_curve, linewidth=2, label='Equity')
    plt.axhline(y=initial_capital, color='r', linestyle='--', 
               alpha=0.5, label='Initial Capital')
    plt.xlabel('Time')
    plt.ylabel('Equity ($)')
    plt.title('Equity Curve')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
