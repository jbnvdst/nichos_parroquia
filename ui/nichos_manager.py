# ui/nichos_manager.py
"""
Interfaz para la gestión de nichos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database.models import get_db_session, Nicho
from sqlalchemy.exc import IntegrityError

class NichosManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.tree = None
        self.search_var = tk.StringVar()
        
    def show(self):
        """Mostrar interfaz de gestión de nichos"""
        main_frame = ttk.LabelFrame(self.parent, text="Gestión de Nichos", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Frame de controles superiores
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)
        
        # Botones de acción
        ttk.Button(controls_frame, text="Nuevo Nicho", 
                  command=self.new_nicho).grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Editar Nicho", 
                  command=self.edit_nicho).grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Eliminar Nicho", 
                  command=self.delete_nicho).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(controls_frame, text="Crear Lote", 
                  command=self.create_batch_nichos).grid(row=0, column=3, padx=(0, 10))
        
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
        filter_frame.grid(row=0, column=3, padx=(10, 0), sticky=(tk.W, tk.E))
        
        self.filter_disponible = tk.StringVar(value="Todos")
        ttk.Radiobutton(filter_frame, text="Todos", variable=self.filter_disponible, 
                       value="Todos", command=self.apply_filters).grid(row=0, column=0)
        ttk.Radiobutton(filter_frame, text="Disponibles", variable=self.filter_disponible, 
                       value="Disponibles", command=self.apply_filters).grid(row=0, column=1)
        ttk.Radiobutton(filter_frame, text="Vendidos", variable=self.filter_disponible, 
                       value="Vendidos", command=self.apply_filters).grid(row=0, column=2)
        
        # Lista de nichos
        self.create_nichos_tree(main_frame)
        
        # Cargar datos
        self.load_nichos()
        
        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.update_info_display(info_frame)
    
    def create_nichos_tree(self, parent):
        """Crear TreeView para mostrar nichos"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        # TreeView
        columns = ('numero', 'seccion', 'fila', 'columna', 'precio', 'disponible', 'descripcion')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        # Configurar columnas
        self.tree.heading('numero', text='Número')
        self.tree.heading('seccion', text='Sección')
        self.tree.heading('fila', text='Fila')
        self.tree.heading('columna', text='Columna')
        self.tree.heading('precio', text='Precio')
        self.tree.heading('disponible', text='Estado')
        self.tree.heading('descripcion', text='Descripción')
        
        self.tree.column('numero', width=100)
        self.tree.column('seccion', width=100)
        self.tree.column('fila', width=60)
        self.tree.column('columna', width=60)
        self.tree.column('precio', width=100)
        self.tree.column('disponible', width=100)
        self.tree.column('descripcion', width=200)
        
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
    
    def load_nichos(self):
        """Cargar nichos desde la base de datos"""
        try:
            db = get_db_session()
            nichos = db.query(Nicho).order_by(Nicho.seccion, Nicho.fila, Nicho.columna).all()
            
            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Agregar nichos
            for nicho in nichos:
                estado = "Disponible" if nicho.disponible else "Vendido"
                precio_formatted = f"${nicho.precio:,.2f}" if nicho.precio is not None else "Sin precio"

                values = (
                    nicho.numero,
                    nicho.seccion,
                    nicho.fila,
                    nicho.columna,
                    precio_formatted,
                    estado,
                    nicho.descripcion or ""
                )
                
                item = self.tree.insert('', 'end', values=values)
                
                # Colorear según disponibilidad
                if not nicho.disponible:
                    self.tree.set(item, 'disponible', 'Vendido')
                    # self.tree.item(item, tags=('vendido',))
            
            # Configurar tags para colores
            self.tree.tag_configure('vendido', background='#ffcccc')
            
            db.close()
            self.update_status(f"Nichos cargados: {len(nichos)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar nichos: {str(e)}")
    
    def new_nicho(self):
        """Crear nuevo nicho"""
        dialog = NichoDialog(self.parent, "Nuevo Nicho")
        if dialog.result:
            try:
                db = get_db_session()
                
                # Verificar que el número no existe
                existing = db.query(Nicho).filter(Nicho.numero == dialog.result['numero']).first()
                if existing:
                    messagebox.showerror("Error", "Ya existe un nicho con ese número")
                    db.close()
                    return
                
                nicho = Nicho(
                    numero=dialog.result['numero'],
                    seccion=dialog.result['seccion'],
                    fila=dialog.result['fila'],
                    columna=dialog.result['columna'],
                    precio=dialog.result['precio'],
                    descripcion=dialog.result['descripcion']
                )
                
                db.add(nicho)
                db.commit()
                db.close()
                
                self.load_nichos()
                self.update_status("Nicho creado exitosamente")
                messagebox.showinfo("Éxito", "Nicho creado exitosamente")
                
            except IntegrityError:
                messagebox.showerror("Error", "Ya existe un nicho con ese número")
            except Exception as e:
                messagebox.showerror("Error", f"Error al crear nicho: {str(e)}")
    
    def edit_nicho(self):
        """Editar nicho seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un nicho para editar")
            return
        
        # Obtener datos del nicho
        item = self.tree.item(selected[0])
        numero_nicho = item['values'][0]
        
        try:
            db = get_db_session()
            nicho = db.query(Nicho).filter(Nicho.numero == numero_nicho).first()
            
            if not nicho:
                messagebox.showerror("Error", "Nicho no encontrado")
                db.close()
                return
            
            # Verificar si el nicho está vendido
            if not nicho.disponible:
                response = messagebox.askyesno("Confirmación", 
                    "Este nicho está vendido. ¿Está seguro de que desea editarlo?")
                if not response:
                    db.close()
                    return
            
            # Abrir diálogo de edición
            dialog = NichoDialog(self.parent, "Editar Nicho", nicho)
            
            if dialog.result:
                nicho.numero = dialog.result['numero']
                nicho.seccion = dialog.result['seccion']
                nicho.fila = dialog.result['fila']
                nicho.columna = dialog.result['columna']
                nicho.precio = dialog.result['precio']
                nicho.descripcion = dialog.result['descripcion']
                
                db.commit()
                db.close()
                
                self.load_nichos()
                self.update_status("Nicho actualizado exitosamente")
                messagebox.showinfo("Éxito", "Nicho actualizado exitosamente")
            else:
                db.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar nicho: {str(e)}")
    
    def delete_nicho(self):
        """Eliminar nicho seleccionado"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Advertencia", "Seleccione un nicho para eliminar")
            return
        
        # Confirmar eliminación
        response = messagebox.askyesno("Confirmación", 
            "¿Está seguro de que desea eliminar este nicho?\n"
            "Esta acción no se puede deshacer.")
        
        if not response:
            return
        
        item = self.tree.item(selected[0])
        numero_nicho = item['values'][0]
        
        try:
            db = get_db_session()
            nicho = db.query(Nicho).filter(Nicho.numero == numero_nicho).first()
            
            if not nicho:
                messagebox.showerror("Error", "Nicho no encontrado")
                db.close()
                return
            
            # Verificar si el nicho tiene ventas asociadas
            if nicho.ventas:
                messagebox.showerror("Error", 
                    "No se puede eliminar este nicho porque tiene ventas asociadas")
                db.close()
                return
            
            db.delete(nicho)
            db.commit()
            db.close()
            
            self.load_nichos()
            self.update_status("Nicho eliminado exitosamente")
            messagebox.showinfo("Éxito", "Nicho eliminado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar nicho: {str(e)}")
    
    def create_batch_nichos(self):
        """Crear lote de nichos"""
        dialog = BatchNichosDialog(self.parent)
        if dialog.result:
            try:
                db = get_db_session()
                created_count = 0
                errors = []

                config = dialog.result

                # Convertir letras de fila a índices
                fila_inicio_letra = config['fila_inicio']
                fila_fin_letra = config['fila_fin']

                # Generar nichos según configuración
                for fila_letra in self._generar_letras(fila_inicio_letra, fila_fin_letra):
                    for columna in range(config['columna_inicio'], config['columna_fin'] + 1):

                        # Generar número de nicho con letra de fila
                        numero = f"{config['prefijo']}{fila_letra}{columna:02d}"

                        # Verificar si ya existe
                        existing = db.query(Nicho).filter(Nicho.numero == numero).first()
                        if existing:
                            errors.append(f"Nicho {numero} ya existe")
                            continue

                        nicho = Nicho(
                            numero=numero,
                            seccion=config['seccion'],
                            fila=fila_letra,
                            columna=str(columna),
                            precio=config['precio'],
                            descripcion=config['descripcion']
                        )

                        db.add(nicho)
                        created_count += 1
                
                db.commit()
                db.close()
                
                self.load_nichos()
                
                message = f"Se crearon {created_count} nichos exitosamente"
                if errors:
                    message += f"\n\nErrores ({len(errors)}):\n" + "\n".join(errors[:5])
                    if len(errors) > 5:
                        message += f"\n... y {len(errors) - 5} errores más"
                
                messagebox.showinfo("Resultado", message)
                self.update_status(f"Lote creado: {created_count} nichos")

            except Exception as e:
                messagebox.showerror("Error", f"Error al crear lote: {str(e)}")

    def _generar_letras(self, letra_inicio, letra_fin):
        """Generar secuencia de letras desde letra_inicio hasta letra_fin"""
        inicio = ord(letra_inicio.upper())
        fin = ord(letra_fin.upper())
        return [chr(i) for i in range(inicio, fin + 1)]

    def on_search(self, event=None):
        """Filtrar nichos según búsqueda"""
        search_term = self.search_var.get().lower()
        
        # Si no hay término de búsqueda, mostrar todos
        if not search_term:
            self.load_nichos()
            return
        
        try:
            db = get_db_session()
            query = db.query(Nicho)
            
            # Filtrar por término de búsqueda
            query = query.filter(
                Nicho.numero.contains(search_term) |
                Nicho.seccion.contains(search_term) |
                Nicho.fila.contains(search_term) |
                Nicho.columna.contains(search_term) |
                Nicho.descripcion.contains(search_term)
            )
            
            nichos = query.order_by(Nicho.seccion, Nicho.fila, Nicho.columna).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for nicho in nichos:
                estado = "Disponible" if nicho.disponible else "Vendido"
                precio_formatted = f"${nicho.precio:,.2f}" if nicho.precio is not None else "Sin precio"

                values = (
                    nicho.numero,
                    nicho.seccion,
                    nicho.fila,
                    nicho.columna,
                    precio_formatted,
                    estado,
                    nicho.descripcion or ""
                )

                self.tree.insert('', 'end', values=values)

            db.close()
            self.update_status(f"Búsqueda: {len(nichos)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error en búsqueda: {str(e)}")
    
    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.filter_disponible.set("Todos")
        self.load_nichos()
    
    def apply_filters(self):
        """Aplicar filtros de disponibilidad"""
        filter_value = self.filter_disponible.get()
        
        try:
            db = get_db_session()
            query = db.query(Nicho)
            
            # Aplicar filtro de búsqueda si existe
            search_term = self.search_var.get().lower()
            if search_term:
                query = query.filter(
                    Nicho.numero.contains(search_term) |
                    Nicho.seccion.contains(search_term) |
                    Nicho.fila.contains(search_term) |
                    Nicho.columna.contains(search_term) |
                    Nicho.descripcion.contains(search_term)
                )
            
            # Aplicar filtro de disponibilidad
            if filter_value == "Disponibles":
                query = query.filter(Nicho.disponible == True)
            elif filter_value == "Vendidos":
                query = query.filter(Nicho.disponible == False)
            
            nichos = query.order_by(Nicho.seccion, Nicho.fila, Nicho.columna).all()
            
            # Actualizar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            for nicho in nichos:
                estado = "Disponible" if nicho.disponible else "Vendido"
                precio_formatted = f"${nicho.precio:,.2f}" if nicho.precio is not None else "Sin precio"

                values = (
                    nicho.numero,
                    nicho.seccion,
                    nicho.fila,
                    nicho.columna,
                    precio_formatted,
                    estado,
                    nicho.descripcion or ""
                )

                self.tree.insert('', 'end', values=values)

            db.close()
            self.update_status(f"Filtro aplicado: {len(nichos)} resultados")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al aplicar filtros: {str(e)}")
    
    def update_info_display(self, parent):
        """Actualizar display de información"""
        try:
            db = get_db_session()
            
            total_nichos = db.query(Nicho).count()
            disponibles = db.query(Nicho).filter(Nicho.disponible == True).count()
            vendidos = total_nichos - disponibles
            
            db.close()
            
            info_text = f"Total: {total_nichos} nichos | Disponibles: {disponibles} | Vendidos: {vendidos}"
            ttk.Label(parent, text=info_text, font=("Arial", 11)).pack()
            
        except Exception as e:
            ttk.Label(parent, text="Error al cargar información").pack()
    
    def on_double_click(self, event):
        """Manejar doble clic en TreeView"""
        self.edit_nicho()
    
    def show_context_menu(self, event):
        """Mostrar menú contextual"""
        # Crear menú contextual
        context_menu = tk.Menu(self.parent, tearoff=0)
        context_menu.add_command(label="Editar", command=self.edit_nicho)
        context_menu.add_command(label="Eliminar", command=self.delete_nicho)
        context_menu.add_separator()
        context_menu.add_command(label="Ver Detalles", command=self.show_nicho_details)
        
        # Mostrar menú
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def show_nicho_details(self):
        """Mostrar detalles del nicho seleccionado"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = self.tree.item(selected[0])
        numero_nicho = item['values'][0]
        
        try:
            db = get_db_session()
            nicho = db.query(Nicho).filter(Nicho.numero == numero_nicho).first()
            
            if nicho:
                precio_text = f"${nicho.precio:,.2f}" if nicho.precio is not None else "Sin precio asignado"
                details = f"""
