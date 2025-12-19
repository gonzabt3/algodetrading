"""
Security utilities for encryption/decryption of sensitive data
"""
import os
import logging
from typing import Optional
from cryptography.fernet import Fernet
from functools import lru_cache

logger = logging.getLogger(__name__)


class EncryptionService:
    """Servicio de encriptación/desencriptación de credenciales"""
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Inicializa el servicio de encriptación
        
        Args:
            encryption_key: Key de encriptación (si None, usa variable de entorno)
        """
        if encryption_key is None:
            encryption_key = os.getenv("ENCRYPTION_KEY")
            
        if not encryption_key:
            # Generar una key temporal para desarrollo
            temp_key = Fernet.generate_key().decode()
            logger.warning("⚠️  No ENCRYPTION_KEY found in environment")
            logger.warning(f"⚠️  Using temporary key (will cause issues on restart)")
            logger.warning(f"⚠️  Add to .env: ENCRYPTION_KEY={temp_key}")
            encryption_key = temp_key
        
        # Si es string, convertir a bytes
        if isinstance(encryption_key, str):
            encryption_key = encryption_key.encode()
            
        try:
            self.cipher = Fernet(encryption_key)
        except Exception as e:
            logger.error(f"❌ Invalid encryption key: {e}")
            # Generar nueva key como fallback
            new_key = Fernet.generate_key()
            logger.warning(f"⚠️  Generated new key: {new_key.decode()}")
            self.cipher = Fernet(new_key)
    
    def encrypt(self, plain_text: str) -> str:
        """
        Encripta un texto
        
        Args:
            plain_text: Texto a encriptar
            
        Returns:
            Texto encriptado (base64) o None si input es None
        """
        if plain_text is None:
            return None
            
        if not plain_text:
            return ""
            
        try:
            encrypted_bytes = self.cipher.encrypt(plain_text.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error encrypting: {e}")
            raise ValueError(f"Encryption failed: {e}")
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Desencripta un texto
        
        Args:
            encrypted_text: Texto encriptado
            
        Returns:
            Texto desencriptado o None si es inválido/corrupto
        """
        if encrypted_text is None:
            return None
            
        if not encrypted_text:
            return ""
            
        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_text.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"Error decrypting: {e}")
            return None  # Return None instead of raising exception for invalid/corrupted data


@lru_cache()
def get_encryption_service() -> EncryptionService:
    """
    Obtiene instancia singleton del servicio de encriptación
    
    Returns:
        EncryptionService instance
    """
    return EncryptionService()


# Helper functions
def encrypt_credential(value: str) -> str:
    """
    Encripta una credencial
    
    Args:
        value: Valor a encriptar
        
    Returns:
        Valor encriptado
    """
    service = get_encryption_service()
    return service.encrypt(value)


def decrypt_credential(value: str) -> str:
    """
    Desencripta una credencial
    
    Args:
        value: Valor encriptado
        
    Returns:
        Valor desencriptado
    """
    service = get_encryption_service()
    return service.decrypt(value)


def generate_encryption_key() -> str:
    """
    Genera una nueva encryption key
    
    Returns:
        Encryption key en formato string
    """
    return Fernet.generate_key().decode()


if __name__ == '__main__':
    # Test del sistema de encriptación
    print("🔐 Testing Encryption Service")
    print("=" * 50)
    
    # Generar nueva key
    key = generate_encryption_key()
    print(f"Generated Key: {key}")
    print()
    
    # Test con la key generada
    service = EncryptionService(key)
    
    # Test de encriptación
    test_data = "my_secret_api_key_12345"
    print(f"Original: {test_data}")
    
    encrypted = service.encrypt(test_data)
    print(f"Encrypted: {encrypted}")
    
    decrypted = service.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert test_data == decrypted, "Encryption/Decryption failed!"
    print()
    print("✅ Encryption test passed!")
    print()
    print("Add this to your .env file:")
    print(f"ENCRYPTION_KEY={key}")
