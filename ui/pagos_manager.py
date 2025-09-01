# ui/pagos_manager.py
"""
Interfaz para la gestión de pagos
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import os
from database.models import (get_db_session, Venta, Pago, Cliente, Nicho, 
                           generar_numero_recibo, buscar_venta_por_contrato)
from reports.pdf_generator import PDFGenerator

class PagosManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.tree = None
        self.search_var = tk.StringVar()
        self.pdf_generator = PDFGenerator()
        
    def show(self):
        """Mostrar interfaz de gestión de pagos"""
        main_frame = ttk.LabelFrame(self.parent, text="Gestión de Pagos", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de controles superiores
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(controls_frame, text="Nuevo Pago", 
                  command=self.new_payment).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Ver Detalles", 
                  command=self.view_payment_details).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Editar Pago", 
                  command=self.edit_payment).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Anular Pago", 
                  command=self.cancel_payment).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Imprimir Recibo", 
                  command=self.print_receipt).pack(side=tk.LEFT, padx=(0, 10))
        
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
        
        # Filtros por fecha
        filter_frame = ttk.LabelFrame(search_frame, text="Filtros por Fecha", padding="5")
        filter_frame.grid(row=0, column=3, padx=(10, 0))
        
        self.filter_fecha = tk.StringVar(value="Todos")
        ttk.Radiobutton(filter_frame, text="Todos", variable=self.filter_fecha, 
                       value="Todos", command=self.apply_filters).grid(row=0, column=0)
        ttk.Radiobutton(filter_frame, text="Hoy", variable=self.filter_fecha, 
                       value="Hoy", command=self.apply_filters).grid(row=0, column=1)
        ttk.Radiobutton(filter_frame, text="Esta Semana", variable=self.filter_fecha, 
                       value="Semana", command=self.apply_filters).grid(row=0, column=2)
        ttk.Radiobutton(filter_frame, text="Este Mes", variable=self.filter_fecha, 
                       value="Mes", command=self.apply_filters).grid(row=0, column=3)
        
        # Lista de pagos
        self.create_payments_tree(main_frame)
        
        # Cargar datos
        self.load_payments()
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Resumen del Día", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.update_info_display(info_frame)
    
    def create_payments_tree(self, parent):
        """Crear TreeView para mostrar pagos"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # TreeView
        columns = ('fecha', 'recibo', 'contrato', 'cliente', 'monto', 'metodo', 'concepto')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('fecha', text='Fecha')
        self.tree.heading('recibo', text='N° Recibo')
        self.tree.heading('contrato', text='Contrato')
        self.tree.heading('cliente', text='Cliente')
        self.tree.heading('monto', text='Monto')
        self.tree.heading('metodo', text='Método')
        self.tree.heading('concepto', text='Concepto')
        
        self.tree.column('fecha', width=100)
        self.tree.column('recibo', width=120)
        self.tree.column('contrato', width=120)
        self.tree.column('cliente', width=200)
        self.tree.column('monto', width=120)
        self.tree.column('metodo', width=100)
        self.tree.column('concepto', width=200)
        
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
    
    def load_payments(self):
        """Cargar pagos desde la base de datos"""
        try:
            db = get_db_session()
            pagos = db.query(Pago).join(Venta).join(Cliente).order_by(Pago.fecha_pago.desc()).all()
            
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar pagos
            for pago in pagos:
                cliente_nombre = pago.venta.cliente.nombre_completo if pago.venta.cliente else "N/A"
                
                values = (
                    pago.fecha_pago.strftime("%d/%m/%Y"),
                    pago.numero_recibo,
                    pago.venta.numero_contrato,
                    cliente_nombre,
                    f"${pago.monto:,.2f}",
                    pago.metodo_pago,
                    pago.concepto
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Pagos cargados: {len(pagos)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar pagos: {str(e)}")
    
    def new_payment(self):
        """Registrar nuevo pago"""
        dialog = PagoDialog(self.parent, "Nuevo Pago")
        if dialog.result:
            try:
                db = get_db_session()
                
                # Buscar la venta
                venta = db.query(Venta).filter(
                    Venta.numero_contrato == dialog.result['numero_contrato']
                ).first()
                
                if not venta:
                    messagebox.showerror("Error", "No se encontró la venta con ese número de contrato")
                    db.close()
                    return
                
                if venta.pagado_completamente:
                    response = messagebox.askyesno("Confirmación", 
                        "Esta venta ya está pagada completamente. ¿Desea continuar?")
                    if not response:
                        db.close()
                        return
                
                # Generar número de recibo
                numero_recibo = generar_numero_recibo()
                
                # Crear pago
                pago = Pago(
                    venta_id=venta.id,
                    numero_recibo=numero_recibo,
                    monto=dialog.result['monto'],
                    metodo_pago=dialog.result['metodo_pago'],
                    concepto=dialog.result['concepto'],
                    observaciones=dialog.result.get('observaciones')
                )
                
                db.add(pago)
                
                # Actualizar saldo de la venta
                venta.actualizar_saldo()
                venta.fecha_ultimo_pago = datetime.now()
                
                db.commit()
                
                # Generar recibo PDF automáticamente
                self.generate_receipt_pdf(pago, venta)
                
                db.close()
                
                self.load_payments()
                self.update_status("Pago registrado exitosamente")
                messagebox.showinfo("Éxito", 
                    f"Pago registrado exitosamente\nRecibo: {numero_recibo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar pago: {str(e)}")
    
    def generate_receipt_pdf(self, pago, venta):
        """Generar PDF del recibo"""
        try:
            # Preparar datos para el PDF
            pago_data = {
                'numero_recibo': pago.numero_recibo,
                'fecha_pago': pago.fecha_pago,
                'monto': pago.monto,
                'metodo_pago': pago.metodo_pago,
                'concepto': pago.concepto,
                'observaciones': pago.observaciones
            }
            
            venta_data = {
                'numero_contrato': venta.numero_contrato,
                'precio_total': venta.precio_total,
                'saldo_anterior': venta.saldo_restante + pago.monto,
                'saldo_restante': venta.saldo_restante,
                'pagado_completamente': venta.pagado_completamente
            }
            
            cliente_data = {
                'nombre': venta.cliente.nombre,
                'apellido': venta.cliente.apellido,
                'cedula': venta.cliente.cedula,
                'telefono': venta.cliente.telefono,
                'direccion': venta.cliente.direccion
            }
            
            nicho_data = {
                'numero': venta.nicho.numero,
                'seccion': venta.nicho.seccion,
                'fila': venta.nicho.fila,
                'columna': venta.nicho.columna
            }
            
            # Generar PDF
            pdf_path = self.pdf_generator.generar_recibo_pago(
                pago_data, venta_data, cliente_data, nicho_data
            )
            
            # Preguntar si desea abrir el PDF
            response = messagebox.askyesno("PDF Generado", 
                f"Recibo generado exitosamente:\n{pdf_path}\n\n¿Desea abrirlo ahora?")
            
            if response:
                os.startfile(pdf_path)  # Windows
                # Para Linux/Mac usar: os.system(f"xdg-open {pdf_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar PDF: {str(e)}")
    
    def view_payment_details(self):
        """Ver detalles del pago seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para ver detalles")
            return
        
        item = self.tree.item(selected[0])
        numero_recibo = item['values'][1]
        
        try:
            db = get_db_session()
            pago = db.query(Pago).filter(Pago.numero_recibo == numero_recibo).first()
            
            if pago:
                PagoDetailsDialog(self.parent, pago)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")
    
    def edit_payment(self):
        """Editar pago seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para editar")
            return
        
        item = self.tree.item(selected[0])
        numero_recibo = item['values'][1]
        
        try:
            db = get_db_session()
            pago = db.query(Pago).filter(Pago.numero_recibo == numero_recibo).first()
            
            if not pago:
                messagebox.showerror("Error", "Pago no encontrado")
                db.close()
                return
            
            # Confirmar edición
            response = messagebox.askyesno("Confirmación", 
                "¿Está seguro de que desea editar este pago?\n"
                "Esto afectará el saldo de la venta.")
            
            if not response:
                db.close()
                return
            
            dialog = PagoDialog(self.parent, "Editar Pago", pago)
            
            if dialog.result:
                # Guardar monto anterior para recalcular saldo
                monto_anterior = pago.monto
                
                # Actualizar datos del pago
                pago.monto = dialog.result['monto']
                pago.metodo_pago = dialog.result['metodo_pago']
                pago.concepto = dialog.result['concepto']
                pago.observaciones = dialog.result.get('observaciones')
                
                # Recalcular saldo de la venta
                venta = pago.venta
                diferencia = dialog.result['monto'] - monto_anterior
                venta.saldo_restante -= diferencia
                venta.actualizar_saldo()
                
                db.commit()
                db.close()
                
                self.load_payments()
                self.update_status("Pago actualizado exitosamente")
                messagebox.showinfo("Éxito", "Pago actualizado exitosamente")
            else:
                db.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar pago: {str(e)}")
    
    def cancel_payment(self):
        """Anular pago seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para anular")
            return
        
        # Confirmar anulación
        response = messagebox.askyesno("Confirmación", 
            "¿Está seguro de que desea anular este pago?\n"
            "Esta acción ajustará el saldo de la venta y no se puede deshacer.")
        
        if not response:
            return
        
        item = self.tree.item(selected[0])
        numero_recibo = item['values'][1]
        
        try:
            db = get_db_session()
            pago = db.query(Pago).filter(Pago.numero_recibo == numero_recibo).first()
            
            if not pago:
                messagebox.showerror("Error", "Pago no encontrado")
                db.close()
                return
            
            # Ajustar saldo de la venta
            venta = pago.venta
            venta.saldo_restante += pago.monto
            venta.pagado_completamente = False
            
            # Eliminar pago
            db.delete(pago)
            
            db.commit()
            db.close()
            
            self.load_payments()
            self.update_status("Pago anulado exitosamente")
            messagebox.showinfo("Éxito", "Pago anulado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al anular pago: {str(e)}")
    
    def print_receipt(self):
        """Imprimir recibo del pago seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un pago para imprimir recibo")
            return
        
        item = self.tree.item(selected[0])
        numero_recibo = item['values'][1]
        
        try:
            db = get_db_session()
            pago = db.query(Pago).filter(Pago.numero_recibo == numero_recibo).first()
            
            if pago:
                self.generate_receipt_pdf(pago, pago.venta)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recibo: {str(e)}")
    
    def on_search(self, event=None):
        """Filtrar pagos según búsqueda"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.load_payments()
            return
        
        try:
            db = get_db_session()
            query = db.query(Pago).join(Venta).join(Cliente)
            
            # Filtrar por término de búsqueda
            query = query.filter(
                Pago.numero_recibo.contains(search_term) |
                Venta.numero_contrato.contains(search_term) |
                Cliente.nombre.contains(search_term) |
                Cliente.apellido.contains(search_term) |
                Cliente.cedula.contains(search_term) |
                Pago.concepto.contains(search_term)
            )
            
            pagos = query.order_by(Pago.fecha_pago.desc()).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for pago in pagos:
                cliente_nombre = pago.venta.cliente.nombre_completo if pago.venta.cliente else "N/A"
                
                values = (
                    pago.fecha_pago.strftime("%d/%m/%Y"),
                    pago.numero_recibo,
                    pago.venta.numero_contrato,
                    cliente_nombre,
                    f"${pago.monto:,.2f}",
                    pago.metodo_pago,
                    pago.concepto
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Búsqueda: {len(pagos)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.filter_fecha.set("Todos")
        self.load_payments()
    
    def apply_filters(self):
        """Aplicar filtros de fecha"""
        filter_value = self.filter_fecha.get()
        
        try:
            db = get_db_session()
            query = db.query(Pago).join(Venta).join(Cliente)
            
            # Aplicar filtro de búsqueda si existe
            search_term = self.search_var.get().lower()
            if search_term:
                query = query.filter(
                    Pago.numero_recibo.contains(search_term) |
                    Venta.numero_contrato.contains(search_term) |
                    Cliente.nombre.contains(search_term) |
                    Cliente.apellido.contains(search_term) |
                    Cliente.cedula.contains(search_term) |
                    Pago.concepto.contains(search_term)
                )
            
            # Aplicar filtro de fecha
            today = datetime.now().date()
            if filter_value == "Hoy":
                query = query.filter(db.func.date(Pago.fecha_pago) == today)
            elif filter_value == "Semana":
                week_start = today - timedelta(days=today.weekday())
                query = query.filter(db.func.date(Pago.fecha_pago) >= week_start)
            elif filter_value == "Mes":
                month_start = today.replace(day=1)
                query = query.filter(db.func.date(Pago.fecha_pago) >= month_start)
            
            pagos = query.order_by(Pago.fecha_pago.desc()).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for pago in pagos:
                cliente_nombre = pago.venta.cliente.nombre_completo if pago.venta.cliente else "N/A"
                
                values = (
                    pago.fecha_pago.strftime("%d/%m/%Y"),
                    pago.numero_recibo,
                    pago.venta.numero_contrato,
                    cliente_nombre,
                    f"${pago.monto:,.2f}",
                    pago.metodo_pago,
                    pago.concepto
                )
                
                self.tree.insert('', 'end', values=values)
            
            db.close()
            self.update_status(f"Filtro aplicado: {len(pagos)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")
    
    def update_info_display(self, parent):
        """Actualizar display de información del día"""
        try:
            db = get_db_session()
            
            today = datetime.now().date()
            
            # Pagos del día
            pagos_hoy = db.query(Pago).filter(
                db.func.date(Pago.fecha_pago) == today
            ).all()
            
            total_pagos = len(pagos_hoy)
            monto_total = sum(pago.monto for pago in pagos_hoy)
            
            # Métodos de pago más usados
            metodos = {}
            for pago in pagos_hoy:
                metodos[pago.metodo_pago] = metodos.get(pago.metodo_pago, 0) + 1
            
            metodo_principal = max(metodos, key=metodos.get) if metodos else "N/A"
            
            db.close()
            
            info_text = (f"Pagos Hoy: {total_pagos} | "
                        f"Monto Total: ${monto_total:,.2f} | "
                        f"Método Principal: {metodo_principal}")
            
            ttk.Label(parent, text=info_text, font=("Arial", 10)).pack()
            
        except Exception as e:
            ttk.Label(parent, text="Error al cargar información del día").pack()
    
    def on_double_click(self, event):
        """Manejar doble clic en TreeView"""
        self.view_payment_details()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Ver Detalles", command=self.view_payment_details)
        context_menu.add_command(label="Editar", command=self.edit_payment)
        context_menu.add_command(label="Imprimir Recibo", command=self.print_receipt)
        context_menu.add_separator()
        context_menu.add_command(label="Anular Pago", command=self.cancel_payment)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()


class PagoDialog:
    def __init__(self, parent, title, pago=None):
        self.result = None
        self.pago = pago
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x600")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.numero_contrato_var = tk.StringVar()
        self.monto_var = tk.StringVar()
        self.metodo_pago_var = tk.StringVar(value="efectivo")
        self.concepto_var = tk.StringVar(value="Abono a cuenta")
        self.observaciones_var = tk.StringVar()
        
        # Variables para mostrar información de la venta
        self.cliente_info_var = tk.StringVar()
        self.venta_info_var = tk.StringVar()
        self.saldo_info_var = tk.StringVar()
        
        # Cargar datos si se está editando
        if pago:
            self.load_pago_data()
        
        self.create_widgets()
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def load_pago_data(self):
        """Cargar datos del pago para edición"""
        if self.pago:
            self.numero_contrato_var.set(self.pago.venta.numero_contrato)
            self.monto_var.set(str(self.pago.monto))
            self.metodo_pago_var.set(self.pago.metodo_pago)
            self.concepto_var.set(self.pago.concepto)
            self.observaciones_var.set(self.pago.observaciones or "")
            
            # Cargar información de la venta
            self.load_venta_info()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Registrar Pago", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Número de contrato
        ttk.Label(main_frame, text="N° de Contrato:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        contrato_frame = ttk.Frame(main_frame)
        contrato_frame.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        contrato_entry = ttk.Entry(contrato_frame, textvariable=self.numero_contrato_var, width=20)
        contrato_entry.pack(side=tk.LEFT)
        
        if not self.pago:  # Solo permitir buscar si es nuevo pago
            ttk.Button(contrato_frame, text="Buscar", 
                      command=self.search_venta).pack(side=tk.LEFT, padx=(10, 0))
        else:
            contrato_entry.config(state="disabled")
        
        # Información del cliente (solo lectura)
        ttk.Label(main_frame, text="Cliente:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.cliente_info_var, 
                 foreground="blue").grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # Información de la venta (solo lectura)
        ttk.Label(main_frame, text="Venta:").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.venta_info_var, 
                 foreground="blue").grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # Información del saldo (solo lectura)
        ttk.Label(main_frame, text="Saldo Actual:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Label(main_frame, textvariable=self.saldo_info_var, 
                 foreground="red", font=("Arial", 11, "bold")).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, 
                                                           sticky=(tk.W, tk.E), pady=20)
        
        # Monto del pago
        ttk.Label(main_frame, text="Monto del Pago:*").grid(row=6, column=0, sticky=tk.W, pady=5)
        monto_frame = ttk.Frame(main_frame)
        monto_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(monto_frame, text="$").pack(side=tk.LEFT)
        monto_entry = ttk.Entry(monto_frame, textvariable=self.monto_var, width=15)
        monto_entry.pack(side=tk.LEFT)
        monto_entry.bind('<KeyRelease>', self.calculate_new_saldo)
        
        # Nuevo saldo (calculado)
        ttk.Label(main_frame, text="Nuevo Saldo:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.nuevo_saldo_label = ttk.Label(main_frame, text="$0.00", 
                                          foreground="green", font=("Arial", 11, "bold"))
        self.nuevo_saldo_label.grid(row=7, column=1, sticky=tk.W, pady=5)
        
        # Método de pago
        ttk.Label(main_frame, text="Método de Pago:*").grid(row=8, column=0, sticky=tk.W, pady=5)
        metodo_combo = ttk.Combobox(main_frame, textvariable=self.metodo_pago_var, width=27)
        metodo_combo['values'] = ('efectivo', 'transferencia', 'cheque', 'tarjeta_credito', 
                                 'tarjeta_debito', 'deposito')
        metodo_combo.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Concepto
        ttk.Label(main_frame, text="Concepto:*").grid(row=9, column=0, sticky=tk.W, pady=5)
        concepto_combo = ttk.Combobox(main_frame, textvariable=self.concepto_var, width=27)
        concepto_combo['values'] = ('Abono a cuenta', 'Pago total', 'Enganche', 
                                   'Cuota mensual', 'Pago parcial', 'Liquidación')
        concepto_combo.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Observaciones
        ttk.Label(main_frame, text="Observaciones:").grid(row=10, column=0, sticky=(tk.W, tk.N), pady=5)
        self.observaciones_text = tk.Text(main_frame, height=4, width=30)
        self.observaciones_text.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5)
        if self.observaciones_var.get():
            self.observaciones_text.insert("1.0", self.observaciones_var.get())
        
        # Nota de campos obligatorios
        ttk.Label(main_frame, text="* Campos obligatorios", font=("Arial", 9), 
                 foreground="red").grid(row=11, column=0, columnspan=2, pady=10)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=12, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Si se está editando, cargar información de la venta
        if self.pago:
            self.load_venta_info()
    
    def search_venta(self):
        """Buscar venta por número de contrato"""
        numero_contrato = self.numero_contrato_var.get().strip()
        if not numero_contrato:
            messagebox.showwarning("Advertencia", "Ingrese un número de contrato")
            return
        
        try:
            db = get_db_session()
            venta = db.query(Venta).filter(Venta.numero_contrato == numero_contrato).first()
            
            if venta:
                self.load_venta_info(venta)
                messagebox.showinfo("Venta Encontrada", 
                    f"Venta encontrada: {venta.cliente.nombre_completo}")
            else:
                messagebox.showerror("Venta No Encontrada", 
                    "No se encontró una venta con ese número de contrato")
                self.clear_venta_info()
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al buscar venta: {str(e)}")
    
    def load_venta_info(self, venta=None):
        """Cargar información de la venta"""
        if not venta and self.pago:
            venta = self.pago.venta
        
        if not venta:
            return
        
        # Información del cliente
        cliente_info = f"{venta.cliente.nombre_completo} - {venta.cliente.cedula}"
        self.cliente_info_var.set(cliente_info)
        
        # Información de la venta
        venta_info = f"Nicho {venta.nicho.numero} - ${venta.precio_total:,.2f} ({venta.tipo_pago})"
        self.venta_info_var.set(venta_info)
        
        # Información del saldo
        saldo_info = f"${venta.saldo_restante:,.2f}"
        if venta.pagado_completamente:
            saldo_info += " (PAGADO)"
        self.saldo_info_var.set(saldo_info)
        
        # Calcular nuevo saldo automáticamente
        self.calculate_new_saldo()
    
    def clear_venta_info(self):
        """Limpiar información de la venta"""
        self.cliente_info_var.set("")
        self.venta_info_var.set("")
        self.saldo_info_var.set("")
        self.nuevo_saldo_label.config(text="$0.00")
    
    def calculate_new_saldo(self, event=None):
        """Calcular nuevo saldo después del pago"""
        try:
            # Obtener saldo actual
            saldo_text = self.saldo_info_var.get()
            if not saldo_text or "(" in saldo_text:
                saldo_actual = 0
            else:
                saldo_actual = float(saldo_text.replace("$", "").replace(",", ""))
            
            # Obtener monto del pago
            monto_pago = float(self.monto_var.get() or 0)
            
            # Calcular nuevo saldo
            nuevo_saldo = max(0, saldo_actual - monto_pago)
            
            # Actualizar etiqueta
            self.nuevo_saldo_label.config(text=f"${nuevo_saldo:,.2f}")
            
            # Cambiar color según el resultado
            if nuevo_saldo == 0:
                self.nuevo_saldo_label.config(foreground="green")
            elif monto_pago > saldo_actual:
                self.nuevo_saldo_label.config(foreground="orange")
            else:
                self.nuevo_saldo_label.config(foreground="blue")
            
        except ValueError:
            self.nuevo_saldo_label.config(text="$0.00", foreground="gray")
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar pago"""
        # Validar campos obligatorios
        if not self.numero_contrato_var.get().strip():
            messagebox.showerror("Error", "El número de contrato es obligatorio")
            return
        
        if not self.metodo_pago_var.get().strip():
            messagebox.showerror("Error", "El método de pago es obligatorio")
            return
        
        if not self.concepto_var.get().strip():
            messagebox.showerror("Error", "El concepto es obligatorio")
            return
        
        try:
            monto = float(self.monto_var.get())
            if monto <= 0:
                raise ValueError("El monto debe ser mayor a 0")
        except ValueError:
            messagebox.showerror("Error", "El monto debe ser un número válido mayor a 0")
            return
        
        # Obtener observaciones del Text widget
        observaciones = self.observaciones_text.get("1.0", tk.END).strip()
        
        self.result = {
            'numero_contrato': self.numero_contrato_var.get().strip(),
            'monto': monto,
            'metodo_pago': self.metodo_pago_var.get().strip(),
            'concepto': self.concepto_var.get().strip(),
            'observaciones': observaciones if observaciones else None
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()


class PagoDetailsDialog:
    def __init__(self, parent, pago):
        self.pago = pago
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"Detalles del Pago - {pago.numero_recibo}")
        self.dialog.geometry("500x600")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Información del pago
        info_text = f"""
INFORMACIÓN DEL PAGO

Número de Recibo: {self.pago.numero_recibo}
Fecha del Pago: {self.pago.fecha_pago.strftime('%d/%m/%Y %H:%M')}
Monto: ${self.pago.monto:,.2f}
Método de Pago: {self.pago.metodo_pago.title()}
Concepto: {self.pago.concepto}

INFORMACIÓN DE LA VENTA

Número de Contrato: {self.pago.venta.numero_contrato}
Fecha de Venta: {self.pago.venta.fecha_venta.strftime('%d/%m/%Y')}
Precio Total: ${self.pago.venta.precio_total:,.2f}
Saldo Restante: ${self.pago.venta.saldo_restante:,.2f}
Estado: {'Pagado Completamente' if self.pago.venta.pagado_completamente else 'Pendiente'}

INFORMACIÓN DEL CLIENTE

Nombre: {self.pago.venta.cliente.nombre_completo}
Cédula: {self.pago.venta.cliente.cedula}
Teléfono: {self.pago.venta.cliente.telefono or 'No registrado'}
Email: {self.pago.venta.cliente.email or 'No registrado'}

INFORMACIÓN DEL NICHO

Número: {self.pago.venta.nicho.numero}
Sección: {self.pago.venta.nicho.seccion}
Ubicación: Fila {self.pago.venta.nicho.fila}, Columna {self.pago.venta.nicho.columna}

OBSERVACIONES

{self.pago.observaciones or 'Sin observaciones'}
"""
        
        text_widget = tk.Text(main_frame, wrap=tk.WORD, font=("Arial", 11))
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", info_text)
        text_widget.config(state="disabled")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Imprimir Recibo", 
                  command=self.print_receipt).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cerrar", 
                  command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def print_receipt(self):
        """Imprimir recibo del pago"""
        try:
            pdf_generator = PDFGenerator()
            
            # Preparar datos
            pago_data = {
                'numero_recibo': self.pago.numero_recibo,
                'fecha_pago': self.pago.fecha_pago,
                'monto': self.pago.monto,
                'metodo_pago': self.pago.metodo_pago,
                'concepto': self.pago.concepto,
                'observaciones': self.pago.observaciones
            }
            
            venta_data = {
                'numero_contrato': self.pago.venta.numero_contrato,
                'precio_total': self.pago.venta.precio_total,
                'saldo_anterior': self.pago.venta.saldo_restante + self.pago.monto,
                'saldo_restante': self.pago.venta.saldo_restante,
                'pagado_completamente': self.pago.venta.pagado_completamente
            }
            
            cliente_data = {
                'nombre': self.pago.venta.cliente.nombre,
                'apellido': self.pago.venta.cliente.apellido,
                'cedula': self.pago.venta.cliente.cedula,
                'telefono': self.pago.venta.cliente.telefono,
                'direccion': self.pago.venta.cliente.direccion
            }
            
            nicho_data = {
                'numero': self.pago.venta.nicho.numero,
                'seccion': self.pago.venta.nicho.seccion,
                'fila': self.pago.venta.nicho.fila,
                'columna': self.pago.venta.nicho.columna
            }
            
            # Generar PDF
            pdf_path = pdf_generator.generar_recibo_pago(
                pago_data, venta_data, cliente_data, nicho_data
            )
            
            # Preguntar si desea abrir el PDF
            response = messagebox.askyesno("PDF Generado", 
                f"Recibo generado exitosamente:\n{pdf_path}\n\n¿Desea abrirlo ahora?")
            
            if response:
                os.startfile(pdf_path)  # Windows
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar recibo: {str(e)}")
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")