Número: {nicho.numero}
Sección: {nicho.seccion}
Ubicación: Fila {nicho.fila}, Columna {nicho.columna}
Precio: {precio_text}
Estado: {'Disponible' if nicho.disponible else 'Vendido'}
Descripción: {nicho.descripcion or 'Sin descripción'}
Fecha de creación: {nicho.fecha_creacion.strftime('%d/%m/%Y')}

Ventas asociadas: {len(nicho.ventas)}
"""
                messagebox.showinfo("Detalles del Nicho", details)
            
            db.close()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar detalles: {str(e)}")


class NichoDialog:
    def __init__(self, parent, title, nicho=None):
        self.result = None
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x500")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.numero_var = tk.StringVar()
        self.seccion_var = tk.StringVar()
        self.fila_var = tk.StringVar()
        self.columna_var = tk.StringVar()
        self.precio_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        
        # Si se está editando, cargar datos
        if nicho:
            self.numero_var.set(nicho.numero)
            self.seccion_var.set(nicho.seccion)
            self.fila_var.set(nicho.fila)
            self.columna_var.set(nicho.columna)
            self.precio_var.set(str(nicho.precio) if nicho.precio is not None else "")
            self.descripcion_var.set(nicho.descripcion or "")
        
        self.create_widgets()
        
        # Centrar ventana
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Número
        ttk.Label(main_frame, text="Número de Nicho:*").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.numero_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Sección
        ttk.Label(main_frame, text="Sección:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        seccion_combo = ttk.Combobox(main_frame, textvariable=self.seccion_var, width=27)
        seccion_combo['values'] = ('A', 'B', 'C', 'D', 'Central', 'Norte', 'Sur', 'Este', 'Oeste')
        seccion_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Fila
        ttk.Label(main_frame, text="Fila:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.fila_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Columna
        ttk.Label(main_frame, text="Columna:*").grid(row=3, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.columna_var, width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Precio
        ttk.Label(main_frame, text="Precio:").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.precio_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nota sobre precio
        ttk.Label(main_frame, text="(Opcional - puede definirse en la venta)",
                 font=("Arial", 8), foreground="gray").grid(row=4, column=1, sticky=tk.W, pady=(35, 0))
        
        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)
        desc_text = tk.Text(main_frame, height=5, width=30)
        desc_text.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        desc_text.insert("1.0", self.descripcion_var.get())
        self.desc_text = desc_text
        
        # Nota de campos obligatorios
        ttk.Label(main_frame, text="* Campos obligatorios", font=("Arial", 9), 
                 foreground="red").grid(row=6, column=0, columnspan=2, pady=10)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar datos"""
        # Validar campos obligatorios
        if not self.numero_var.get().strip():
            messagebox.showerror("Error", "El número de nicho es obligatorio")
            return
        
        if not self.seccion_var.get().strip():
            messagebox.showerror("Error", "La sección es obligatoria")
            return
        
        if not self.fila_var.get().strip():
            messagebox.showerror("Error", "La fila es obligatoria")
            return
        
        if not self.columna_var.get().strip():
            messagebox.showerror("Error", "La columna es obligatoria")
            return

        # Validar precio (opcional)
        precio = None
        if self.precio_var.get().strip():
            try:
                precio = float(self.precio_var.get().strip())
                if precio <= 0:
                    raise ValueError("El precio debe ser mayor a 0")
            except ValueError:
                messagebox.showerror("Error", "El precio debe ser un número válido mayor a 0")
                return
        
        # Obtener descripción del Text widget
        descripcion = self.desc_text.get("1.0", tk.END).strip()
        
        self.result = {
            'numero': self.numero_var.get().strip(),
            'seccion': self.seccion_var.get().strip(),
            'fila': self.fila_var.get().strip(),
            'columna': self.columna_var.get().strip(),
            'precio': precio,
            'descripcion': descripcion if descripcion else None
        }
        
        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()


