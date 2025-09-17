# config/logger_config.py
"""
Configuración de logging para la aplicación
"""

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logging():
    """Configurar sistema de logging"""
    # Crear directorio de logs si no existe
    os.makedirs("logs", exist_ok=True)
    
    # Configurar logger principal
    logger = logging.getLogger('criptas_app')
    logger.setLevel(logging.INFO)
    
    # Crear formateador
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        'logs/criptas_app.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Handler para consola (solo errores)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.ERROR)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_user_action(action, details="", user="System"):
    """Registrar acción del usuario"""
    logger = logging.getLogger('criptas_app')
    logger.info(f"USER_ACTION - User: {user} - Action: {action} - Details: {details}")

def log_database_operation(operation, table, record_id=None, details=""):
    """Registrar operación de base de datos"""
    logger = logging.getLogger('criptas_app')
    record_info = f"ID: {record_id}" if record_id else "Multiple records"
    logger.info(f"DB_OPERATION - Operation: {operation} - Table: {table} - {record_info} - Details: {details}")

def log_error(error, context=""):
    """Registrar error"""
    logger = logging.getLogger('criptas_app')
    logger.error(f"ERROR - Context: {context} - Error: {str(error)}")

def log_backup_operation(operation, result, details=""):
    """Registrar operación de respaldo"""
    logger = logging.getLogger('criptas_app')
    status = "SUCCESS" if result else "FAILED"
    logger.info(f"BACKUP - Operation: {operation} - Status: {status} - Details: {details}")

# Configurar logging al importar
setup_logging()