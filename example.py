"""
Quick Start Example
This script demonstrates how to run a simple backtest
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import project modules
from strategies.ma_crossover import MovingAverageCrossover
from backtesting.backtester import Backtester


def generate_sample_data(days=365):
    """
    Generate sample OHLCV data for testing
    This is useful when you don't have access to real market data yet
    """
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    
    # Generate synthetic price data with trend and noise
    base_price = 100
    trend = np.linspace(0, 50, days)
    noise = np.random.randn(days) * 5
    close = base_price + trend + noise
    
    data = pd.DataFrame({
        'open': close + np.random.randn(days) * 2,
        'high': close + abs(np.random.randn(days) * 3),
        'low': close - abs(np.random.randn(days) * 3),
        'close': close,
        'volume': np.random.randint(1000, 10000, days)
    }, index=dates)
    
    # Ensure high is highest and low is lowest
    data['high'] = data[['open', 'high', 'close']].max(axis=1)
    data['low'] = data[['open', 'low', 'close']].min(axis=1)
    
    return data


def main():
    """Run a simple backtest example"""
    print("=" * 60)
    print("Algorithmic Trading System - Quick Start Example")
    print("=" * 60)
    print()
    
    # Generate sample data
    print("1. Generating sample market data...")
    data = generate_sample_data(days=365)
    print(f"   Generated {len(data)} days of data")
    print()
    
    # Create strategy
    print("2. Initializing Moving Average Crossover strategy...")
    strategy = MovingAverageCrossover(params={
        'fast_period': 20,
        'slow_period': 50
    })
    print(f"   Strategy: {strategy.name}")
    print(f"   Parameters: {strategy.params}")
    print()
    
    # Create backtester
    print("3. Setting up backtester...")
    backtester = Backtester(
        strategy=strategy,
        initial_capital=10000.0,
        commission=0.001
    )
    print(f"   Initial capital: $10,000")
    print(f"   Commission: 0.1%")
    print()
    
    # Run backtest
    print("4. Running backtest...")
    data_with_signals = backtester.run(data)
    print()
    
    # Display results
    print("5. Results:")
    backtester.print_results()
    
    # Show sample of data with signals
    print("\n6. Sample of trading signals:")
    # Get the data with signals from the backtester
    signals_df = strategy.generate_signals(strategy.calculate_indicators(data.copy()))
    signals = signals_df[signals_df['signal'] != 0][['close', 'signal']].head(10)
    if len(signals) > 0:
        print(signals)
    else:
        print("   No signals generated")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("\nNext steps:")
    print("- Try different strategy parameters")
    print("- Test other strategies (RSI, MACD)")
    print("- Use real market data with data_fetcher")
    print("- Add visualization with --plot flag")
    print("=" * 60)


if __name__ == '__main__':
    main()