class BatchNichosDialog:
    def __init__(self, parent):
        self.result = None
        
        # Crear ventana modal
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Crear Lote de Nichos")
        self.dialog.geometry("500x550")  # Aumenté la altura para que se vean todos los elementos
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Variables
        self.prefijo_var = tk.StringVar(value="N")
        self.seccion_var = tk.StringVar()
        self.fila_inicio_var = tk.StringVar(value="A")
        self.fila_fin_var = tk.StringVar(value="J")
        self.columna_inicio_var = tk.StringVar(value="1")
        self.columna_fin_var = tk.StringVar(value="10")
        self.precio_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        
        self.create_widgets()
        self.center_window()
        
        # Esperar a que se cierre la ventana
        self.dialog.wait_window()
    
    def create_widgets(self):
        """Crear widgets del diálogo"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        ttk.Label(main_frame, text="Crear Lote de Nichos", 
                 font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Prefijo
        ttk.Label(main_frame, text="Prefijo:*").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.prefijo_var, width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Sección
        ttk.Label(main_frame, text="Sección:*").grid(row=2, column=0, sticky=tk.W, pady=5)
        seccion_combo = ttk.Combobox(main_frame, textvariable=self.seccion_var, width=27)
        seccion_combo['values'] = ('A', 'B', 'C', 'D', 'Central', 'Norte', 'Sur', 'Este', 'Oeste')
        seccion_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Rango de filas
        ttk.Label(main_frame, text="Filas (desde - hasta):*").grid(row=3, column=0, sticky=tk.W, pady=5)
        fila_frame = ttk.Frame(main_frame)
        fila_frame.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(fila_frame, textvariable=self.fila_inicio_var, width=10).pack(side=tk.LEFT)
        ttk.Label(fila_frame, text=" - ").pack(side=tk.LEFT)
        ttk.Entry(fila_frame, textvariable=self.fila_fin_var, width=10).pack(side=tk.LEFT)
        
        # Rango de columnas
        ttk.Label(main_frame, text="Columnas (desde - hasta):*").grid(row=4, column=0, sticky=tk.W, pady=5)
        columna_frame = ttk.Frame(main_frame)
        columna_frame.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(columna_frame, textvariable=self.columna_inicio_var, width=10).pack(side=tk.LEFT)
        ttk.Label(columna_frame, text=" - ").pack(side=tk.LEFT)
        ttk.Entry(columna_frame, textvariable=self.columna_fin_var, width=10).pack(side=tk.LEFT)
        
        # Precio
        ttk.Label(main_frame, text="Precio por nicho:").grid(row=5, column=0, sticky=tk.W, pady=5)
        precio_entry = ttk.Entry(main_frame, textvariable=self.precio_var, width=30)
        precio_entry.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nota sobre precio
        ttk.Label(main_frame, text="(Dejar vacío si el precio se definirá en cada venta)",
                 font=("Arial", 8), foreground="gray").grid(row=5, column=1, sticky=tk.W, pady=(35, 0))
        
        # Descripción
        ttk.Label(main_frame, text="Descripción:").grid(row=6, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.descripcion_var, width=30).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)
        
        # Vista previa
        preview_frame = ttk.LabelFrame(main_frame, text="Vista Previa", padding="10")
        preview_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        self.preview_label = ttk.Label(preview_frame, text="")
        self.preview_label.pack()
        
        # Actualizar vista previa cuando cambien los valores
        for var in [self.prefijo_var, self.fila_inicio_var, self.fila_fin_var, 
                   self.columna_inicio_var, self.columna_fin_var]:
            var.trace('w', self.update_preview)
        
        # Nota de campos obligatorios
        ttk.Label(main_frame, text="* Campos obligatorios", font=("Arial", 9), 
                 foreground="red").grid(row=8, column=0, columnspan=2, pady=10)
        
        # Separador
        ttk.Separator(main_frame, orient='horizontal').grid(row=9, column=0, columnspan=2, 
                                                           sticky=(tk.W, tk.E), pady=10)
        
        # Botones (hacer más visibles)
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=20)
        
        # Botón principal más grande y visible
        crear_btn = ttk.Button(button_frame, text="✅ CREAR LOTE DE NICHOS", 
                              command=self.save, width=25)
        crear_btn.pack(side=tk.LEFT, padx=10)
        
        cancelar_btn = ttk.Button(button_frame, text="❌ Cancelar", 
                                 command=self.cancel, width=15)
        cancelar_btn.pack(side=tk.LEFT, padx=10)
        
        # Configurar grid
        main_frame.columnconfigure(1, weight=1)
        
        # Actualizar vista previa inicial
        self.update_preview()
    
    def update_preview(self, *args):
        """Actualizar vista previa"""
        try:
            prefijo = self.prefijo_var.get()
            fila_inicio = self.fila_inicio_var.get().strip().upper() or "A"
            fila_fin = self.fila_fin_var.get().strip().upper() or "A"
            columna_inicio = int(self.columna_inicio_var.get() or 1)
            columna_fin = int(self.columna_fin_var.get() or 1)

            # Validar que sean letras únicas
            if len(fila_inicio) != 1 or len(fila_fin) != 1:
                raise ValueError("Las filas deben ser letras únicas")

            if not fila_inicio.isalpha() or not fila_fin.isalpha():
                raise ValueError("Las filas deben ser letras")

            # Calcular total de nichos
            num_filas = ord(fila_fin) - ord(fila_inicio) + 1
            num_columnas = columna_fin - columna_inicio + 1
            total_nichos = num_filas * num_columnas

            ejemplo1 = f"{prefijo}{fila_inicio}{columna_inicio:02d}"
            ejemplo2 = f"{prefijo}{fila_fin}{columna_fin:02d}"

            preview_text = f"Se crearán {total_nichos} nichos\n"
            preview_text += f"Ejemplos: {ejemplo1}, {ejemplo2}"

        except ValueError:
            preview_text = "Ingrese valores válidos para ver la vista previa"

        self.preview_label.config(text=preview_text)
    
    def center_window(self):
        """Centrar ventana en la pantalla"""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (self.dialog.winfo_width() // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
    
    def save(self):
        """Guardar configuración del lote"""
        # Validar campos obligatorios
        if not self.prefijo_var.get().strip():
            messagebox.showerror("Error", "El prefijo es obligatorio")
            return
        
        if not self.seccion_var.get().strip():
            messagebox.showerror("Error", "La sección es obligatoria")
            return
        
        # Validar que los campos de fila no estén vacíos
        if not self.fila_inicio_var.get().strip():
            messagebox.showerror("Error", "La fila de inicio es obligatoria")
            return

        if not self.fila_fin_var.get().strip():
            messagebox.showerror("Error", "La fila final es obligatoria")
            return

        if not self.columna_inicio_var.get().strip():
            messagebox.showerror("Error", "La columna de inicio es obligatoria")
            return

        if not self.columna_fin_var.get().strip():
            messagebox.showerror("Error", "La columna final es obligatoria")
            return

        try:
            # Validar y procesar letras de fila
            fila_inicio = self.fila_inicio_var.get().strip().upper()
            fila_fin = self.fila_fin_var.get().strip().upper()

            # Validar que sean letras únicas
            if len(fila_inicio) != 1 or not fila_inicio.isalpha():
                raise ValueError("La fila de inicio debe ser una letra única (A-Z)")

            if len(fila_fin) != 1 or not fila_fin.isalpha():
                raise ValueError("La fila final debe ser una letra única (A-Z)")

            # Convertir y validar números enteros para columnas
            columna_inicio = int(self.columna_inicio_var.get().strip())
            columna_fin = int(self.columna_fin_var.get().strip())

            # Convertir y validar precio (opcional)
            precio = None
            precio_str = self.precio_var.get().strip()
            if precio_str:
                precio_str = precio_str.replace(',', '')
                precio = float(precio_str)
                if precio <= 0:
                    raise ValueError("El precio debe ser mayor a 0")

            # Validaciones lógicas
            if columna_inicio <= 0:
                raise ValueError("La columna de inicio debe ser mayor a 0")

            if ord(fila_inicio) > ord(fila_fin):
                raise ValueError("La fila de inicio debe ser menor o igual a la fila final")

            if columna_inicio > columna_fin:
                raise ValueError("La columna de inicio debe ser menor o igual a la columna final")
                
        except ValueError as e:
            # Manejar errores específicos de conversión
            error_msg = str(e)
            if "could not convert string to float" in error_msg:
                messagebox.showerror("Error", "El precio debe ser un número válido (ejemplo: 1500 o 1500.50)")
            elif "invalid literal for int()" in error_msg:
                messagebox.showerror("Error", "Las columnas deben ser números enteros válidos")
            else:
                messagebox.showerror("Error", f"Error en los datos: {error_msg}")
            return

        # Calcular total de nichos usando letras
        num_filas = ord(fila_fin) - ord(fila_inicio) + 1
        num_columnas = columna_fin - columna_inicio + 1
        total_nichos = num_filas * num_columnas

        # Validar que el total no sea excesivo
        if total_nichos > 1000:
            response = messagebox.askyesno("Advertencia",
                f"Está a punto de crear {total_nichos} nichos. "
                f"Esto podría tomar mucho tiempo. ¿Desea continuar?")
            if not response:
                return

        # Confirmar creación
        precio_text = f"${precio:,.2f} cada uno" if precio else "Sin precio (se definirá en cada venta)"
        response = messagebox.askyesno("Confirmación",
            f"¿Está seguro de crear {total_nichos} nichos?\n"
            f"Sección: {self.seccion_var.get()}\n"
            f"Filas: {fila_inicio} a {fila_fin}\n"
            f"Columnas: {columna_inicio} a {columna_fin}\n"
            f"Precio: {precio_text}")
        
        if not response:
            return

        self.result = {
            'prefijo': self.prefijo_var.get().strip(),
            'seccion': self.seccion_var.get().strip(),
            'fila_inicio': fila_inicio,  # Ahora es una letra
            'fila_fin': fila_fin,  # Ahora es una letra
            'columna_inicio': columna_inicio,
            'columna_fin': columna_fin,
            'precio': precio,
            'descripcion': self.descripcion_var.get().strip() or None
        }

        self.dialog.destroy()
    
    def cancel(self):
        """Cancelar operación"""
        self.dialog.destroy()