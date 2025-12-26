"""
CRUD operations for database models
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime

from api.models import (
    Strategy,
    Backtest,
    Trade,
    EquityPoint,
    MarketData
)


# ============================================================================
# MARKET DATA CRUD
# ============================================================================

def save_market_data_batch(db: Session, data_list: list) -> int:
    """Guardar múltiples registros de datos de mercado"""
    try:
        # Eliminar duplicados existentes
        if data_list:
            symbol = data_list[0]['symbol']
            db.query(MarketData).filter(MarketData.symbol == symbol).delete()
            db.commit()
        
        # Insertar nuevos registros
        records = []
        for data in data_list:
            record = MarketData(
                symbol=data['symbol'],
                asset_type=data.get('asset_type', 'crypto'),
                timestamp=data['timestamp'],
                timeframe=data.get('timeframe', '1d'),
                open=float(data['open']),
                high=float(data['high']),
                low=float(data['low']),
                close=float(data['close']),
                volume=float(data['volume'])
            )
            records.append(record)
        
        db.bulk_save_objects(records)
        db.commit()
        return len(records)
    except Exception as e:
        db.rollback()
        raise


def bulk_insert_market_data(db: Session, records: list) -> int:
    """
    Insertar múltiples registros de datos de mercado en bulk.
    Alias para save_market_data_batch con el mismo formato.
    """
    return save_market_data_batch(db, records)


def get_market_data(
    db: Session,
    symbol: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    timeframe: str = '1d',
    limit: int = 10000
) -> List[MarketData]:
    """Obtener datos de mercado de la base de datos"""
    query = db.query(MarketData).filter(
        and_(
            MarketData.symbol == symbol,
            MarketData.timeframe == timeframe
        )
    )
    
    if start_date:
        query = query.filter(MarketData.timestamp >= start_date)
    if end_date:
        query = query.filter(MarketData.timestamp <= end_date)
    
    query = query.order_by(MarketData.timestamp.asc()).limit(limit)
    
    return query.all()


def delete_market_data(db: Session, symbol: str) -> int:
    """Eliminar todos los datos de un símbolo"""
    count = db.query(MarketData).filter(MarketData.symbol == symbol).delete()
    db.commit()
    return count


def get_data_source(db: Session, symbol: str) -> Optional['DataSource']:
    """Obtener información de una fuente de datos"""
    from api.models import DataSource
    return db.query(DataSource).filter(DataSource.symbol == symbol).first()


def get_all_data_sources(db: Session, asset_type: Optional[str] = None) -> List['DataSource']:
    """Obtener todas las fuentes de datos"""
    from api.models import DataSource
    query = db.query(DataSource)
    if asset_type:
        query = query.filter(DataSource.asset_type == asset_type)
    return query.order_by(DataSource.symbol).all()


def create_or_update_data_source(
    db: Session,
    symbol: str,
    asset_type: str,
    name: str,
    exchange: Optional[str] = None
) -> 'DataSource':
    """Crear o actualizar metadatos de fuente de datos"""
    from api.models import DataSource
    
    source = get_data_source(db, symbol)
    
    if source:
        source.name = name
        source.asset_type = asset_type
        source.exchange = exchange
        source.last_updated = datetime.now()
    else:
        source = DataSource(
            symbol=symbol,
            asset_type=asset_type,
            name=name,
            exchange=exchange,
            last_updated=datetime.now()
        )
        db.add(source)
    
    db.commit()
    db.refresh(source)
    return source


def update_data_source_stats(db: Session, symbol: str) -> Optional['DataSource']:
    """Actualizar estadísticas de una fuente de datos"""
    from api.models import DataSource
    from sqlalchemy import func
    
    source = get_data_source(db, symbol)
    if not source:
        return None
    
    stats = db.query(
        func.count(MarketData.id).label('count'),
        func.min(MarketData.timestamp).label('min_date'),
        func.max(MarketData.timestamp).label('max_date')
    ).filter(MarketData.symbol == symbol).first()
    
    source.total_records = stats.count or 0
    source.min_date = stats.min_date
    source.max_date = stats.max_date
    source.last_updated = datetime.now()
    
    db.commit()
    db.refresh(source)
    return source


# ============================================================================
# STRATEGY CRUD
# ============================================================================

def create_strategy(
    db: Session,
    name: str,
    strategy_type: str,
    description: str = None,
    default_params: dict = None
) -> Strategy:
    """Create a new strategy"""
    strategy = Strategy(
        name=name,
        strategy_type=strategy_type,
        description=description,
        default_params=default_params or {}
    )
    db.add(strategy)
    db.commit()
    db.refresh(strategy)
    return strategy


def get_strategy(db: Session, strategy_id: int) -> Optional[Strategy]:
    """Get strategy by ID"""
    return db.query(Strategy).filter(Strategy.id == strategy_id).first()


def get_strategy_by_type(db: Session, strategy_type: str) -> Optional[Strategy]:
    """Get strategy by type"""
    return db.query(Strategy).filter(Strategy.strategy_type == strategy_type).first()


def get_all_strategies(db: Session) -> List[Strategy]:
    """Get all strategies"""
    return db.query(Strategy).all()


def get_or_create_strategy(
    db: Session,
    strategy_type: str,
    name: str,
    description: str = None,
    default_params: dict = None
) -> Strategy:
    """Get existing strategy or create new one"""
    strategy = get_strategy_by_type(db, strategy_type)
    if not strategy:
        strategy = create_strategy(
            db=db,
            name=name,
            strategy_type=strategy_type,
            description=description,
            default_params=default_params
        )
    return strategy


# ============================================================================
# BACKTEST CRUD
# ============================================================================

def create_backtest(
    db: Session,
    strategy_id: int,
    symbol: str,
    params: dict,
    initial_capital: float,
    commission: float = 0.001,
    slippage: float = 0.0,
    start_date: datetime = None,
    end_date: datetime = None
) -> Backtest:
    """Create a new backtest record"""
    backtest = Backtest(
        strategy_id=strategy_id,
        symbol=symbol,
        params=params,
        initial_capital=initial_capital,
        commission=commission,
        slippage=slippage,
        start_date=start_date,
        end_date=end_date,
        status="running"
    )
    db.add(backtest)
    db.commit()
    db.refresh(backtest)
    return backtest


def update_backtest_results(
    db: Session,
    backtest_id: int,
    results: dict,
    execution_time: float = None
) -> Backtest:
    """Update backtest with results"""
    import numpy as np
    
    # Helper function to convert numpy types to Python native types
    def to_native_type(value):
        if value is None:
            return None
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        return value
    
    backtest = db.query(Backtest).filter(Backtest.id == backtest_id).first()
    if backtest:
        backtest.final_capital = to_native_type(results.get('final_capital'))
        backtest.total_return = to_native_type(results.get('total_return'))
        backtest.sharpe_ratio = to_native_type(results.get('sharpe_ratio'))
        backtest.max_drawdown = to_native_type(results.get('max_drawdown'))
        backtest.total_trades = to_native_type(results.get('total_trades'))
        backtest.win_rate = to_native_type(results.get('win_rate'))
        backtest.status = "completed"
        if execution_time:
            backtest.execution_time = execution_time
        
        db.commit()
        db.refresh(backtest)
    return backtest


def get_backtest(db: Session, backtest_id: int) -> Optional[Backtest]:
    """Get backtest by ID"""
    return db.query(Backtest).filter(Backtest.id == backtest_id).first()


def get_backtests(
    db: Session,
    strategy_id: int = None,
    symbol: str = None,
    limit: int = 50,
    offset: int = 0
) -> List[Backtest]:
    """Get backtests with optional filters"""
    query = db.query(Backtest)
    
    if strategy_id:
        query = query.filter(Backtest.strategy_id == strategy_id)
    if symbol:
        query = query.filter(Backtest.symbol == symbol)
    
    return query.order_by(desc(Backtest.executed_at)).limit(limit).offset(offset).all()


def get_best_backtest(
    db: Session,
    metric: str = "total_return",
    strategy_id: int = None,
    symbol: str = None
) -> Optional[Backtest]:
    """Get best performing backtest by metric"""
    query = db.query(Backtest).filter(Backtest.status == "completed")
    
    if strategy_id:
        query = query.filter(Backtest.strategy_id == strategy_id)
    if symbol:
        query = query.filter(Backtest.symbol == symbol)
    
    # Map metric to column
    metric_column = {
        'total_return': Backtest.total_return,
        'sharpe_ratio': Backtest.sharpe_ratio,
        'win_rate': Backtest.win_rate,
    }.get(metric, Backtest.total_return)
    
    return query.order_by(desc(metric_column)).first()


# ============================================================================
# TRADE CRUD
# ============================================================================

def create_trade(
    db: Session,
    backtest_id: int,
    trade_type: str,
    entry_date: datetime,
    entry_price: float,
    shares: float,
    exit_date: datetime = None,
    exit_price: float = None
) -> Trade:
    """Create a trade record"""
    trade = Trade(
        backtest_id=backtest_id,
        trade_type=trade_type,
        entry_date=entry_date,
        entry_price=entry_price,
        shares=shares,
        exit_date=exit_date,
        exit_price=exit_price
    )
    
    # Calculate P&L if trade is closed
    if exit_price and trade_type == "BUY":
        trade.gross_profit = (exit_price - entry_price) * shares
        trade.net_profit = trade.gross_profit  # Commission handled elsewhere
        trade.return_pct = ((exit_price - entry_price) / entry_price) * 100
    
    db.add(trade)
    db.commit()
    db.refresh(trade)
    return trade


def bulk_create_trades(db: Session, backtest_id: int, trades_data: List[dict]):
    """Bulk create trades for a backtest"""
    import numpy as np
    import pandas as pd
    
    # Helper function to convert numpy/pandas types to Python native types
    def to_native_type(value):
        if value is None:
            return None
        if isinstance(value, (np.integer, np.floating)):
            return float(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, (pd.Timestamp, pd.DatetimeTZDtype)):
            return value.to_pydatetime() if hasattr(value, 'to_pydatetime') else value
        return value
    
    trades = []
    for trade_data in trades_data:
        trade = Trade(
            backtest_id=backtest_id,
            trade_type=trade_data.get('type', 'BUY'),
            entry_date=to_native_type(trade_data.get('date')),
            entry_price=to_native_type(trade_data.get('price')),
            shares=to_native_type(trade_data.get('shares'))
        )
        trades.append(trade)
    
    db.bulk_save_objects(trades)
    db.commit()


# ============================================================================
# EQUITY CURVE CRUD
# ============================================================================

def bulk_create_equity_points(
    db: Session,
    backtest_id: int,
    equity_data: List[dict]
):
    """Bulk create equity curve points"""
    points = []
    for data in equity_data:
        point = EquityPoint(
            backtest_id=backtest_id,
            timestamp=data.get('timestamp'),
            equity=data.get('equity'),
            position_value=data.get('position_value', 0),
            cash=data.get('cash')
        )
        points.append(point)
    
    db.bulk_save_objects(points)
    db.commit()


# ============================================================================
# MARKET DATA CRUD
# ============================================================================

def save_market_data(
    db: Session,
    symbol: str,
    timeframe: str,
    data_points: List[dict]
):
    """Save market data to cache"""
    # Delete existing data for this symbol/timeframe
    db.query(MarketData).filter(
        and_(
            MarketData.symbol == symbol,
            MarketData.timeframe == timeframe
        )
    ).delete()
    
    # Insert new data
    records = []
    for point in data_points:
        record = MarketData(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=point['timestamp'],
            open=point['open'],
            high=point['high'],
            low=point['low'],
            close=point['close'],
            volume=point['volume']
        )
        records.append(record)
    
    db.bulk_save_objects(records)
    db.commit()


def get_market_data(
    db: Session,
    symbol: str,
    timeframe: str = "1d",
    start_date: datetime = None,
    end_date: datetime = None
) -> List[MarketData]:
    """Get cached market data"""
    query = db.query(MarketData).filter(
        and_(
            MarketData.symbol == symbol,
            MarketData.timeframe == timeframe
        )
    )
    
    if start_date:
        query = query.filter(MarketData.timestamp >= start_date)
    if end_date:
        query = query.filter(MarketData.timestamp <= end_date)
    
    return query.order_by(MarketData.timestamp).all()


# ============================================================================
# STATISTICS
# ============================================================================

def get_backtest_stats(db: Session) -> dict:
    """Get overall statistics"""
    from sqlalchemy import func
    
    total_backtests = db.query(func.count(Backtest.id)).scalar()
    
    if total_backtests == 0:
        return {
            'total_backtests': 0,
            'strategies_tested': 0,
            'avg_return': 0,
            'total_trades': 0
        }
    
    stats = db.query(
        func.count(Backtest.id).label('count'),
        func.count(func.distinct(Backtest.strategy_id)).label('strategies'),
        func.avg(Backtest.total_return).label('avg_return'),
        func.sum(Backtest.total_trades).label('total_trades'),
        func.avg(Backtest.sharpe_ratio).label('avg_sharpe'),
        func.avg(Backtest.win_rate).label('avg_win_rate'),
        func.max(Backtest.total_return).label('best_return')
    ).filter(Backtest.status == "completed").first()
    
    return {
        'total_backtests': stats.count or 0,
        'strategies_tested': stats.strategies or 0,
        'avg_return': float(stats.avg_return or 0),
        'total_trades': int(stats.total_trades or 0),
        'avg_sharpe': float(stats.avg_sharpe or 0),
        'avg_win_rate': float(stats.avg_win_rate or 0),
        'best_return': float(stats.best_return or 0)
    }
