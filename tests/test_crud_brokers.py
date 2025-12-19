"""
Unit tests for api/crud_brokers.py - Broker CRUD Operations
"""
import pytest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.database import Base
from api.models import BrokerConfig, BrokerCredential, BrokerType, ValidationStatus
from api.crud_brokers import (
    get_broker_configs,
    get_broker_config,
    create_broker_config,
    update_broker_config,
    get_broker_credentials,
    get_broker_credential,
    create_broker_credential,
    update_broker_credential,
    delete_broker_credential,
    update_validation_status
)
from api.security import encrypt_credential


# Test database setup
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test_brokers.db"


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


@pytest.fixture
def sample_broker_config(test_db):
    """Create a sample broker config for testing"""
    config = BrokerConfig(
        broker_name="test_binance",
        display_name="Test Binance",
        broker_type=BrokerType.CRYPTO,
        logo_url="/logos/binance.png",
        requires_api_key=True,
        requires_api_secret=True,
        requires_passphrase=False,
        testnet_available=True,
        setup_instructions="Test instructions",
        website_url="https://test.binance.com",
        is_active=True
    )
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)
    return config


class TestBrokerConfigCRUD:
    """Test suite for BrokerConfig CRUD operations"""
    
    def test_create_broker_config(self, test_db):
        """Test creating a new broker config"""
        from api.models import BrokerConfigCreate
        
        broker_data = BrokerConfigCreate(
            broker_name="kraken",
            display_name="Kraken Exchange",
            broker_type=BrokerType.CRYPTO,
            logo_url="/logos/kraken.png",
            requires_api_key=True,
            requires_api_secret=True,
            requires_passphrase=False,
            testnet_available=False,
            setup_instructions="Create API key on Kraken",
            website_url="https://www.kraken.com"
        )
        
        created = create_broker_config(test_db, broker_data)
        
        assert created.id is not None
        assert created.broker_name == "kraken"
        assert created.display_name == "Kraken Exchange"
        assert created.broker_type == BrokerType.CRYPTO
        assert created.is_active is True
        assert created.created_at is not None
    
    def test_get_broker_configs_all(self, test_db, sample_broker_config):
        """Test retrieving all broker configs"""
        configs = get_broker_configs(test_db)
        
        assert len(configs) == 1
        assert configs[0].broker_name == "test_binance"
    
    def test_get_broker_configs_by_type(self, test_db, sample_broker_config):
        """Test filtering broker configs by type"""
        # Add another broker of different type
        from api.models import BrokerConfigCreate
        yahoo_data = BrokerConfigCreate(
            broker_name="yahoo",
            display_name="Yahoo Finance",
            broker_type=BrokerType.STOCKS,
            logo_url="/logos/yahoo.png",
            requires_api_key=False,
            setup_instructions="No API key needed",
            website_url="https://finance.yahoo.com"
        )
        create_broker_config(test_db, yahoo_data)
        
        # Get only crypto brokers
        crypto_configs = get_broker_configs(test_db, broker_type=BrokerType.CRYPTO)
        assert len(crypto_configs) == 1
        assert crypto_configs[0].broker_type == BrokerType.CRYPTO
        
        # Get only stock brokers
        stock_configs = get_broker_configs(test_db, broker_type=BrokerType.STOCKS)
        assert len(stock_configs) == 1
        assert stock_configs[0].broker_type == BrokerType.STOCKS
    
    def test_get_broker_configs_active_only(self, test_db, sample_broker_config):
        """Test filtering only active broker configs"""
        # Deactivate the sample broker
        sample_broker_config.is_active = False
        test_db.commit()
        
        # Get active only
        active_configs = get_broker_configs(test_db, is_active=True)
        assert len(active_configs) == 0
        
        # Get all
        all_configs = get_broker_configs(test_db, is_active=None)
        assert len(all_configs) == 1
    
    def test_get_broker_config_by_id(self, test_db, sample_broker_config):
        """Test getting broker config by ID"""
        config = get_broker_config(test_db, broker_id=sample_broker_config.id)
        
        assert config is not None
        assert config.id == sample_broker_config.id
        assert config.broker_name == "test_binance"
    
    def test_get_broker_config_by_name(self, test_db, sample_broker_config):
        """Test getting broker config by name"""
        config = get_broker_config(test_db, broker_name="test_binance")
        
        assert config is not None
        assert config.broker_name == "test_binance"
    
    def test_get_broker_config_not_found(self, test_db):
        """Test getting non-existent broker config"""
        config = get_broker_config(test_db, broker_id=9999)
        assert config is None
        
        config = get_broker_config(test_db, broker_name="nonexistent")
        assert config is None
    
    def test_update_broker_config(self, test_db, sample_broker_config):
        """Test updating broker config"""
        from api.models import BrokerConfigCreate
        
        update_data = BrokerConfigCreate(
            broker_name="test_binance",
            display_name="Updated Binance",
            broker_type=BrokerType.CRYPTO,
            logo_url="/logos/binance_new.png",
            requires_api_key=True,
            requires_api_secret=True,
            setup_instructions="Updated instructions",
            website_url="https://updated.binance.com"
        )
        
        updated = update_broker_config(test_db, sample_broker_config.id, update_data)
        
        assert updated.display_name == "Updated Binance"
        assert updated.logo_url == "/logos/binance_new.png"
        assert updated.setup_instructions == "Updated instructions"


