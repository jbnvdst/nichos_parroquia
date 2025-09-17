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

class CriptasApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Administración de Criptas - Parroquia")
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
        
        # Configurar respaldos automáticos
        self.setup_auto_backup()
        
        # Verificar actualizaciones (placeholder)
        self.check_for_updates()
    
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
            Base.metadata.create_all(bind=engine)
            print("Base de datos inicializada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al inicializar la base de datos: {str(e)}")
    
    def setup_auto_backup(self):
        """Configurar respaldos automáticos semanales"""
        # Programar respaldo cada domingo a las 23:00
        schedule.every().sunday.at("23:00").do(self.backup_manager.create_backup)
        
        # Ejecutar scheduler en un hilo separado
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verificar cada minuto
        
        backup_thread = threading.Thread(target=run_scheduler, daemon=True)
        backup_thread.start()
    
    def check_for_updates(self):
        """Verificar actualizaciones remotas (placeholder)"""
        # Aquí implementarías la lógica para verificar actualizaciones
        # Puedes usar requests para conectar a un servidor y verificar versiones
        pass
    
    def run(self):
        """Ejecutar la aplicación"""
        try:
            self.root.mainloop()
        except Exception as e:
            messagebox.showerror("Error Fatal", f"Error en la aplicación: {str(e)}")

if __name__ == "__main__":
    app = CriptasApp()
    app.run()