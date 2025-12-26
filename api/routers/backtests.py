"""
Backtest Router - Handles backtest history
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from api.database import get_db
from api import crud
from api.models import BacktestResult, BacktestDetailResult

router = APIRouter(prefix="/api", tags=["backtests"])


@router.get("/backtests", response_model=List[BacktestResult])
async def list_backtests(
    strategy_id: Optional[int] = None,
    symbol: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get backtest history"""
    backtests = crud.get_backtests(
        db=db,
        strategy_id=strategy_id,
        symbol=symbol,
        limit=limit,
        offset=offset
    )
    
    results = []
    for bt in backtests:
        results.append(BacktestResult(
            id=bt.id,
            strategy_id=bt.strategy_id,
            strategy_name=bt.strategy.name,
            symbol=bt.symbol,
            start_date=bt.start_date,
            end_date=bt.end_date,
            params=bt.params,
            initial_capital=bt.initial_capital,
            final_capital=bt.final_capital,
            total_return=bt.total_return,
            sharpe_ratio=bt.sharpe_ratio,
            max_drawdown=bt.max_drawdown,
            total_trades=bt.total_trades,
            win_rate=bt.win_rate,
            executed_at=bt.executed_at,
            status=bt.status
        ))
    
    return results


@router.get("/backtests/{backtest_id}", response_model=BacktestDetailResult)
async def get_backtest(backtest_id: int, db: Session = Depends(get_db)):
    """Get specific backtest details"""
    bt = crud.get_backtest(db, backtest_id)
    if not bt:
        raise HTTPException(status_code=404, detail="Backtest not found")
    
    # Build trades list
    trades = [
        {
            'id': t.id,
            'trade_type': t.trade_type,
            'entry_date': t.entry_date.isoformat() if t.entry_date else None,
            'exit_date': t.exit_date.isoformat() if t.exit_date else None,
            'entry_price': t.entry_price,
            'exit_price': t.exit_price,
            'shares': t.shares,
            'gross_profit': t.gross_profit,
            'net_profit': t.net_profit,
            'commission': t.commission
        }
        for t in bt.trades
    ]
    
    # Build equity points
    equity_points = [
        {
            'timestamp': ep.timestamp.isoformat(),
            'equity': ep.equity,
            'cash': ep.cash,
            'position_value': ep.position_value
        }
        for ep in bt.equity_points
    ]
    
    return BacktestDetailResult(
        id=bt.id,
        strategy_id=bt.strategy_id,
        strategy_name=bt.strategy.name,
        symbol=bt.symbol,
        start_date=bt.start_date,
        end_date=bt.end_date,
        params=bt.params,
        initial_capital=bt.initial_capital,
        final_capital=bt.final_capital,
        total_return=bt.total_return,
        sharpe_ratio=bt.sharpe_ratio,
        max_drawdown=bt.max_drawdown,
        total_trades=bt.total_trades,
        win_rate=bt.win_rate,
        executed_at=bt.executed_at,
        status=bt.status,
        trades=trades,
        equity_curve=equity_points
    )
