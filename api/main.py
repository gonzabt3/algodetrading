"""
FastAPI application for Trading Dashboard
"""
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from sqlalchemy.orm import Session
import asyncio
import time
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from api.models import (
    BacktestRequest,
    BacktestResponse,
    StrategyInfo,
    BacktestResult,
    BacktestDetailResult,
    MarketDataRequest,
    Strategy as DBStrategy
)
from api.database import get_db, Base, engine
from api import crud
from api.routers import brokers as broker_router
from utils.data_fetcher import DataFetcher
from backtesting.backtester import Backtester

# Import strategies
from strategies.ma_crossover import MovingAverageCrossover
from strategies.rsi_strategy import RSIStrategy
from strategies.macd_strategy import MACDStrategy
from strategies.bollinger_bands import BollingerBandsStrategy
from strategies.mean_reversion import MeanReversionStrategy
from strategies.multi_indicator import MultiIndicatorStrategy


# Create tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Algorithmic Trading Dashboard",
    description="API for backtesting trading strategies",
    version="1.0.0"
)

# Include routers
app.include_router(broker_router.router)

# CORS - permite requests desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite y React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities
data_fetcher = DataFetcher()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ============================================================================
# STRATEGY REGISTRY
# ============================================================================

STRATEGIES = {
    'ma_crossover': {
        'class': MovingAverageCrossover,
        'name': 'MA Crossover',
        'description': 'Moving Average Crossover - Buy when fast MA crosses above slow MA',
        'params': {'fast_period': 20, 'slow_period': 50}
    },
    'rsi': {
        'class': RSIStrategy,
        'name': 'RSI Strategy',
        'description': 'RSI-based mean reversion - Buy oversold, sell overbought',
        'params': {'period': 14, 'oversold': 30, 'overbought': 70}
    },
    'macd': {
        'class': MACDStrategy,
        'name': 'MACD Strategy',
        'description': 'MACD momentum strategy - Buy on bullish crossover',
        'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
    },
    'bollinger_bands': {
        'class': BollingerBandsStrategy,
        'name': 'Bollinger Bands',
        'description': 'Volatility-based strategy - Buy at lower band, sell at upper',
        'params': {'period': 20, 'std_dev': 2}
    },
    'mean_reversion': {
        'class': MeanReversionStrategy,
        'name': 'Mean Reversion',
        'description': 'Z-score based mean reversion',
        'params': {'period': 20, 'entry_threshold': 2, 'exit_threshold': 0}
    },
    'multi_indicator': {
        'class': MultiIndicatorStrategy,
        'name': 'Multi-Indicator',
        'description': 'Combines RSI + MACD + Volume for confirmation',
        'params': {
            'rsi_period': 14,
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'macd_fast': 12,
            'macd_slow': 26,
            'macd_signal': 9,
            'volume_period': 20
        }
    }
}


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "message": "Trading API is running",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/strategies", response_model=List[StrategyInfo])
async def list_strategies(db: Session = Depends(get_db)):
    """Get all available strategies"""
    # Initialize strategies in DB if not exists
    for key, info in STRATEGIES.items():
        crud.get_or_create_strategy(
            db=db,
            strategy_type=key,
            name=info['name'],
            description=info['description'],
            default_params=info['params']
        )
    
    strategies = []
    for key, info in STRATEGIES.items():
        strategies.append(StrategyInfo(
            id=key,
            name=info['name'],
            description=info['description'],
            default_params=info['params']
        ))
    return strategies


@app.get("/api/backtests", response_model=List[BacktestResult])
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


@app.get("/api/backtests/{backtest_id}", response_model=BacktestDetailResult)
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
            'return_pct': t.return_pct
        }
        for t in bt.trades
    ]
    
    # Build equity curve
    equity_curve = [
        {
            'timestamp': ep.timestamp.isoformat() if ep.timestamp else None,
            'equity': ep.equity,
            'position_value': ep.position_value,
            'cash': ep.cash
        }
        for ep in bt.equity_curve
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
        equity_curve=equity_curve
    )


