# ui/busqueda_manager.py
"""
Interfaz para búsquedas avanzadas en el sistema
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database.models import get_db_session, Cliente, Nicho, Venta, Pago

class BusquedaManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.results_tree = None
        
    def show(self):
        """Mostrar interfaz de búsqueda"""
        main_frame = ttk.LabelFrame(self.parent, text="Búsqueda Avanzada", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de criterios de búsqueda
        search_frame = ttk.LabelFrame(main_frame, text="Criterios de Búsqueda", padding="15")
        search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)
        
        self.create_search_widgets(search_frame)
        
        # Frame de búsqueda rápida
        quick_frame = ttk.LabelFrame(main_frame, text="Búsqueda Rápida", padding="10")
        quick_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        quick_frame.columnconfigure(1, weight=1)
        
        self.create_quick_search_widgets(quick_frame)
        
        # Frame de resultados
        results_frame = ttk.LabelFrame(main_frame, text="Resultados de Búsqueda", padding="10")
        results_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        self.create_results_widgets(results_frame)
    
    def create_search_widgets(self, parent):
        """Crear widgets de búsqueda avanzada"""
        # Tipo de búsqueda
        ttk.Label(parent, text="Buscar en:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.search_type = tk.StringVar(value="todo")
        search_type_combo = ttk.Combobox(parent, textvariable=self.search_type, width=30, state="readonly")
        search_type_combo['values'] = ('todo', 'clientes', 'nichos', 'ventas', 'pagos')
        search_type_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        search_type_combo.bind('<<ComboboxSelected>>', self.on_search_type_changed)
        
        # Término de búsqueda
        ttk.Label(parent, text="Término:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.search_term = tk.StringVar()
        search_entry = ttk.Entry(parent, textvariable=self.search_term, width=30)
        search_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        search_entry.bind('<Return>', self.perform_search)
        
        # Campos específicos para cada tipo
        self.fields_frame = ttk.Frame(parent)
        self.fields_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Filtros adicionales
        filters_frame = ttk.LabelFrame(parent, text="Filtros", padding="10")
        filters_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        # Estado
        ttk.Label(filters_frame, text="Estado:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.filter_estado = tk.StringVar(value="todos")
        estado_combo = ttk.Combobox(filters_frame, textvariable=self.filter_estado, width=20, state="readonly")
        estado_combo['values'] = ('todos', 'activos', 'inactivos', 'pagados', 'pendientes', 'disponibles', 'vendidos')
        estado_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        
        # Rango de fechas
        ttk.Label(filters_frame, text="Desde:").grid(row=0, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.fecha_desde = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self.fecha_desde, width=12).grid(row=0, column=3, pady=5, padx=(5, 0))
        
        ttk.Label(filters_frame, text="Hasta:").grid(row=0, column=4, sticky=tk.W, pady=5, padx=(10, 0))
        self.fecha_hasta = tk.StringVar()
        ttk.Entry(filters_frame, textvariable=self.fecha_hasta, width=12).grid(row=0, column=5, pady=5, padx=(5, 0))
        
        # Botones de búsqueda
        buttons_frame = ttk.Frame(parent)
        buttons_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(buttons_frame, text="Buscar", 
                  command=self.perform_search).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Limpiar", 
                  command=self.clear_search).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Búsqueda Guardada", 
                  command=self.save_search).pack(side=tk.LEFT, padx=5)
    
    def create_quick_search_widgets(self, parent):
        """Crear widgets de búsqueda rápida"""
        # Búsqueda por número de contrato
        ttk.Label(parent, text="N° Contrato:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.contrato_var = tk.StringVar()
        contrato_entry = ttk.Entry(parent, textvariable=self.contrato_var, width=20)
        contrato_entry.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Button(parent, text="Buscar", 
                  command=self.search_by_contrato).grid(row=0, column=2, padx=(10, 0))
        
        # Búsqueda por número de cripta
        ttk.Label(parent, text="N° Cripta:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.cripta_var = tk.StringVar()
        cripta_entry = ttk.Entry(parent, textvariable=self.cripta_var, width=20)
        cripta_entry.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Button(parent, text="Buscar", 
                  command=self.search_by_cripta).grid(row=1, column=2, padx=(10, 0))
        
        # Búsqueda por cliente
        ttk.Label(parent, text="Cliente:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.cliente_var = tk.StringVar()
        cliente_entry = ttk.Entry(parent, textvariable=self.cliente_var, width=20)
        cliente_entry.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        ttk.Button(parent, text="Buscar", 
                  command=self.search_by_cliente).grid(row=2, column=2, padx=(10, 0))
        
        # Vincular Enter a búsquedas
        contrato_entry.bind('<Return>', lambda e: self.search_by_contrato())
        cripta_entry.bind('<Return>', lambda e: self.search_by_cripta())
        cliente_entry.bind('<Return>', lambda e: self.search_by_cliente())
    
    def create_results_widgets(self, parent):
        """Crear widgets para mostrar resultados"""
        # TreeView para resultados
        self.results_tree = ttk.Treeview(parent, show='headings', height=15)
        self.results_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.results_tree.yview)
        h_scrollbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Frame de información de resultados
        info_frame = ttk.Frame(parent)
        info_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.results_label = ttk.Label(info_frame, text="Utilice los criterios de búsqueda para encontrar información", 
                                      font=("Arial", 10))
        self.results_label.pack(side=tk.LEFT)
        
        # Botones de acción para resultados
        actions_frame = ttk.Frame(info_frame)
        actions_frame.pack(side=tk.RIGHT)
        
        ttk.Button(actions_frame, text="Ver Detalles", 
                  command=self.view_details).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(actions_frame, text="Exportar Resultados", 
                  command=self.export_results).pack(side=tk.LEFT, padx=5)
        
        # Eventos
        self.results_tree.bind('<Double-1>', self.on_double_click)
        self.results_tree.bind('<Button-3>', self.show_context_menu)
    
    def on_search_type_changed(self, event=None):
        """Manejar cambio de tipo de búsqueda"""
        # Limpiar frame de campos específicos
        for widget in self.fields_frame.winfo_children():
            widget.destroy()
        
        search_type = self.search_type.get()
        
        if search_type == 'clientes':
            self.create_cliente_fields()
        elif search_type == 'nichos':
            self.create_nicho_fields()
        elif search_type == 'ventas':
            self.create_venta_fields()
        elif search_type == 'pagos':
            self.create_pago_fields()
    
    def create_cliente_fields(self):
        """Crear campos específicos para búsqueda de clientes"""
        ttk.Label(self.fields_frame, text="Buscar en:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.cliente_field = tk.StringVar(value="nombre")
        field_combo = ttk.Combobox(self.fields_frame, textvariable=self.cliente_field, 
                                  width=20, state="readonly")
        field_combo['values'] = ('nombre', 'apellido', 'cedula', 'telefono', 'email')
        field_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    def create_nicho_fields(self):
        """Crear campos específicos para búsqueda de nichos"""
        ttk.Label(self.fields_frame, text="Buscar en:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.nicho_field = tk.StringVar(value="numero")
        field_combo = ttk.Combobox(self.fields_frame, textvariable=self.nicho_field, 
                                  width=20, state="readonly")
        field_combo['values'] = ('numero', 'seccion', 'fila', 'columna', 'descripcion')
        field_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    def create_venta_fields(self):
        """Crear campos específicos para búsqueda de ventas"""
        ttk.Label(self.fields_frame, text="Buscar en:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.venta_field = tk.StringVar(value="numero_contrato")
        field_combo = ttk.Combobox(self.fields_frame, textvariable=self.venta_field, 
                                  width=20, state="readonly")
        field_combo['values'] = ('numero_contrato', 'tipo_pago', 'observaciones')
        field_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    def create_pago_fields(self):
        """Crear campos específicos para búsqueda de pagos"""
        ttk.Label(self.fields_frame, text="Buscar en:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.pago_field = tk.StringVar(value="numero_recibo")
        field_combo = ttk.Combobox(self.fields_frame, textvariable=self.pago_field, 
                                  width=20, state="readonly")
        field_combo['values'] = ('numero_recibo', 'metodo_pago', 'concepto', 'observaciones')
        field_combo.grid(row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
    
    def perform_search(self, event=None):
        """Realizar búsqueda avanzada"""
        search_type = self.search_type.get()
        search_term = self.search_term.get().strip().lower()
        
        if not search_term:
            messagebox.showwarning("Advertencia", "Ingrese un término de búsqueda")
            return
        
        try:
            if search_type == 'todo':
                results = self.search_all(search_term)
            elif search_type == 'clientes':
                results = self.search_clientes(search_term)
            elif search_type == 'nichos':
                results = self.search_nichos(search_term)
            elif search_type == 'ventas':
                results = self.search_ventas(search_term)
            elif search_type == 'pagos':
                results = self.search_pagos(search_term)
            else:
                results = []
            
            self.display_results(results, search_type)
            self.update_status(f"Búsqueda completada: {len(results)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def search_all(self, term):
        """Búsqueda en todas las entidades"""
        results = []
        
        # Buscar en clientes
        cliente_results = self.search_clientes(term)
        for result in cliente_results:
            result['tipo'] = 'Cliente'
            results.append(result)
        
        # Buscar en nichos
        nicho_results = self.search_nichos(term)
        for result in nicho_results:
            result['tipo'] = 'Nicho'
            results.append(result)
        
        # Buscar en ventas
        venta_results = self.search_ventas(term)
        for result in venta_results:
            result['tipo'] = 'Venta'
            results.append(result)
        
        # Buscar en pagos
        pago_results = self.search_pagos(term)
        for result in pago_results:
            result['tipo'] = 'Pago'
            results.append(result)
        
        return results
    
    def search_clientes(self, term):
        """Búsqueda en clientes"""
        db = get_db_session()
        
        # Construir query base
        query = db.query(Cliente)
        
        # Aplicar filtros de búsqueda
        if hasattr(self, 'cliente_field') and self.cliente_field.get():
            field = self.cliente_field.get()
            if field == 'nombre':
                query = query.filter(Cliente.nombre.contains(term))
            elif field == 'apellido':
                query = query.filter(Cliente.apellido.contains(term))
            elif field == 'cedula':
                query = query.filter(Cliente.cedula.contains(term))
            elif field == 'telefono':
                query = query.filter(Cliente.telefono.contains(term))
            elif field == 'email':
                query = query.filter(Cliente.email.contains(term))
        else:
            # Búsqueda general en todos los campos
            query = query.filter(
                Cliente.nombre.contains(term) |
                Cliente.apellido.contains(term) |
                Cliente.cedula.contains(term) |
                Cliente.telefono.contains(term) |
                Cliente.email.contains(term)
            )
        
        # Aplicar filtros de fecha si están configurados
        if self.fecha_desde.get():
            fecha_desde = datetime.strptime(self.fecha_desde.get(), "%Y-%m-%d")
            query = query.filter(Cliente.fecha_registro >= fecha_desde)
        
        if self.fecha_hasta.get():
            fecha_hasta = datetime.strptime(self.fecha_hasta.get(), "%Y-%m-%d")
            query = query.filter(Cliente.fecha_registro <= fecha_hasta)
        
        clientes = query.limit(100).all()  # Limitar resultados
        
        results = []
        for cliente in clientes:
            total_ventas = len(cliente.ventas)
            results.append({
                'id': cliente.id,
                'nombre': cliente.nombre_completo,
                'cedula': cliente.cedula,
                'telefono': cliente.telefono or 'N/A',
                'email': cliente.email or 'N/A',
                'ventas': str(total_ventas),
                'fecha_registro': cliente.fecha_registro.strftime('%d/%m/%Y')
            })
        
        db.close()
        return results
    
    def search_nichos(self, term):
        """Búsqueda en nichos"""
        db = get_db_session()
        
        query = db.query(Nicho)
        
        # Aplicar filtros de búsqueda
        if hasattr(self, 'nicho_field') and self.nicho_field.get():
            field = self.nicho_field.get()
            if field == 'numero':
                query = query.filter(Nicho.numero.contains(term))
            elif field == 'seccion':
                query = query.filter(Nicho.seccion.contains(term))
            elif field == 'fila':
                query = query.filter(Nicho.fila.contains(term))
            elif field == 'columna':
                query = query.filter(Nicho.columna.contains(term))
            elif field == 'descripcion':
                query = query.filter(Nicho.descripcion.contains(term))
        else:
            # Búsqueda general
            query = query.filter(
                Nicho.numero.contains(term) |
                Nicho.seccion.contains(term) |
                Nicho.fila.contains(term) |
                Nicho.columna.contains(term) |
                Nicho.descripcion.contains(term)
            )
        
        # Aplicar filtro de estado
        if self.filter_estado.get() == 'disponibles':
            query = query.filter(Nicho.disponible == True)
        elif self.filter_estado.get() == 'vendidos':
            query = query.filter(Nicho.disponible == False)
        
        nichos = query.limit(100).all()
        
        results = []
        for nicho in nichos:
            estado = "Disponible" if nicho.disponible else "Vendido"
            cliente = ""
            if nicho.ventas:
                cliente = nicho.ventas[0].cliente.nombre_completo
            
            results.append({
                'id': nicho.id,
                'numero': nicho.numero,
                'seccion': nicho.seccion,
                'ubicacion': f"F{nicho.fila}-C{nicho.columna}",
                'precio': f"${nicho.precio:,.2f}",
                'estado': estado,
                'cliente': cliente
            })
        
        db.close()
        return results
    
    def search_ventas(self, term):
        """Búsqueda en ventas"""
        db = get_db_session()
        
        query = db.query(Venta).join(Cliente).join(Nicho)
        
        # Aplicar filtros de búsqueda
        if hasattr(self, 'venta_field') and self.venta_field.get():
            field = self.venta_field.get()
            if field == 'numero_contrato':
                query = query.filter(Venta.numero_contrato.contains(term))
            elif field == 'tipo_pago':
                query = query.filter(Venta.tipo_pago.contains(term))
            elif field == 'observaciones':
                query = query.filter(Venta.observaciones.contains(term))
        else:
            # Búsqueda general
            query = query.filter(
                Venta.numero_contrato.contains(term) |
                Cliente.nombre.contains(term) |
                Cliente.apellido.contains(term) |
                Cliente.cedula.contains(term) |
                Nicho.numero.contains(term)
            )
        
        # Aplicar filtros de estado
        if self.filter_estado.get() == 'pagados':
            query = query.filter(Venta.pagado_completamente == True)
        elif self.filter_estado.get() == 'pendientes':
            query = query.filter(Venta.pagado_completamente == False)
        
        # Aplicar filtros de fecha
        if self.fecha_desde.get():
            fecha_desde = datetime.strptime(self.fecha_desde.get(), "%Y-%m-%d")
            query = query.filter(Venta.fecha_venta >= fecha_desde)
        
        if self.fecha_hasta.get():
            fecha_hasta = datetime.strptime(self.fecha_hasta.get(), "%Y-%m-%d")
            query = query.filter(Venta.fecha_venta <= fecha_hasta)
        
        ventas = query.limit(100).all()
        
        results = []
        for venta in ventas:
            estado = "Pagado" if venta.pagado_completamente else "Pendiente"
            results.append({
                'id': venta.id,
                'contrato': venta.numero_contrato,
                'fecha': venta.fecha_venta.strftime('%d/%m/%Y'),
                'cliente': venta.cliente.nombre_completo,
                'nicho': venta.nicho.numero,
                'precio': f"${venta.precio_total:,.2f}",
                'saldo': f"${venta.saldo_restante:,.2f}",
                'estado': estado
            })
        
        db.close()
        return results
    
    def search_pagos(self, term):
        """Búsqueda en pagos"""
        db = get_db_session()
        
        query = db.query(Pago).join(Venta).join(Cliente)
        
        # Aplicar filtros de búsqueda
        if hasattr(self, 'pago_field') and self.pago_field.get():
            field = self.pago_field.get()
            if field == 'numero_recibo':
                query = query.filter(Pago.numero_recibo.contains(term))
            elif field == 'metodo_pago':
                query = query.filter(Pago.metodo_pago.contains(term))
            elif field == 'concepto':
                query = query.filter(Pago.concepto.contains(term))
            elif field == 'observaciones':
                query = query.filter(Pago.observaciones.contains(term))
        else:
            # Búsqueda general
            query = query.filter(
                Pago.numero_recibo.contains(term) |
                Pago.concepto.contains(term) |
                Venta.numero_contrato.contains(term) |
                Cliente.nombre.contains(term) |
                Cliente.apellido.contains(term)
            )
        
        # Aplicar filtros de fecha
        if self.fecha_desde.get():
            fecha_desde = datetime.strptime(self.fecha_desde.get(), "%Y-%m-%d")
            query = query.filter(Pago.fecha_pago >= fecha_desde)
        
        if self.fecha_hasta.get():
            fecha_hasta = datetime.strptime(self.fecha_hasta.get(), "%Y-%m-%d")
            query = query.filter(Pago.fecha_pago <= fecha_hasta)
        
        pagos = query.limit(100).all()
        
        results = []
        for pago in pagos:
            results.append({
                'id': pago.id,
                'recibo': pago.numero_recibo,
                'fecha': pago.fecha_pago.strftime('%d/%m/%Y'),
                'contrato': pago.venta.numero_contrato,
                'cliente': pago.venta.cliente.nombre_completo,
                'monto': f"${pago.monto:,.2f}",
                'metodo': pago.metodo_pago,
                'concepto': pago.concepto
            })
        
        db.close()
        return results
    
    def display_results(self, results, search_type):
        """Mostrar resultados en el TreeView"""
        # Limpiar resultados anteriores
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        if not results:
            self.results_label.config(text="No se encontraron resultados")
            return
        
        # Configurar columnas según el tipo de búsqueda
        if search_type == 'todo':
            columns = ['tipo', 'id', 'descripcion', 'detalle1', 'detalle2']
            self.results_tree['columns'] = columns
            self.results_tree.heading('tipo', text='Tipo')
            self.results_tree.heading('id', text='ID')
            self.results_tree.heading('descripcion', text='Descripción')
            self.results_tree.heading('detalle1', text='Detalle 1')
            self.results_tree.heading('detalle2', text='Detalle 2')
            
            for result in results:
                if result['tipo'] == 'Cliente':
                    values = (result['tipo'], result['id'], result['nombre'], 
                             result['cedula'], result['telefono'])
                elif result['tipo'] == 'Nicho':
                    values = (result['tipo'], result['id'], result['numero'], 
                             result['seccion'], result['estado'])
                elif result['tipo'] == 'Venta':
                    values = (result['tipo'], result['id'], result['contrato'], 
                             result['cliente'], result['estado'])
                elif result['tipo'] == 'Pago':
                    values = (result['tipo'], result['id'], result['recibo'], 
                             result['cliente'], result['monto'])
                else:
                    values = (result['tipo'], result['id'], '', '', '')
                
                self.results_tree.insert('', 'end', values=values)
        
        elif search_type == 'clientes':
            columns = ['nombre', 'cedula', 'telefono', 'email', 'ventas', 'fecha_registro']
            self.results_tree['columns'] = columns
            for col in columns:
                self.results_tree.heading(col, text=col.replace('_', ' ').title())
            
            for result in results:
                values = tuple(result[col] for col in columns)
                self.results_tree.insert('', 'end', values=values)
        
        elif search_type == 'nichos':
            columns = ['numero', 'seccion', 'ubicacion', 'precio', 'estado', 'cliente']
            self.results_tree['columns'] = columns
            for col in columns:
                self.results_tree.heading(col, text=col.replace('_', ' ').title())
            
            for result in results:
                values = tuple(result[col] for col in columns)
                self.results_tree.insert('', 'end', values=values)
        
        elif search_type == 'ventas':
            columns = ['contrato', 'fecha', 'cliente', 'nicho', 'precio', 'saldo', 'estado']
            self.results_tree['columns'] = columns
            for col in columns:
                self.results_tree.heading(col, text=col.replace('_', ' ').title())
            
            for result in results:
                values = tuple(result[col] for col in columns)
                self.results_tree.insert('', 'end', values=values)
        
        elif search_type == 'pagos':
            columns = ['recibo', 'fecha', 'contrato', 'cliente', 'monto', 'metodo', 'concepto']
            self.results_tree['columns'] = columns
            for col in columns:
                self.results_tree.heading(col, text=col.replace('_', ' ').title())
            
            for result in results:
                values = tuple(result[col] for col in columns)
                self.results_tree.insert('', 'end', values=values)
        
        # Ajustar ancho de columnas
        for col in self.results_tree['columns']:
            self.results_tree.column(col, width=120)
        
        # Actualizar etiqueta de resultados
        self.results_label.config(text=f"Encontrados {len(results)} resultados")
    
    def search_by_contrato(self):
        """Búsqueda rápida por número de contrato"""
        contrato = self.contrato_var.get().strip()
        if not contrato:
            messagebox.showwarning("Advertencia", "Ingrese un número de contrato")
            return
        
        try:
            db = get_db_session()
            venta = db.query(Venta).join(Cliente).join(Nicho).filter(
                Venta.numero_contrato.contains(contrato)
            ).first()
            
            if venta:
                # Mostrar resultado
                results = [{
                    'id': venta.id,
                    'contrato': venta.numero_contrato,
                    'fecha': venta.fecha_venta.strftime('%d/%m/%Y'),
                    'cliente': venta.cliente.nombre_completo,
                    'nicho': venta.nicho.numero,
                    'precio': f"${venta.precio_total:,.2f}",
                    'saldo': f"${venta.saldo_restante:,.2f}",
                    'estado': "Pagado" if venta.pagado_completamente else "Pendiente"
                }]
                
                self.display_results(results, 'ventas')
                self.update_status("Venta encontrada")
            else:
                self.results_label.config(text="No se encontró venta con ese número de contrato")
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def search_by_cripta(self):
        """Búsqueda rápida por número de cripta"""
        cripta = self.cripta_var.get().strip()
        if not cripta:
            messagebox.showwarning("Advertencia", "Ingrese un número de cripta")
            return
        
        try:
            db = get_db_session()
            nicho = db.query(Nicho).filter(
                Nicho.numero.contains(cripta)
            ).first()
            
            if nicho:
                cliente = ""
                if nicho.ventas:
                    cliente = nicho.ventas[0].cliente.nombre_completo
                
                results = [{
                    'id': nicho.id,
                    'numero': nicho.numero,
                    'seccion': nicho.seccion,
                    'ubicacion': f"F{nicho.fila}-C{nicho.columna}",
                    'precio': f"${nicho.precio:,.2f}",
                    'estado': "Disponible" if nicho.disponible else "Vendido",
                    'cliente': cliente
                }]
                
                self.display_results(results, 'nichos')
                self.update_status("Cripta encontrada")
            else:
                self.results_label.config(text="No se encontró cripta con ese número")
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def search_by_cliente(self):
        """Búsqueda rápida por nombre de cliente"""
        cliente = self.cliente_var.get().strip()
        if not cliente:
            messagebox.showwarning("Advertencia", "Ingrese un nombre de cliente")
            return
        
        try:
            db = get_db_session()
            clientes = db.query(Cliente).filter(
                Cliente.nombre.contains(cliente) |
                Cliente.apellido.contains(cliente) |
                Cliente.cedula.contains(cliente)
            ).limit(10).all()
            
            if clientes:
                results = []
                for cli in clientes:
                    total_ventas = len(cli.ventas)
                    results.append({
                        'id': cli.id,
                        'nombre': cli.nombre_completo,
                        'cedula': cli.cedula,
                        'telefono': cli.telefono or 'N/A',
                        'email': cli.email or 'N/A',
                        'ventas': str(total_ventas),
                        'fecha_registro': cli.fecha_registro.strftime('%d/%m/%Y')
                    })
                
                self.display_results(results, 'clientes')
                self.update_status(f"Encontrados {len(results)} clientes")
            else:
                self.results_label.config(text="No se encontraron clientes con ese criterio")
                for item in self.results_tree.get_children():
                    self.results_tree.delete(item)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def clear_search(self):
        """Limpiar criterios de búsqueda y resultados"""
        self.search_term.set("")
        self.contrato_var.set("")
        self.cripta_var.set("")
        self.cliente_var.set("")
        self.fecha_desde.set("")
        self.fecha_hasta.set("")
        self.filter_estado.set("todos")
        
        # Limpiar resultados
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        self.results_label.config(text="Utilice los criterios de búsqueda para encontrar información")
        self.update_status("Búsqueda limpiada")
    
    def view_details(self):
        """Ver detalles del elemento seleccionado"""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un elemento para ver detalles")
            return
        
        # Aquí implementarías la lógica para mostrar detalles
        # dependiendo del tipo de resultado seleccionado
        messagebox.showinfo("Información", "Funcionalidad de detalles próximamente")
    
    def export_results(self):
        """Exportar resultados de búsqueda"""
        if not self.results_tree.get_children():
            messagebox.showwarning("Advertencia", "No hay resultados para exportar")
            return
        
        # Aquí implementarías la exportación de resultados
        messagebox.showinfo("Información", "Funcionalidad de exportación próximamente")
    
    def save_search(self):
        """Guardar criterios de búsqueda"""
        messagebox.showinfo("Información", "Funcionalidad de búsquedas guardadas próximamente")
    
    def on_double_click(self, event):
        """Manejar doble clic en resultado"""
        self.view_details()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Ver Detalles", command=self.view_details)
        context_menu.add_command(label="Exportar Resultados", command=self.export_results)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()