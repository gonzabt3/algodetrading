"""
Market Data Router - Handles market data operations
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from api.database import get_db
from api.models import MarketDataRequest
from utils.data_fetcher import DataFetcher

router = APIRouter(prefix="/api", tags=["market-data"])
data_fetcher = DataFetcher()


@router.post("/fetch-data")
async def fetch_market_data(request: MarketDataRequest, db: Session = Depends(get_db)):
    """Fetch and store market data"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=request.days)
        
        data = data_fetcher.get_data(
            symbol=request.symbol,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            db=db
        )
        
        return {
            "success": True,
            "message": f"Fetched {len(data)} records for {request.symbol}",
            "symbol": request.symbol,
            "records": len(data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/data-health/{symbol}")
async def check_data_health(symbol: str, db: Session = Depends(get_db)):
    """Check data availability for a symbol"""
    from api import crud
    
    # Get last 30 days of data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    data = crud.get_market_data(db, symbol, start_date, end_date)
    
    return {
        "symbol": symbol,
        "records": len(data),
        "has_data": len(data) > 0,
        "oldest_record": data[0].timestamp.isoformat() if data else None,
        "newest_record": data[-1].timestamp.isoformat() if data else None
    }
