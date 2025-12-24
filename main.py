"""
Main entry point for the algorithmic trading system
"""
import argparse
import logging
from datetime import datetime, timedelta
import pandas as pd

from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from backtesting.backtester import Backtester
from utils.data_fetcher import DataFetcher
from utils.visualizer import plot_results


def setup_logging():
    """Configure logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/trading.log'),
            logging.StreamHandler()
        ]
    )


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Algorithmic Trading System')
    parser.add_argument(
        '--strategy',
        type=str,
        choices=['ma_crossover', 'rsi', 'macd', 'bollinger_bands'],
        default='ma_crossover',
        help='Trading strategy to use'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        default='BTC/USDT',
        help='Trading symbol (e.g., BTC/USDT)'
    )
    parser.add_argument(
        '--timeframe',
        type=str,
        default='1d',
        help='Timeframe (e.g., 1m, 5m, 1h, 1d)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=365,
        help='Number of days of historical data'
    )
    parser.add_argument(
        '--capital',
        type=float,
        default=10000.0,
        help='Initial capital'
    )
    parser.add_argument(
        '--plot',
        action='store_true',
        help='Plot results'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting algorithmic trading system")
    logger.info(f"Strategy: {args.strategy}")
    logger.info(f"Symbol: {args.symbol}")
    logger.info(f"Timeframe: {args.timeframe}")
    
    # Initialize strategy
    if args.strategy == 'ma_crossover':
        strategy = MovingAverageCrossover(
            params={'fast_period': 20, 'slow_period': 50}
        )
    elif args.strategy == 'rsi':
        strategy = RSIStrategy(
            params={'period': 14, 'oversold': 30, 'overbought': 70}
        )
    elif args.strategy == 'macd':
        strategy = MACDStrategy(
            params={'fast': 12, 'slow': 26, 'signal': 9}
        )
    elif args.strategy == 'bollinger_bands':
        strategy = BollingerBandsStrategy(
            params={'period': 20, 'std_dev': 2.0}
        )
    else:
        logger.error(f"Unknown strategy: {args.strategy}")
        return
    
    # Fetch data
    logger.info("Fetching market data...")
    data_fetcher = DataFetcher()
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days)
        
        # Fetch historical data
        data = data_fetcher.fetch_ohlcv(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=start_date,
            end_date=end_date
        )
        
        if data is None or len(data) == 0:
            logger.error("No data fetched")
            return
        
        logger.info(f"Fetched {len(data)} candles")
        
        # Run backtest
        logger.info("Running backtest...")
        backtester = Backtester(
            strategy=strategy,
            initial_capital=args.capital,
            commission=0.001  # 0.1% commission
        )
        
        results = backtester.run(data)
        backtester.print_results()
        
        # Plot results if requested
        if args.plot:
            logger.info("Generating plots...")
            plot_results(data, strategy, results)
        
        logger.info("Done!")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == '__main__':
    main()
