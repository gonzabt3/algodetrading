"""
Script para inicializar los brokers soportados en la base de datos
"""
import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal
from api.models import BrokerConfigCreate, BrokerType
from api import crud_brokers
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Definición de brokers soportados
SUPPORTED_BROKERS = [
    # ==================== CRYPTO ====================
    {
        "broker_name": "binance",
        "display_name": "Binance",
        "broker_type": BrokerType.CRYPTO,
        "logo_url": "/assets/logos/binance.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": False,
        "testnet_available": True,
        "website_url": "https://www.binance.com",
        "setup_instructions": """
1. Go to Binance → Profile → API Management
2. Create a new API key
3. Enable 'Spot & Margin Trading' permission
4. (Optional) Whitelist your IP address
5. Copy API Key and Secret Key
6. Never share your secret key!
        """.strip()
    },
    {
        "broker_name": "kraken",
        "display_name": "Kraken",
        "broker_type": BrokerType.CRYPTO,
        "logo_url": "/assets/logos/kraken.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": False,
        "testnet_available": False,
        "website_url": "https://www.kraken.com",
        "setup_instructions": """
1. Go to Kraken → Settings → API
2. Create new API key
3. Select permissions: 'Query Funds', 'Query Open Orders & Trades'
4. Generate key and copy both API Key and Private Key
        """.strip()
    },
    {
        "broker_name": "coinbase",
        "display_name": "Coinbase Pro",
        "broker_type": BrokerType.CRYPTO,
        "logo_url": "/assets/logos/coinbase.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": True,
        "testnet_available": True,
        "website_url": "https://pro.coinbase.com",
        "setup_instructions": """
1. Go to Coinbase Pro → API
2. Create new API key
3. Select permissions: 'View'
4. Copy API Key, API Secret, and Passphrase
5. Store passphrase safely - it won't be shown again!
        """.strip()
    },
    {
        "broker_name": "kucoin",
        "display_name": "KuCoin",
        "broker_type": BrokerType.CRYPTO,
        "logo_url": "/assets/logos/kucoin.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": True,
        "testnet_available": True,
        "website_url": "https://www.kucoin.com",
        "setup_instructions": """
1. Go to KuCoin → API Management
2. Create new API
3. Set API Passphrase
4. Select permissions: 'General', 'Trade'
5. Copy API Key, Secret Key, and Passphrase
        """.strip()
    },
    
    # ==================== STOCKS/INDICES ====================
    {
        "broker_name": "yahoo_finance",
        "display_name": "Yahoo Finance",
        "broker_type": BrokerType.STOCKS,
        "logo_url": "/assets/logos/yahoo.png",
        "requires_api_key": False,
        "requires_api_secret": False,
        "requires_passphrase": False,
        "testnet_available": False,
        "website_url": "https://finance.yahoo.com",
        "setup_instructions": """
Yahoo Finance is free and doesn't require API credentials.
Just enable it and start downloading stock data!

Supports:
- US Stocks (AAPL, MSFT, GOOGL, etc.)
- Global stocks
- ETFs
- Indices (^GSPC, ^DJI, ^IXIC)
- Cryptocurrencies (BTC-USD, ETH-USD)
        """.strip()
    },
    {
        "broker_name": "alpha_vantage",
        "display_name": "Alpha Vantage",
        "broker_type": BrokerType.STOCKS,
        "logo_url": "/assets/logos/alphavantage.png",
        "requires_api_key": True,
        "requires_api_secret": False,
        "requires_passphrase": False,
        "testnet_available": False,
        "website_url": "https://www.alphavantage.co",
        "setup_instructions": """
1. Go to https://www.alphavantage.co/support/#api-key
2. Fill out the form (free tier available)
3. Copy your API key
4. Paste it below

Free tier: 25 requests/day, 5 requests/minute
Premium: $49.99/month for unlimited requests
        """.strip()
    },
    
    # ==================== ARGENTINA 🇦🇷 ====================
    {
        "broker_name": "iol",
        "display_name": "Invertir Online (IOL)",
        "broker_type": BrokerType.ARGENTINA,
        "logo_url": "/assets/logos/iol.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": False,
        "testnet_available": False,
        "website_url": "https://www.invertironline.com",
        "setup_instructions": """
1. Crear cuenta en https://www.invertironline.com
2. Solicitar acceso a API en: https://api.invertironline.com
3. Obtener credenciales de API
4. Usar username como API Key
5. Usar password como API Secret

Nota: Requiere cuenta activa en IOL
        """.strip()
    },
    {
        "broker_name": "ppi",
        "display_name": "Portfolio Personal Inversiones",
        "broker_type": BrokerType.ARGENTINA,
        "logo_url": "/assets/logos/ppi.png",
        "requires_api_key": True,
        "requires_api_secret": True,
        "requires_passphrase": False,
        "testnet_available": False,
        "website_url": "https://www.portfoliopersonal.com",
        "setup_instructions": """
1. Crear cuenta en Portfolio Personal
2. Contactar soporte para acceso a API
3. Documentación: https://api.portfoliopersonal.com
4. Obtener API credentials

Nota: Requiere cuenta activa en PPI
        """.strip()
    },
]


def init_brokers():
    """Inicializa los brokers en la base de datos"""
    db = SessionLocal()
    
    try:
        logger.info("=" * 70)
        logger.info("🚀 INICIALIZANDO BROKERS SOPORTADOS")
        logger.info("=" * 70)
        logger.info("")
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for broker_data in SUPPORTED_BROKERS:
            broker_name = broker_data["broker_name"]
            
            # Verificar si ya existe
            existing = crud_brokers.get_broker_config(db, broker_name=broker_name)
            
            if existing:
                logger.info(f"⚪ {broker_data['display_name']} - Ya existe, saltando...")
                skipped_count += 1
                continue
            
            # Crear nuevo broker
            broker_create = BrokerConfigCreate(**broker_data)
            crud_brokers.create_broker_config(db, broker_create)
            created_count += 1
            logger.info(f"✅ {broker_data['display_name']} - Creado")
        
        logger.info("")
        logger.info("=" * 70)
        logger.info("📊 RESUMEN")
        logger.info("=" * 70)
        logger.info(f"  • Creados: {created_count}")
        logger.info(f"  • Actualizados: {updated_count}")
        logger.info(f"  • Omitidos: {skipped_count}")
        logger.info(f"  • TOTAL: {len(SUPPORTED_BROKERS)} brokers")
        logger.info("")
        
        # Mostrar por tipo
        crypto_count = len([b for b in SUPPORTED_BROKERS if b['broker_type'] == BrokerType.CRYPTO])
        stocks_count = len([b for b in SUPPORTED_BROKERS if b['broker_type'] == BrokerType.STOCKS])
        argentina_count = len([b for b in SUPPORTED_BROKERS if b['broker_type'] == BrokerType.ARGENTINA])
        
        logger.info("Por tipo:")
        logger.info(f"  • Crypto: {crypto_count} brokers")
        logger.info(f"  • Stocks: {stocks_count} brokers")
        logger.info(f"  • Argentina 🇦🇷: {argentina_count} brokers")
        logger.info("")
        logger.info("✅ Inicialización completada!")
        
    except Exception as e:
        logger.error(f"❌ Error inicializando brokers: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_brokers()