@app.post("/api/backtests/run", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest, db: Session = Depends(get_db)):
    """Run a new backtest"""
    start_time = time.time()
    
    try:
        # Validate strategy
        if request.strategy_id not in STRATEGIES:
            raise HTTPException(status_code=400, detail=f"Unknown strategy: {request.strategy_id}")
        
        # Get or create strategy in DB
        strategy_info = STRATEGIES[request.strategy_id]
        db_strategy = crud.get_or_create_strategy(
            db=db,
            strategy_type=request.strategy_id,
            name=strategy_info['name'],
            description=strategy_info['description'],
            default_params=strategy_info['params']
        )
        
        # Broadcast start event
        await manager.broadcast({
            'type': 'backtest_started',
            'strategy': request.strategy_id,
            'symbol': request.symbol
        })
        
        # Get market data
        if request.use_real_data:
            print(f"Fetching real data for {request.symbol}...")
            start_date = datetime.now() - timedelta(days=request.days)
            data = data_fetcher.fetch_historical_data(
                symbol=request.symbol,
                start_date=start_date
            )
            if data is None or data.empty:
                raise HTTPException(status_code=400, detail="Failed to fetch market data")
        else:
            # Generate synthetic data
            dates = pd.date_range(end=datetime.now(), periods=request.days, freq='D')
            prices = 100 + np.cumsum(np.random.randn(request.days) * 2)
            
            data = pd.DataFrame({
                'open': prices * (1 + np.random.randn(request.days) * 0.01),
                'high': prices * (1 + abs(np.random.randn(request.days)) * 0.02),
                'low': prices * (1 - abs(np.random.randn(request.days)) * 0.02),
                'close': prices,
                'volume': np.random.randint(1000, 10000, request.days)
            }, index=dates)
        
        # Create backtest record
        backtest = crud.create_backtest(
            db=db,
            strategy_id=db_strategy.id,
            symbol=request.symbol,
            params=request.params if request.params else strategy_info['params'],
            initial_capital=request.initial_capital,
            commission=request.commission,
            start_date=data.index[0].to_pydatetime() if hasattr(data.index[0], 'to_pydatetime') else data.index[0],
            end_date=data.index[-1].to_pydatetime() if hasattr(data.index[-1], 'to_pydatetime') else data.index[-1]
        )
        
        # Create strategy instance
        params = request.params if request.params else strategy_info['params']
        strategy = strategy_info['class'](params=params)
        
        # Run backtest
        backtester = Backtester(
            strategy=strategy,
            initial_capital=request.initial_capital,
            commission=request.commission,
            save_results=False  # We're saving to DB instead
        )
        
        results = backtester.run(data)
        
        # Update backtest with results
        execution_time = time.time() - start_time
        crud.update_backtest_results(
            db=db,
            backtest_id=backtest.id,
            results=results,
            execution_time=execution_time
        )
        
        # Save trades
        if results.get('trades'):
            trades_to_save = []
            for trade in results['trades']:
                trades_to_save.append({
                    'type': trade['type'],
                    'date': trade['date'],
                    'price': trade['price'],
                    'shares': trade['shares']
                })
            crud.bulk_create_trades(db, backtest.id, trades_to_save)
        
        # Broadcast completion
        await manager.broadcast({
            'type': 'backtest_completed',
            'backtest_id': backtest.id,
            'strategy': request.strategy_id,
            'symbol': request.symbol,
            'total_return': results['total_return']
        })
        
        return BacktestResponse(
            success=True,
            message="Backtest completed successfully",
            backtest_id=backtest.id,
            results=results
        )
        
    except Exception as e:
        await manager.broadcast({
            'type': 'backtest_error',
            'error': str(e)
        })
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint simplificado para el frontend
@app.post("/api/backtest")
async def run_simple_backtest(
    request: BacktestRequest,
    db: Session = Depends(get_db)
):
    """Endpoint simplificado para ejecutar backtest desde frontend"""
    return await run_backtest(request, db)


