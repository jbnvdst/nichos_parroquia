# config/app_config.py
"""
Configuración de la aplicación del sistema de criptas
"""

import json
import os
from pathlib import Path

class AppConfig:
    def __init__(self):
        self.config_file = "app_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        """Cargar configuración desde archivo"""
        default_config = {
            "version": "1.0.0",
            "database": {
                "url": "sqlite:///criptas.db",
                "backup_enabled": True,
                "backup_schedule": "weekly"
            },
            "parroquia": {
                "nombre": "Parroquia San José",
                "direccion": "Calle Principal #123, Ciudad",
                "telefono": "+1 (555) 123-4567",
                "email": "info@parroquiasanjose.org",
                "logo_path": "assets/logo_parroquia.png",
                "parroco": "Padre José María",
                "administrador": "Juan Pérez"
            },
            "pdf": {
                "template_recibo": "templates/recibo_template.html",
                "template_titulo": "templates/titulo_template.html",
                "output_dir_recibos": "recibos",
                "output_dir_titulos": "titulos",
                "output_dir_reportes": "reportes",
                "include_logo": True,
                "font_size": 11,
                "page_size": "letter"
            },
            "backup": {
                "directory": "backups",
                "max_backups": 10,
                "auto_backup": True,
                "schedule_time": "23:00",
                "compression_level": 6,
                "include_reports": True
            },
            "ui": {
                "theme": "default",
                "window_size": "1200x800",
                "font_family": "Arial",
                "font_size": 10,
                "show_tooltips": True,
                "auto_save": True
            },
            "business": {
                "currency": "USD",
                "currency_symbol": "$",
                "decimal_places": 2,
                "tax_rate": 0.0,
                "default_payment_method": "efectivo",
                "require_payment_confirmation": True,
                "allow_negative_balance": False
            },
            "security": {
                "session_timeout": 3600,  # segundos
                "require_password": False,
                "log_activities": True,
                "backup_encryption": False
            },
            "notifications": {
                "email_enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "email_user": "",
                "email_password": "",
                "notification_email": "",
                "send_payment_notifications": False,
                "send_backup_notifications": False
            },
            "reports": {
                "default_format": "pdf",
                "include_charts": True,
                "auto_open_after_generate": True,
                "default_period": "mes_actual",
                "include_summary": True
            },
            "updates": {
                "check_for_updates": True,
                "update_server_url": "https://your-server.com/api/updates",
                "auto_download": False,
                "notify_on_update": True
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Combinar con configuración por defecto
                    return self._merge_configs(default_config, loaded_config)
            except Exception as e:
                print(f"Error al cargar configuración: {e}")
                return default_config
        
        # Crear archivo de configuración por defecto
        self.save_config(default_config)
        return default_config
    
    def _merge_configs(self, default, loaded):
        """Combinar configuraciones manteniendo la estructura por defecto"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    default[key] = self._merge_configs(default[key], value)
                else:
                    default[key] = value
        return default
    
    def save_config(self, config=None):
        """Guardar configuración en archivo"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
            return False
    
    def get(self, section, key=None, default=None):
        """Obtener valor de configuración"""
        try:
            if key is None:
                return self.config.get(section, default)
            return self.config.get(section, {}).get(key, default)
        except Exception:
            return default
    
    def set(self, section, key, value):
        """Establecer valor de configuración"""
        if section not in self.config:
            self.config[section] = {}
        
        if isinstance(key, str):
            self.config[section][key] = value
        else:
            # Si key es un diccionario, actualizar toda la sección
            self.config[section] = key
        
        return self.save_config()
    
    def get_database_url(self):
        """Obtener URL de base de datos"""
        return self.get("database", "url", "sqlite:///criptas.db")
    
    def get_parroquia_info(self):
        """Obtener información de la parroquia"""
        return self.get("parroquia", default={})
    
    def get_pdf_config(self):
        """Obtener configuración de PDF"""
        return self.get("pdf", default={})
    
    def get_backup_config(self):
        """Obtener configuración de respaldos"""
        return self.get("backup", default={})
    
    def get_ui_config(self):
        """Obtener configuración de interfaz"""
        return self.get("ui", default={})
    
    def create_directories(self):
        """Crear directorios necesarios"""
        directories = [
            self.get("pdf", "output_dir_recibos", "recibos"),
            self.get("pdf", "output_dir_titulos", "titulos"),
            self.get("pdf", "output_dir_reportes", "reportes"),
            self.get("backup", "directory", "backups"),
            "assets",
            "templates",
            "logs",
            "database"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def validate_config(self):
        """Validar configuración"""
        errors = []
        
        # Validar información de parroquia
        parroquia = self.get("parroquia")
        required_fields = ["nombre", "direccion", "telefono"]
        for field in required_fields:
            if not parroquia.get(field):
                errors.append(f"Campo requerido en parroquia: {field}")
        
        # Validar configuración de PDF
        pdf_config = self.get("pdf")
        output_dirs = ["output_dir_recibos", "output_dir_titulos", "output_dir_reportes"]
        for dir_key in output_dirs:
            directory = pdf_config.get(dir_key)
            if directory and not os.path.exists(directory):
                try:
                    os.makedirs(directory, exist_ok=True)
                except Exception as e:
                    errors.append(f"No se puede crear directorio {directory}: {e}")
        
        return errors
    
    def reset_to_defaults(self):
        """Restablecer configuración por defecto"""
        if os.path.exists(self.config_file):
            os.rename(self.config_file, f"{self.config_file}.backup")
        
        self.config = self.load_config()
        return True
    
    def export_config(self, filepath):
        """Exportar configuración a archivo"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al exportar configuración: {e}")
            return False
    
    def import_config(self, filepath):
        """Importar configuración desde archivo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # Validar configuración importada
            if isinstance(imported_config, dict):
                self.config = self._merge_configs(self.config, imported_config)
                return self.save_config()
            else:
                return False
                
        except Exception as e:
            print(f"Error al importar configuración: {e}")
            return False

# Instancia global de configuración
app_config = AppConfig()

# Crear directorios necesarios al importar
app_config.create_directories()


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


# config/constants.py
"""
Constantes de la aplicación
"""

# Versión de la aplicación
APP_VERSION = "1.0.0"
APP_NAME = "Sistema de Administración de Criptas"

# Estados de pagos
PAYMENT_STATUS = {
    'PENDING': 'pendiente',
    'PAID': 'pagado',
    'OVERDUE': 'vencido',
    'CANCELLED': 'cancelado'
}

# Tipos de pago
PAYMENT_TYPES = {
    'CASH': 'contado',
    'CREDIT': 'credito'
}

# Métodos de pago
PAYMENT_METHODS = [
    'efectivo',
    'transferencia',
    'cheque',
    'tarjeta_credito',
    'tarjeta_debito',
    'deposito'
]

# Estados de nichos
NICHO_STATUS = {
    'AVAILABLE': True,
    'SOLD': False
}

# Tipos de reportes
REPORT_TYPES = [
    'movimientos',
    'ventas',
    'pagos',
    'clientes',
    'nichos',
    'saldos_pendientes',
    'resumen_financiero'
]

# Períodos de reportes
REPORT_PERIODS = [
    'hoy',
    'ayer',
    'semana_actual',
    'semana_pasada',
    'mes_actual',
    'mes_pasado',
    'trimestre_actual',
    'año_actual',
    'personalizado',
    'todo'
]

# Formatos de exportación
EXPORT_FORMATS = [
    'pdf',
    'csv',
    'excel'
]

# Códigos de error
ERROR_CODES = {
    'DB_CONNECTION_FAILED': 1001,
    'INVALID_DATA': 1002,
    'RECORD_NOT_FOUND': 1003,
    'PERMISSION_DENIED': 1004,
    'BACKUP_FAILED': 1005,
    'PDF_GENERATION_FAILED': 1006
}

# Configuración de interfaz
UI_COLORS = {
    'PRIMARY': '#2196F3',
    'SECONDARY': '#FFC107',
    'SUCCESS': '#4CAF50',
    'DANGER': '#F44336',
    'WARNING': '#FF9800',
    'INFO': '#17A2B8',
    'LIGHT': '#F8F9FA',
    'DARK': '#343A40'
}

# Configuración de base de datos
DB_SETTINGS = {
    'POOL_SIZE': 10,
    'MAX_OVERFLOW': 20,
    'POOL_TIMEOUT': 30,
    'POOL_RECYCLE': 3600
}

# Límites de la aplicación
LIMITS = {
    'MAX_BENEFICIARIOS': 2,
    'MAX_SEARCH_RESULTS': 100,
    'MAX_BATCH_OPERATIONS': 1000,
    'MAX_FILE_SIZE_MB': 50
}

# Mensajes de la aplicación
MESSAGES = {
    'SUCCESS': {
        'RECORD_SAVED': 'Registro guardado exitosamente',
        'RECORD_DELETED': 'Registro eliminado exitosamente',
        'BACKUP_CREATED': 'Respaldo creado exitosamente',
        'PDF_GENERATED': 'PDF generado exitosamente'
    },
    'ERROR': {
        'RECORD_NOT_FOUND': 'Registro no encontrado',
        'INVALID_DATA': 'Datos inválidos',
        'OPERATION_FAILED': 'Operación fallida',
        'PERMISSION_DENIED': 'Permiso denegado'
    },
    'WARNING': {
        'UNSAVED_CHANGES': 'Hay cambios sin guardar',
        'DELETE_CONFIRMATION': '¿Está seguro de eliminar este registro?',
        'OPERATION_CONFIRMATION': '¿Está seguro de realizar esta operación?'
    }
}