# config/constants.py
"""
Constantes de la aplicación
"""

# Versión de la aplicación
APP_VERSION = "1.1.7"
APP_NAME = "Sistema de Administración de Criptas"

# Estados de pagos
PAYMENT_STATUS = {
    'PENDING': 'Pendiente',
    'PAID': 'Pagado',
    'OVERDUE': 'Vencido',
    'CANCELLED': 'Cancelado'
}

# Tipos de pago
PAYMENT_TYPES = {
    'CASH': 'Contado',
    'CREDIT': 'Credito'
}

# Métodos de pago
PAYMENT_METHODS = [
    'Efectivo',
    'Transferencia',
    'Cheque',
    'Tarjeta_credito',
    'Tarjeta_debito',
    'Deposito'
]

# Estados de nichos
NICHO_STATUS = {
    'AVAILABLE': True,
    'SOLD': False
}

# Tipos de reportes
REPORT_TYPES = [
    'Movimientos',
    'Ventas',
    'Pagos',
    'Clientes',
    'Nichos',
    'Saldos_pendientes',
    'Resumen_financiero'
]

# Períodos de reportes
REPORT_PERIODS = [
    'Hoy',
    'Ayer',
    'Semana_actual',
    'Semana_pasada',
    'Mes_actual',
    'Mes_pasado',
    'Trimestre_actual',
    'Año_actual',
    'Personalizado',
    'Todo'
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