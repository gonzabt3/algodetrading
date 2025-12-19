"""
Broker validation service
"""
import logging
from typing import Dict, Any, Optional
import ccxt

from .models import BrokerValidationResult, ValidationStatus

logger = logging.getLogger(__name__)


class BrokerValidator:
    """Validador de credenciales de brokers"""
    
    @staticmethod
    def validate_ccxt_broker(
        broker_name: str,
        api_key: str,
        api_secret: str,
        is_testnet: bool = False
    ) -> BrokerValidationResult:
        """
        Valida credenciales de un broker CCXT (crypto)
        
        Args:
            broker_name: Nombre del broker (binance, kraken, etc.)
            api_key: API key
            api_secret: API secret
            is_testnet: Si usar testnet
            
        Returns:
            BrokerValidationResult
        """
        try:
            # Obtener clase del broker
            if not hasattr(ccxt, broker_name):
                return BrokerValidationResult(
                    success=False,
                    status=ValidationStatus.ERROR,
                    message=f"Broker '{broker_name}' not supported by CCXT"
                )
            
            exchange_class = getattr(ccxt, broker_name)
            
            # Configurar exchange
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'enableRateLimit': True,
            }
            
            if is_testnet:
                config['options'] = {'defaultType': 'test'}
            
            exchange = exchange_class(config)
            
            # Test: fetch balance
            balance = exchange.fetch_balance()
            
            return BrokerValidationResult(
                success=True,
                status=ValidationStatus.VALID,
                message=f"Successfully connected to {broker_name}",
                details={
                    "total_balance": balance.get('total', {}),
                    "currencies": list(balance.get('total', {}).keys())[:5]
                }
            )
            
        except ccxt.AuthenticationError as e:
            logger.warning(f"Authentication failed for {broker_name}: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.INVALID,
                message="Authentication failed. Check your API key and secret.",
                details={"error": str(e)}
            )
            
        except ccxt.PermissionDenied as e:
            logger.warning(f"Permission denied for {broker_name}: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.INVALID,
                message="Permission denied. Enable 'Read' permission for your API key.",
                details={"error": str(e)}
            )
            
        except ccxt.NetworkError as e:
            logger.error(f"Network error for {broker_name}: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message="Network error. Please try again later.",
                details={"error": str(e)}
            )
            
        except Exception as e:
            logger.error(f"Unexpected error validating {broker_name}: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {str(e)}",
                details={"error": str(e), "type": type(e).__name__}
            )
    
    @staticmethod
    def validate_yahoo_finance() -> BrokerValidationResult:
        """
        Valida Yahoo Finance (no requiere credenciales)
        
        Returns:
            BrokerValidationResult
        """
        try:
            import yfinance as yf
            
            # Test: descargar un símbolo
            test_ticker = yf.Ticker("AAPL")
            info = test_ticker.info
            
            if info and 'symbol' in info:
                return BrokerValidationResult(
                    success=True,
                    status=ValidationStatus.VALID,
                    message="Yahoo Finance is accessible",
                    details={"test_symbol": "AAPL", "available": True}
                )
            else:
                return BrokerValidationResult(
                    success=False,
                    status=ValidationStatus.ERROR,
                    message="Yahoo Finance returned empty response"
                )
                
        except Exception as e:
            logger.error(f"Yahoo Finance validation failed: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message=f"Yahoo Finance validation failed: {str(e)}"
            )
    
    @staticmethod
    def validate_alpha_vantage(
        api_key: str
    ) -> BrokerValidationResult:
        """
        Valida credenciales de Alpha Vantage
        
        Args:
            api_key: API key
            
        Returns:
            BrokerValidationResult
        """
        try:
            import requests
            
            url = "https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': 'IBM',
                'interval': '5min',
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Error Message' in data:
                return BrokerValidationResult(
                    success=False,
                    status=ValidationStatus.INVALID,
                    message="Invalid API key"
                )
            
            if 'Note' in data:
                # API call limit reached
                return BrokerValidationResult(
                    success=True,
                    status=ValidationStatus.VALID,
                    message="API key valid but rate limit reached",
                    details={"note": data['Note']}
                )
            
            if 'Meta Data' in data:
                return BrokerValidationResult(
                    success=True,
                    status=ValidationStatus.VALID,
                    message="Alpha Vantage API key validated successfully"
                )
            
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message="Unexpected response from Alpha Vantage"
            )
            
        except Exception as e:
            logger.error(f"Alpha Vantage validation failed: {e}")
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message=f"Validation failed: {str(e)}"
            )
    
    @staticmethod
    def validate_credentials(
        broker_name: str,
        broker_type: str,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        api_passphrase: Optional[str] = None,
        is_testnet: bool = False
    ) -> BrokerValidationResult:
        """
        Valida credenciales según el tipo de broker
        
        Args:
            broker_name: Nombre del broker
            broker_type: Tipo (crypto, stocks, etc.)
            api_key: API key
            api_secret: API secret
            api_passphrase: API passphrase (opcional)
            is_testnet: Si usar testnet
            
        Returns:
            BrokerValidationResult
        """
        logger.info(f"🔍 Validating {broker_name} ({broker_type})")
        
        # Yahoo Finance (sin credenciales)
        if broker_name == 'yahoo_finance':
            return BrokerValidator.validate_yahoo_finance()
        
        # Alpha Vantage
        if broker_name == 'alpha_vantage':
            if not api_key:
                return BrokerValidationResult(
                    success=False,
                    status=ValidationStatus.INVALID,
                    message="API key is required"
                )
            return BrokerValidator.validate_alpha_vantage(api_key)
        
        # Brokers CCXT (crypto)
        if broker_type == 'crypto':
            if not api_key or not api_secret:
                return BrokerValidationResult(
                    success=False,
                    status=ValidationStatus.INVALID,
                    message="API key and secret are required"
                )
            return BrokerValidator.validate_ccxt_broker(
                broker_name, api_key, api_secret, is_testnet
            )
        
        # Brokers argentinos (futura implementación)
        if broker_type == 'argentina':
            # TODO: Implementar validación para IOL, PPI, etc.
            return BrokerValidationResult(
                success=False,
                status=ValidationStatus.ERROR,
                message=f"Validation not implemented for {broker_name}"
            )
        
        return BrokerValidationResult(
            success=False,
            status=ValidationStatus.ERROR,
            message=f"Unknown broker type: {broker_type}"
        )
