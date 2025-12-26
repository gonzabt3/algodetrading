"""
Strategy Router - Separation of Concerns
All strategy-related endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from api.database import get_db
from api.models import StrategyInfo, BacktestRequest, BacktestResponse
from api.services.strategy_registry import registry
from api.services.backtest_service import BacktestService
from utils.data_fetcher import DataFetcher

router = APIRouter(prefix="/api", tags=["strategies"])
data_fetcher = DataFetcher()


@router.get("/strategies", response_model=List[StrategyInfo])
async def get_strategies():
    """Get all available strategies"""
    strategies = []
    for strategy_id, info in registry.list_all().items():
        strategies.append(StrategyInfo(
            id=strategy_id,
            name=info['name'],
            description=info['description'],
            default_params=info['params']
        ))
    return strategies


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """Execute a backtest"""
    try:
        # Validate strategy exists
        if not registry.exists(request.strategy_id):
            raise HTTPException(status_code=404, detail=f"Strategy '{request.strategy_id}' not found")
        
        strategy_info = registry.get_strategy_info(request.strategy_id)
        service = BacktestService(db, data_fetcher)
        
        # Execute based on strategy type
        if strategy_info['type'] == 'multi_symbol':
            # Multi-symbol strategy
            symbols = [request.symbol_a, request.symbol_b]
            results = service.execute_multi_symbol_backtest(
                strategy_id=request.strategy_id,
                symbols=symbols,
                days=request.days,
                initial_capital=request.initial_capital,
                commission=request.commission,
                params=request.params
            )
        else:
            # Single-symbol strategy
            results = service.execute_single_symbol_backtest(
                strategy_id=request.strategy_id,
                symbol=request.symbol,
                days=request.days,
                initial_capital=request.initial_capital,
                commission=request.commission,
                params=request.params
            )
        
        return BacktestResponse(
            success=True,
            message="Backtest completed successfully",
            results=results
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")
