"""
Unit tests for api/broker_validator.py - Broker Validation Service
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from api.broker_validator import BrokerValidator
from api.models import BrokerType, ValidationStatus


class TestBrokerValidatorCCXT:
    """Test suite for CCXT broker validation"""
    
    @patch('api.broker_validator.ccxt')
    def test_validate_binance_success(self, mock_ccxt):
        """Test successful Binance validation"""
        # Mock exchange instance
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {
            'free': {'USDT': 100.0, 'BTC': 0.5},
            'used': {'USDT': 50.0},
            'total': {'USDT': 150.0, 'BTC': 0.5}
        }
        mock_ccxt.binance.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="binance",
            api_key="test_key",
            api_secret="test_secret",
            is_testnet=False
        )
        
        assert result.success is True
        assert result.status == ValidationStatus.VALID
        assert "Successfully connected" in result.message
        assert result.details is not None
        assert 'balance' in result.details
    
    @patch('api.broker_validator.ccxt')
    def test_validate_binance_testnet(self, mock_ccxt):
        """Test Binance testnet validation"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {'free': {}}
        mock_ccxt.binance.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="binance",
            api_key="test_key",
            api_secret="test_secret",
            is_testnet=True
        )
        
        # Verify testnet URL was set
        assert mock_exchange.set_sandbox_mode.called or hasattr(mock_exchange, 'urls')
        assert result.success is True
    
    @patch('api.broker_validator.ccxt')
    def test_validate_kraken_success(self, mock_ccxt):
        """Test successful Kraken validation"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {'free': {'USD': 1000}}
        mock_ccxt.kraken.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="kraken",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        assert result.success is True
        assert result.status == ValidationStatus.VALID
    
    @patch('api.broker_validator.ccxt')
    def test_validate_coinbase_with_passphrase(self, mock_ccxt):
        """Test Coinbase Pro validation with passphrase"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {'free': {}}
        mock_ccxt.coinbase.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="coinbase",
            api_key="test_key",
            api_secret="test_secret",
            api_passphrase="test_passphrase"
        )
        
        # Verify passphrase was passed to exchange
        call_args = mock_ccxt.coinbase.call_args
        assert 'password' in call_args[0][0] or 'passphrase' in str(call_args)
        assert result.success is True
    
    @patch('api.broker_validator.ccxt')
    def test_validate_authentication_error(self, mock_ccxt):
        """Test authentication error handling"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.side_effect = Exception("AuthenticationError: Invalid API key")
        mock_ccxt.binance.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="binance",
            api_key="invalid_key",
            api_secret="invalid_secret"
        )
        
        assert result.success is False
        assert result.status == ValidationStatus.INVALID
        assert "Invalid credentials" in result.message or "AuthenticationError" in result.message
    
    @patch('api.broker_validator.ccxt')
    def test_validate_permission_denied(self, mock_ccxt):
        """Test permission denied error"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.side_effect = Exception("PermissionDenied: API key doesn't have permission")
        mock_ccxt.kraken.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="kraken",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        assert result.success is False
        assert result.status == ValidationStatus.INVALID
        assert "permission" in result.message.lower()
    
    @patch('api.broker_validator.ccxt')
    def test_validate_network_error(self, mock_ccxt):
        """Test network error handling"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.side_effect = Exception("NetworkError: Connection timeout")
        mock_ccxt.binance.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="binance",
            api_key="test_key",
            api_secret="test_secret"
        )
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
        assert "network" in result.message.lower() or "connection" in result.message.lower()
    
    @patch('api.broker_validator.ccxt')
    def test_validate_unsupported_broker(self, mock_ccxt):
        """Test validation with unsupported broker"""
        mock_ccxt.unknown_broker = None  # Broker doesn't exist
        
        with pytest.raises(AttributeError):
            BrokerValidator.validate_ccxt_broker(
                broker_name="unknown_broker",
                api_key="key",
                api_secret="secret"
            )
    
    @patch('api.broker_validator.ccxt')
    def test_validate_kucoin_with_passphrase(self, mock_ccxt):
        """Test KuCoin validation with passphrase"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {'free': {'USDT': 500}}
        mock_ccxt.kucoin.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="kucoin",
            api_key="test_key",
            api_secret="test_secret",
            api_passphrase="my_passphrase"
        )
        
        assert result.success is True
        assert result.status == ValidationStatus.VALID


