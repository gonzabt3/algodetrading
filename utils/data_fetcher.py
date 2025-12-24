"""
Data Fetcher - Gestión centralizada de datos de mercado desde PostgreSQL
"""
import os
import pandas as pd
import ccxt
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
import sys

# Agregar el directorio raíz al path para importar módulos
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api import crud


class DataFetcher:
    """
    Clase para obtener datos de mercado desde la base de datos PostgreSQL.
    Binance API se usa solo para poblar la base de datos.
    """
    
    def __init__(self):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        
    def fetch_from_db(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Obtener datos de mercado desde la base de datos PostgreSQL
        
        Args:
            symbol: Símbolo del activo (ej: BTC/USDT)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            timeframe: Temporalidad (default: 1d)
            
        Returns:
            DataFrame con columnas [timestamp, open, high, low, close, volume]
        """
        db = SessionLocal()
        try:
            # Convertir símbolo formato ccxt a DB (BTC/USDT -> BTC_USDT)
            db_symbol = symbol.replace('/', '_')
            
            # Obtener datos de la DB
            records = crud.get_market_data(
                db=db,
                symbol=db_symbol,
                start_date=start_date,
                end_date=end_date,
                timeframe=timeframe
            )
            
            if not records:
                print(f"⚠️  No hay datos en la base de datos para {symbol}")
                return pd.DataFrame()
            
            # Convertir a DataFrame
            data = []
            for record in records:
                data.append({
                    'timestamp': record.timestamp,
                    'open': float(record.open),
                    'high': float(record.high),
                    'low': float(record.low),
                    'close': float(record.close),
                    'volume': float(record.volume)
                })
            
            df = pd.DataFrame(data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            
            print(f"✅ Cargados {len(df)} registros desde DB para {symbol}")
            return df
            
        finally:
            db.close()
    
    def fetch_and_store_binance_data(
        self,
        symbol: str,
        timeframe: str = '1d',
        days: int = 365,
        asset_type: str = 'crypto'
    ) -> Dict:
        """
        Descargar datos desde Binance API y guardar en la base de datos
        
        Args:
            symbol: Símbolo en formato ccxt (ej: BTC/USDT)
            timeframe: Temporalidad (1d, 4h, 1h, etc.)
            days: Número de días históricos
            asset_type: Tipo de activo (crypto, stock, forex, etc.)
            
        Returns:
            Dict con estadísticas de la operación
        """
        db = SessionLocal()
        try:
            print(f"📥 Descargando {symbol} desde Binance...")
            
            # Calcular fecha de inicio
            since = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Descargar datos
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, since=since)
            
            if not ohlcv:
                return {'success': False, 'error': 'No se obtuvieron datos de Binance'}
            
            # Preparar datos para guardar
            db_symbol = symbol.replace('/', '_')
            data_list = []
            
            for candle in ohlcv:
                data_list.append({
                    'symbol': db_symbol,
                    'asset_type': asset_type,
                    'timestamp': datetime.fromtimestamp(candle[0] / 1000),
                    'timeframe': timeframe,
                    'open': candle[1],
                    'high': candle[2],
                    'low': candle[3],
                    'close': candle[4],
                    'volume': candle[5]
                })
            
            # Guardar en la base de datos
            count = crud.save_market_data_batch(db, data_list)
            
            # Actualizar metadatos de la fuente
            source = crud.create_or_update_data_source(
                db=db,
                symbol=db_symbol,
                asset_type=asset_type,
                name=symbol,
                exchange='binance'
            )
            crud.update_data_source_stats(db, db_symbol)
            
            print(f"✅ Guardados {count} registros para {symbol}")
            
            return {
                'success': True,
                'symbol': symbol,
                'records_saved': count,
                'min_date': data_list[0]['timestamp'],
                'max_date': data_list[-1]['timestamp']
            }
            
        except Exception as e:
            print(f"❌ Error descargando {symbol}: {str(e)}")
            return {'success': False, 'error': str(e)}
        finally:
            db.close()
    
    def get_available_symbols(self, asset_type: Optional[str] = None) -> List[Dict]:
        """
        Obtener lista de símbolos disponibles en la base de datos
        
        Args:
            asset_type: Filtrar por tipo de activo (opcional)
            
        Returns:
            Lista de diccionarios con información de símbolos
        """
        db = SessionLocal()
        try:
            sources = crud.get_all_data_sources(db, asset_type)
            
            result = []
            for source in sources:
                result.append({
                    'symbol': source.symbol,
                    'name': source.name,
                    'asset_type': source.asset_type,
                    'exchange': source.exchange,
                    'total_records': source.total_records,
                    'min_date': source.min_date.isoformat() if source.min_date else None,
                    'max_date': source.max_date.isoformat() if source.max_date else None,
                    'last_updated': source.last_updated.isoformat() if source.last_updated else None
                })
            
            return result
            
        finally:
            db.close()
    
    def validate_data_quality(
        self,
        df: pd.DataFrame,
        symbol: str
    ) -> Dict[str, any]:
        """
        Valida la calidad e integridad de los datos de mercado
        
        Args:
            df: DataFrame con datos OHLCV
            symbol: Símbolo del activo para contexto
            
        Returns:
            Diccionario con resultados de validación y errores encontrados
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        if df is None or df.empty:
            validation_result['is_valid'] = False
            validation_result['errors'].append("DataFrame está vacío o es None")
            return validation_result
        
        # 1. Verificar columnas requeridas
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Columnas faltantes: {missing_cols}")
            return validation_result
        
        # 2. Verificar valores nulos
        null_counts = df[required_cols].isnull().sum()
        if null_counts.any():
            validation_result['warnings'].append(f"Valores nulos encontrados: {null_counts[null_counts > 0].to_dict()}")
        
        # 3. Verificar valores negativos
        for col in required_cols:
            negative_count = (df[col] < 0).sum()
            if negative_count > 0:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Valores negativos en '{col}': {negative_count} registros")
        
        # 4. Verificar relación OHLC (Open, High, Low, Close)
        invalid_ohlc = (
            (df['high'] < df['low']) |
            (df['high'] < df['open']) |
            (df['high'] < df['close']) |
            (df['low'] > df['open']) |
            (df['low'] > df['close'])
        ).sum()
        
        if invalid_ohlc > 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Relación OHLC inválida en {invalid_ohlc} registros (high debe ser >= all, low debe ser <= all)")
        
        # 5. Verificar outliers extremos (variaciones > 50% en un día)
        if len(df) > 1:
            price_changes = df['close'].pct_change().abs()
            extreme_changes = price_changes > 0.5
            if extreme_changes.any():
                extreme_count = extreme_changes.sum()
                max_change = price_changes.max() * 100
                validation_result['warnings'].append(
                    f"Cambios de precio extremos detectados: {extreme_count} días con variación > 50% (máximo: {max_change:.1f}%)"
                )
        
        # 6. Verificar gaps temporales
        if hasattr(df.index, 'to_series'):
            time_diffs = df.index.to_series().diff()
            expected_diff = pd.Timedelta(days=1)  # Para timeframe diario
            gaps = (time_diffs > expected_diff * 2).sum()  # Gaps > 2 días
            if gaps > 0:
                validation_result['warnings'].append(f"Gaps temporales detectados: {gaps} saltos en la serie")
        
        # 7. Verificar duplicados
        duplicates = df.index.duplicated().sum()
        if duplicates > 0:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Timestamps duplicados: {duplicates} registros")
        
        # 8. Estadísticas generales
        validation_result['stats'] = {
            'total_records': len(df),
            'date_range': {
                'start': df.index.min().isoformat() if len(df) > 0 else None,
                'end': df.index.max().isoformat() if len(df) > 0 else None
            },
            'price_range': {
                'min': float(df['close'].min()),
                'max': float(df['close'].max()),
                'current': float(df['close'].iloc[-1]) if len(df) > 0 else None
            },
            'avg_volume': float(df['volume'].mean())
        }
        
        return validation_result
    
    def fetch_historical_data(
        self,
        symbol: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        timeframe: str = '1d'
    ) -> pd.DataFrame:
        """
        Método principal: obtener datos históricos desde la base de datos
        
        Args:
            symbol: Símbolo del activo (formato ccxt: BTC/USDT)
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            timeframe: Temporalidad
            
        Returns:
            DataFrame con datos OHLCV
        """
        return self.fetch_from_db(symbol, start_date, end_date, timeframe)
