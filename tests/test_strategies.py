"""
Example test for MA Crossover strategy
"""
import pytest
import pandas as pd
import numpy as np
from strategies.ma_crossover import MovingAverageCrossover


def test_ma_crossover_init():
    """Test strategy initialization"""
    strategy = MovingAverageCrossover()
    assert strategy.name == "MA Crossover"
    assert strategy.params['fast_period'] == 20
    assert strategy.params['slow_period'] == 50


def test_ma_crossover_custom_params():
    """Test strategy with custom parameters"""
    params = {'fast_period': 10, 'slow_period': 30}
    strategy = MovingAverageCrossover(params=params)
    assert strategy.params['fast_period'] == 10
    assert strategy.params['slow_period'] == 30


def test_calculate_indicators():
    """Test indicator calculation"""
    # Create sample data
    dates = pd.date_range('2024-01-01', periods=100)
    data = pd.DataFrame({
        'open': np.random.rand(100) * 100,
        'high': np.random.rand(100) * 100,
        'low': np.random.rand(100) * 100,
        'close': np.random.rand(100) * 100,
        'volume': np.random.rand(100) * 1000
    }, index=dates)
    
    strategy = MovingAverageCrossover()
    result = strategy.calculate_indicators(data)
    
    assert 'ma_fast' in result.columns
    assert 'ma_slow' in result.columns


def test_generate_signals():
    """Test signal generation"""
    dates = pd.date_range('2024-01-01', periods=100)
    data = pd.DataFrame({
        'close': np.linspace(50, 150, 100),  # Uptrend
        'open': np.linspace(50, 150, 100),
        'high': np.linspace(50, 150, 100),
        'low': np.linspace(50, 150, 100),
        'volume': np.random.rand(100) * 1000
    }, index=dates)
    
    strategy = MovingAverageCrossover()
    data = strategy.calculate_indicators(data)
    result = strategy.generate_signals(data)
    
    assert 'signal' in result.columns
    assert result['signal'].isin([0, 1, -1]).all()


def test_validate_params():
    """Test parameter validation"""
    # Valid params
    strategy = MovingAverageCrossover({'fast_period': 10, 'slow_period': 20})
    assert strategy.validate_params() is True
    
    # Invalid params (fast >= slow)
    strategy = MovingAverageCrossover({'fast_period': 50, 'slow_period': 20})
    assert strategy.validate_params() is False