@app.get("/api/market-data/{symbol}")
async def get_market_data(
    symbol: str,
    days: int = 365
):
    """Get market data for a symbol"""
    try:
        start_date = datetime.now() - timedelta(days=days)
        data = data_fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=start_date
        )
        if data is None or data.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Convert to JSON-serializable format
        data_dict = data.reset_index().to_dict(orient='records')
        for record in data_dict:
            if 'date' in record:
                record['date'] = record['date'].isoformat()
        
        return {
            'symbol': symbol,
            'data': data_dict,
            'count': len(data_dict)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# DATA MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/data/fetch")
async def fetch_market_data(
    symbol: str,
    timeframe: str = '1d',
    days: int = 365,
    asset_type: str = 'crypto',
    db: Session = Depends(get_db)
):
    """
    Descargar datos desde Binance API y guardar en la base de datos
    
    Args:
        symbol: Símbolo en formato ccxt (ej: BTC/USDT)
        timeframe: Temporalidad (1d, 4h, 1h, etc.)
        days: Número de días históricos a descargar
        asset_type: Tipo de activo (crypto, stock, forex, commodity, index)
    """
    try:
        result = data_fetcher.fetch_and_store_binance_data(
            symbol=symbol,
            timeframe=timeframe,
            days=days,
            asset_type=asset_type
        )
        
        if result['success']:
            return {
                'status': 'success',
                'message': f'Datos guardados exitosamente para {symbol}',
                'data': result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Error desconocido'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/sources")
async def get_data_sources(asset_type: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Obtener lista de todas las fuentes de datos disponibles
    
    Args:
        asset_type: Filtrar por tipo de activo (opcional)
    """
    try:
        sources = data_fetcher.get_available_symbols(asset_type)
        return {
            'status': 'success',
            'count': len(sources),
            'sources': sources
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/data/{symbol}")
async def delete_market_data_endpoint(symbol: str, db: Session = Depends(get_db)):
    """
    Eliminar todos los datos de un símbolo
    
    Args:
        symbol: Símbolo a eliminar (formato: BTC_USDT)
    """
    try:
        # El símbolo viene en formato BTC_USDT desde el frontend
        count = crud.delete_market_data(db, symbol)
        
        if count > 0:
            return {
                'status': 'success',
                'message': f'Eliminados {count} registros de {symbol}',
                'deleted_count': count
            }
        else:
            return {
                'status': 'warning',
                'message': f'No se encontraron datos para {symbol}',
                'deleted_count': 0
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/data/{symbol}/refresh")
async def refresh_market_data(
    symbol: str,
    timeframe: str = '1d',
    days: int = 365,
    db: Session = Depends(get_db)
):
    """
    Actualizar datos de un símbolo (eliminar y volver a descargar)
    
    Args:
        symbol: Símbolo en formato ccxt (ej: BTC/USDT)
        timeframe: Temporalidad
        days: Días históricos
    """
    try:
        # Convertir formato para DB
        db_symbol = symbol.replace('/', '_')
        
        # Eliminar datos existentes
        crud.delete_market_data(db, db_symbol)
        
        # Descargar nuevos datos
        result = data_fetcher.fetch_and_store_binance_data(
            symbol=symbol,
            timeframe=timeframe,
            days=days
        )
        
        if result['success']:
            return {
                'status': 'success',
                'message': f'Datos actualizados exitosamente para {symbol}',
                'data': result
            }
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Error desconocido'))
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data-health/{symbol}")
async def check_data_health(symbol: str):
    """Diagnóstico de salud de los datos de mercado (desde API en vivo)"""
    try:
        # Obtener datos directamente de la base de datos (últimos 30 días)
        start_date = datetime.now() - timedelta(days=30)
        data = data_fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=start_date
        )
        
        if data is None or data.empty:
            return {
                'status': 'error',
                'message': 'No se pudieron obtener datos del exchange',
                'symbol': symbol,
                'using_real_data': False
            }
        
        # Estadísticas
        stats = {
            'status': 'ok',
            'symbol': symbol,
            'data_source': 'Live Exchange API (Binance)',
            'using_real_data': True,
            'total_records': len(data),
            'date_range': {
                'start': str(data.index.min()),
                'end': str(data.index.max()),
                'days': (data.index.max() - data.index.min()).days
            },
            'price_stats': {
                'max_high': float(data['high'].max()),
                'min_low': float(data['low'].min()),
                'avg_close': float(data['close'].mean()),
                'current_price': float(data['close'].iloc[-1]),
                'first_price': float(data['close'].iloc[0])
            },
            'data_quality': {
                'has_nulls': bool(data.isnull().any().any()),
                'null_count': int(data.isnull().sum().sum()),
                'columns': list(data.columns)
            },
            'recent_data': []
        }
        
        # Últimos 5 registros
        for idx in range(max(0, len(data) - 5), len(data)):
            row = data.iloc[idx]
            stats['recent_data'].append({
                'date': str(data.index[idx]),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': float(row['volume']) if 'volume' in data.columns else 0
            })
        
        # Verificación de precios realistas
        if 'BTC' in symbol or 'bitcoin' in symbol.lower():
            if stats['price_stats']['max_high'] < 1000:
                stats['warning'] = '⚠️ Los precios de BTC parecen demasiado bajos (< $1,000). Posiblemente datos sintéticos.'
            elif stats['price_stats']['max_high'] > 20000:
                stats['verification'] = '✅ Precios de BTC en rango realista (> $20k) - Datos en vivo del exchange'
        
        return stats
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'symbol': symbol,
            'using_real_data': False
        }


@app.post("/api/data/validate/{symbol}")
async def validate_market_data(symbol: str, days: int = 365):
    """
    Valida la calidad e integridad de los datos de mercado
    
    Verifica:
    - Valores nulos o faltantes
    - Valores negativos
    - Relación OHLC correcta
    - Outliers extremos
    - Gaps temporales
    - Duplicados
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        data = data_fetcher.fetch_historical_data(
            symbol=symbol,
            start_date=start_date
        )
        
        if data is None or data.empty:
            return {
                'status': 'error',
                'message': f'No hay datos disponibles para {symbol}',
                'is_valid': False
            }
        
        validation = data_fetcher.validate_data_quality(data, symbol)
        
        return {
            'status': 'success',
            'symbol': symbol,
            'timeframe': '1d',
            **validation
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'is_valid': False
        }


@app.get("/api/stats/summary")
async def get_stats_summary(db: Session = Depends(get_db)):
    """Get overall statistics"""
    stats = crud.get_backtest_stats(db)
    
    if stats['total_backtests'] == 0:
        return {
            'total_backtests': 0,
            'strategies_tested': 0,
            'best_strategy': None,
            'avg_return': 0,
            'total_trades': 0,
            'avg_sharpe': 0,
            'avg_win_rate': 0,
            'best_return': 0
        }
    
    # Get best strategy
    best_backtest = crud.get_best_backtest(db, metric='total_return')
    
    return {
        'total_backtests': stats['total_backtests'],
        'strategies_tested': stats['strategies_tested'],
        'best_strategy': best_backtest.strategy.name if best_backtest else None,
        'best_return': stats['best_return'],
        'avg_return': stats['avg_return'],
        'total_trades': stats['total_trades'],
        'avg_sharpe': stats['avg_sharpe'],
        'avg_win_rate': stats['avg_win_rate']
    }


# ============================================================================
# WEBSOCKET
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back for now
            await websocket.send_json({
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ============================================================================
# STARTUP/SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on startup"""
    print("🚀 Trading API started")
    print("📊 Dashboard: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown"""
    print("👋 Trading API shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
