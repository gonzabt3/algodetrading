"""
Unit tests for api/security.py - Encryption Service
"""
import pytest
from cryptography.fernet import Fernet
from api.security import (
    EncryptionService,
    get_encryption_service,
    encrypt_credential,
    decrypt_credential,
    generate_encryption_key
)


class TestEncryptionService:
    """Test suite for EncryptionService class"""
    
    def test_singleton_pattern(self):
        """Test that get_encryption_service returns the same instance"""
        service1 = get_encryption_service()
        service2 = get_encryption_service()
        assert service1 is service2
    
    def test_encrypt_decrypt_roundtrip(self):
        """Test that encryption and decryption work correctly"""
        service = get_encryption_service()
        original_text = "my_secret_api_key_12345"
        
        # Encrypt
        encrypted = service.encrypt(original_text)
        assert encrypted != original_text
        assert isinstance(encrypted, str)
        
        # Decrypt
        decrypted = service.decrypt(encrypted)
        assert decrypted == original_text
    
    def test_encrypt_empty_string(self):
        """Test encrypting an empty string"""
        service = get_encryption_service()
        encrypted = service.encrypt("")
        decrypted = service.decrypt(encrypted)
        assert decrypted == ""
    
    def test_encrypt_none_returns_none(self):
        """Test that encrypting None returns None"""
        service = get_encryption_service()
        result = service.encrypt(None)
        assert result is None
    
    def test_decrypt_none_returns_none(self):
        """Test that decrypting None returns None"""
        service = get_encryption_service()
        result = service.decrypt(None)
        assert result is None
    
    def test_decrypt_invalid_data_returns_none(self):
        """Test that decrypting invalid data returns None"""
        service = get_encryption_service()
        result = service.decrypt("invalid_encrypted_data")
        assert result is None
    
    def test_encrypt_different_texts_produce_different_results(self):
        """Test that different inputs produce different encrypted outputs"""
        service = get_encryption_service()
        encrypted1 = service.encrypt("secret1")
        encrypted2 = service.encrypt("secret2")
        assert encrypted1 != encrypted2
    
    def test_encrypt_same_text_produces_different_results(self):
        """Test that same input produces different encrypted outputs (due to random IV)"""
        service = get_encryption_service()
        text = "same_secret"
        encrypted1 = service.encrypt(text)
        encrypted2 = service.encrypt(text)
        
        # Different encrypted values due to random initialization vector
        assert encrypted1 != encrypted2
        
        # But both decrypt to same original value
        assert service.decrypt(encrypted1) == text
        assert service.decrypt(encrypted2) == text
    
    def test_encrypt_unicode_text(self):
        """Test encrypting unicode characters"""
        service = get_encryption_service()
        original = "Contraseña 🔐 特殊文字"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)
        assert decrypted == original
    
    def test_encrypt_long_text(self):
        """Test encrypting long text"""
        service = get_encryption_service()
        original = "a" * 10000  # 10KB of 'a' characters
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)
        assert decrypted == original


class TestHelperFunctions:
    """Test suite for helper functions"""
    
    def test_encrypt_credential_helper(self):
        """Test encrypt_credential helper function"""
        original = "my_api_key"
        encrypted = encrypt_credential(original)
        assert encrypted != original
        assert isinstance(encrypted, str)
    
    def test_decrypt_credential_helper(self):
        """Test decrypt_credential helper function"""
        original = "my_api_secret"
        encrypted = encrypt_credential(original)
        decrypted = decrypt_credential(encrypted)
        assert decrypted == original
    
    def test_encrypt_decrypt_credential_none(self):
        """Test helpers with None values"""
        assert encrypt_credential(None) is None
        assert decrypt_credential(None) is None
    
    def test_generate_encryption_key(self):
        """Test that generate_encryption_key produces valid Fernet keys"""
        key1 = generate_encryption_key()
        key2 = generate_encryption_key()
        
        # Keys should be strings
        assert isinstance(key1, str)
        assert isinstance(key2, str)
        
        # Keys should be different
        assert key1 != key2
        
        # Keys should be valid Fernet keys (can create Fernet instance)
        try:
            Fernet(key1.encode())
            Fernet(key2.encode())
        except Exception as e:
            pytest.fail(f"Generated key is not a valid Fernet key: {e}")


class TestEncryptionServiceWithCustomKey:
    """Test EncryptionService with a custom encryption key"""
    
    def test_custom_key(self, monkeypatch):
        """Test using a custom encryption key"""
        # Generate a valid Fernet key
        custom_key = Fernet.generate_key().decode()
        
        # Set environment variable
        monkeypatch.setenv("ENCRYPTION_KEY", custom_key)
        
        # Clear the lru_cache to force new instance
        get_encryption_service.cache_clear()
        
        # Create service with custom key
        service = get_encryption_service()
        
        # Test encryption/decryption works
        original = "test_with_custom_key"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == original
        
        # Cleanup
        get_encryption_service.cache_clear()
    
    def test_auto_generated_key_warning(self, monkeypatch, caplog):
        """Test that auto-generated key produces a warning"""
        import logging
        
        # Remove ENCRYPTION_KEY from environment
        monkeypatch.delenv("ENCRYPTION_KEY", raising=False)
        
        # Clear cache
        get_encryption_service.cache_clear()
        
        # Create service (should auto-generate key)
        with caplog.at_level(logging.WARNING):
            service = get_encryption_service()
        
        # Check warning was logged (check for part of the message)
        assert any("No ENCRYPTION_KEY" in record.message or "ENCRYPTION_KEY not found" in record.message 
                   for record in caplog.records)
        
        # Service should still work
        original = "test"
        encrypted = service.encrypt(original)
        decrypted = service.decrypt(encrypted)
        assert decrypted == original
        
        # Cleanup
        get_encryption_service.cache_clear()


class TestEncryptionEdgeCases:
    """Test edge cases and error handling"""
    
    def test_decrypt_corrupted_data(self):
        """Test decrypting corrupted encrypted data"""
        service = get_encryption_service()
        
        # Encrypt valid data
        encrypted = service.encrypt("valid_data")
        
        # Corrupt the encrypted data (change a character)
        corrupted = encrypted[:-5] + "xxxxx"
        
        # Should return None instead of raising exception
        result = service.decrypt(corrupted)
        assert result is None
    
    def test_encrypt_special_characters(self):
        """Test encrypting special characters"""
        service = get_encryption_service()
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        
        encrypted = service.encrypt(special_chars)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == special_chars
    
    def test_encrypt_newlines_and_tabs(self):
        """Test encrypting text with newlines and tabs"""
        service = get_encryption_service()
        text_with_whitespace = "line1\nline2\tcolumn2"
        
        encrypted = service.encrypt(text_with_whitespace)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == text_with_whitespace
    
    def test_encrypt_json_string(self):
        """Test encrypting a JSON string"""
        service = get_encryption_service()
        json_str = '{"api_key": "abc123", "secret": "xyz789"}'
        
        encrypted = service.encrypt(json_str)
        decrypted = service.decrypt(encrypted)
        
        assert decrypted == json_str


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
