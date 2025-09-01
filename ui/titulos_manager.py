# ui/titulos_manager.py
"""
Interfaz para la gestión de títulos de propiedad
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
from database.models import get_db_session, Venta, Cliente, Nicho, Beneficiario
from reports.pdf_generator import PDFGenerator

class TitulosManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.tree = None
        self.search_var = tk.StringVar()
        self.pdf_generator = PDFGenerator()
        
    def show(self):
        """Mostrar interfaz de gestión de títulos"""
        main_frame = ttk.LabelFrame(self.parent, text="Gestión de Títulos de Propiedad", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de controles superiores
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Generar Título", 
                  command=self.generate_title).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Ver Título", 
                  command=self.view_title).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Imprimir Título", 
                  command=self.print_title).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Lote de Títulos", 
                  command=self.batch_titles).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de búsqueda y filtros
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search)
        
        ttk.Button(search_frame, text="Limpiar", 
                  command=self.clear_search).grid(row=0, column=2)
        
        # Filtros
        filter_frame = ttk.LabelFrame(search_frame, text="Filtros", padding="5")
        filter_frame.grid(row=0, column=3, padx=(10, 0))
        
        self.filter_estado = tk.StringVar(value="Todos")
        ttk.Radiobutton(filter_frame, text="Todos", variable=self.filter_estado, 
                       value="Todos", command=self.apply_filters).grid(row=0, column=0)
        ttk.Radiobutton(filter_frame, text="Listos", variable=self.filter_estado, 
                       value="Listos", command=self.apply_filters).grid(row=0, column=1)
        ttk.Radiobutton(filter_frame, text="Pendientes", variable=self.filter_estado, 
                       value="Pendientes", command=self.apply_filters).grid(row=0, column=2)
        
        # Lista de ventas elegibles para títulos
        self.create_titles_tree(main_frame)
        
        # Cargar datos
        self.load_eligible_sales()
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.update_info_display(info_frame)
    
    def create_titles_tree(self, parent):
        """Crear TreeView para mostrar ventas elegibles"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # TreeView
        columns = ('contrato', 'fecha_venta', 'cliente', 'nicho', 'precio', 
                  'estado_pago', 'beneficiarios', 'titulo_generado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('contrato', text='Contrato')
        self.tree.heading('fecha_venta', text='Fecha Venta')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('nicho', text='Nicho')
        self.tree.heading('precio', text='Precio')
        self.tree.heading('estado_pago', text='Estado Pago')
        self.tree.heading('beneficiarios', text='Beneficiarios')
        self.tree.heading('titulo_generado', text='Título')
        
        self.tree.column('contrato', width=120)
        self.tree.column('fecha_venta', width=100)
        self.tree.column('cliente', width=200)
        self.tree.column('nicho', width=100)
        self.tree.column('precio', width=120)
        self.tree.column('estado_pago', width=100)
        self.tree.column('beneficiarios', width=100)
        self.tree.column('titulo_generado', width=100)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Grid
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Eventos
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-3>', self.show_context_menu)
    
    def load_eligible_sales(self):
        """Cargar ventas elegibles para generar títulos"""
        try:
            db = get_db_session()
            
            # Obtener todas las ventas
            ventas = db.query(Venta).join(Cliente).join(Nicho).order_by(
                Venta.fecha_venta.desc()
            ).all()
            
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar ventas
            for venta in ventas:
                cliente_nombre = venta.cliente.nombre_completo if venta.cliente else "N/A"
                nicho_numero = venta.nicho.numero if venta.nicho else "N/A"
                estado_pago = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                # Contar beneficiarios
                num_beneficiarios = len(venta.beneficiarios)
                beneficiarios_text = f"{num_beneficiarios} registrados" if num_beneficiarios > 0 else "Sin beneficiarios"
                
                # Verificar si ya se generó título (esto se podría guardar en una tabla separada)
                titulo_generado = "No" if not venta.pagado_completamente else "Listo"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    estado_pago,
                    beneficiarios_text,
                    titulo_generado
                )
                
                item = self.tree.insert('', 'end', values=values)
                
                # Colorear según estado
                if venta.pagado_completamente:
                    # self.tree.item(item, tags=('listo',))
                    pass
                else:
                    # self.tree.item(item, tags=('pendiente',))
                    pass
            
            # Configurar tags para colores
            self.tree.tag_configure('listo', background='#d4edda')
            self.tree.tag_configure('pendiente', background='#fff3cd')
            
            db.close()
            self.update_status(f"Ventas cargadas: {len(ventas)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")
    
    def generate_title(self):
        """Generar título de propiedad para la venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para generar el título")
            return
        
        item = self.tree.item(selected[0])
        numero_contrato = item['values'][0]
        
        try:
            db = get_db_session()
            venta = db.query(Venta).filter(Venta.numero_contrato == numero_contrato).first()
            
            if not venta:
                messagebox.showerror("Error", "Venta no encontrada")
                db.close()
                return
            
            # Verificar si la venta está pagada completamente
            if not venta.pagado_completamente:
                response = messagebox.askyesno("Confirmación", 
                    "Esta venta no está pagada completamente.\n"
                    "¿Está seguro de que desea generar el título?")
                if not response:
                    db.close()
                    return
            
            # Generar título PDF
            self.create_title_pdf(venta)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar título: {str(e)}")
    
    def create_title_pdf(self, venta):
        """Crear PDF del título de propiedad"""
        try:
            # Preparar datos para el PDF
            venta_data = {
                'numero_contrato': venta.numero_contrato,
                'fecha_venta': venta.fecha_venta,
                'precio_total': venta.precio_total,
                'pagado_completamente': venta.pagado_completamente,
                'tipo_pago': venta.tipo_pago,
                'observaciones': venta.observaciones
            }
            
            cliente_data = {
                'nombre': venta.cliente.nombre,
                'apellido': venta.cliente.apellido,
                'cedula': venta.cliente.cedula,
                'telefono': venta.cliente.telefono,
                'email': venta.cliente.email,
                'direccion': venta.cliente.direccion
            }
            
            nicho_data = {
                'numero': venta.nicho.numero,
                'seccion': venta.nicho.seccion,
                'fila': venta.nicho.fila,
                'columna': venta.nicho.columna,
                'precio': venta.nicho.precio,
                'descripcion': venta.nicho.descripcion
            }
            
            # Preparar datos de beneficiarios
            beneficiarios_data = []
            for beneficiario in venta.beneficiarios:
                if beneficiario.beneficiario_persona and beneficiario.activo:
                    ben = beneficiario.beneficiario_persona
                    beneficiarios_data.append({
                        'nombre': ben.nombre,
                        'apellido': ben.apellido,
                        'cedula': ben.cedula,
                        'telefono': ben.telefono,
                        'email': ben.email,
                        'direccion': ben.direccion,
                        'orden': beneficiario.orden
                    })
            
            # Generar PDF del título
            pdf_path = self.pdf_generator.generar_titulo_propiedad(
                venta_data, cliente_data, nicho_data, beneficiarios_data
            )
            
            # Preguntar si desea abrir el PDF
            response = messagebox.askyesno("Título Generado", 
                f"Título de propiedad generado exitosamente:\n{pdf_path}\n\n¿Desea abrirlo ahora?")
            
            if response:
                os.startfile(pdf_path)  # Windows
            
            self.update_status("Título de propiedad generado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar título: {str(e)}")
    
    def view_title(self):
        """Ver título existente o generar vista previa"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para ver el título")
            return
        
        item = self.tree.item(selected[0])
        numero_contrato = item['values'][0]
        
        # Buscar archivo de título existente
        titulo_path = f"titulos/titulo_{numero_contrato}*.pdf"
        
        # Aquí podrías implementar la búsqueda de archivos existentes
        # Por ahora, generar una vista previa
        self.generate_title()
    
    def print_title(self):
        """Imprimir título de propiedad"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para imprimir el título")
            return
        
        item = self.tree.item(selected[0])
        estado_pago = item['values'][5]
        
        if estado_pago != "Pagado":
            response = messagebox.askyesno("Confirmación", 
                "Esta venta no está pagada completamente.\n"
                "¿Está seguro de que desea imprimir el título?")
            if not response:
                return
        
        # Generar y abrir para imprimir
        self.generate_title()
    
    def batch_titles(self):
        """Generar títulos en lote"""
        dialog = BatchTitulosDialog(self.parent)
        if dialog.result:
            try:
                db = get_db_session()
                
                # Obtener ventas según criterios
                query = db.query(Venta).join(Cliente).join(Nicho)
                
                if dialog.result['solo_pagadas']:
                    query = query.filter(Venta.pagado_completamente == True)
                
                if dialog.result['fecha_desde']:
                    fecha_desde = datetime.strptime(dialog.result['fecha_desde'], "%Y-%m-%d")
                    query = query.filter(Venta.fecha_venta >= fecha_desde)
                
                if dialog.result['fecha_hasta']:
                    fecha_hasta = datetime.strptime(dialog.result['fecha_hasta'], "%Y-%m-%d")
                    query = query.filter(Venta.fecha_venta <= fecha_hasta)
                
                ventas = query.all()
                
                if not ventas:
                    messagebox.showinfo("Información", "No se encontraron ventas que cumplan los criterios")
                    db.close()
                    return
                
                # Confirmar generación
                response = messagebox.askyesno("Confirmación", 
                    f"Se generarán {len(ventas)} títulos de propiedad.\n¿Desea continuar?")
                
                if not response:
                    db.close()
                    return
                
                # Generar títulos
                generated_count = 0
                errors = []
                
                progress_dialog = ProgressDialog(self.parent, "Generando Títulos", len(ventas))
                
                for i, venta in enumerate(ventas):
                    try:
                        progress_dialog.update_progress(i + 1, f"Generando título para {venta.numero_contrato}")
                        self.create_title_pdf(venta)
                        generated_count += 1
                    except Exception as e:
                        errors.append(f"Error en {venta.numero_contrato}: {str(e)}")
                    
                    if progress_dialog.cancelled:
                        break
                
                progress_dialog.close()
                
                # Mostrar resultado
                message = f"Se generaron {generated_count} títulos exitosamente"
                if errors:
                    message += f"\n\nErrores ({len(errors)}):\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... y {len(errors) - 5} errores más"
                
                messagebox.showinfo("Resultado", message)
                self.update_status(f"Lote generado: {generated_count} títulos")
                
                db.close()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al generar lote: {str(e)}")
    
    def on_search(self, event=None):
        """Filtrar ventas según búsqueda"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.load_eligible_sales()
            return
        
        try:
            db = get_db_session()
            query = db.query(Venta).join(Cliente).join(Nicho)
            
            # Filtrar por término de búsqueda
            query = query.filter(
                Venta.numero_contrato.contains(search_term) |
                Cliente.nombre.contains(search_term) |
                Cliente.apellido.contains(search_term) |
                Cliente.cedula.contains(search_term) |
                Nicho.numero.contains(search_term)
            )
            
            ventas = query.order_by(Venta.fecha_venta.desc()).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for venta in ventas:
                cliente_nombre = venta.cliente.nombre_completo if venta.cliente else "N/A"
                nicho_numero = venta.nicho.numero if venta.nicho else "N/A"
                estado_pago = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                num_beneficiarios = len(venta.beneficiarios)
                beneficiarios_text = f"{num_beneficiarios} registrados" if num_beneficiarios > 0 else "Sin beneficiarios"
                
                titulo_generado = "No" if not venta.pagado_completamente else "Listo"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    estado_pago,
                    beneficiarios_text,
                    titulo_generado
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Búsqueda: {len(ventas)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.filter_estado.set("Todos")
        self.load_eligible_sales()
    
    def apply_filters(self):
        """Aplicar filtros de estado"""
        filter_value = self.filter_estado.get()
        
        try:
            db = get_db_session()
            query = db.query(Venta).join(Cliente).join(Nicho)
            
            # Aplicar filtro de búsqueda si existe
            search_term = self.search_var.get().lower()
            if search_term:
                query = query.filter(
                    Venta.numero_contrato.contains(search_term) |
                    Cliente.nombre.contains(search_term) |
                    Cliente.apellido.contains(search_term) |
                    Cliente.cedula.contains(search_term) |
                    Nicho.numero.contains(search_term)
                )
            
            # Aplicar filtro de estado
            if filter_value == "Listos":
                query = query.filter(Venta.pagado_completamente == True)
            elif filter_value == "Pendientes":
                query = query.filter(Venta.pagado_completamente == False)
            
            ventas = query.order_by(Venta.fecha_venta.desc()).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for venta in ventas:
                cliente_nombre = venta.cliente.nombre_completo if venta.cliente else "N/A"
                nicho_numero = venta.nicho.numero if venta.nicho else "N/A"
                estado_pago = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                num_beneficiarios = len(venta.beneficiarios)
                beneficiarios_text = f"{num_beneficiarios} registrados" if num_beneficiarios > 0 else "Sin beneficiarios"
                
                titulo_generado = "No" if not venta.pagado_completamente else "Listo"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    estado_pago,
                    beneficiarios_text,
                    titulo_generado
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Filtro aplicado: {len(ventas)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")
    
    def update_info_display(self, parent):
        """Actualizar display de información"""
        try:
            db = get_db_session()
            
            total_ventas = db.query(Venta).count()
            ventas_pagadas = db.query(Venta).filter(Venta.pagado_completamente == True).count()
            ventas_pendientes = total_ventas - ventas_pagadas
            
            db.close()
            
            info_text = (f"Total Ventas: {total_ventas} | "
                        f"Listas para Título: {ventas_pagadas} | "
                        f"Pendientes: {ventas_pendientes}")
            
            ttk.Label(parent, text=info_text, font=("Arial", 10)).pack()
            
        except Exception as e:
            ttk.Label(parent, text="Error al cargar información").pack()
    
    def on_double_click(self, event):
        """Manejar doble clic en TreeView"""
        self.generate_title()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Generar Título", command=self.generate_title)
        context_menu.add_command(label="Ver Título", command=self.view_title)
        context_menu.add_command(label="Imprimir Título", command=self.print_title)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()


class BatchTitulosDialog:
    def __init__(self, parent):
        self.result = None
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Generación de Títulos en Lote")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.solo_pagadas = tk.BooleanVar(value=True)
        self.fecha_desde = tk.StringVar()
        self.fecha_hasta = tk.StringVar()
        
        self.create_widgets()
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Generar Títulos en Lote", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Filtros
        ttk.Label(main_frame, text="Criterios de Selección:", 
                 font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Solo ventas pagadas
        ttk.Checkbutton(main_frame, text="Solo ventas pagadas completamente", 
                       variable=self.solo_pagadas).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Rango de fechas
        ttk.Label(main_frame, text="Rango de fechas de venta (opcional):").grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(10, 5))
        
        ttk.Label(main_frame, text="Desde:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.fecha_desde, width=15).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="Hasta:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.fecha_hasta, width=15).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Nota
        ttk.Label(main_frame, text="Formato de fecha: YYYY-MM-DD", 
                 font=("Arial", 9), foreground="gray").grid(row=6, column=0, columnspan=2, pady=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Generar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar configuración"""
        # Validar fechas si se proporcionaron
        fecha_desde = self.fecha_desde.get().strip()
        fecha_hasta = self.fecha_hasta.get().strip()
        
        if fecha_desde:
            try:
                datetime.strptime(fecha_desde, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha 'Desde' inválido. Use YYYY-MM-DD")
                return
        
        if fecha_hasta:
            try:
                datetime.strptime(fecha_hasta, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha 'Hasta' inválido. Use YYYY-MM-DD")
                return
        
        self.result = {
            'solo_pagadas': self.solo_pagadas.get(),
            'fecha_desde': fecha_desde if fecha_desde else None,
            'fecha_hasta': fecha_hasta if fecha_hasta else None
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()


class ProgressDialog:
    def __init__(self, parent, title, total_items):
        self.cancelled = False
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel)
        
        self.total_items = total_items
        
        self.create_widgets()
        self.center_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Etiqueta de progreso
        self.progress_label = ttk.Label(main_frame, text="Iniciando...")
        self.progress_label.pack(pady=(0, 10))
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, length=300, mode='determinate')
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar['maximum'] = self.total_items
        
        # Etiqueta de conteo
        self.count_label = ttk.Label(main_frame, text=f"0 de {self.total_items}")
        self.count_label.pack(pady=(0, 10))
        
        # Botón cancelar
        ttk.Button(main_frame, text="Cancelar", command=self.cancel).pack()
    
    def update_progress(self, current, message=""):
        """Actualizar progreso"""
        self.progress_bar['value'] = current
        self.count_label.config(text=f"{current} de {self.total_items}")
        if message:
            self.progress_label.config(text=message)
        
        self.dialog.update_idletasks()
    
    def cancel(self):
        """Cancelar operación"""
        self.cancelled = True
    
    def close(self):
        """Cerrar diálogo"""
        self.dialog.destroy()
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")