class TestBrokerCredentialCRUD:
    """Test suite for BrokerCredential CRUD operations"""
    
    def test_create_broker_credential(self, test_db, sample_broker_config):
        """Test creating new broker credentials"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="test_api_key_123",
            api_secret="test_secret_456",
            is_testnet=True
        )
        
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        assert created.id is not None
        assert created.user_id == 1
        assert created.broker_config_id == sample_broker_config.id
        assert created.api_key_encrypted is not None
        assert created.api_key_encrypted != "test_api_key_123"  # Should be encrypted
        assert created.is_testnet is True
        assert created.validation_status == ValidationStatus.PENDING
    
    def test_create_credential_with_passphrase(self, test_db, sample_broker_config):
        """Test creating credentials with passphrase"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="key",
            api_secret="secret",
            api_passphrase="passphrase123",
            is_testnet=False
        )
        
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        assert created.api_passphrase_encrypted is not None
        assert created.api_passphrase_encrypted != "passphrase123"
    
    def test_get_broker_credentials_list(self, test_db, sample_broker_config):
        """Test getting list of credentials without secrets"""
        from api.models import BrokerCredentialCreate
        
        # Create 2 credentials
        for i in range(2):
            cred_data = BrokerCredentialCreate(
                broker_config_id=sample_broker_config.id,
                api_key=f"key_{i}",
                api_secret=f"secret_{i}"
            )
            create_broker_credential(test_db, cred_data, user_id=1)
        
        credentials = get_broker_credentials(test_db, user_id=1)
        
        assert len(credentials) == 2
        # Check secrets are not exposed
        for cred in credentials:
            assert hasattr(cred, 'has_api_key')
            assert cred.has_api_key is True
            # api_key should not be in response
            assert not hasattr(cred, 'api_key')
    
    def test_get_credentials_filtered_by_type(self, test_db, sample_broker_config):
        """Test filtering credentials by broker type"""
        from api.models import BrokerCredentialCreate, BrokerConfigCreate
        
        # Create stock broker config
        stock_broker_data = BrokerConfigCreate(
            broker_name="yahoo",
            display_name="Yahoo",
            broker_type=BrokerType.STOCKS,
            setup_instructions="test",
            website_url="http://test.com"
        )
        stock_broker = create_broker_config(test_db, stock_broker_data)
        
        # Create credentials for both brokers
        crypto_cred = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="crypto_key",
            api_secret="crypto_secret"
        )
        create_broker_credential(test_db, crypto_cred, user_id=1)
        
        stock_cred = BrokerCredentialCreate(
            broker_config_id=stock_broker.id,
            api_key="stock_key",
            api_secret="stock_secret"
        )
        create_broker_credential(test_db, stock_cred, user_id=1)
        
        # Filter by crypto
        crypto_creds = get_broker_credentials(test_db, user_id=1, broker_type=BrokerType.CRYPTO)
        assert len(crypto_creds) == 1
        
        # Filter by stocks
        stock_creds = get_broker_credentials(test_db, user_id=1, broker_type=BrokerType.STOCKS)
        assert len(stock_creds) == 1
    
    def test_get_broker_credential_with_decryption(self, test_db, sample_broker_config):
        """Test getting single credential with decryption"""
        from api.models import BrokerCredentialCreate
        
        original_key = "my_api_key_789"
        original_secret = "my_secret_xyz"
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key=original_key,
            api_secret=original_secret
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Get without decryption
        cred_no_decrypt = get_broker_credential(test_db, created.id, user_id=1, decrypt=False)
        assert not hasattr(cred_no_decrypt, 'api_key_decrypted')
        
        # Get with decryption
        cred_decrypted = get_broker_credential(test_db, created.id, user_id=1, decrypt=True)
        assert cred_decrypted.api_key_decrypted == original_key
        assert cred_decrypted.api_secret_decrypted == original_secret
    
    def test_get_credential_user_ownership(self, test_db, sample_broker_config):
        """Test that users can only access their own credentials"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="user1_key",
            api_secret="user1_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # User 1 can access
        cred = get_broker_credential(test_db, created.id, user_id=1)
        assert cred is not None
        
        # User 2 cannot access
        cred = get_broker_credential(test_db, created.id, user_id=2)
        assert cred is None
    
    def test_update_broker_credential(self, test_db, sample_broker_config):
        """Test updating credentials"""
        from api.models import BrokerCredentialCreate, BrokerCredentialUpdate
        
        # Create credential
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="old_key",
            api_secret="old_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Update
        update_data = BrokerCredentialUpdate(
            api_key="new_key",
            api_secret="new_secret",
            is_testnet=True
        )
        updated = update_broker_credential(test_db, created.id, update_data, user_id=1)
        
        # Verify update
        assert updated.is_testnet is True
        
        # Verify decrypted values
        cred = get_broker_credential(test_db, created.id, user_id=1, decrypt=True)
        assert cred.api_key_decrypted == "new_key"
        assert cred.api_secret_decrypted == "new_secret"
    
    def test_update_credential_partial(self, test_db, sample_broker_config):
        """Test partial credential update (only some fields)"""
        from api.models import BrokerCredentialCreate, BrokerCredentialUpdate
        
        # Create credential
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="original_key",
            api_secret="original_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Update only api_key
        update_data = BrokerCredentialUpdate(api_key="updated_key")
        updated = update_broker_credential(test_db, created.id, update_data, user_id=1)
        
        # Verify
        cred = get_broker_credential(test_db, created.id, user_id=1, decrypt=True)
        assert cred.api_key_decrypted == "updated_key"
        assert cred.api_secret_decrypted == "original_secret"  # Should remain unchanged
    
    def test_delete_broker_credential(self, test_db, sample_broker_config):
        """Test deleting credentials"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="to_delete",
            api_secret="will_be_deleted"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Delete
        result = delete_broker_credential(test_db, created.id, user_id=1)
        assert result is True
        
        # Verify deletion
        cred = get_broker_credential(test_db, created.id, user_id=1)
        assert cred is None
    
    def test_delete_credential_user_ownership(self, test_db, sample_broker_config):
        """Test that users can only delete their own credentials"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="user1_key",
            api_secret="user1_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # User 2 cannot delete user 1's credential
        result = delete_broker_credential(test_db, created.id, user_id=2)
        assert result is False
        
        # Credential still exists
        cred = get_broker_credential(test_db, created.id, user_id=1)
        assert cred is not None
    
    def test_update_validation_status(self, test_db, sample_broker_config):
        """Test updating validation status"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="test_key",
            api_secret="test_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Update to valid
        updated = update_validation_status(
            test_db,
            created.id,
            ValidationStatus.VALID,
            error=None
        )
        
        assert updated.validation_status == ValidationStatus.VALID
        assert updated.validation_error is None
        assert updated.last_validated_at is not None
    
    def test_update_validation_status_with_error(self, test_db, sample_broker_config):
        """Test updating validation status with error message"""
        from api.models import BrokerCredentialCreate
        
        cred_data = BrokerCredentialCreate(
            broker_config_id=sample_broker_config.id,
            api_key="invalid_key",
            api_secret="invalid_secret"
        )
        created = create_broker_credential(test_db, cred_data, user_id=1)
        
        # Update to invalid with error
        error_msg = "Invalid API key: Authentication failed"
        updated = update_validation_status(
            test_db,
            created.id,
            ValidationStatus.INVALID,
            error=error_msg
        )
        
        assert updated.validation_status == ValidationStatus.INVALID
        assert updated.validation_error == error_msg
        assert updated.last_validated_at is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
