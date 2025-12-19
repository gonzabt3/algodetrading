"""
CRUD operations for broker management
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
import logging

from . import models
from .security import encrypt_credential, decrypt_credential

logger = logging.getLogger(__name__)


# ==================== BROKER CONFIGS ====================

def get_broker_configs(
    db: Session,
    broker_type: Optional[str] = None,
    is_active: bool = True
) -> List[models.BrokerConfig]:
    """
    Obtiene configuraciones de brokers
    
    Args:
        db: Database session
        broker_type: Filtrar por tipo (crypto, stocks, etc.)
        is_active: Filtrar por activos
        
    Returns:
        Lista de BrokerConfig
    """
    query = db.query(models.BrokerConfig)
    
    if broker_type:
        query = query.filter(models.BrokerConfig.broker_type == broker_type)
    
    if is_active:
        query = query.filter(models.BrokerConfig.is_active == True)
    
    return query.all()


def get_broker_config(
    db: Session,
    broker_id: Optional[int] = None,
    broker_name: Optional[str] = None
) -> Optional[models.BrokerConfig]:
    """
    Obtiene una configuración de broker por ID o nombre
    
    Args:
        db: Database session
        broker_id: ID del broker
        broker_name: Nombre del broker
        
    Returns:
        BrokerConfig o None
    """
    if broker_id:
        return db.query(models.BrokerConfig).filter(
            models.BrokerConfig.id == broker_id
        ).first()
    elif broker_name:
        return db.query(models.BrokerConfig).filter(
            models.BrokerConfig.broker_name == broker_name
        ).first()
    return None


def create_broker_config(
    db: Session,
    broker: models.BrokerConfigCreate
) -> models.BrokerConfig:
    """
    Crea una nueva configuración de broker
    
    Args:
        db: Database session
        broker: Datos del broker
        
    Returns:
        BrokerConfig creado
    """
    db_broker = models.BrokerConfig(**broker.dict())
    db.add(db_broker)
    db.commit()
    db.refresh(db_broker)
    
    logger.info(f"✅ Broker config created: {db_broker.broker_name}")
    return db_broker


def update_broker_config(
    db: Session,
    broker_id: int,
    broker_update: models.BrokerConfigBase
) -> Optional[models.BrokerConfig]:
    """
    Actualiza una configuración de broker
    
    Args:
        db: Database session
        broker_id: ID del broker
        broker_update: Datos a actualizar
        
    Returns:
        BrokerConfig actualizado o None
    """
    db_broker = get_broker_config(db, broker_id=broker_id)
    
    if not db_broker:
        return None
    
    update_data = broker_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_broker, key, value)
    
    db.commit()
    db.refresh(db_broker)
    
    logger.info(f"✅ Broker config updated: {db_broker.broker_name}")
    return db_broker


# ==================== BROKER CREDENTIALS ====================

def get_broker_credentials(
    db: Session,
    user_id: int = 1,
    broker_type: Optional[str] = None,
    is_active: Optional[bool] = None
) -> List[models.BrokerCredentialResponse]:
    """
    Obtiene credenciales de brokers (sin exponer secrets)
    
    Args:
        db: Database session
        user_id: ID del usuario
        broker_type: Filtrar por tipo
        is_active: Filtrar por activos
        
    Returns:
        Lista de credenciales (sin secrets)
    """
    query = db.query(models.BrokerCredential).options(
        joinedload(models.BrokerCredential.broker_config)
    ).filter(models.BrokerCredential.user_id == user_id)
    
    if broker_type:
        query = query.join(models.BrokerConfig).filter(
            models.BrokerConfig.broker_type == broker_type
        )
    
    if is_active is not None:
        query = query.filter(models.BrokerCredential.is_active == is_active)
    
    credentials = query.all()
    
    # Transformar a schema sin exponer secrets
    result = []
    for cred in credentials:
        result.append(models.BrokerCredentialResponse(
            id=cred.id,
            user_id=cred.user_id,
            broker_config_id=cred.broker_config_id,
            broker_name=cred.broker_config.broker_name,
            broker_display_name=cred.broker_config.display_name,
            broker_type=cred.broker_config.broker_type,
            is_active=cred.is_active,
            is_testnet=cred.is_testnet,
            validation_status=cred.validation_status,
            last_validated_at=cred.last_validated_at,
            validation_error=cred.validation_error,
            created_at=cred.created_at,
            updated_at=cred.updated_at,
            has_api_key=bool(cred.api_key_encrypted),
            has_api_secret=bool(cred.api_secret_encrypted),
            has_api_passphrase=bool(cred.api_passphrase_encrypted),
        ))
    
    return result


def get_broker_credential(
    db: Session,
    credential_id: int,
    user_id: int = 1,
    decrypt: bool = False
) -> Optional[models.BrokerCredential]:
    """
    Obtiene una credencial específica
    
    Args:
        db: Database session
        credential_id: ID de la credencial
        user_id: ID del usuario (para validar ownership)
        decrypt: Si True, desencripta los secrets
        
    Returns:
        BrokerCredential o None
    """
    cred = db.query(models.BrokerCredential).options(
        joinedload(models.BrokerCredential.broker_config)
    ).filter(
        and_(
            models.BrokerCredential.id == credential_id,
            models.BrokerCredential.user_id == user_id
        )
    ).first()
    
    if not cred:
        return None
    
    if decrypt:
        # Crear objeto temporal con credenciales desencriptadas
        # No modificamos el objeto de DB
        cred.api_key_decrypted = decrypt_credential(cred.api_key_encrypted) if cred.api_key_encrypted else None
        cred.api_secret_decrypted = decrypt_credential(cred.api_secret_encrypted) if cred.api_secret_encrypted else None
        cred.api_passphrase_decrypted = decrypt_credential(cred.api_passphrase_encrypted) if cred.api_passphrase_encrypted else None
    
    return cred


def create_broker_credential(
    db: Session,
    credential: models.BrokerCredentialCreate,
    user_id: int = 1
) -> models.BrokerCredential:
    """
    Crea una nueva credencial de broker
    
    Args:
        db: Database session
        credential: Datos de la credencial
        user_id: ID del usuario
        
    Returns:
        BrokerCredential creado
    """
    # Verificar que el broker config existe
    broker_config = get_broker_config(db, broker_id=credential.broker_config_id)
    if not broker_config:
        raise ValueError(f"Broker config {credential.broker_config_id} not found")
    
    # Encriptar credenciales
    encrypted_data = {
        "user_id": user_id,
        "broker_config_id": credential.broker_config_id,
        "api_key_encrypted": encrypt_credential(credential.api_key) if credential.api_key else None,
        "api_secret_encrypted": encrypt_credential(credential.api_secret) if credential.api_secret else None,
        "api_passphrase_encrypted": encrypt_credential(credential.api_passphrase) if credential.api_passphrase else None,
        "is_testnet": credential.is_testnet,
        "is_active": credential.is_active,
        "validation_status": "pending"
    }
    
    db_credential = models.BrokerCredential(**encrypted_data)
    db.add(db_credential)
    db.commit()
    db.refresh(db_credential)
    
    logger.info(f"✅ Broker credential created: ID {db_credential.id} for {broker_config.display_name}")
    return db_credential


def update_broker_credential(
    db: Session,
    credential_id: int,
    credential_update: models.BrokerCredentialUpdate,
    user_id: int = 1
) -> Optional[models.BrokerCredential]:
    """
    Actualiza una credencial de broker
    
    Args:
        db: Database session
        credential_id: ID de la credencial
        credential_update: Datos a actualizar
        user_id: ID del usuario
        
    Returns:
        BrokerCredential actualizado o None
    """
    db_credential = get_broker_credential(db, credential_id, user_id, decrypt=False)
    
    if not db_credential:
        return None
    
    # Actualizar campos
    update_data = credential_update.dict(exclude_unset=True)
    
    # Encriptar nuevas credenciales si existen
    if "api_key" in update_data and update_data["api_key"]:
        db_credential.api_key_encrypted = encrypt_credential(update_data.pop("api_key"))
    
    if "api_secret" in update_data and update_data["api_secret"]:
        db_credential.api_secret_encrypted = encrypt_credential(update_data.pop("api_secret"))
    
    if "api_passphrase" in update_data and update_data["api_passphrase"]:
        db_credential.api_passphrase_encrypted = encrypt_credential(update_data.pop("api_passphrase"))
    
    # Actualizar otros campos
    for key, value in update_data.items():
        setattr(db_credential, key, value)
    
    # Marcar como pendiente de validación si se actualizaron credenciales
    if any(k in credential_update.dict(exclude_unset=True) for k in ['api_key', 'api_secret', 'api_passphrase']):
        db_credential.validation_status = "pending"
    
    db_credential.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_credential)
    
    logger.info(f"✅ Broker credential updated: ID {credential_id}")
    return db_credential


def delete_broker_credential(
    db: Session,
    credential_id: int,
    user_id: int = 1
) -> bool:
    """
    Elimina una credencial de broker
    
    Args:
        db: Database session
        credential_id: ID de la credencial
        user_id: ID del usuario
        
    Returns:
        True si se eliminó, False si no existía
    """
    db_credential = get_broker_credential(db, credential_id, user_id, decrypt=False)
    
    if not db_credential:
        return False
    
    db.delete(db_credential)
    db.commit()
    
    logger.info(f"✅ Broker credential deleted: ID {credential_id}")
    return True


def update_validation_status(
    db: Session,
    credential_id: int,
    status: str,
    error: Optional[str] = None
) -> Optional[models.BrokerCredential]:
    """
    Actualiza el estado de validación de una credencial
    
    Args:
        db: Database session
        credential_id: ID de la credencial
        status: Estado (pending, valid, invalid, error)
        error: Mensaje de error (opcional)
        
    Returns:
        BrokerCredential actualizado o None
    """
    db_credential = db.query(models.BrokerCredential).filter(
        models.BrokerCredential.id == credential_id
    ).first()
    
    if not db_credential:
        return None
    
    db_credential.validation_status = status
    db_credential.last_validated_at = datetime.utcnow()
    db_credential.validation_error = error
    
    db.commit()
    db.refresh(db_credential)
    
    logger.info(f"✅ Validation status updated: ID {credential_id} -> {status}")
    return db_credential
