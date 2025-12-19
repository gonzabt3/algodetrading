"""
FastAPI router for broker management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from ..database import get_db
from .. import models, crud_brokers
from ..broker_validator import BrokerValidator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/brokers",
    tags=["brokers"]
)


# ==================== BROKER CONFIGS ====================

@router.get("/configs", response_model=List[models.BrokerConfigResponse])
async def get_broker_configs(
    broker_type: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """
    Obtiene la lista de brokers soportados
    
    Args:
        broker_type: Filtrar por tipo (crypto, stocks, argentina, forex)
        is_active: Filtrar solo activos
        
    Returns:
        Lista de configuraciones de brokers
    """
    try:
        configs = crud_brokers.get_broker_configs(db, broker_type, is_active)
        return configs
    except Exception as e:
        logger.error(f"Error getting broker configs: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving broker configurations: {str(e)}"
        )


@router.get("/configs/{broker_id}", response_model=models.BrokerConfigResponse)
async def get_broker_config(
    broker_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene la configuración de un broker específico
    
    Args:
        broker_id: ID del broker
        
    Returns:
        Configuración del broker
    """
    config = crud_brokers.get_broker_config(db, broker_id=broker_id)
    
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Broker config {broker_id} not found"
        )
    
    return config


@router.post("/configs", response_model=models.BrokerConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_broker_config(
    broker: models.BrokerConfigCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva configuración de broker (solo admin)
    
    Args:
        broker: Datos del broker
        
    Returns:
        Broker creado
    """
    try:
        # Verificar que no exista ya
        existing = crud_brokers.get_broker_config(db, broker_name=broker.broker_name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Broker '{broker.broker_name}' already exists"
            )
        
        return crud_brokers.create_broker_config(db, broker)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating broker config: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating broker: {str(e)}"
        )


# ==================== BROKER CREDENTIALS ====================

@router.get("/credentials", response_model=List[models.BrokerCredentialResponse])
async def get_broker_credentials(
    broker_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene las credenciales de brokers del usuario
    
    Args:
        broker_type: Filtrar por tipo
        is_active: Filtrar por activos
        
    Returns:
        Lista de credenciales (sin exponer secrets)
    """
    try:
        # TODO: Obtener user_id del token JWT
        user_id = 1  # Por ahora hardcoded
        
        credentials = crud_brokers.get_broker_credentials(
            db, user_id=user_id, broker_type=broker_type, is_active=is_active
        )
        return credentials
    except Exception as e:
        logger.error(f"Error getting credentials: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving credentials: {str(e)}"
        )


@router.get("/credentials/{credential_id}", response_model=models.BrokerCredentialResponse)
async def get_broker_credential(
    credential_id: int,
    db: Session = Depends(get_db)
):
    """
    Obtiene una credencial específica
    
    Args:
        credential_id: ID de la credencial
        
    Returns:
        Credencial (sin exponer secrets)
    """
    user_id = 1  # TODO: Obtener del token
    
    credential = crud_brokers.get_broker_credential(
        db, credential_id=credential_id, user_id=user_id, decrypt=False
    )
    
    if not credential:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential {credential_id} not found"
        )
    
    # Transformar a response model
    return models.BrokerCredentialResponse(
        id=credential.id,
        user_id=credential.user_id,
        broker_config_id=credential.broker_config_id,
        broker_name=credential.broker_config.broker_name,
        broker_display_name=credential.broker_config.display_name,
        broker_type=credential.broker_config.broker_type,
        is_active=credential.is_active,
        is_testnet=credential.is_testnet,
        validation_status=credential.validation_status,
        last_validated_at=credential.last_validated_at,
        validation_error=credential.validation_error,
        created_at=credential.created_at,
        updated_at=credential.updated_at,
        has_api_key=bool(credential.api_key_encrypted),
        has_api_secret=bool(credential.api_secret_encrypted),
        has_api_passphrase=bool(credential.api_passphrase_encrypted),
    )


@router.post("/credentials", response_model=models.BrokerCredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_broker_credential(
    credential: models.BrokerCredentialCreate,
    db: Session = Depends(get_db)
):
    """
    Crea una nueva credencial de broker
    
    Args:
        credential: Datos de la credencial
        
    Returns:
        Credencial creada (sin exponer secrets)
    """
    try:
        user_id = 1  # TODO: Obtener del token
        
        db_credential = crud_brokers.create_broker_credential(db, credential, user_id)
        
        # Transformar a response
        return models.BrokerCredentialResponse(
            id=db_credential.id,
            user_id=db_credential.user_id,
            broker_config_id=db_credential.broker_config_id,
            broker_name=db_credential.broker_config.broker_name,
            broker_display_name=db_credential.broker_config.display_name,
            broker_type=db_credential.broker_config.broker_type,
            is_active=db_credential.is_active,
            is_testnet=db_credential.is_testnet,
            validation_status=db_credential.validation_status,
            last_validated_at=db_credential.last_validated_at,
            validation_error=db_credential.validation_error,
            created_at=db_credential.created_at,
            updated_at=db_credential.updated_at,
            has_api_key=bool(db_credential.api_key_encrypted),
            has_api_secret=bool(db_credential.api_secret_encrypted),
            has_api_passphrase=bool(db_credential.api_passphrase_encrypted),
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error creating credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating credential: {str(e)}"
        )


@router.put("/credentials/{credential_id}", response_model=models.BrokerCredentialResponse)
async def update_broker_credential(
    credential_id: int,
    credential_update: models.BrokerCredentialUpdate,
    db: Session = Depends(get_db)
):
    """
    Actualiza una credencial de broker
    
    Args:
        credential_id: ID de la credencial
        credential_update: Datos a actualizar
        
    Returns:
        Credencial actualizada
    """
    try:
        user_id = 1  # TODO: Obtener del token
        
        db_credential = crud_brokers.update_broker_credential(
            db, credential_id, credential_update, user_id
        )
        
        if not db_credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential {credential_id} not found"
            )
        
        return models.BrokerCredentialResponse(
            id=db_credential.id,
            user_id=db_credential.user_id,
            broker_config_id=db_credential.broker_config_id,
            broker_name=db_credential.broker_config.broker_name,
            broker_display_name=db_credential.broker_config.display_name,
            broker_type=db_credential.broker_config.broker_type,
            is_active=db_credential.is_active,
            is_testnet=db_credential.is_testnet,
            validation_status=db_credential.validation_status,
            last_validated_at=db_credential.last_validated_at,
            validation_error=db_credential.validation_error,
            created_at=db_credential.created_at,
            updated_at=db_credential.updated_at,
            has_api_key=bool(db_credential.api_key_encrypted),
            has_api_secret=bool(db_credential.api_secret_encrypted),
            has_api_passphrase=bool(db_credential.api_passphrase_encrypted),
        )
        
    except Exception as e:
        logger.error(f"Error updating credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating credential: {str(e)}"
        )


@router.delete("/credentials/{credential_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_broker_credential(
    credential_id: int,
    db: Session = Depends(get_db)
):
    """
    Elimina una credencial de broker
    
    Args:
        credential_id: ID de la credencial
    """
    user_id = 1  # TODO: Obtener del token
    
    success = crud_brokers.delete_broker_credential(db, credential_id, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Credential {credential_id} not found"
        )


@router.post("/credentials/{credential_id}/validate", response_model=models.BrokerValidationResult)
async def validate_broker_credential(
    credential_id: int,
    db: Session = Depends(get_db)
):
    """
    Valida una credencial de broker
    
    Args:
        credential_id: ID de la credencial
        
    Returns:
        Resultado de la validación
    """
    try:
        user_id = 1  # TODO: Obtener del token
        
        # Obtener credencial con secrets desencriptados
        credential = crud_brokers.get_broker_credential(
            db, credential_id, user_id, decrypt=True
        )
        
        if not credential:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Credential {credential_id} not found"
            )
        
        # Validar credenciales
        result = BrokerValidator.validate_credentials(
            broker_name=credential.broker_config.broker_name,
            broker_type=credential.broker_config.broker_type,
            api_key=getattr(credential, 'api_key_decrypted', None),
            api_secret=getattr(credential, 'api_secret_decrypted', None),
            api_passphrase=getattr(credential, 'api_passphrase_decrypted', None),
            is_testnet=credential.is_testnet
        )
        
        # Actualizar estado en DB
        crud_brokers.update_validation_status(
            db,
            credential_id,
            result.status.value,
            None if result.success else result.message
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating credential: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation error: {str(e)}"
        )
