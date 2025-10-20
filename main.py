# main.py
"""
Sistema de Administración de Criptas
Aplicación completa para gestionar nichos, ventas, pagos y reportes
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
import os
import shutil
import json
from pathlib import Path
import threading
import schedule
import time

# Importaciones de nuestros módulos
from database.models import Base, engine, SessionLocal
from database.models import Nicho, Cliente, Venta, Pago, Beneficiario
from ui.main_window import MainWindow
from reports.pdf_generator import PDFGenerator
from backup.backup_manager import BackupManager
from github_updater import GitHubUpdater

class CriptasApp:
    # Versión de la aplicación (actualizar en cada release)
    VERSION = "1.0.2"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"Sistema de Administración de Criptas - Parroquia v{self.VERSION}")
        self.root.geometry("1536x864")
        self.root.configure(bg='#f0f0f0')

        # Configurar estilo
        self.setup_style()

        # Crear base de datos si no existe
        self.init_database()

        # Inicializar ventana principal
        self.main_window = MainWindow(self.root)

        # Inicializar generador de PDFs
        self.pdf_generator = PDFGenerator()

        # Inicializar gestor de respaldos
        self.backup_manager = BackupManager()

        # Inicializar sistema de actualizaciones
        self.updater = GitHubUpdater(
            repo_owner="jbnvdst",
            repo_name="nichos_parroquia",
            current_version=self.VERSION
        )

        # Configurar respaldos automáticos
        self.setup_auto_backup()

        # Verificar actualizaciones al iniciar (silenciosamente)
        self.check_for_updates_on_startup()
    
    def setup_style(self):
        """Configurar estilos de la aplicación"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores personalizados
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Heading.TLabel', font=('Arial', 12, 'bold'), background='#f0f0f0')
        style.configure('Custom.TButton', font=('Arial', 10), padding=10)
    
    def init_database(self):
        """Inicializar la base de datos"""
        try:
            # Ejecutar migración para agregar columna 'familia' si no existe
            self.migrate_database()

            Base.metadata.create_all(bind=engine)
            print("Base de datos inicializada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar la base de datos: {str(e)}")

    def migrate_database(self):
        """Ejecutar migraciones de base de datos"""
        try:
            db_path = "criptas.db"
            if os.path.exists(db_path):
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # Migración 1: Agregar columna 'familia' a la tabla 'ventas'
                cursor.execute("PRAGMA table_info(ventas)")
                columns = [column[1] for column in cursor.fetchall()]

                if 'familia' not in columns:
                    print("Agregando columna 'familia' a la tabla ventas...")
                    cursor.execute("ALTER TABLE ventas ADD COLUMN familia VARCHAR(100)")
                    conn.commit()
                    print("✓ Columna 'familia' agregada exitosamente")

                conn.close()
        except Exception as e:
            print(f"Error en migración: {str(e)}")
    
    def setup_auto_backup(self):
        """Configurar respaldos automáticos semanales"""
        # Programar respaldo cada sábado a las 12:00 PM
        schedule.every().saturday.at("12:00").do(self.backup_manager.create_backup)
        
        # Ejecutar scheduler en un hilo separado
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        
        backup_thread = threading.Thread(target=run_scheduler, daemon=True)
        backup_thread.start()
    
    def check_for_updates_on_startup(self):
        """Verificar actualizaciones al iniciar la aplicación (silenciosamente)"""
        try:
            self.updater.check_updates_on_startup(self.root)
        except Exception as e:
            # No mostrar errores al verificar actualizaciones en el inicio
            print(f"Error al verificar actualizaciones: {e}")

    def check_for_updates_manual(self):
        """Verificar actualizaciones manualmente (desde menú Ayuda)"""
        try:
            self.updater.check_for_updates(silent=False)
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"No se pudo verificar actualizaciones:\n{str(e)}"
            )
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error Fatal", f"Error en la aplicación: {str(e)}")

if __name__ == "__main__":
    app = CriptasApp()
    app.run()