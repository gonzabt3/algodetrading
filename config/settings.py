# Trading Configuration

# Exchange settings
EXCHANGE = "binance"
API_KEY = "your_api_key_here"  # Replace with your actual API key
API_SECRET = "your_api_secret_here"  # Replace with your actual API secret

# Trading parameters
DEFAULT_CAPITAL = 10000.0
COMMISSION = 0.001  # 0.1% commission
SLIPPAGE = 0.0005  # 0.05% slippage

# Risk management
MAX_POSITION_SIZE = 0.95  # Maximum 95% of capital per position
MAX_RISK_PER_TRADE = 0.02  # Maximum 2% risk per trade
MAX_DRAWDOWN = 0.20  # Stop trading if drawdown exceeds 20%

# Data settings
DEFAULT_TIMEFRAME = "1d"
DEFAULT_HISTORY_DAYS = 365

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "logs/trading.log"
