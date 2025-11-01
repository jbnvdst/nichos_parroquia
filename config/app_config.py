# config/app_config.py
"""
Configuración de la aplicación del sistema de criptas
"""

import json
import os
from pathlib import Path
from config.paths import AppPaths

class AppConfig:
    def __init__(self):
        self.config_file = AppPaths.get_config_file_path()
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
                "nombre": "Parroquia Nuesta Señora del Consuelo de los Afligidos",
                "direccion": "C. Girasoles 960, La Mora, Los Girasoles, 45138 Zapopan, Jal.",
                "telefono": "+523336334968",
                "email": "info@parroquiasanjose.org",
                "logo_path": "assets/logo_parroquia.png",
                "parroco": "Pbro. Rafael del Toro Mendiola",
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
        # Usar AppPaths para crear directorios en el lugar correcto
        AppPaths.initialize_all_directories()

        # Actualizar la configuración con las rutas correctas
        self.config["pdf"]["output_dir_recibos"] = AppPaths.get_recibos_dir()
        self.config["pdf"]["output_dir_titulos"] = AppPaths.get_titulos_dir()
        self.config["pdf"]["output_dir_reportes"] = AppPaths.get_reportes_dir()
        self.config["backup"]["directory"] = AppPaths.get_backups_dir()
    
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