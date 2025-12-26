"""
Tests for Pair Trading Strategy
"""
import unittest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from strategies.pair_trading import PairTradingStrategy
from utils.pair_data_fetcher import PairDataFetcher
from backtesting.backtester import MultiSymbolBacktester


class TestPairTradingStrategy(unittest.TestCase):
    """Test suite for pair trading strategy"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create synthetic data for two correlated assets
        np.random.seed(42)
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        
        # Asset A: base price around 100
        prices_a = 100 + np.cumsum(np.random.randn(100) * 2)
        
        # Asset B: correlated with A (spread oscillates)
        spread = np.sin(np.linspace(0, 4*np.pi, 100)) * 10
        prices_b = prices_a * 0.5 + spread
        
        self.data_a = pd.DataFrame({
            'open': prices_a * 0.99,
            'high': prices_a * 1.01,
            'low': prices_a * 0.98,
            'close': prices_a,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.data_b = pd.DataFrame({
            'open': prices_b * 0.99,
            'high': prices_b * 1.01,
            'low': prices_b * 0.98,
            'close': prices_b,
            'volume': np.random.randint(1000, 10000, 100)
        }, index=dates)
        
        self.symbols = ['TEST_A', 'TEST_B']
    
    def test_strategy_initialization(self):
        """Test strategy initialization"""
        strategy = PairTradingStrategy(
            symbols=self.symbols,
            params={
                'window': 20,
                'entry_threshold': 2.0,
                'exit_threshold': 0.5,
                'hedge_ratio': 1.0
            }
        )
        
        self.assertEqual(strategy.name, "Pair Trading")
        self.assertEqual(strategy.symbol_a, 'TEST_A')
        self.assertEqual(strategy.symbol_b, 'TEST_B')
        self.assertEqual(strategy.params['window'], 20)
    
    def test_strategy_requires_two_symbols(self):
        """Test that strategy requires exactly 2 symbols"""
        with self.assertRaises(ValueError):
            PairTradingStrategy(symbols=['TEST_A'])
        
        with self.assertRaises(ValueError):
            PairTradingStrategy(symbols=['TEST_A', 'TEST_B', 'TEST_C'])
    
    def test_calculate_indicators(self):
        """Test indicator calculation (spread, z-score)"""
        strategy = PairTradingStrategy(
            symbols=self.symbols,
            params={'window': 20, 'hedge_ratio': 1.0}
        )
        
        data_dict = {
            'TEST_A': self.data_a.copy(),
            'TEST_B': self.data_b.copy()
        }
        
        result = strategy.calculate_multi_symbol_indicators(data_dict)
        
        # Check that indicators were added
        self.assertIn('spread', result['TEST_A'].columns)
        self.assertIn('z_score', result['TEST_A'].columns)
        self.assertIn('spread_mean', result['TEST_A'].columns)
        self.assertIn('spread_std', result['TEST_A'].columns)
        
        # Check that both dataframes have same indicators
        self.assertIn('spread', result['TEST_B'].columns)
        
        # Check z-score calculation
        # After window period, z-scores should not all be NaN
        valid_zscores = result['TEST_A']['z_score'].dropna()
        self.assertGreater(len(valid_zscores), 0)
    
    def test_generate_signals(self):
        """Test signal generation"""
        strategy = PairTradingStrategy(
            symbols=self.symbols,
            params={
                'window': 20,
                'entry_threshold': 1.5,
                'exit_threshold': 0.3,
                'hedge_ratio': 1.0
            }
        )
        
        data_dict = {
            'TEST_A': self.data_a.copy(),
            'TEST_B': self.data_b.copy()
        }
        
        # Calculate indicators first
        data_dict = strategy.calculate_multi_symbol_indicators(data_dict)
        
        # Generate signals
        result = strategy.generate_multi_symbol_signals(data_dict)
        
        # Check that signals were added
        self.assertIn('signal', result['TEST_A'].columns)
        self.assertIn('signal', result['TEST_B'].columns)
        
        # Signals should be in {-1, 0, 1}
        unique_signals_a = set(result['TEST_A']['signal'].unique())
        self.assertTrue(unique_signals_a.issubset({-1, 0, 1}))
        
        # Signals for A and B should be opposite when entering positions
        for i in range(len(result['TEST_A'])):
            signal_a = result['TEST_A']['signal'].iloc[i]
            signal_b = result['TEST_B']['signal'].iloc[i]
            
            # If signal_a is non-zero, signal_b should be opposite
            if signal_a != 0:
                self.assertEqual(signal_a, -signal_b, 
                               f"Signals should be opposite at index {i}")
    
    def test_validate_params(self):
        """Test parameter validation"""
        # Valid params
        strategy = PairTradingStrategy(
            symbols=self.symbols,
            params={
                'window': 20,
                'entry_threshold': 2.0,
                'exit_threshold': 0.5,
                'hedge_ratio': 1.0
            }
        )
        self.assertTrue(strategy.validate_params())
        
        # Invalid: window too small
        with self.assertRaises(ValueError):
            strategy = PairTradingStrategy(
                symbols=self.symbols,
                params={'window': 2, 'entry_threshold': 2.0, 'exit_threshold': 0.5}
            )
            strategy.validate_params()
        
        # Invalid: exit >= entry
        with self.assertRaises(ValueError):
            strategy = PairTradingStrategy(
                symbols=self.symbols,
                params={'window': 20, 'entry_threshold': 1.0, 'exit_threshold': 2.0}
            )
            strategy.validate_params()
    
    def test_backtest_execution(self):
        """Test full backtest execution"""
        strategy = PairTradingStrategy(
            symbols=self.symbols,
            params={
                'window': 20,
                'entry_threshold': 1.5,
                'exit_threshold': 0.3,
                'hedge_ratio': 1.0
            }
        )
        
        data_dict = {
            'TEST_A': self.data_a.copy(),
            'TEST_B': self.data_b.copy()
        }
        
        backtester = MultiSymbolBacktester(
            strategy=strategy,
            initial_capital=10000,
            commission=0.001
        )
        
        results = backtester.run(data_dict)
        
        # Check that results contain expected keys
        self.assertIn('initial_capital', results)
        self.assertIn('final_capital', results)
        self.assertIn('total_return', results)
        self.assertIn('trades', results)
        self.assertIn('symbols', results)
        
        # Check symbols
        self.assertEqual(results['symbols'], self.symbols)
        
        # Final capital should be a number
        self.assertIsInstance(results['final_capital'], float)
        
        # Should have some trades
        self.assertGreater(len(results['trades']), 0)
        
        # Trades should have symbol information
        first_trade = results['trades'][0]
        self.assertIn('symbol', first_trade)
        self.assertIn(first_trade['symbol'], self.symbols)


class TestPairDataFetcher(unittest.TestCase):
    """Test suite for pair data fetcher"""
    
    def test_align_dataframes(self):
        """Test dataframe alignment"""
        # Create dataframes with overlapping dates
        dates_a = pd.date_range('2023-01-01', periods=100, freq='D')
        dates_b = pd.date_range('2023-01-05', periods=100, freq='D')  # 4 days offset
        
        data_a = pd.DataFrame({
            'close': np.random.randn(100) + 100
        }, index=dates_a)
        
        data_b = pd.DataFrame({
            'close': np.random.randn(100) + 50
        }, index=dates_b)
        
        fetcher = PairDataFetcher()
        aligned_a, aligned_b = fetcher._align_dataframes(data_a, data_b)
        
        # Should have same length
        self.assertEqual(len(aligned_a), len(aligned_b))
        
        # Should have only overlapping dates
        self.assertEqual(len(aligned_a), 96)  # 100 - 4 days offset
        
        # Indices should match
        self.assertTrue(aligned_a.index.equals(aligned_b.index))
    
    def test_calculate_hedge_ratio(self):
        """Test hedge ratio calculation"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create data with known relationship: B = 2 * A + noise
        prices_a = 100 + np.cumsum(np.random.randn(100))
        prices_b = 2 * prices_a + np.random.randn(100) * 5
        
        data_a = pd.DataFrame({'close': prices_a}, index=dates)
        data_b = pd.DataFrame({'close': prices_b}, index=dates)
        
        fetcher = PairDataFetcher()
        hedge_ratio = fetcher.calculate_hedge_ratio(data_a, data_b)
        
        # Should be close to 2.0 (the true relationship)
        self.assertAlmostEqual(hedge_ratio, 2.0, delta=0.3)
    
    def test_calculate_correlation(self):
        """Test correlation calculation"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100, freq='D')
        
        # Create highly correlated data
        base = np.random.randn(100)
        prices_a = 100 + np.cumsum(base)
        prices_b = 50 + np.cumsum(base * 0.5)  # Correlated
        
        data_a = pd.DataFrame({'close': prices_a}, index=dates)
        data_b = pd.DataFrame({'close': prices_b}, index=dates)
        
        fetcher = PairDataFetcher()
        correlation = fetcher.calculate_correlation(data_a, data_b)
        
        # Should be high positive correlation
        self.assertGreater(correlation, 0.5)


if __name__ == '__main__':
    unittest.main()
