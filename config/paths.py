# config/paths.py
"""
Gestor de rutas de directorios para la aplicación
Maneja directorios del usuario (AppData en Windows) para evitar problemas de permisos
cuando la aplicación se instala para todos los usuarios
"""

import os
import sys
from pathlib import Path
import platform

class AppPaths:
    """Gestor centralizado de rutas de directorios de la aplicación"""

    # Nombre de la aplicación
    APP_NAME = "CriptasParroquia"

    @staticmethod
    def get_app_data_dir() -> str:
        """
        Obtener el directorio AppData de la aplicación

        Windows: %LOCALAPPDATA%\CriptasParroquia
        Linux: ~/.local/share/CriptasParroquia
        macOS: ~/Library/Application Support/CriptasParroquia

        Returns:
            str: Ruta al directorio de datos de la aplicación
        """
        system = platform.system()

        if system == "Windows":
            # En Windows usar LOCALAPPDATA
            appdata = os.environ.get('LOCALAPPDATA')
            if not appdata:
                appdata = os.path.expanduser('~\\AppData\\Local')
        elif system == "Darwin":
            # macOS
            appdata = os.path.expanduser('~/Library/Application Support')
        else:
            # Linux y otros
            appdata = os.path.expanduser('~/.local/share')

        app_dir = os.path.join(appdata, AppPaths.APP_NAME)
        return app_dir

    @staticmethod
    def get_backups_dir() -> str:
        """Obtener directorio de respaldos"""
        backups_dir = os.path.join(AppPaths.get_app_data_dir(), "backups")
        AppPaths._ensure_dir_exists(backups_dir)
        return backups_dir

    @staticmethod
    def get_recibos_dir() -> str:
        """Obtener directorio de recibos"""
        recibos_dir = os.path.join(AppPaths.get_app_data_dir(), "recibos")
        AppPaths._ensure_dir_exists(recibos_dir)
        return recibos_dir

    @staticmethod
    def get_titulos_dir() -> str:
        """Obtener directorio de títulos"""
        titulos_dir = os.path.join(AppPaths.get_app_data_dir(), "titulos")
        AppPaths._ensure_dir_exists(titulos_dir)
        return titulos_dir

    @staticmethod
    def get_reportes_dir() -> str:
        """Obtener directorio de reportes"""
        reportes_dir = os.path.join(AppPaths.get_app_data_dir(), "reportes")
        AppPaths._ensure_dir_exists(reportes_dir)
        return reportes_dir

    @staticmethod
    def get_logs_dir() -> str:
        """Obtener directorio de logs"""
        logs_dir = os.path.join(AppPaths.get_app_data_dir(), "logs")
        AppPaths._ensure_dir_exists(logs_dir)
        return logs_dir

    @staticmethod
    def get_database_path() -> str:
        """
        Obtener ruta de la base de datos
        La BD se guarda en AppData para permitir actualización de la aplicación
        sin perder datos
        """
        db_dir = os.path.join(AppPaths.get_app_data_dir(), "database")
        AppPaths._ensure_dir_exists(db_dir)
        return os.path.join(db_dir, "criptas.db")

    @staticmethod
    def get_config_file_path() -> str:
        """Obtener ruta del archivo de configuración"""
        app_dir = AppPaths.get_app_data_dir()
        AppPaths._ensure_dir_exists(app_dir)
        return os.path.join(app_dir, "app_config.json")

    @staticmethod
    def get_backup_config_file_path() -> str:
        """Obtener ruta del archivo de configuración de respaldos"""
        app_dir = AppPaths.get_app_data_dir()
        AppPaths._ensure_dir_exists(app_dir)
        return os.path.join(app_dir, "backup_config.json")

    @staticmethod
    def get_templates_dir() -> str:
        """
        Obtener directorio de templates
        Se mantiene en la carpeta de instalación (directorio de ejecución)
        """
        return os.path.join(os.path.dirname(sys.executable), "templates")

    @staticmethod
    def get_assets_dir() -> str:
        """
        Obtener directorio de assets (logos, fuentes, etc)
        Se mantiene en la carpeta de instalación
        """
        return os.path.join(os.path.dirname(sys.executable), "assets")

    @staticmethod
    def initialize_all_directories():
        """
        Inicializar todos los directorios necesarios
        Llamar esto al inicio de la aplicación
        """
        try:
            # Crear directorio base
            app_data_dir = AppPaths.get_app_data_dir()
            AppPaths._ensure_dir_exists(app_data_dir)

            # Crear todos los subdirectorios
            AppPaths.get_backups_dir()
            AppPaths.get_recibos_dir()
            AppPaths.get_titulos_dir()
            AppPaths.get_reportes_dir()
            AppPaths.get_logs_dir()

            # BD
            db_path = AppPaths.get_database_path()
            AppPaths._ensure_dir_exists(os.path.dirname(db_path))

            return True
        except Exception as e:
            print(f"Error al inicializar directorios: {e}")
            return False

    @staticmethod
    def _ensure_dir_exists(directory: str):
        """Asegurar que un directorio existe, crearlo si es necesario"""
        try:
            os.makedirs(directory, exist_ok=True)
        except PermissionError as e:
            raise PermissionError(
                f"Permiso denegado al crear directorio '{directory}'. "
                f"Asegúrese de que tiene permisos de escritura en {AppPaths.get_app_data_dir()}"
            ) from e
        except Exception as e:
            raise Exception(f"Error al crear directorio '{directory}': {e}") from e