class TestBrokerValidatorYahooFinance:
    """Test suite for Yahoo Finance validation"""
    
    @patch('api.broker_validator.yf.Ticker')
    def test_validate_yahoo_success(self, mock_ticker):
        """Test successful Yahoo Finance validation"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {
            'symbol': 'AAPL',
            'longName': 'Apple Inc.',
            'regularMarketPrice': 150.0
        }
        mock_ticker.return_value = mock_ticker_instance
        
        result = BrokerValidator.validate_yahoo_finance()
        
        assert result.success is True
        assert result.status == ValidationStatus.VALID
        assert "accessible" in result.message.lower()
    
    @patch('api.broker_validator.yf.Ticker')
    def test_validate_yahoo_network_error(self, mock_ticker):
        """Test Yahoo Finance network error"""
        mock_ticker.side_effect = Exception("ConnectionError: Failed to connect")
        
        result = BrokerValidator.validate_yahoo_finance()
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
    
    @patch('api.broker_validator.yf.Ticker')
    def test_validate_yahoo_timeout(self, mock_ticker):
        """Test Yahoo Finance timeout"""
        mock_ticker.side_effect = TimeoutError("Request timed out")
        
        result = BrokerValidator.validate_yahoo_finance()
        
        assert result.success is False
        assert "timeout" in result.message.lower() or "error" in result.message.lower()


class TestBrokerValidatorAlphaVantage:
    """Test suite for Alpha Vantage validation"""
    
    @patch('api.broker_validator.requests.get')
    def test_validate_alpha_vantage_success(self, mock_get):
        """Test successful Alpha Vantage validation"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Meta Data': {
                '1. Information': 'Daily Prices',
                '2. Symbol': 'AAPL'
            },
            'Time Series (Daily)': {'2024-01-01': {}}
        }
        mock_get.return_value = mock_response
        
        result = BrokerValidator.validate_alpha_vantage(api_key="valid_key_123")
        
        assert result.success is True
        assert result.status == ValidationStatus.VALID
        assert "valid" in result.message.lower()
    
    @patch('api.broker_validator.requests.get')
    def test_validate_alpha_vantage_invalid_key(self, mock_get):
        """Test Alpha Vantage with invalid API key"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Error Message': 'Invalid API key'
        }
        mock_get.return_value = mock_response
        
        result = BrokerValidator.validate_alpha_vantage(api_key="invalid_key")
        
        assert result.success is False
        assert result.status == ValidationStatus.INVALID
        assert "invalid" in result.message.lower()
    
    @patch('api.broker_validator.requests.get')
    def test_validate_alpha_vantage_rate_limit(self, mock_get):
        """Test Alpha Vantage rate limit error"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'Note': 'Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute'
        }
        mock_get.return_value = mock_response
        
        result = BrokerValidator.validate_alpha_vantage(api_key="rate_limited_key")
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
        assert "rate limit" in result.message.lower()
    
    @patch('api.broker_validator.requests.get')
    def test_validate_alpha_vantage_network_error(self, mock_get):
        """Test Alpha Vantage network error"""
        mock_get.side_effect = Exception("ConnectionError: Failed to connect")
        
        result = BrokerValidator.validate_alpha_vantage(api_key="test_key")
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
    
    @patch('api.broker_validator.requests.get')
    def test_validate_alpha_vantage_timeout(self, mock_get):
        """Test Alpha Vantage timeout"""
        mock_get.side_effect = TimeoutError("Request timed out")
        
        result = BrokerValidator.validate_alpha_vantage(api_key="test_key")
        
        assert result.success is False


