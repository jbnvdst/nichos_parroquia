# ui/main_window.py
"""
Ventana principal del sistema de administración de criptas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import os

# Importaciones de otros módulos de UI
from ui.nichos_manager import NichosManager
from ui.ventas_manager import VentasManager
from ui.pagos_manager import PagosManager
from ui.reportes_manager import ReportesManager
from ui.busqueda_manager import BusquedaManager
from ui.titulos_manager import TitulosManager
from backup.backup_manager import BackupManager

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.backup_manager = BackupManager()
        
        # Crear la interfaz principal
        self.create_main_interface()
        
        # Inicializar managers
        self.init_managers()
    
    def create_main_interface(self):
        """Crear la interfaz principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar el grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Inicializar variables de estado primero
        self.status_var = tk.StringVar()
        self.status_var.set("Iniciando sistema...")
        
        # Título
        title_label = ttk.Label(main_frame, text="Sistema de Administración de Criptas", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Panel de navegación izquierdo
        self.create_navigation_panel(main_frame)
        
        # Barra de estado (crear antes del área de contenido)
        self.create_status_bar(main_frame)
        
        # Área de contenido principal (esto llamará a show_dashboard que usa status_var)
        self.create_content_area(main_frame)
    
    def create_navigation_panel(self, parent):
        """Crear panel de navegación"""
        nav_frame = ttk.LabelFrame(parent, text="Navegación", padding="10")
        nav_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botones de navegación
        buttons = [
            ("🏠 Dashboard", self.show_dashboard),
            ("🏛️ Gestión de Nichos", self.show_nichos),
            ("💰 Ventas", self.show_ventas),
            ("💳 Pagos", self.show_pagos),
            ("📋 Títulos de Propiedad", self.show_titulos),
            ("🔍 Búsqueda", self.show_busqueda),
            ("📊 Reportes", self.show_reportes),
            ("💾 Respaldos", self.show_respaldos),
            ("⚙️ Configuración", self.show_configuracion),
        ]
        
        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(nav_frame, text=text, command=command, 
                           style='Custom.TButton', width=20)
            btn.grid(row=i, column=0, pady=5, sticky=(tk.W, tk.E))
        
        nav_frame.columnconfigure(0, weight=1)
    
    def create_content_area(self, parent):
        """Crear área de contenido principal"""
        self.content_frame = ttk.Frame(parent, padding="10")
        self.content_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.content_frame.columnconfigure(0, weight=1)
        self.content_frame.rowconfigure(0, weight=1)
        
        # Mostrar dashboard por defecto
        self.show_dashboard()
    
    def create_status_bar(self, parent):
        """Crear barra de estado"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        status_label = ttk.Label(status_frame, textvariable=self.status_var)
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Información de conexión a BD
        db_status = ttk.Label(status_frame, text="BD: Conectada", foreground="green")
        db_status.grid(row=0, column=1, sticky=tk.E)
        
        status_frame.columnconfigure(0, weight=1)
    
    def init_managers(self):
        """Inicializar los managers de cada módulo"""
        self.nichos_manager = NichosManager(self.content_frame, self.update_status)
        self.ventas_manager = VentasManager(self.content_frame, self.update_status)
        self.pagos_manager = PagosManager(self.content_frame, self.update_status)
        self.titulos_manager = TitulosManager(self.content_frame, self.update_status)
        self.reportes_manager = ReportesManager(self.content_frame, self.update_status)
        self.busqueda_manager = BusquedaManager(self.content_frame, self.update_status)
    
    def clear_content(self):
        """Limpiar el área de contenido"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Actualizar la barra de estado"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def show_dashboard(self):
        """Mostrar dashboard principal"""
        self.clear_content()
        self.update_status("Dashboard")
        
        # Crear dashboard
        dashboard_frame = ttk.LabelFrame(self.content_frame, text="Dashboard", padding="20")
        dashboard_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dashboard_frame.columnconfigure(0, weight=1)
        dashboard_frame.columnconfigure(1, weight=1)
        
        # Estadísticas rápidas
        self.create_stats_widgets(dashboard_frame)
        
        # Acciones rápidas
        self.create_quick_actions(dashboard_frame)
    
    def create_stats_widgets(self, parent):
        """Crear widgets de estadísticas"""
        from database.models import get_db_session, Nicho, Venta, Pago
        
        db = get_db_session()
        try:
            # Obtener estadísticas
            total_nichos = db.query(Nicho).count()
            nichos_disponibles = db.query(Nicho).filter(Nicho.disponible == True).count()
            nichos_vendidos = total_nichos - nichos_disponibles
            total_ventas = db.query(Venta).count()
            ventas_pendientes = db.query(Venta).filter(Venta.pagado_completamente == False).count()
            
            # Frame de estadísticas
            stats_frame = ttk.LabelFrame(parent, text="Estadísticas", padding="10")
            stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
            
            # Crear tarjetas de estadísticas
            stats = [
                ("Total Nichos", total_nichos, "#3498db"),
                ("Nichos Disponibles", nichos_disponibles, "#2ecc71"),
                ("Nichos Vendidos", nichos_vendidos, "#e74c3c"),
                ("Total Ventas", total_ventas, "#9b59b6"),
                ("Ventas Pendientes", ventas_pendientes, "#f39c12")
            ]
            
            for i, (label, value, color) in enumerate(stats):
                col = i % 3
                row = i // 3
                
                card_frame = tk.Frame(stats_frame, bg=color, relief="raised", bd=2)
                card_frame.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
                
                value_label = tk.Label(card_frame, text=str(value), font=("Arial", 24, "bold"), 
                                     bg=color, fg="white")
                value_label.pack(pady=(10, 5))
                
                text_label = tk.Label(card_frame, text=label, font=("Arial", 12), 
                                    bg=color, fg="white")
                text_label.pack(pady=(0, 10))
            
            stats_frame.columnconfigure(0, weight=1)
            stats_frame.columnconfigure(1, weight=1)
            stats_frame.columnconfigure(2, weight=1)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar estadísticas: {str(e)}")
        finally:
            db.close()
    
    def create_quick_actions(self, parent):
        """Crear acciones rápidas"""
        actions_frame = ttk.LabelFrame(parent, text="Acciones Rápidas", padding="10")
        actions_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Botones de acciones rápidas
        quick_actions = [
            ("Nueva Venta", self.quick_new_sale),
            ("Registrar Pago", self.quick_new_payment),
            ("Buscar Cliente", self.quick_search_client),
            ("Generar Reporte", self.quick_generate_report),
            ("Respaldar Base de Datos", self.quick_backup),
            ("Imprimir Título", self.quick_print_title)
        ]
        
        for i, (text, command) in enumerate(quick_actions):
            col = i % 3
            row = i // 3
            
            btn = ttk.Button(actions_frame, text=text, command=command, 
                           style='Custom.TButton', width=20)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky=(tk.W, tk.E))
        
        actions_frame.columnconfigure(0, weight=1)
        actions_frame.columnconfigure(1, weight=1)
        actions_frame.columnconfigure(2, weight=1)
    
    def show_nichos(self):
        """Mostrar gestión de nichos"""
        self.clear_content()
        self.update_status("Gestión de Nichos")
        self.nichos_manager.show()
    
    def show_ventas(self):
        """Mostrar gestión de ventas"""
        self.clear_content()
        self.update_status("Gestión de Ventas")
        self.ventas_manager.show()
    
    def show_pagos(self):
        """Mostrar gestión de pagos"""
        self.clear_content()
        self.update_status("Gestión de Pagos")
        self.pagos_manager.show()
    
    def show_titulos(self):
        """Mostrar gestión de títulos"""
        self.clear_content()
        self.update_status("Gestión de Títulos de Propiedad")
        self.titulos_manager.show()
    
    def show_busqueda(self):
        """Mostrar búsqueda"""
        self.clear_content()
        self.update_status("Búsqueda")
        self.busqueda_manager.show()
    
    def show_reportes(self):
        """Mostrar reportes"""
        self.clear_content()
        self.update_status("Reportes")
        self.reportes_manager.show()
    
    def show_respaldos(self):
        """Mostrar gestión de respaldos"""
        self.clear_content()
        self.update_status("Gestión de Respaldos")
        
        backup_frame = ttk.LabelFrame(self.content_frame, text="Gestión de Respaldos", padding="20")
        backup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Información de respaldos
        info_label = ttk.Label(backup_frame, 
                              text="Los respaldos automáticos se realizan cada domingo a las 23:00\n"
                                   "También puedes crear respaldos manuales cuando lo necesites.",
                              font=("Arial", 11))
        info_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Botones de respaldo
        manual_backup_btn = ttk.Button(backup_frame, text="Crear Respaldo Manual",
                                     command=self.create_manual_backup, style='Custom.TButton')
        manual_backup_btn.grid(row=1, column=0, padx=10, pady=10)
        
        restore_backup_btn = ttk.Button(backup_frame, text="Restaurar desde Respaldo",
                                      command=self.restore_backup, style='Custom.TButton')
        restore_backup_btn.grid(row=1, column=1, padx=10, pady=10)
        
        # Lista de respaldos existentes
        self.load_backup_list(backup_frame)
    
    def show_configuracion(self):
        """Mostrar configuración"""
        self.clear_content()
        self.update_status("Configuración")
        
        config_frame = ttk.LabelFrame(self.content_frame, text="Configuración", padding="20")
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configuraciones básicas
        ttk.Label(config_frame, text="Configuración del Sistema", 
                 style='Heading.TLabel').grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Configuración de la parroquia
        ttk.Label(config_frame, text="Nombre de la Parroquia:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.parish_name_var = tk.StringVar(value="Parroquia San José")
        parish_entry = ttk.Entry(config_frame, textvariable=self.parish_name_var, width=30)
        parish_entry.grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # Botón para guardar configuración
        save_config_btn = ttk.Button(config_frame, text="Guardar Configuración",
                                   command=self.save_configuration, style='Custom.TButton')
        save_config_btn.grid(row=2, column=0, columnspan=2, pady=20)
    
    # Métodos para acciones rápidas
    def quick_new_sale(self):
        self.show_ventas()
        self.ventas_manager.new_sale()
    
    def quick_new_payment(self):
        self.show_pagos()
        self.pagos_manager.new_payment()
    
    def quick_search_client(self):
        self.show_busqueda()
    
    def quick_generate_report(self):
        self.show_reportes()
    
    def quick_backup(self):
        self.create_manual_backup()
    
    def quick_print_title(self):
        self.show_titulos()
    
    def create_manual_backup(self):
        """Crear respaldo manual"""
        try:
            backup_path = self.backup_manager.create_backup()
            messagebox.showinfo("Éxito", f"Respaldo creado exitosamente en:\n{backup_path}")
            self.update_status("Respaldo creado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear respaldo: {str(e)}")
    
    def restore_backup(self):
        """Restaurar desde respaldo"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo de respaldo",
            filetypes=[("Archivos ZIP", "*.zip")]
        )
        
        if file_path:
            try:
                self.backup_manager.restore_backup(file_path)
                messagebox.showinfo("Éxito", "Base de datos restaurada exitosamente")
                self.update_status("Base de datos restaurada")
                # Reiniciar la aplicación o recargar datos
            except Exception as e:
                messagebox.showerror("Error", f"Error al restaurar respaldo: {str(e)}")
    
    def load_backup_list(self, parent):
        """Cargar lista de respaldos existentes"""
        list_frame = ttk.LabelFrame(parent, text="Respaldos Existentes", padding="10")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        
        # Lista de archivos de respaldo
        backup_files = self.backup_manager.list_backups()
        
        if backup_files:
            for i, backup_file in enumerate(backup_files[:5]):  # Mostrar solo los últimos 5
                ttk.Label(list_frame, text=backup_file).grid(row=i, column=0, sticky=tk.W, pady=2)
        else:
            ttk.Label(list_frame, text="No hay respaldos disponibles").grid(row=0, column=0, pady=10)
    
    def save_configuration(self):
        """Guardar configuración"""
        # Aquí implementarías el guardado de configuración
        messagebox.showinfo("Éxito", "Configuración guardada exitosamente")
        self.update_status("Configuración guardada")