"""
SQLAlchemy models for PostgreSQL and Pydantic schemas for API
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from api.database import Base


# ============================================================================
# Enums
# ============================================================================

class BrokerType(str, Enum):
    """Tipos de broker soportados"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"
    ARGENTINA = "argentina"


class ValidationStatus(str, Enum):
    """Estado de validación de credenciales"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"


# ============================================================================
# Enums
# ============================================================================

class BrokerType(str, Enum):
    """Tipos de broker soportados"""
    CRYPTO = "crypto"
    STOCKS = "stocks"
    FOREX = "forex"
    ARGENTINA = "argentina"


class ValidationStatus(str, Enum):
    """Estado de validación de credenciales"""
    PENDING = "pending"
    VALID = "valid"
    INVALID = "invalid"
    ERROR = "error"


# ============================================================================
# SQLAlchemy Models (Database)
# ============================================================================

class BrokerConfig(Base):
    """Configuración de brokers soportados"""
    __tablename__ = "broker_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    broker_name = Column(String(50), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    broker_type = Column(String(20), nullable=False)  # crypto, stocks, forex, argentina
    logo_url = Column(String(255))
    requires_api_key = Column(Boolean, default=True)
    requires_api_secret = Column(Boolean, default=True)
    requires_passphrase = Column(Boolean, default=False)
    testnet_available = Column(Boolean, default=False)
    setup_instructions = Column(Text)
    website_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    credentials = relationship("BrokerCredential", back_populates="broker_config", cascade="all, delete-orphan")


class BrokerCredential(Base):
    """Credenciales encriptadas de brokers"""
    __tablename__ = "broker_credentials"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, default=1, index=True)  # Para multi-usuario futuro
    broker_config_id = Column(Integer, ForeignKey("broker_configs.id"), nullable=False)
    
    # Credenciales encriptadas
    api_key_encrypted = Column(Text, nullable=False)
    api_secret_encrypted = Column(Text)
    api_passphrase_encrypted = Column(Text)
    
    # Configuración
    is_active = Column(Boolean, default=True)
    is_testnet = Column(Boolean, default=False)
    
    # Metadatos de validación
    validation_status = Column(String(20), default="pending")
    last_validated_at = Column(DateTime(timezone=True))
    last_validation_error = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    broker_config = relationship("BrokerConfig", back_populates="credentials")


class AssetType(str, Enum):
    """Tipos de activos soportados"""
    CRYPTO = "crypto"
    STOCK = "stock"
    FOREX = "forex"
    COMMODITY = "commodity"
    INDEX = "index"


class MarketData(Base):
    """Datos OHLCV de mercado almacenados en la base de datos"""
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), index=True, nullable=False)
    asset_type = Column(String(20), nullable=False, default="crypto")
    timestamp = Column(DateTime(timezone=True), index=True, nullable=False)
    timeframe = Column(String(10), default='1d', nullable=False)
    
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DataSource(Base):
    """Metadatos de fuentes de datos disponibles"""
    __tablename__ = "data_sources"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50), unique=True, nullable=False, index=True)
    asset_type = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    exchange = Column(String(50), nullable=True)
    last_updated = Column(DateTime(timezone=True), nullable=True)
    total_records = Column(Integer, default=0)
    min_date = Column(DateTime(timezone=True), nullable=True)
    max_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(String(20), default="active")
    validation_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Strategy(Base):
    """Trading strategy definition"""
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    strategy_type = Column(String(50), nullable=False)  # ma_crossover, rsi, etc.
    default_params = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    backtests = relationship("Backtest", back_populates="strategy", cascade="all, delete-orphan")


class Backtest(Base):
    """Backtest execution record"""
    __tablename__ = "backtests"
    
    id = Column(Integer, primary_key=True, index=True)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), default="1d")
    start_date = Column(DateTime(timezone=True))
    end_date = Column(DateTime(timezone=True))
    
    # Parameters
    params = Column(JSON)
    initial_capital = Column(Float, nullable=False)
    commission = Column(Float, default=0.001)
    slippage = Column(Float, default=0.0)
    
    # Results
    final_capital = Column(Float)
    total_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    total_trades = Column(Integer)
    winning_trades = Column(Integer)
    losing_trades = Column(Integer)
    win_rate = Column(Float)
    
    # Metadata
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    execution_time = Column(Float)  # seconds
    status = Column(String(20), default="completed")  # pending, running, completed, failed
    error_message = Column(Text)
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")
    trades = relationship("Trade", back_populates="backtest", cascade="all, delete-orphan")
    equity_curve = relationship("EquityPoint", back_populates="backtest", cascade="all, delete-orphan")


class Trade(Base):
    """Individual trade record"""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    
    trade_type = Column(String(10), nullable=False)  # BUY, SELL
    entry_date = Column(DateTime(timezone=True))
    exit_date = Column(DateTime(timezone=True))
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    shares = Column(Float, nullable=False)
    
    # P&L
    gross_profit = Column(Float)
    net_profit = Column(Float)  # after commission
    return_pct = Column(Float)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="trades")


class EquityPoint(Base):
    """Equity curve data point"""
    __tablename__ = "equity_points"
    
    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    
    timestamp = Column(DateTime(timezone=True), nullable=False)
    equity = Column(Float, nullable=False)
    position_value = Column(Float, default=0)
    cash = Column(Float)
    
    # Relationships
    backtest = relationship("Backtest", back_populates="equity_curve")


# ============================================================================
# Pydantic Schemas (API)
# ============================================================================

class StrategyInfo(BaseModel):
    """Strategy information"""
    id: str
    name: str
    description: str
    default_params: Dict[str, Any]



class BacktestRequest(BaseModel):
    """Request to run a backtest"""
    strategy_id: str = Field(..., description="Strategy ID to use")
    strategy_type: Optional[str] = Field(None, description="Alias for strategy_id")
    symbol: str = Field(default="BTC/USDT", description="Trading symbol")
    days: int = Field(default=365, ge=1, le=3650, description="Days of historical data")
    initial_capital: float = Field(default=10000, gt=0, description="Initial capital")
    commission: float = Field(default=0.001, ge=0, le=0.1, description="Commission rate")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Strategy parameters")
    use_real_data: bool = Field(default=True, description="Use real market data vs synthetic")
    
    def __init__(self, **data):
        # Allow strategy_type as alias for strategy_id
        if 'strategy_type' in data and 'strategy_id' not in data:
            data['strategy_id'] = data['strategy_type']
        super().__init__(**data)


class BacktestResponse(BaseModel):
    """Response from backtest"""
    success: bool
    message: str
    backtest_id: Optional[int] = None
    results: Optional[Dict[str, Any]] = None


class TradeSchema(BaseModel):
    """Trade information"""
    id: int
    trade_type: str
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    shares: float
    gross_profit: Optional[float]
    net_profit: Optional[float]
    return_pct: Optional[float]
    
    class Config:
        from_attributes = True


class BacktestResult(BaseModel):
    """Backtest result details"""
    id: int
    strategy_id: int
    strategy_name: str
    symbol: str
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    params: Dict[str, Any]
    initial_capital: float
    final_capital: Optional[float]
    total_return: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    total_trades: Optional[int]
    win_rate: Optional[float]
    executed_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class BacktestDetailResult(BacktestResult):
    """Backtest with trades and equity curve"""
    trades: List[TradeSchema] = []
    equity_curve: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True


class MarketDataRequest(BaseModel):
    """Request for market data"""
    symbol: str
    days: int = Field(default=365, ge=1, le=3650)


class MarketDataResponse(BaseModel):
    """Market data response"""
    symbol: str
    data: List[Dict[str, Any]]
    count: int


# ============================================================================
# Broker Pydantic Schemas
# ============================================================================

class BrokerConfigBase(BaseModel):
    """Base schema for broker configuration"""
    broker_name: str
    display_name: str
    broker_type: BrokerType
    logo_url: Optional[str] = None
    requires_api_key: bool = True
    requires_api_secret: bool = True
    requires_passphrase: bool = False
    testnet_available: bool = False
    setup_instructions: Optional[str] = None
    website_url: Optional[str] = None
    is_active: bool = True


class BrokerConfigCreate(BrokerConfigBase):
    """Schema for creating broker config"""
    pass


class BrokerConfigResponse(BrokerConfigBase):
    """Schema for broker config response"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class BrokerCredentialCreate(BaseModel):
    """Schema for creating broker credentials"""
    broker_config_id: int
    api_key: str
    api_secret: Optional[str] = None
    api_passphrase: Optional[str] = None
    is_testnet: bool = False
    is_active: bool = True


class BrokerCredentialUpdate(BaseModel):
    """Schema for updating broker credentials"""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    api_passphrase: Optional[str] = None
    is_testnet: Optional[bool] = None
    is_active: Optional[bool] = None


class BrokerCredentialResponse(BaseModel):
    """Schema for broker credential response (without exposing secrets)"""
    id: int
    user_id: int
    broker_config_id: int
    broker_name: str
    broker_display_name: str
    broker_type: str
    is_active: bool
    is_testnet: bool
    validation_status: str
    last_validated_at: Optional[datetime] = None
    validation_error: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    has_api_key: bool
    has_api_secret: bool
    has_api_passphrase: bool


class BrokerValidationResult(BaseModel):
    """Resultado de validación de credenciales"""
    success: bool
    status: ValidationStatus
    message: str
    details: Optional[Dict[str, Any]] = None

