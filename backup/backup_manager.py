# backup/backup_manager.py
"""
Gestor de respaldos para la base de datos del sistema de criptas
"""

import os
import shutil
import zipfile
import sqlite3
from datetime import datetime
import json
from pathlib import Path

class BackupManager:
    def __init__(self):
        self.backup_dir = "backups"
        self.db_path = "criptas.db"
        self.config_file = "backup_config.json"
        
        # Crear directorio de respaldos si no existe
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Cargar configuración
        self.config = self.load_config()
    
    def load_config(self):
        """Cargar configuración de respaldos"""
        default_config = {
            "max_backups": 10,
            "auto_backup_enabled": True,
            "backup_schedule": "weekly",
            "include_reports": True,
            "compression_level": 6
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    return {**default_config, **config}
            except Exception:
                return default_config
        
        return default_config
    
    def save_config(self):
        """Guardar configuración de respaldos"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error al guardar configuración: {e}")
    
    def create_backup(self, backup_name=None):
        """
        Crear un respaldo completo del sistema
        
        Args:
            backup_name: Nombre personalizado para el respaldo
            
        Returns:
            str: Ruta del archivo de respaldo creado
        """
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
        
        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=self.config['compression_level']) as zipf:
                
                # Respaldar base de datos principal
                if os.path.exists(self.db_path):
                    zipf.write(self.db_path, "database/criptas.db")
                
                # Respaldar archivos de configuración
                config_files = [
                    self.config_file,
                    "app_config.json"  # Si existe configuración de la app
                ]
                
                for config_file in config_files:
                    if os.path.exists(config_file):
                        zipf.write(config_file, f"config/{config_file}")
                
                # Respaldar reportes si está habilitado
                if self.config['include_reports']:
                    self._backup_reports(zipf)
                
                # Respaldar logos y assets
                self._backup_assets(zipf)
                
                # Crear archivo de metadatos del respaldo
                metadata = self._create_backup_metadata()
                zipf.writestr("backup_metadata.json", json.dumps(metadata, indent=4, ensure_ascii=False))
            
            # Limpiar respaldos antiguos
            self._cleanup_old_backups()
            
            print(f"Respaldo creado exitosamente: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Error al crear respaldo: {e}")
            # Eliminar archivo parcial si existe
            if os.path.exists(backup_path):
                os.remove(backup_path)
            raise e
    
    def _backup_reports(self, zipf):
        """Respaldar archivos de reportes"""
        report_dirs = ["reportes", "recibos", "titulos"]
        
        for report_dir in report_dirs:
            if os.path.exists(report_dir):
                for root, dirs, files in os.walk(report_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = file_path.replace("\\", "/")  # Normalizar path para ZIP
                        zipf.write(file_path, arc_path)
    
    def _backup_assets(self, zipf):
        """Respaldar assets y archivos estáticos"""
        asset_dirs = ["assets", "images", "fonts"]
        
        for asset_dir in asset_dirs:
            if os.path.exists(asset_dir):
                for root, dirs, files in os.walk(asset_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = file_path.replace("\\", "/")
                        zipf.write(file_path, arc_path)
    
    def _create_backup_metadata(self):
        """Crear metadatos del respaldo"""
        metadata = {
            "backup_date": datetime.now().isoformat(),
            "backup_type": "full",
            "version": "1.0",
            "database_size": self._get_file_size(self.db_path),
            "total_records": self._count_database_records(),
            "config": self.config.copy()
        }
        return metadata
    
    def _get_file_size(self, file_path):
        """Obtener tamaño de archivo en bytes"""
        try:
            return os.path.getsize(file_path)
        except OSError:
            return 0
    
    def _count_database_records(self):
        """Contar registros en la base de datos"""
        if not os.path.exists(self.db_path):
            return {}
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Obtener todas las tablas
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            record_counts = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                record_counts[table_name] = count
            
            conn.close()
            return record_counts
            
        except Exception as e:
            print(f"Error al contar registros: {e}")
            return {}
    
    def restore_backup(self, backup_path):
        """
        Restaurar desde un archivo de respaldo
        
        Args:
            backup_path: Ruta del archivo de respaldo
        """
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Archivo de respaldo no encontrado: {backup_path}")
        
        # Crear respaldo de seguridad antes de restaurar
        safety_backup = self.create_backup("pre_restore_safety")
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                
                # Verificar que es un respaldo válido
                if "backup_metadata.json" not in zipf.namelist():
                    raise ValueError("Archivo de respaldo inválido: falta metadata")
                
                # Leer metadatos
                metadata_content = zipf.read("backup_metadata.json").decode('utf-8')
                metadata = json.loads(metadata_content)
                
                print(f"Restaurando respaldo del {metadata['backup_date']}")
                
                # Cerrar conexiones de base de datos antes de restaurar
                self._close_database_connections()
                
                # Restaurar base de datos
                if "database/criptas.db" in zipf.namelist():
                    # Hacer backup de la BD actual
                    if os.path.exists(self.db_path):
                        shutil.copy2(self.db_path, f"{self.db_path}.backup")
                    
                    # Extraer nueva BD
                    zipf.extract("database/criptas.db", "temp_restore")
                    shutil.move("temp_restore/database/criptas.db", self.db_path)
                    shutil.rmtree("temp_restore", ignore_errors=True)
                
                # Restaurar archivos de configuración
                for item in zipf.namelist():
                    if item.startswith("config/"):
                        target_path = item.replace("config/", "")
                        zipf.extract(item, "temp_restore")
                        shutil.move(f"temp_restore/{item}", target_path)
                
                # Restaurar reportes si existen
                if self.config['include_reports']:
                    self._restore_reports(zipf)
                
                # Restaurar assets
                self._restore_assets(zipf)
                
                # Limpiar archivos temporales
                shutil.rmtree("temp_restore", ignore_errors=True)
                
                print("Restauración completada exitosamente")
                
        except Exception as e:
            print(f"Error durante la restauración: {e}")
            # Intentar restaurar desde el backup de seguridad
            if os.path.exists(f"{self.db_path}.backup"):
                shutil.move(f"{self.db_path}.backup", self.db_path)
            raise e
        finally:
            # Limpiar archivos de backup temporal
            if os.path.exists(f"{self.db_path}.backup"):
                os.remove(f"{self.db_path}.backup")
    
    def _close_database_connections(self):
        """Cerrar todas las conexiones a la base de datos"""
        # Aquí podrías implementar lógica para cerrar conexiones activas
        # Por ahora, solo agregamos un pequeño delay
        import time
        time.sleep(1)
    
    def _restore_reports(self, zipf):
        """Restaurar archivos de reportes"""
        report_dirs = ["reportes", "recibos", "titulos"]
        
        for item in zipf.namelist():
            for report_dir in report_dirs:
                if item.startswith(f"{report_dir}/"):
                    zipf.extract(item, ".")
    
    def _restore_assets(self, zipf):
        """Restaurar assets"""
        asset_dirs = ["assets", "images", "fonts"]
        
        for item in zipf.namelist():
            for asset_dir in asset_dirs:
                if item.startswith(f"{asset_dir}/"):
                    zipf.extract(item, ".")
    
    def list_backups(self):
        """Listar todos los respaldos disponibles"""
        if not os.path.exists(self.backup_dir):
            return []
        
        backups = []
        for file in os.listdir(self.backup_dir):
            if file.endswith('.zip'):
                file_path = os.path.join(self.backup_dir, file)
                stat = os.stat(file_path)
                
                backup_info = {
                    'filename': file,
                    'path': file_path,
                    'size': stat.st_size,
                    'created': datetime.fromtimestamp(stat.st_ctime),
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                }
                
                # Intentar leer metadatos si es posible
                try:
                    with zipfile.ZipFile(file_path, 'r') as zipf:
                        if "backup_metadata.json" in zipf.namelist():
                            metadata_content = zipf.read("backup_metadata.json").decode('utf-8')
                            metadata = json.loads(metadata_content)
                            backup_info['metadata'] = metadata
                except Exception:
                    pass  # Ignorar errores al leer metadatos
                
                backups.append(backup_info)
        
        # Ordenar por fecha de creación (más reciente primero)
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups
    
    def _cleanup_old_backups(self):
        """Limpiar respaldos antiguos según la configuración"""
        backups = self.list_backups()
        
        if len(backups) > self.config['max_backups']:
            # Eliminar los respaldos más antiguos
            backups_to_delete = backups[self.config['max_backups']:]
            
            for backup in backups_to_delete:
                try:
                    os.remove(backup['path'])
                    print(f"Respaldo antiguo eliminado: {backup['filename']}")
                except Exception as e:
                    print(f"Error al eliminar respaldo {backup['filename']}: {e}")
    
    def delete_backup(self, backup_filename):
        """Eliminar un respaldo específico"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if os.path.exists(backup_path):
            os.remove(backup_path)
            print(f"Respaldo eliminado: {backup_filename}")
            return True
        return False
    
    def get_backup_info(self, backup_filename):
        """Obtener información detallada de un respaldo"""
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        if not os.path.exists(backup_path):
            return None
        
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                info = {
                    'filename': backup_filename,
                    'size': os.path.getsize(backup_path),
                    'files': zipf.namelist(),
                    'file_count': len(zipf.namelist())
                }
                
                # Leer metadatos si existen
                if "backup_metadata.json" in zipf.namelist():
                    metadata_content = zipf.read("backup_metadata.json").decode('utf-8')
                    info['metadata'] = json.loads(metadata_content)
                
                return info
                
        except Exception as e:
            print(f"Error al leer información del respaldo: {e}")
            return None
    
    def verify_backup(self, backup_path):
        """Verificar la integridad de un respaldo"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                # Verificar que el archivo ZIP no esté corrupto
                bad_files = zipf.testzip()
                if bad_files:
                    return False, f"Archivos corruptos: {bad_files}"
                
                # Verificar que contenga los archivos esenciales
                required_files = ["database/criptas.db", "backup_metadata.json"]
                missing_files = [f for f in required_files if f not in zipf.namelist()]
                
                if missing_files:
                    return False, f"Archivos faltantes: {missing_files}"
                
                return True, "Respaldo íntegro"
                
        except Exception as e:
            return False, f"Error al verificar respaldo: {e}"
    
    def export_backup_report(self, output_path=None):
        """Exportar reporte de respaldos en formato JSON"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"backup_report_{timestamp}.json"
        
        backups = self.list_backups()
        
        report = {
            "generated_date": datetime.now().isoformat(),
            "backup_directory": self.backup_dir,
            "total_backups": len(backups),
            "config": self.config,
            "backups": []
        }
        
        for backup in backups:
            backup_report = {
                "filename": backup['filename'],
                "size_bytes": backup['size'],
                "size_mb": round(backup['size'] / (1024 * 1024), 2),
                "created": backup['created'].isoformat(),
                "metadata": backup.get('metadata', {})
            }
            report["backups"].append(backup_report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=4, ensure_ascii=False)
        
        return output_path