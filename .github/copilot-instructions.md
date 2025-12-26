# Algorithmic Trading System - AI Agent Instructions

## Architecture Overview
**Full-stack trading platform**: FastAPI backend + React frontend + PostgreSQL + Docker infrastructure

**Key Pattern**: Dual strategy architecture
- Single-symbol strategies: Inherit from `BaseStrategy` (strategies/base_strategy.py)
- Multi-symbol strategies: Inherit from `MultiSymbolStrategy` (strategies/base_multi_symbol_strategy.py) for pair trading, statistical arbitrage
- Each strategy type has dedicated backtester: `Backtester` vs `MultiSymbolBacktester`

**Data Flow**: 
1. Market data stored in PostgreSQL via `utils/data_fetcher.py` (crypto: ccxt, stocks: yfinance)
2. Backend API (api/main.py) orchestrates backtests, strategy selection
3. Frontend (web/frontend) visualizes results with recharts, manages dual-symbol selectors for pair trading

## Critical Startup Sequence
```bash
# 1. Database (required first)
docker-compose up -d postgres redis

# 2. Backend API (port 8000)
source venv/bin/activate
uvicorn api.main:app --reload --port 8000

# 3. Frontend (port 3000, requires Node.js 20.19+)
cd web/frontend && npm run dev
```

**Common Issue**: Backend uses port 5433 for PostgreSQL (not 5432) - see docker-compose.yml line 14

## Strategy Implementation Pattern
Multi-symbol strategies (pair_trading.py example):
1. Implement `fetch_multi_symbol_data()`: Align timestamps via inner join
2. Implement `calculate_multi_symbol_indicators()`: Compute spread, z-score
3. Implement `generate_multi_symbol_signals()`: Return `Dict[symbol, signal]` where signals are opposite (long A / short B)
4. Register in `api/main.py` STRATEGIES dict with `'type': 'multi_symbol'`

**Key Files**:
- strategies/pair_trading.py: Statistical arbitrage via z-score mean reversion
- utils/pair_data_fetcher.py: Timestamp alignment, hedge ratio calculation (sklearn LinearRegression)
- backtesting/backtester.py: Lines 310-593 contain MultiSymbolBacktester with portfolio tracking

## Database Architecture
**SQLAlchemy models** (api/models.py):
- `MarketData`: OHLCV data, indexed by (symbol, timestamp, timeframe)
- `Backtest`: Results storage with equity_points for chart rendering
- `BrokerConfig`: Exchange API credentials (encrypted)

**Migration workflow**: 
```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Frontend Architecture
**Component hierarchy**:
- App.jsx → StrategyRunner.jsx (main orchestrator)
  - StrategySelector.jsx (strategy picker)
  - BacktestForm.jsx (config + dual symbol selectors for pair trading)
  - PairChart.jsx (shows only when strategy.id === 'pair_trading', 3 view modes)

**Data fetching pattern**: React Query (@tanstack/react-query) with tradingApi service (services/api.js)

**Critical**: PairChart requires backend endpoint `/api/pair-data` which returns normalized prices (base 100), spread, z-score

## Testing
```bash
pytest tests/                               # All tests
pytest tests/test_pair_trading.py          # Specific strategy
```

**Test pattern**: Use pytest fixtures for DB session, mock market data as DataFrame with DatetimeIndex

## Data Download Scripts
**Argentine stocks**: `utils/download_argentine_stocks.py` uses yfinance, saves via `crud.bulk_insert_market_data()`
**Crypto**: DataFetcher uses ccxt (binance default), respects exchange rate limits

**Important**: Always download data before running backtests - empty DB will fail silently

## Project-Specific Conventions
1. **Signal convention**: 1=buy/long, -1=sell/short, 0=hold (NOT True/False)
2. **Pair trading signals must be opposite**: If A=1 then B=-1 (spread long), validated in backtester
3. **Date handling**: Backend uses datetime.fromisoformat(), frontend sends 'YYYY-MM-DD' strings
4. **Capital tracking**: Portfolio equity = cash + sum(position_value) across all symbols
5. **Frontend dual selectors**: Use optgroups "Criptomonedas"/"Acciones Argentinas" - see BacktestForm.jsx lines 103-128

## Common Debugging Commands
```bash
# Check if strategies endpoint works
curl http://localhost:8000/api/strategies | python3 -m json.tool

# Verify DB has data for symbol
docker exec -it trading_postgres psql -U trading_user -d trading_db -c "SELECT COUNT(*) FROM market_data WHERE symbol='VIST';"

# Frontend hot reload issues: kill Node.js process
lsof -ti:3000 | xargs kill -9

# Backend auto-reload sometimes misses changes: restart uvicorn
```

## Never Commit
- API keys in .env (use .env.example template)
- Database credentials (docker-compose.yml uses defaults, override with environment variables)
- test_*.db files (SQLite test artifacts)
