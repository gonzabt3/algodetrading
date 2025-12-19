# Trading Dashboard - Full Stack Guide

## 🚀 Quick Start

### Prerequisites
- Docker running (PostgreSQL + Redis)
- Python virtual environment activated
- Node.js 18+ installed

### 1. Start Database Services

```bash
# Check if containers are running
sudo docker ps --filter "name=trading_"

# If not running, start them
sudo docker start trading_postgres trading_redis
```

### 2. Start Backend API

```bash
# From project root
cd /home/gonza/Develop/algodetraiding

# Activate virtual environment
source venv/bin/activate

# Start FastAPI server
uvicorn api.main:app --reload --port 8000
```

Backend will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 3. Start Frontend Dashboard

```bash
# In a new terminal
cd /home/gonza/Develop/algodetraiding/web/frontend

# Start Vite dev server
npm run dev
```

Frontend will be available at:
- **Dashboard**: http://localhost:3000

## 📊 Using the Dashboard

### Overview
The dashboard provides a professional interface to manage and analyze trading strategies.

### Features

1. **Real-Time Statistics**
   - Total backtests executed
   - Best performing strategy
   - Average return across all strategies
   - Total trades executed
   - Auto-refreshes every 5 seconds

2. **Strategy Selector**
   - View all available trading strategies
   - See strategy descriptions
   - Click to select a strategy for backtesting

3. **Backtest Configuration**
   - **Symbol**: Trading pair (e.g., BTC/USDT, ETH/USDT)
   - **Days**: Historical data range (30 days to 10 years)
   - **Initial Capital**: Starting portfolio value
   - **Commission**: Trading fees percentage
   - **Real Data**: Toggle between synthetic/real market data
   - Strategy parameters are displayed (read-only for now)

4. **Backtest Results**
   - View all executed backtests in a sortable table
   - Color-coded returns (green = profit, red = loss)
   - Sharpe ratio quality indicator
   - Win rate and trade count
   - Click any row to view detailed JSON results

## 🎯 Workflow Example

1. **Select a Strategy**
   - Click on "MA Crossover" or any other strategy
   - The backtest form will appear

2. **Configure Backtest**
   - Set symbol: `BTC/USDT`
   - Adjust days slider: `365` (1 year)
   - Set capital: `$10,000`
   - Commission: `0.1%` (0.001)
   - Check "Use Real Data" if you want actual market data

3. **Run Backtest**
   - Click "🚀 Run Backtest" button
   - Wait for execution (loading spinner will show)
   - Results will appear in the table below

4. **Analyze Results**
   - Check total return (green = profitable)
   - Review Sharpe ratio (>2 = excellent, >1 = good)
   - Examine win rate and trade count
   - Click row to see full JSON details

## 🔧 API Endpoints

### Strategies
```bash
GET /api/strategies
# Returns list of all available strategies
```

### Backtests
```bash
GET /api/backtests
# Get all backtests (supports filters)

GET /api/backtests/{id}
# Get detailed backtest with trades and equity curve

POST /api/backtests/run
# Execute new backtest
Body: {
  "strategy_id": "ma_crossover",
  "symbol": "BTC/USDT",
  "days": 365,
  "initial_capital": 10000,
  "commission": 0.001,
  "use_real_data": false,
  "params": {...}
}
```

### Statistics
```bash
GET /api/stats/summary
# Get overall statistics across all backtests
```

## 🗄️ Database Schema

### Tables
- **strategies**: Strategy metadata (id, name, description, params)
- **backtests**: Backtest execution records
- **trades**: Individual trade records (FK to backtests)
- **equity_points**: Equity curve data (FK to backtests)
- **market_data**: Cached historical price data

### Connection
```
postgresql://trading_user:trading_pass@localhost:5433/trading_db
```

## 🛠️ Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

### Hot Reload
Both backend and frontend support hot reload:
- **Backend**: Edit Python files in `api/`, `strategies/`, `utils/`
- **Frontend**: Edit React files in `web/frontend/src/`
- Changes will auto-refresh (backend restarts, frontend HMR)

### Testing Backend

```bash
# Test with curl
curl http://localhost:8000/api/strategies

# Or use Swagger UI
# Visit http://localhost:8000/docs
```

## 🚨 Troubleshooting

### Backend won't start
- Check database is running: `sudo docker ps`
- Verify database connection in `.env`
- Check logs for import errors

### Frontend won't start
- Ensure Node 18+ is installed: `node --version`
- Clear node_modules: `rm -rf node_modules && npm install`
- Check port 3000 is available

### CORS errors
- Verify backend CORS settings in `api/main.py`
- Check frontend proxy in `vite.config.js`
- Ensure both servers are running on correct ports

### No data showing
- Run a backtest first from the UI
- Check browser console for errors (F12)
- Verify API calls in Network tab
- Check backend logs for database errors

## 📝 Next Steps

### Planned Features
- [ ] Equity curve charts (Recharts integration)
- [ ] WebSocket real-time updates
- [ ] Parameter optimization interface
- [ ] Strategy comparison charts
- [ ] Export results to CSV/PDF
- [ ] Dark/light theme toggle
- [ ] Mobile responsive design improvements
- [ ] Trade-by-trade analysis view
- [ ] Multi-strategy portfolio backtesting
- [ ] Migrate existing JSON results to database

## 🎨 Tech Stack

**Backend**
- FastAPI 0.124.4
- PostgreSQL 16
- SQLAlchemy 2.0.45
- Alembic 1.17.2
- Redis 7

**Frontend**
- React 18.2.0
- Vite 5.0.0
- TailwindCSS 3.4.0
- React Query 5.14.0
- Recharts 2.10.0
- Axios 1.6.0

**Infrastructure**
- Docker (PostgreSQL + Redis)
- Uvicorn ASGI server
- Node.js 18.20.8

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Query Guide](https://tanstack.com/query/latest)
- [Vite Documentation](https://vite.dev/)
- [TailwindCSS](https://tailwindcss.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