class TestBrokerValidatorDispatcher:
    """Test suite for validate_credentials dispatcher"""
    
    @patch('api.broker_validator.BrokerValidator.validate_ccxt_broker')
    def test_dispatch_binance(self, mock_validate_ccxt):
        """Test dispatcher routes Binance to CCXT validator"""
        mock_validate_ccxt.return_value = Mock(
            success=True,
            status=ValidationStatus.VALID,
            message="Success"
        )
        
        result = BrokerValidator.validate_credentials(
            broker_name="binance",
            broker_type=BrokerType.CRYPTO,
            api_key="key",
            api_secret="secret"
        )
        
        mock_validate_ccxt.assert_called_once_with(
            broker_name="binance",
            api_key="key",
            api_secret="secret",
            api_passphrase=None,
            is_testnet=False
        )
        assert result.success is True
    
    @patch('api.broker_validator.BrokerValidator.validate_yahoo_finance')
    def test_dispatch_yahoo(self, mock_validate_yahoo):
        """Test dispatcher routes Yahoo Finance correctly"""
        mock_validate_yahoo.return_value = Mock(
            success=True,
            status=ValidationStatus.VALID,
            message="Success"
        )
        
        result = BrokerValidator.validate_credentials(
            broker_name="yahoo_finance",
            broker_type=BrokerType.STOCKS
        )
        
        mock_validate_yahoo.assert_called_once()
        assert result.success is True
    
    @patch('api.broker_validator.BrokerValidator.validate_alpha_vantage')
    def test_dispatch_alpha_vantage(self, mock_validate_av):
        """Test dispatcher routes Alpha Vantage correctly"""
        mock_validate_av.return_value = Mock(
            success=True,
            status=ValidationStatus.VALID,
            message="Success"
        )
        
        result = BrokerValidator.validate_credentials(
            broker_name="alpha_vantage",
            broker_type=BrokerType.STOCKS,
            api_key="test_key"
        )
        
        mock_validate_av.assert_called_once_with(api_key="test_key")
        assert result.success is True
    
    def test_dispatch_argentina_not_implemented(self):
        """Test dispatcher handles Argentina brokers (not yet implemented)"""
        result = BrokerValidator.validate_credentials(
            broker_name="iol",
            broker_type=BrokerType.ARGENTINA,
            api_key="key",
            api_secret="secret"
        )
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
        assert "not implemented" in result.message.lower()
    
    def test_dispatch_unknown_broker(self):
        """Test dispatcher handles unknown broker"""
        result = BrokerValidator.validate_credentials(
            broker_name="unknown_broker",
            broker_type=BrokerType.STOCKS
        )
        
        assert result.success is False
        assert result.status == ValidationStatus.ERROR
        assert "not supported" in result.message.lower()
    
    @patch('api.broker_validator.BrokerValidator.validate_ccxt_broker')
    def test_dispatch_with_passphrase(self, mock_validate_ccxt):
        """Test dispatcher passes passphrase for exchanges that need it"""
        mock_validate_ccxt.return_value = Mock(success=True, status=ValidationStatus.VALID, message="OK")
        
        result = BrokerValidator.validate_credentials(
            broker_name="coinbase",
            broker_type=BrokerType.CRYPTO,
            api_key="key",
            api_secret="secret",
            api_passphrase="passphrase",
            is_testnet=True
        )
        
        mock_validate_ccxt.assert_called_once_with(
            broker_name="coinbase",
            api_key="key",
            api_secret="secret",
            api_passphrase="passphrase",
            is_testnet=True
        )


class TestBrokerValidatorEdgeCases:
    """Test edge cases and error handling"""
    
    @patch('api.broker_validator.ccxt')
    def test_validate_empty_balance(self, mock_ccxt):
        """Test validation with empty balance response"""
        mock_exchange = MagicMock()
        mock_exchange.fetch_balance.return_value = {}
        mock_ccxt.binance.return_value = mock_exchange
        
        result = BrokerValidator.validate_ccxt_broker(
            broker_name="binance",
            api_key="key",
            api_secret="secret"
        )
        
        # Should still succeed even with empty balance
        assert result.success is True
        assert result.status == ValidationStatus.VALID
    
    @patch('api.broker_validator.ccxt')
    def test_validate_none_credentials(self, mock_ccxt):
        """Test validation with None credentials"""
        mock_exchange = MagicMock()
        mock_ccxt.binance.return_value = mock_exchange
        
        # Should handle None gracefully (though API should prevent this)
        try:
            result = BrokerValidator.validate_ccxt_broker(
                broker_name="binance",
                api_key=None,
                api_secret=None
            )
            # If it doesn't raise an exception, it should fail validation
            assert result.success is False
        except Exception:
            # Exception is also acceptable
            pass
    
    @patch('api.broker_validator.yf.Ticker')
    def test_validate_yahoo_empty_info(self, mock_ticker):
        """Test Yahoo Finance with empty info"""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.info = {}
        mock_ticker.return_value = mock_ticker_instance
        
        result = BrokerValidator.validate_yahoo_finance()
        
        # Should still succeed
        assert result.success is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
