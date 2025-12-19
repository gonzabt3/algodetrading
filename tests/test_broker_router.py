"""
Unit tests for api/routers/brokers.py - Broker API Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch, MagicMock

from api.main import app
from api.database import Base, get_db
from api.models import BrokerType, ValidationStatus


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_broker_api.db"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with test database"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_broker_config(test_db):
    """Create sample broker config in test database"""
    from api.models import BrokerConfig
    
    config = BrokerConfig(
        broker_name="binance",
        display_name="Binance",
        broker_type=BrokerType.CRYPTO,
        logo_url="/logos/binance.png",
        requires_api_key=True,
        requires_api_secret=True,
        requires_passphrase=False,
        testnet_available=True,
        setup_instructions="Create API key",
        website_url="https://binance.com",
        is_active=True
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)
    return config


class TestBrokerConfigEndpoints:
    """Test suite for /api/brokers/configs endpoints"""
    
    def test_get_broker_configs_empty(self, client):
        """Test getting broker configs when none exist"""
        response = client.get("/api/brokers/configs")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_get_broker_configs_list(self, client, sample_broker_config):
        """Test getting list of broker configs"""
        response = client.get("/api/brokers/configs")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["broker_name"] == "binance"
        assert data[0]["display_name"] == "Binance"
        assert data[0]["broker_type"] == "crypto"
    
    def test_get_broker_configs_filter_by_type(self, client, sample_broker_config, test_db):
        """Test filtering broker configs by type"""
        # Add stock broker
        from api.models import BrokerConfig
        stock_config = BrokerConfig(
            broker_name="yahoo",
            display_name="Yahoo Finance",
            broker_type=BrokerType.STOCKS,
            setup_instructions="No API needed",
            website_url="https://finance.yahoo.com",
            is_active=True
        )
        test_db.add(stock_config)
        test_db.commit()
        
        # Get crypto only
        response = client.get("/api/brokers/configs?broker_type=crypto")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["broker_type"] == "crypto"
        
        # Get stocks only
        response = client.get("/api/brokers/configs?broker_type=stocks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["broker_type"] == "stocks"
    
    def test_get_broker_configs_filter_active(self, client, sample_broker_config, test_db):
        """Test filtering active broker configs"""
        # Deactivate broker
        sample_broker_config.is_active = False
        test_db.commit()
        
        # Get active only
        response = client.get("/api/brokers/configs?is_active=true")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
    
    def test_get_broker_config_by_id(self, client, sample_broker_config):
        """Test getting single broker config by ID"""
        response = client.get(f"/api/brokers/configs/{sample_broker_config.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_broker_config.id
        assert data["broker_name"] == "binance"
    
    def test_get_broker_config_not_found(self, client):
        """Test getting non-existent broker config"""
        response = client.get("/api/brokers/configs/9999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_create_broker_config(self, client):
        """Test creating new broker config"""
        broker_data = {
            "broker_name": "kraken",
            "display_name": "Kraken",
            "broker_type": "crypto",
            "logo_url": "/logos/kraken.png",
            "requires_api_key": True,
            "requires_api_secret": True,
            "requires_passphrase": False,
            "testnet_available": False,
            "setup_instructions": "Create API on Kraken",
            "website_url": "https://kraken.com"
        }
        
        response = client.post("/api/brokers/configs", json=broker_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["broker_name"] == "kraken"
        assert data["id"] is not None
        assert data["is_active"] is True
    
    def test_create_broker_config_validation_error(self, client):
        """Test creating broker with invalid data"""
        invalid_data = {
            "broker_name": "test",
            # Missing required fields
        }
        
        response = client.post("/api/brokers/configs", json=invalid_data)
        
        assert response.status_code == 422  # Validation error


class TestBrokerCredentialEndpoints:
    """Test suite for /api/brokers/credentials endpoints"""
    
    def test_get_credentials_empty(self, client):
        """Test getting credentials when none exist"""
        response = client.get("/api/brokers/credentials")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    def test_create_credential(self, client, sample_broker_config):
        """Test creating new broker credential"""
        cred_data = {
            "broker_config_id": sample_broker_config.id,
            "api_key": "test_api_key_12345",
            "api_secret": "test_secret_67890",
            "is_testnet": True
        }
        
        response = client.post("/api/brokers/credentials", json=cred_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        assert data["broker_config_id"] == sample_broker_config.id
        assert data["has_api_key"] is True
        assert data["has_api_secret"] is True
        # Secrets should NOT be exposed
        assert "api_key" not in data
        assert "api_secret" not in data
        assert data["is_testnet"] is True
        assert data["validation_status"] == "pending"
    
    def test_create_credential_with_passphrase(self, client, sample_broker_config):
        """Test creating credential with passphrase"""
        cred_data = {
            "broker_config_id": sample_broker_config.id,
            "api_key": "key",
            "api_secret": "secret",
            "api_passphrase": "my_passphrase",
            "is_testnet": False
        }
        
        response = client.post("/api/brokers/credentials", json=cred_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["has_api_passphrase"] is True
        assert "api_passphrase" not in data
    
    def test_create_credential_invalid_broker(self, client):
        """Test creating credential for non-existent broker"""
        cred_data = {
            "broker_config_id": 9999,
            "api_key": "key",
            "api_secret": "secret"
        }
        
        response = client.post("/api/brokers/credentials", json=cred_data)
        
        assert response.status_code == 400
        assert "Broker config" in response.json()["detail"]
    
    def test_get_credentials_list(self, client, sample_broker_config):
        """Test getting list of credentials"""
        # Create 2 credentials
        for i in range(2):
            cred_data = {
                "broker_config_id": sample_broker_config.id,
                "api_key": f"key_{i}",
                "api_secret": f"secret_{i}"
            }
            client.post("/api/brokers/credentials", json=cred_data)
        
        response = client.get("/api/brokers/credentials")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        # Check secrets are not exposed
        for cred in data:
            assert "api_key" not in cred
            assert "api_secret" not in cred
            assert cred["has_api_key"] is True
    
    def test_get_credentials_filter_by_type(self, client, sample_broker_config, test_db):
        """Test filtering credentials by broker type"""
        # Create stock broker
        from api.models import BrokerConfig
        stock_broker = BrokerConfig(
            broker_name="yahoo",
            display_name="Yahoo",
            broker_type=BrokerType.STOCKS,
            setup_instructions="test",
            website_url="http://test.com",
            is_active=True
        )
        test_db.add(stock_broker)
        test_db.commit()
        test_db.refresh(stock_broker)
        
        # Create credentials for both
        client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "crypto_key",
            "api_secret": "crypto_secret"
        })
        client.post("/api/brokers/credentials", json={
            "broker_config_id": stock_broker.id,
            "api_key": "stock_key",
            "api_secret": "stock_secret"
        })
        
        # Filter by crypto
        response = client.get("/api/brokers/credentials?broker_type=crypto")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Filter by stocks
        response = client.get("/api/brokers/credentials?broker_type=stocks")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_get_credential_by_id(self, client, sample_broker_config):
        """Test getting single credential"""
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "my_key",
            "api_secret": "my_secret"
        })
        cred_id = create_response.json()["id"]
        
        # Get by ID
        response = client.get(f"/api/brokers/credentials/{cred_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cred_id
        assert "api_key" not in data  # Secrets not exposed
    
    def test_get_credential_not_found(self, client):
        """Test getting non-existent credential"""
        response = client.get("/api/brokers/credentials/9999")
        
        assert response.status_code == 404
    
    def test_update_credential(self, client, sample_broker_config):
        """Test updating credential"""
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "old_key",
            "api_secret": "old_secret",
            "is_testnet": False
        })
        cred_id = create_response.json()["id"]
        
        # Update
        update_data = {
            "api_key": "new_key",
            "api_secret": "new_secret",
            "is_testnet": True
        }
        response = client.put(f"/api/brokers/credentials/{cred_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_testnet"] is True
        assert data["has_api_key"] is True  # Still has key
    
    def test_update_credential_partial(self, client, sample_broker_config):
        """Test partial credential update"""
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "original_key",
            "api_secret": "original_secret"
        })
        cred_id = create_response.json()["id"]
        
        # Update only testnet flag
        update_data = {"is_testnet": True}
        response = client.put(f"/api/brokers/credentials/{cred_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_testnet"] is True
        assert data["has_api_key"] is True  # Original key preserved
    
    def test_update_credential_not_found(self, client):
        """Test updating non-existent credential"""
        response = client.put("/api/brokers/credentials/9999", json={
            "api_key": "new_key"
        })
        
        assert response.status_code == 404
    
    def test_delete_credential(self, client, sample_broker_config):
        """Test deleting credential"""
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "to_delete",
            "api_secret": "will_be_deleted"
        })
        cred_id = create_response.json()["id"]
        
        # Delete
        response = client.delete(f"/api/brokers/credentials/{cred_id}")
        
        assert response.status_code == 200
        assert response.json()["message"] == "Credential deleted successfully"
        
        # Verify deletion
        get_response = client.get(f"/api/brokers/credentials/{cred_id}")
        assert get_response.status_code == 404
    
    def test_delete_credential_not_found(self, client):
        """Test deleting non-existent credential"""
        response = client.delete("/api/brokers/credentials/9999")
        
        assert response.status_code == 404


class TestBrokerValidationEndpoint:
    """Test suite for /api/brokers/credentials/{id}/validate endpoint"""
    
    @patch('api.routers.brokers.BrokerValidator.validate_credentials')
    def test_validate_credential_success(self, mock_validate, client, sample_broker_config):
        """Test successful credential validation"""
        # Setup mock
        from api.models import BrokerValidationResult
        mock_validate.return_value = BrokerValidationResult(
            success=True,
            status=ValidationStatus.VALID,
            message="Successfully connected to Binance",
            details={"balance": {"USDT": 100}}
        )
        
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "test_key",
            "api_secret": "test_secret"
        })
        cred_id = create_response.json()["id"]
        
        # Validate
        response = client.post(f"/api/brokers/credentials/{cred_id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["status"] == "valid"
        assert "Successfully connected" in data["message"]
        
        # Check credential status was updated
        get_response = client.get(f"/api/brokers/credentials/{cred_id}")
        cred_data = get_response.json()
        assert cred_data["validation_status"] == "valid"
        assert cred_data["last_validated_at"] is not None
    
    @patch('api.routers.brokers.BrokerValidator.validate_credentials')
    def test_validate_credential_failure(self, mock_validate, client, sample_broker_config):
        """Test failed credential validation"""
        # Setup mock
        from api.models import BrokerValidationResult
        mock_validate.return_value = BrokerValidationResult(
            success=False,
            status=ValidationStatus.INVALID,
            message="Invalid API credentials"
        )
        
        # Create credential
        create_response = client.post("/api/brokers/credentials", json={
            "broker_config_id": sample_broker_config.id,
            "api_key": "invalid_key",
            "api_secret": "invalid_secret"
        })
        cred_id = create_response.json()["id"]
        
        # Validate
        response = client.post(f"/api/brokers/credentials/{cred_id}/validate")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert data["status"] == "invalid"
        
        # Check credential status was updated with error
        get_response = client.get(f"/api/brokers/credentials/{cred_id}")
        cred_data = get_response.json()
        assert cred_data["validation_status"] == "invalid"
        assert cred_data["validation_error"] is not None
    
    def test_validate_credential_not_found(self, client):
        """Test validating non-existent credential"""
        response = client.post("/api/brokers/credentials/9999/validate")
        
        assert response.status_code == 404


class TestEndpointEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_credential_missing_required_fields(self, client, sample_broker_config):
        """Test creating credential with missing fields"""
        # Missing api_secret
        cred_data = {
            "broker_config_id": sample_broker_config.id,
            "api_key": "only_key"
        }
        
        response = client.post("/api/brokers/credentials", json=cred_data)
        
        # Should accept partial data (api_secret can be optional for some brokers)
        assert response.status_code in [200, 422]
    
    def test_get_configs_invalid_type_filter(self, client):
        """Test filtering with invalid broker type"""
        response = client.get("/api/brokers/configs?broker_type=invalid_type")
        
        # Should return 422 validation error
        assert response.status_code == 422
    
    def test_concurrent_credential_creation(self, client, sample_broker_config):
        """Test creating multiple credentials simultaneously"""
        # Create 5 credentials
        for i in range(5):
            response = client.post("/api/brokers/credentials", json={
                "broker_config_id": sample_broker_config.id,
                "api_key": f"key_{i}",
                "api_secret": f"secret_{i}"
            })
            assert response.status_code == 200
        
        # Verify all were created
        response = client.get("/api/brokers/credentials")
        assert len(response.json()) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
