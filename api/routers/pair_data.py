"""
Pair Data Router - Single Responsibility
Handles pair trading data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pandas as pd

from api.database import get_db
from api import crud

router = APIRouter(prefix="/api", tags=["pair-data"])


@router.get("/pair-data")
async def get_pair_data(
    symbol_a: str,
    symbol_b: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """
    Get normalized pair trading data for visualization.
    Returns prices, spread, and z-score.
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        # Fetch data - usar argumentos con nombre explícitos
        data_a = crud.get_market_data(
            db=db,
            symbol=symbol_a,
            start_date=start,
            end_date=end,
            timeframe='1d'
        )
        data_b = crud.get_market_data(
            db=db,
            symbol=symbol_b,
            start_date=start,
            end_date=end,
            timeframe='1d'
        )
        
        if not data_a or not data_b:
            raise HTTPException(
                status_code=404,
                detail="No data found for one or both symbols"
            )
        
        # Convert to DataFrames
        df_a = pd.DataFrame([{
            'timestamp': d.timestamp,
            'close': d.close
        } for d in data_a])
        
        df_b = pd.DataFrame([{
            'timestamp': d.timestamp,
            'close': d.close
        } for d in data_b])
        
        # Align timestamps
        merged = pd.merge(df_a, df_b, on='timestamp', suffixes=('_a', '_b'), how='inner')
        
        if len(merged) == 0:
            raise HTTPException(
                status_code=404,
                detail="No matching timestamps between symbols"
            )
        
        # Normalize prices (base 100)
        merged['close_a_norm'] = (merged['close_a'] / merged['close_a'].iloc[0]) * 100
        merged['close_b_norm'] = (merged['close_b'] / merged['close_b'].iloc[0]) * 100
        
        # Calculate spread and z-score
        merged['spread'] = merged['close_a_norm'] - merged['close_b_norm']
        window = 20
        merged['spread_ma'] = merged['spread'].rolling(window=window).mean()
        merged['spread_std'] = merged['spread'].rolling(window=window).std()
        merged['z_score'] = (merged['spread'] - merged['spread_ma']) / merged['spread_std']
        
        # Format response
        merged['timestamp'] = pd.to_datetime(merged['timestamp']).dt.strftime('%Y-%m-%d')
        
        return {
            'timestamps': merged['timestamp'].tolist(),
            'symbol_a': {
                'name': symbol_a,
                'prices': merged['close_a'].tolist(),
                'prices_normalized': merged['close_a_norm'].tolist()
            },
            'symbol_b': {
                'name': symbol_b,
                'prices': merged['close_b'].tolist(),
                'prices_normalized': merged['close_b_norm'].tolist()
            },
            'spread': merged['spread'].tolist(),
            'z_score': merged['z_score'].fillna(0).tolist(),
            'spread_ma': merged['spread_ma'].fillna(0).tolist()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
