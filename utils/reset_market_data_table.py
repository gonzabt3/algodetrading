"""Drop and recreate market_data table"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from api.database import engine
from api.models import MarketData, DataSource, Base

# Drop existing table
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS market_data CASCADE'))
    conn.commit()
    print('✅ Tabla market_data eliminada')

# Recreate with new structure
Base.metadata.create_all(bind=engine)
print('✅ Tabla market_data recreada con nueva estructura')
