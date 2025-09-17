# ui/ventas_manager.py
"""
Interfaz para la gestión de ventas
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.models import (get_db_session, Cliente, Nicho, Venta, Beneficiario, 
                           generar_numero_contrato, buscar_nichos_disponibles)

class VentasManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.tree = None
        self.search_var = tk.StringVar()
        
    def show(self):
        """Mostrar interfaz de gestión de ventas"""
        main_frame = ttk.LabelFrame(self.parent, text="Gestión de Ventas", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de controles superiores
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Nueva Venta", 
                  command=self.new_sale).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Ver Detalles", 
                  command=self.view_sale_details).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Editar Venta", 
                  command=self.edit_sale).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Anular Venta", 
                  command=self.cancel_sale).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de búsqueda
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
        
        self.filter_estado = tk.StringVar(value="Todas")
        ttk.Radiobutton(filter_frame, text="Todas", variable=self.filter_estado, 
                       value="Todas", command=self.apply_filters).grid(row=0, column=0)
        ttk.Radiobutton(filter_frame, text="Pagadas", variable=self.filter_estado, 
                       value="Pagadas", command=self.apply_filters).grid(row=0, column=1)
        ttk.Radiobutton(filter_frame, text="Pendientes", variable=self.filter_estado, 
                       value="Pendientes", command=self.apply_filters).grid(row=0, column=2)
        
        # Lista de ventas
        self.create_sales_tree(main_frame)
        
        # Cargar datos
        self.load_sales()
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Resumen", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.update_info_display(info_frame)
    
    def create_sales_tree(self, parent):
        """Crear TreeView para mostrar ventas"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # TreeView
        columns = ('contrato', 'fecha', 'cliente', 'nicho', 'precio_total', 
                  'tipo_pago', 'saldo', 'estado')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('contrato', text='Contrato')
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('nicho', text='Nicho')
        self.tree.heading('precio_total', text='Precio Total')
        self.tree.heading('tipo_pago', text='Tipo Pago')
        self.tree.heading('saldo', text='Saldo')
        self.tree.heading('estado', text='Estado')
        
        self.tree.column('contrato', width=120)
        self.tree.column('fecha', width=100)
        self.tree.column('cliente', width=200)
        self.tree.column('nicho', width=100)
        self.tree.column('precio_total', width=120)
        self.tree.column('tipo_pago', width=100)
        self.tree.column('saldo', width=120)
        self.tree.column('estado', width=100)
        
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
    
    def load_sales(self):
        """Cargar ventas desde la base de datos"""
        try:
            db = get_db_session()
            ventas = db.query(Venta).order_by(Venta.fecha_venta.desc()).all()
            
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar ventas
            for venta in ventas:
                cliente_nombre = venta.cliente.nombre_completo if venta.cliente else "N/A"
                nicho_numero = venta.nicho.numero if venta.nicho else "N/A"
                estado = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    venta.tipo_pago.title(),
                    f"${venta.saldo_restante:,.2f}",
                    estado
                )
                
                item = self.tree.insert('', 'end', values=values)
                
                # Colorear según estado
                if venta.pagado_completamente:
                    self.tree.set(item, 'estado', 'Pagado')
                    # self.tree.item(item, tags=('pagado',))
                else:
                    # self.tree.item(item, tags=('pendiente',))
                    pass
            
            # Configurar tags para colores
            self.tree.tag_configure('pagado', background='#d4edda')
            self.tree.tag_configure('pendiente', background='#fff3cd')
            
            db.close()
            self.update_status(f"Ventas cargadas: {len(ventas)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")
    
    def new_sale(self):
        """Crear nueva venta"""
        dialog = VentaDialog(self.parent, "Nueva Venta")
        if dialog.result:
            try:
                db = get_db_session()
                
                # Crear o buscar cliente
                cliente = self.get_or_create_cliente(db, dialog.result['cliente'])
                if not cliente:
                    db.close()
                    return
                
                # Verificar que el nicho esté disponible
                nicho = db.query(Nicho).filter(Nicho.id == dialog.result['nicho_id']).first()
                if not nicho or not nicho.disponible:
                    messagebox.showerror("Error", "El nicho seleccionado no está disponible")
                    db.close()
                    return
                
                # Crear venta
                numero_contrato = generar_numero_contrato()
                
                venta = Venta(
                    numero_contrato=numero_contrato,
                    cliente_id=cliente.id,
                    nicho_id=nicho.id,
                    precio_total=dialog.result['precio_total'],
                    enganche=dialog.result['enganche'],
                    saldo_restante=dialog.result['precio_total'] - dialog.result['enganche'],
                    tipo_pago=dialog.result['tipo_pago'],
                    pagado_completamente=dialog.result['tipo_pago'] == 'contado',
                    observaciones=dialog.result.get('observaciones')
                )
                
                db.add(venta)
                db.flush()  # Para obtener el ID de la venta
                
                # Crear beneficiarios si los hay
                if dialog.result.get('beneficiarios'):
                    for i, beneficiario_data in enumerate(dialog.result['beneficiarios'], 1):
                        beneficiario_cliente = self.get_or_create_cliente(db, beneficiario_data)
                        if beneficiario_cliente:
                            beneficiario = Beneficiario(
                                venta_id=venta.id,
                                titular_id=cliente.id,
                                beneficiario_id=beneficiario_cliente.id,
                                orden=i
                            )
                            db.add(beneficiario)
                
                # Marcar nicho como no disponible
                nicho.disponible = False
                
                db.commit()
                db.close()
                
                self.load_sales()
                self.update_status("Venta creada exitosamente")
                messagebox.showinfo("Éxito", 
                    f"Venta creada exitosamente\nContrato: {numero_contrato}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear venta: {str(e)}")
    
    def get_or_create_cliente(self, db, cliente_data):
        """Obtener cliente existente o crear nuevo"""
        # Buscar cliente existente por cédula

        try:
            cliente = Cliente(
                nombre=cliente_data['nombre'],
                apellido=cliente_data['apellido'],
                # La cédula se genera automáticamente
                telefono=cliente_data.get('telefono'),
                email=cliente_data.get('email'),
                direccion=cliente_data.get('direccion')
            )
            
            db.add(cliente)
            db.flush()  # CRÍTICO: Esto genera el ID del cliente
            return cliente
            
        except Exception as e:
            print(f"Error al crear cliente: {e}")
            return None
    
    def view_sale_details(self):
        """Ver detalles de la venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para ver detalles")
            return
        
        item = self.tree.item(selected[0])
        numero_contrato = item['values'][0]
        
        try:
            db = get_db_session()
            venta = db.query(Venta).filter(Venta.numero_contrato == numero_contrato).first()
            
            if venta:
                VentaDetailsDialog(self.parent, venta)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def edit_sale(self):
        """Editar venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para editar")
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
            
            # Verificar si se puede editar
            if venta.pagos:
                response = messagebox.askyesno("Confirmación", 
                    "Esta venta tiene pagos registrados. ¿Está seguro de que desea editarla?")
                if not response:
                    db.close()
                    return
            
            dialog = VentaDialog(self.parent, "Editar Venta", venta)
            
            if dialog.result:
                # Actualizar datos de la venta
                venta.precio_total = dialog.result['precio_total']
                venta.enganche = dialog.result['enganche']
                venta.saldo_restante = dialog.result['precio_total'] - dialog.result['enganche'] - venta.total_pagado
                venta.tipo_pago = dialog.result['tipo_pago']
                venta.observaciones = dialog.result.get('observaciones')
                
                # Actualizar estado de pago
                venta.actualizar_saldo()
                
                db.commit()
                db.close()
                
                self.load_sales()
                self.update_status("Venta actualizada exitosamente")
                messagebox.showinfo("Éxito", "Venta actualizada exitosamente")
            else:
                db.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar venta: {str(e)}")
    
    def cancel_sale(self):
        """Anular venta seleccionada"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione una venta para anular")
            return
        
        # Confirmar anulación
        response = messagebox.askyesno("Confirmación", 
            "¿Está seguro de que desea anular esta venta?\n"
            "Esta acción liberará el nicho y no se puede deshacer.")
        
        if not response:
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
            
            # Verificar si tiene pagos
            if venta.pagos:
                messagebox.showerror("Error", 
                    "No se puede anular una venta que tiene pagos registrados.\n"
                    "Primero debe anular los pagos.")
                db.close()
                return
            
            # Liberar nicho
            if venta.nicho:
                venta.nicho.disponible = True
            
            # Eliminar beneficiarios
            for beneficiario in venta.beneficiarios:
                db.delete(beneficiario)
            
            # Eliminar venta
            db.delete(venta)
            
            db.commit()
            db.close()
            
            self.load_sales()
            self.update_status("Venta anulada exitosamente")
            messagebox.showinfo("Éxito", "Venta anulada exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al anular venta: {str(e)}")
    
    def on_search(self, event=None):
        """Filtrar ventas según búsqueda"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.load_sales()
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
                estado = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    venta.tipo_pago.title(),
                    f"${venta.saldo_restante:,.2f}",
                    estado
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Búsqueda: {len(ventas)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.filter_estado.set("Todas")
        self.load_sales()
    
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
            if filter_value == "Pagadas":
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
                estado = "Pagado" if venta.pagado_completamente else "Pendiente"
                
                values = (
                    venta.numero_contrato,
                    venta.fecha_venta.strftime("%d/%m/%Y"),
                    cliente_nombre,
                    nicho_numero,
                    f"${venta.precio_total:,.2f}",
                    venta.tipo_pago.title(),
                    f"${venta.saldo_restante:,.2f}",
                    estado
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
            
            # Calcular totales monetarios
            total_vendido = db.query(Venta).with_entities(
                db.func.sum(Venta.precio_total)).scalar() or 0
            total_pendiente = db.query(Venta).with_entities(
                db.func.sum(Venta.saldo_restante)).scalar() or 0
            
            db.close()
            
            info_text = (f"Total Ventas: {total_ventas} | "
                        f"Pagadas: {ventas_pagadas} | "
                        f"Pendientes: {ventas_pendientes} | "
                        f"Monto Total: ${total_vendido:,.2f} | "
                        f"Saldo Pendiente: ${total_pendiente:,.2f}")
            
            ttk.Label(parent, text=info_text, font=("Arial", 10)).pack()
            
        except Exception as e:
            ttk.Label(parent, text="Error al cargar información").pack()
    
    def on_double_click(self, event):
        """Manejar doble clic en TreeView"""
        self.view_sale_details()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Ver Detalles", command=self.view_sale_details)
        context_menu.add_command(label="Editar", command=self.edit_sale)
        context_menu.add_separator()
        context_menu.add_command(label="Anular Venta", command=self.cancel_sale)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()


class VentaDialog:
    def __init__(self, parent, title, venta=None):
        self.result = None
        self.venta = venta
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("600x700")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables para cliente titular
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        
        # Variables para venta
        self.nicho_var = tk.StringVar()
        self.precio_var = tk.StringVar()
        self.enganche_var = tk.StringVar(value="0")
        self.tipo_pago_var = tk.StringVar(value="contado")
        self.observaciones_var = tk.StringVar()
        
        # Lista de beneficiarios
        self.beneficiarios = []
        
        # Cargar datos si se está editando
        if venta:
            self.load_venta_data()
        
        self.create_widgets()
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def load_venta_data(self):
        """Cargar datos de la venta para edición"""
        if self.venta and self.venta.cliente:
            cliente = self.venta.cliente
            self.nombre_var.set(cliente.nombre)
            self.apellido_var.set(cliente.apellido)
            self.telefono_var.set(cliente.telefono or "")
            self.email_var.set(cliente.email or "")
            self.direccion_var.set(cliente.direccion or "")
        
        if self.venta:
            if self.venta.nicho:
                self.nicho_var.set(f"{self.venta.nicho.numero} - {self.venta.nicho.seccion}")
            self.precio_var.set(str(self.venta.precio_total))
            self.enganche_var.set(str(self.venta.enganche))
            self.tipo_pago_var.set(self.venta.tipo_pago)
            self.observaciones_var.set(self.venta.observaciones or "")
            
            # Cargar beneficiarios
            for beneficiario in self.venta.beneficiarios:
                if beneficiario.beneficiario_persona:
                    ben = beneficiario.beneficiario_persona
                    self.beneficiarios.append({
                        'nombre': ben.nombre,
                        'apellido': ben.apellido,
                        'cedula': ben.cedula,
                        'telefono': ben.telefono,
                        'email': ben.email,
                        'direccion': ben.direccion
                    })
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        # Notebook para pestañas
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Pestaña de Cliente
        cliente_frame = ttk.Frame(notebook, padding="20")
        notebook.add(cliente_frame, text="Cliente Titular")
        self.create_cliente_widgets(cliente_frame)
        
        # Pestaña de Nicho
        nicho_frame = ttk.Frame(notebook, padding="20")
        notebook.add(nicho_frame, text="Nicho y Venta")
        self.create_nicho_widgets(nicho_frame)
        
        # Pestaña de Beneficiarios
        beneficiarios_frame = ttk.Frame(notebook, padding="20")
        notebook.add(beneficiarios_frame, text="Beneficiarios")
        self.create_beneficiarios_widgets(beneficiarios_frame)
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
    
    def create_cliente_widgets(self, parent):
        """Crear widgets para datos del cliente"""
        ttk.Label(parent, text="Datos del Cliente Titular", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Nombre
        ttk.Label(parent, text="Nombre:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.nombre_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Apellido
        ttk.Label(parent, text="Apellido:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.apellido_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Teléfono
        ttk.Label(parent, text="Teléfono:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.telefono_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Email
        ttk.Label(parent, text="Email:").grid(row=5, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.email_var, width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Dirección
        ttk.Label(parent, text="Dirección:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=5)
        self.direccion_text = tk.Text(parent, height=3, width=30)
        self.direccion_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        if self.direccion_var.get():
            self.direccion_text.insert("1.0", self.direccion_var.get())
        
        parent.columnconfigure(1, weight=1)
    
    def create_nicho_widgets(self, parent):
        """Crear widgets para selección de nicho y datos de venta"""
        ttk.Label(parent, text="Información de la Venta", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Selección de nicho
        ttk.Label(parent, text="Nicho:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        nicho_frame = ttk.Frame(parent)
        nicho_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        self.nicho_combo = ttk.Combobox(nicho_frame, textvariable=self.nicho_var, 
                                       width=25, state="readonly")
        self.nicho_combo.pack(side=tk.LEFT)
        self.nicho_combo.bind('<<ComboboxSelected>>', self.on_nicho_selected)
        
        ttk.Button(nicho_frame, text="Actualizar", 
                  command=self.update_nichos_list).pack(side=tk.LEFT, padx=(10, 0))
        
        # Precio
        ttk.Label(parent, text="Precio Total:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(parent, textvariable=self.precio_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Tipo de pago
        ttk.Label(parent, text="Tipo de Pago:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        tipo_frame = ttk.Frame(parent)
        tipo_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Radiobutton(tipo_frame, text="Contado", variable=self.tipo_pago_var, 
                       value="contado", command=self.on_tipo_pago_changed).pack(side=tk.LEFT)
        ttk.Radiobutton(tipo_frame, text="Crédito", variable=self.tipo_pago_var, 
                       value="credito", command=self.on_tipo_pago_changed).pack(side=tk.LEFT, padx=(20, 0))
        
        # Enganche (solo para crédito)
        ttk.Label(parent, text="Enganche:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.enganche_entry = ttk.Entry(parent, textvariable=self.enganche_var, width=30)
        self.enganche_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.enganche_entry.bind('<KeyRelease>', self.calculate_saldo)
        
        # Saldo restante
        ttk.Label(parent, text="Saldo Restante:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.saldo_label = ttk.Label(parent, text="$0.00", font=("Arial", 10, "bold"))
        self.saldo_label.grid(row=5, column=1, sticky=tk.W, pady=5)
        
        # Observaciones
        ttk.Label(parent, text="Observaciones:").grid(row=6, column=0, sticky=(tk.W, tk.N), pady=5)
        self.observaciones_text = tk.Text(parent, height=3, width=30)
        self.observaciones_text.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        if self.observaciones_var.get():
            self.observaciones_text.insert("1.0", self.observaciones_var.get())
        
        # Cargar nichos disponibles
        self.update_nichos_list()
        
        # Configurar estado inicial
        self.on_tipo_pago_changed()
        
        parent.columnconfigure(1, weight=1)
    
    def create_beneficiarios_widgets(self, parent):
        """Crear widgets para gestión de beneficiarios"""
        ttk.Label(parent, text="Beneficiarios (Máximo 2)", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Lista de beneficiarios
        list_frame = ttk.LabelFrame(parent, text="Beneficiarios Registrados", padding="10")
        list_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # TreeView para beneficiarios
        self.beneficiarios_tree = ttk.Treeview(list_frame, columns=('nombre', 'cedula'), 
                                             show='headings', height=6)
        self.beneficiarios_tree.heading('nombre', text='Nombre Completo')
        self.beneficiarios_tree.heading('cedula', text='Cédula')
        self.beneficiarios_tree.column('nombre', width=250)
        self.beneficiarios_tree.column('cedula', width=150)
        self.beneficiarios_tree.pack(fill=tk.BOTH, expand=True)
        
        # Botones para beneficiarios
        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="Agregar Beneficiario", 
                  command=self.add_beneficiario).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Eliminar Beneficiario", 
                  command=self.remove_beneficiario).pack(side=tk.LEFT, padx=5)
        
        # Cargar beneficiarios existentes
        self.update_beneficiarios_tree()
        
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
    
    def update_nichos_list(self):
        """Actualizar lista de nichos disponibles"""
        try:
            nichos_disponibles = buscar_nichos_disponibles()
            
            # Si estamos editando, incluir el nicho actual aunque esté vendido
            if self.venta and self.venta.nicho:
                current_nicho = self.venta.nicho
                nicho_actual = f"{current_nicho.numero} - {current_nicho.seccion} (${current_nicho.precio:,.2f})"
                nichos_list = [nicho_actual]
                
                # Agregar otros nichos disponibles
                for nicho in nichos_disponibles:
                    if nicho.id != current_nicho.id:
                        nicho_text = f"{nicho.numero} - {nicho.seccion} (${nicho.precio:,.2f})"
                        nichos_list.append(nicho_text)
            else:
                nichos_list = []
                for nicho in nichos_disponibles:
                    nicho_text = f"{nicho.numero} - {nicho.seccion} (${nicho.precio:,.2f})"
                    nichos_list.append(nicho_text)
            
            self.nicho_combo['values'] = nichos_list
            
            # Si hay un nicho seleccionado y estamos editando, mantenerlo
            if self.venta and self.venta.nicho and not self.nicho_var.get():
                current_nicho = self.venta.nicho
                self.nicho_var.set(f"{current_nicho.numero} - {current_nicho.seccion} (${current_nicho.precio:,.2f})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar nichos: {str(e)}")
    
    def on_nicho_selected(self, event=None):
        """Manejar selección de nicho"""
        nicho_text = self.nicho_var.get()
        if nicho_text:
            # Extraer precio del texto del nicho
            try:
                # Formato: "N0101 - A ($1,500.00)"
                precio_part = nicho_text.split('($')[1].replace(')', '').replace(',', '')
                precio = float(precio_part)
                self.precio_var.set(str(precio))
                self.calculate_saldo()
            except (IndexError, ValueError):
                pass
    
    def on_tipo_pago_changed(self):
        """Manejar cambio de tipo de pago"""
        if self.tipo_pago_var.get() == "contado":
            self.enganche_entry.config(state="disabled")
            self.enganche_var.set(self.precio_var.get())
        else:
            self.enganche_entry.config(state="normal")
            if self.enganche_var.get() == self.precio_var.get():
                self.enganche_var.set("0")
        
        self.calculate_saldo()
    
    def calculate_saldo(self, event=None):
        """Calcular saldo restante"""
        try:
            precio_total = float(self.precio_var.get() or 0)
            enganche = float(self.enganche_var.get() or 0)
            saldo = precio_total - enganche
            self.saldo_label.config(text=f"${saldo:,.2f}")
        except ValueError:
            self.saldo_label.config(text="$0.00")
    
    def add_beneficiario(self):
        """Agregar beneficiario"""
        if len(self.beneficiarios) >= 2:
            messagebox.showwarning("Límite Alcanzado", "Máximo 2 beneficiarios permitidos")
            return
        
        dialog = BeneficiarioDialog(self.dialog, "Agregar Beneficiario")
        if dialog.result:
            self.beneficiarios.append(dialog.result)
            self.update_beneficiarios_tree()
    
    def remove_beneficiario(self):
        """Eliminar beneficiario seleccionado"""
        selected = self.beneficiarios_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un beneficiario para eliminar")
            return
        
        index = self.beneficiarios_tree.index(selected[0])
        del self.beneficiarios[index]
        self.update_beneficiarios_tree()
    
    def update_beneficiarios_tree(self):
        """Actualizar TreeView de beneficiarios"""
        # Limpiar TreeView
        for item in self.beneficiarios_tree.get_children():
            self.beneficiarios_tree.delete(item)
        
        # Agregar beneficiarios
        for i, beneficiario in enumerate(self.beneficiarios, 1):
            nombre_completo = f"{i}. {beneficiario['nombre']} {beneficiario['apellido']}"
            cedula_display = "Se generará automáticamente"
            self.beneficiarios_tree.insert('', 'end', values=(nombre_completo, cedula_display))
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar venta"""
        # Validar datos del cliente (SIN CEDULA)
        if not all([self.nombre_var.get().strip(), self.apellido_var.get().strip()]):
            messagebox.showerror("Error", "Nombre y apellido son obligatorios")
            return
        
        # Validar datos de la venta
        if not self.nicho_var.get():
            messagebox.showerror("Error", "Debe seleccionar un nicho")
            return
        
        try:
            precio_total = float(self.precio_var.get())
            enganche = float(self.enganche_var.get() or 0)
            
            if precio_total <= 0:
                raise ValueError("El precio debe ser mayor a 0")
            
            if enganche < 0 or enganche > precio_total:
                raise ValueError("El enganche debe estar entre 0 y el precio total")
                
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los datos: {str(e)}")
            return
        
        # Obtener dirección del Text widget
        direccion = self.direccion_text.get("1.0", tk.END).strip()
        observaciones = self.observaciones_text.get("1.0", tk.END).strip()
        
        # Obtener ID del nicho seleccionado
        nicho_id = self.get_selected_nicho_id()
        if not nicho_id:
            messagebox.showerror("Error", "No se pudo identificar el nicho seleccionado")
            return
        
        self.result = {
            'cliente': {
                'nombre': self.nombre_var.get().strip(),
                'apellido': self.apellido_var.get().strip(),
                # ELIMINADA: 'cedula': self.cedula_var.get().strip(),
                'telefono': self.telefono_var.get().strip() or None,
                'email': self.email_var.get().strip() or None,
                'direccion': direccion or None
            },
            'nicho_id': nicho_id,
            'precio_total': precio_total,
            'enganche': enganche,
            'tipo_pago': self.tipo_pago_var.get(),
            'observaciones': observaciones or None,
            'beneficiarios': self.beneficiarios.copy()
        }
        
        self.dialog.destroy()
    
    def get_selected_nicho_id(self):
        """Obtener ID del nicho seleccionado"""
        nicho_text = self.nicho_var.get()
        if not nicho_text:
            return None
        
        try:
            # Extraer número del nicho del texto
            nicho_numero = nicho_text.split(' - ')[0]
            
            db = get_db_session()
            nicho = db.query(Nicho).filter(Nicho.numero == nicho_numero).first()
            
            if nicho:
                nicho_id = nicho.id
            else:
                nicho_id = None
            
            db.close()
            return nicho_id
            
        except Exception:
            return None
        
    def get_client_data(self):
        """Obtener datos del cliente del formulario"""
        direccion = self.direccion_text.get("1.0", tk.END).strip()
        
        return {
            'nombre': self.nombre_var.get().strip(),
            'apellido': self.apellido_var.get().strip(),
            # *** ELIMINADA: 'cedula': self.cedula_var.get().strip(), ***
            'telefono': self.telefono_var.get().strip(),
            'email': self.email_var.get().strip(),
            'direccion': direccion if direccion else None
        }
    
    def validate_cliente_data(self, cliente_data):
        """Validar datos del cliente (SIN validación de cédula)"""
        if not cliente_data['nombre']:
            messagebox.showerror("Error", "El nombre es obligatorio")
            return False
        
        if not cliente_data['apellido']:
            messagebox.showerror("Error", "El apellido es obligatorio")
            return False
        
        return True
    
    def show_cliente_info(self, cliente):
        """Mostrar información del cliente recién creado"""
        messagebox.showinfo("Cliente Creado", 
            f"Cliente creado exitosamente:\n"
            f"Nombre: {cliente.nombre_completo}\n"
            f"Cédula: {cliente.cedula}\n"
            f"Teléfono: {cliente.telefono or 'N/A'}")
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()


class BeneficiarioDialog:
    def __init__(self, parent, title):
        self.result = None
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.nombre_var = tk.StringVar()
        self.apellido_var = tk.StringVar()
        self.telefono_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        
        self.create_widgets()
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Datos del Beneficiario", 
                 font=("Arial", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Nombre
        ttk.Label(main_frame, text="Nombre:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.nombre_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Apellido
        ttk.Label(main_frame, text="Apellido:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.apellido_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Teléfono
        ttk.Label(main_frame, text="Teléfono:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.telefono_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Email
        ttk.Label(main_frame, text="Email:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.email_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Dirección
        ttk.Label(main_frame, text="Dirección:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        self.direccion_text = tk.Text(main_frame, height=3, width=30)
        self.direccion_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

        
        # Nota de campos obligatorios
        ttk.Label(main_frame, text="* Campos obligatorios", font=("Arial", 9), 
                 foreground="red").grid(row=6, column=0, columnspan=2, pady=10)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        main_frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar beneficiario"""
        # Validar campos obligatorios
        if not all([self.nombre_var.get().strip(), self.apellido_var.get().strip()]):
            messagebox.showerror("Error", "Nombre y apellido son obligatorios")
            return
        
        # Obtener dirección del Text widget
        direccion = self.direccion_text.get("1.0", tk.END).strip()
        
        self.result = {
            'nombre': self.nombre_var.get().strip(),
            'apellido': self.apellido_var.get().strip(),
            'telefono': self.telefono_var.get().strip() or None,
            'email': self.email_var.get().strip() or None,
            'direccion': direccion or None
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()


class VentaDetailsDialog:
    def __init__(self, parent, venta):
        self.venta = venta
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Detalles de Venta - {venta.numero_contrato}")
        self.dialog.geometry("600x700")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        # Notebook para pestañas
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de información general
        general_frame = ttk.Frame(notebook, padding="20")
        notebook.add(general_frame, text="Información General")
        self.create_general_info(general_frame)
        
        # Pestaña de pagos
        pagos_frame = ttk.Frame(notebook, padding="20")
        notebook.add(pagos_frame, text="Historial de Pagos")
        self.create_pagos_info(pagos_frame)
        
        # Pestaña de beneficiarios
        beneficiarios_frame = ttk.Frame(notebook, padding="20")
        notebook.add(beneficiarios_frame, text="Beneficiarios")
        self.create_beneficiarios_info(beneficiarios_frame)
        
        # Botón cerrar
        ttk.Button(self.dialog, text="Cerrar", command=self.dialog.destroy).pack(pady=10)
    
    def create_general_info(self, parent):
        """Crear información general"""
        # Información de la venta
        info_text = f"""
INFORMACIÓN DE LA VENTA

Número de Contrato: {self.venta.numero_contrato}
Fecha de Venta: {self.venta.fecha_venta.strftime('%d/%m/%Y %H:%M')}
Tipo de Pago: {self.venta.tipo_pago.title()}
Estado: {'Pagado Completamente' if self.venta.pagado_completamente else 'Pendiente'}

CLIENTE TITULAR

Nombre: {self.venta.cliente.nombre_completo}
Cédula: {self.venta.cliente.cedula}
Teléfono: {self.venta.cliente.telefono or 'No registrado'}
Email: {self.venta.cliente.email or 'No registrado'}
Dirección: {self.venta.cliente.direccion or 'No registrada'}

INFORMACIÓN DEL NICHO

Número: {self.venta.nicho.numero}
Sección: {self.venta.nicho.seccion}
Ubicación: Fila {self.venta.nicho.fila}, Columna {self.venta.nicho.columna}

INFORMACIÓN FINANCIERA

Precio Total: ${self.venta.precio_total:,.2f}
Enganche: ${self.venta.enganche:,.2f}
Total Pagado: ${self.venta.total_pagado:,.2f}
Saldo Restante: ${self.venta.saldo_restante:,.2f}

OBSERVACIONES

{self.venta.observaciones or 'Sin observaciones'}
"""
        
        text_widget = tk.Text(parent, wrap=tk.WORD, font=("Arial", 11))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", info_text)
        text_widget.config(state="disabled")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_pagos_info(self, parent):
        """Crear información de pagos"""
        if not self.venta.pagos:
            ttk.Label(parent, text="No hay pagos registrados", 
                     font=("Arial", 12)).pack(pady=50)
            return
        
        # TreeView para pagos
        columns = ('fecha', 'recibo', 'monto', 'metodo', 'concepto')
        tree = ttk.Treeview(parent, columns=columns, show='headings', height=10)
        
        tree.heading('fecha', text='Fecha')
        tree.heading('recibo', text='Recibo')
        tree.heading('monto', text='Monto')
        tree.heading('metodo', text='Método')
        tree.heading('concepto', text='Concepto')
        
        tree.column('fecha', width=100)
        tree.column('recibo', width=120)
        tree.column('monto', width=100)
        tree.column('metodo', width=100)
        tree.column('concepto', width=150)
        
        # Agregar pagos
        for pago in self.venta.pagos:
            values = (
                pago.fecha_pago.strftime('%d/%m/%Y'),
                pago.numero_recibo,
                f"${pago.monto:,.2f}",
                pago.metodo_pago,
                pago.concepto
            )
            tree.insert('', 'end', values=values)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_beneficiarios_info(self, parent):
        """Crear información de beneficiarios"""
        if not self.venta.beneficiarios:
            ttk.Label(parent, text="No hay beneficiarios registrados", 
                     font=("Arial", 12)).pack(pady=50)
            return
        
        for i, beneficiario in enumerate(self.venta.beneficiarios, 1):
            if beneficiario.beneficiario_persona:
                ben = beneficiario.beneficiario_persona
                
                frame = ttk.LabelFrame(parent, text=f"Beneficiario {i}", padding="10")
                frame.pack(fill=tk.X, pady=10)
                
                info_text = f"""
Nombre: {ben.nombre_completo}
Cédula: {ben.cedula}
Teléfono: {ben.telefono or 'No registrado'}
Email: {ben.email or 'No registrado'}
Dirección: {ben.direccion or 'No registrada'}
Estado: {'Activo' if beneficiario.activo else 'Inactivo'}
Fecha de Registro: {beneficiario.fecha_registro.strftime('%d/%m/%Y')}
"""
                
                ttk.Label(frame, text=info_text, font=("Arial", 10)).pack(anchor=tk.W)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")