# ui/urnas_manager.py
"""
Interfaz para la gestión de urnas depositadas en nichos
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from tkcalendar import DateEntry
from database.models import (
    get_db_session, Urna, Venta, Nicho,
    generar_numero_urna_para_nicho
)
from datetime import datetime, timedelta
from sqlalchemy import and_
from reports.pdf_generator import PDFGenerator

class UrnasManager:
    def __init__(self, parent, update_status_callback):
        self.parent = parent
        self.update_status = update_status_callback
        self.tree = None
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="Todos")
        self.pdf_generator = PDFGenerator()

    def show(self):
        """Mostrar interfaz de gestión de urnas"""
        main_frame = ttk.LabelFrame(self.parent, text="Gestión de Urnas", padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

        # Frame de controles superiores
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        controls_frame.columnconfigure(1, weight=1)

        # Botones de acción
        ttk.Button(controls_frame, text="Depositar Urna",
                  command=self.new_urna).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(controls_frame, text="Editar",
                  command=self.edit_urna).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(controls_frame, text="Imprimir Comprobante",
                  command=self.print_consent).grid(row=0, column=2, padx=(0, 10))

        ttk.Button(controls_frame, text="Eliminar",
                  command=self.delete_urna).grid(row=0, column=3, padx=(0, 10))

        ttk.Button(controls_frame, text="Actualizar",
                  command=self.load_urnas).grid(row=0, column=4, padx=(0, 10))

        # Frame de búsqueda
        search_frame = ttk.Frame(main_frame)
        search_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        search_frame.columnconfigure(1, weight=1)

        ttk.Label(search_frame, text="Buscar:").grid(row=0, column=0, padx=(0, 5))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        search_entry.bind('<KeyRelease>', self.on_search)

        ttk.Button(search_frame, text="Limpiar",
                  command=self.clear_search).grid(row=0, column=2, padx=(0, 10))

        # Crear TreeView
        self.create_urnas_tree(main_frame)

        # Cargar datos
        self.load_urnas()

        # Frame de información
        info_frame = ttk.LabelFrame(main_frame, text="Información", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        self.update_info_display(info_frame)

    def create_urnas_tree(self, parent):
        """Crear TreeView para mostrar urnas"""
        tree_frame = ttk.Frame(parent)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)

        # TreeView
        columns = ('nicho', 'urna_num', 'difunto', 'defuncion', 'deposito', 'depositante', 'crematorio')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)

        # Configurar columnas
        self.tree.heading('nicho', text='Nicho')
        self.tree.heading('urna_num', text='Urna #')
        self.tree.heading('difunto', text='Nombre del Difunto')
        self.tree.heading('defuncion', text='Fecha Defuncion')
        self.tree.heading('deposito', text='Fecha Deposito')
        self.tree.heading('depositante', text='Depositante')
        self.tree.heading('crematorio', text='Crematorio')

        self.tree.column('nicho', width=80)
        self.tree.column('urna_num', width=60)
        self.tree.column('difunto', width=150)
        self.tree.column('defuncion', width=100)
        self.tree.column('deposito', width=100)
        self.tree.column('depositante', width=150)
        self.tree.column('crematorio', width=150)

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

    def load_urnas(self):
        """Cargar urnas desde la base de datos"""
        try:
            db = get_db_session()
            urnas = db.query(Urna).join(Venta).join(Nicho).order_by(
                Nicho.numero, Urna.fecha_deposito_urna
            ).all()

            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Agregar urnas
            for urna in urnas:
                venta = urna.venta
                nicho = venta.nicho
                valores = (
                    nicho.numero,
                    urna.numero_urna,
                    urna.nombre_difunto,
                    urna.fecha_defuncion.strftime("%d/%m/%Y"),
                    urna.fecha_deposito_urna.strftime("%d/%m/%Y"),
                    urna.nombre_depositante,
                    urna.nombre_crematorio or "N/A"
                )

                self.tree.insert('', 'end', values=valores)

            self.update_status(f"Total urnas: {len(urnas)}")
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar urnas: {str(e)}")
            self.update_status("Error al cargar urnas")

    def on_search(self, event):
        """Buscar urnas mientras se escribe"""
        self.load_filtered_urnas()

    def clear_search(self):
        """Limpiar búsqueda"""
        self.search_var.set("")
        self.load_urnas()

    def load_filtered_urnas(self):
        """Cargar urnas filtradas por búsqueda"""
        search_text = self.search_var.get().lower()
        if not search_text:
            self.load_urnas()
            return

        try:
            db = get_db_session()
            urnas = db.query(Urna).join(Venta).join(Nicho).filter(
                (Urna.nombre_difunto.ilike(f"%{search_text}%")) |
                (Urna.nombre_depositante.ilike(f"%{search_text}%")) |
                (Nicho.numero.ilike(f"%{search_text}%")) |
                (Urna.nombre_crematorio.ilike(f"%{search_text}%"))
            ).order_by(Nicho.numero, Urna.fecha_deposito_urna).all()

            # Limpiar TreeView
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Agregar urnas filtradas
            for urna in urnas:
                venta = urna.venta
                nicho = venta.nicho
                valores = (
                    nicho.numero,
                    urna.numero_urna,
                    urna.nombre_difunto,
                    urna.fecha_defuncion.strftime("%d/%m/%Y"),
                    urna.fecha_deposito_urna.strftime("%d/%m/%Y"),
                    urna.nombre_depositante,
                    urna.nombre_crematorio or "N/A"
                )

                self.tree.insert('', 'end', values=valores)

            self.update_status(f"Resultados encontrados: {len(urnas)}")
            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")

    def on_double_click(self, event):
        """Editar urna con doble click"""
        self.edit_urna()

    def new_urna(self):
        """Crear nueva urna - abre diálogo de registro"""
        dialog = UrnasDialog(self.parent, "Depositar Nueva Urna", mode="new")
        self.parent.wait_window(dialog.window)

        if dialog.result:
            try:
                # Validar que la venta esté completamente pagada
                db = get_db_session()
                venta = db.query(Venta).filter(Venta.id == dialog.result['venta_id']).first()

                if not venta:
                    messagebox.showerror("Error", "Venta no encontrada")
                    db.close()
                    return

                if not venta.pagado_completamente:
                    messagebox.showerror("Error", "El nicho debe estar completamente pagado para depositar una urna")
                    db.close()
                    return

                # Generar número de urna automático
                numero_urna = generar_numero_urna_para_nicho(venta.nicho_id)

                urna = Urna(
                    venta_id=dialog.result['venta_id'],
                    numero_urna=numero_urna,
                    nombre_difunto=dialog.result['nombre_difunto'],
                    fecha_defuncion=dialog.result['fecha_defuncion'],
                    fecha_deposito_urna=dialog.result['fecha_deposito_urna'],
                    fecha_cremacion=dialog.result['fecha_cremacion'],
                    nombre_depositante=dialog.result['nombre_depositante'],
                    nombre_crematorio=dialog.result['nombre_crematorio'],
                    oficialia_registro_civil=dialog.result['oficialia_registro_civil'],
                    libro=dialog.result['libro'],
                    acta=dialog.result['acta'],
                    observaciones=dialog.result['observaciones']
                )

                db.add(urna)
                db.commit()

                # Preparar datos para generar consentimiento
                cliente = venta.cliente
                nicho = venta.nicho

                # Diccionarios con datos para el PDF
                urna_data = {
                    'numero_urna': numero_urna,
                    'nombre_difunto': urna.nombre_difunto,
                    'fecha_defuncion': urna.fecha_defuncion.strftime('%d/%m/%Y') if urna.fecha_defuncion else 'N/A',
                    'fecha_deposito_urna': urna.fecha_deposito_urna.strftime('%d/%m/%Y') if urna.fecha_deposito_urna else 'N/A',
                }

                venta_data = {
                    'numero_contrato': venta.numero_contrato,
                    'saldo_restante': venta.saldo_restante,
                }

                cliente_data = {
                    'nombre': cliente.nombre,
                    'apellido': cliente.apellido,
                    'cedula': cliente.cedula,
                }

                nicho_data = {
                    'numero': nicho.numero,
                    'seccion': nicho.seccion,
                    'fila': nicho.fila,
                    'columna': nicho.columna,
                }

                # Generar PDF de consentimiento
                consentimiento_path = None
                try:
                    consentimiento_path = self.pdf_generator.generar_consentimiento_urna(
                        urna_data, venta_data, cliente_data, nicho_data
                    )

                    # Preguntar si desea imprimir ahora
                    imprimir_ahora = messagebox.askyesno(
                        "Éxito",
                        f"Urna #{numero_urna} registrada correctamente\n\n"
                        f"¿Desea imprimir el documento de consentimiento ahora?"
                    )

                    if imprimir_ahora and consentimiento_path:
                        # Abrir el archivo PDF
                        import subprocess
                        import os
                        if os.name == 'nt':  # Windows
                            os.startfile(consentimiento_path)
                        else:  # Linux y macOS
                            subprocess.Popen(['xdg-open', consentimiento_path])

                except Exception as pdf_error:
                    # Si hay error en PDF, mostrar advertencia pero continuar
                    messagebox.showwarning(
                        "Advertencia",
                        f"Urna #{numero_urna} registrada correctamente\n\n"
                        f"Sin embargo, hubo un error al generar el PDF de consentimiento:\n{str(pdf_error)}"
                    )

                db.close()
                self.load_urnas()
                self.update_status(f"Urna #{numero_urna} registrada exitosamente")

            except Exception as e:
                messagebox.showerror("Error", f"Error al registrar urna: {str(e)}")

    def edit_urna(self):
        """Editar urna seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una urna para editar")
            return

        item = self.tree.item(selection[0])
        nicho_numero = item['values'][0]
        urna_numero = item['values'][1]

        try:
            db = get_db_session()
            urna = db.query(Urna).join(Venta).join(Nicho).filter(
                and_(Nicho.numero == nicho_numero, Urna.numero_urna == urna_numero)
            ).first()

            if not urna:
                messagebox.showerror("Error", "Urna no encontrada")
                db.close()
                return

            dialog = UrnasDialog(
                self.parent,
                "Editar Urna",
                mode="edit",
                urna=urna
            )
            self.parent.wait_window(dialog.window)

            if dialog.result:
                urna.nombre_difunto = dialog.result['nombre_difunto']
                urna.fecha_defuncion = dialog.result['fecha_defuncion']
                urna.fecha_deposito_urna = dialog.result['fecha_deposito_urna']
                urna.fecha_cremacion = dialog.result['fecha_cremacion']
                urna.nombre_depositante = dialog.result['nombre_depositante']
                urna.nombre_crematorio = dialog.result['nombre_crematorio']
                urna.oficialia_registro_civil = dialog.result['oficialia_registro_civil']
                urna.libro = dialog.result['libro']
                urna.acta = dialog.result['acta']
                urna.observaciones = dialog.result['observaciones']

                db.add(urna)
                db.commit()
                db.close()

                messagebox.showinfo("Éxito", "Urna actualizada correctamente")
                self.load_urnas()
        except Exception as e:
            messagebox.showerror("Error", f"Error al editar urna: {str(e)}")

    def delete_urna(self):
        """Eliminar urna seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una urna para eliminar")
            return

        if messagebox.askyesno("Confirmar", "¿Está seguro que desea eliminar esta urna?"):
            item = self.tree.item(selection[0])
            nicho_numero = item['values'][0]
            urna_numero = item['values'][1]

            try:
                db = get_db_session()
                urna = db.query(Urna).join(Venta).join(Nicho).filter(
                    and_(Nicho.numero == nicho_numero, Urna.numero_urna == urna_numero)
                ).first()

                if urna:
                    db.delete(urna)
                    db.commit()
                    db.close()
                    messagebox.showinfo("Éxito", "Urna eliminada correctamente")
                    self.load_urnas()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar urna: {str(e)}")

    def print_consent(self):
        """Imprimir consentimiento de urna seleccionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Advertencia", "Selecciona una urna para imprimir el consentimiento")
            return

        item = self.tree.item(selection[0])
        nicho_numero = item['values'][0]
        urna_numero = item['values'][1]

        try:
            db = get_db_session()
            urna = db.query(Urna).join(Venta).join(Nicho).filter(
                and_(Nicho.numero == nicho_numero, Urna.numero_urna == urna_numero)
            ).first()

            if not urna:
                messagebox.showerror("Error", "Urna no encontrada")
                db.close()
                return

            # Obtener datos relacionados
            venta = urna.venta
            cliente = venta.cliente
            nicho = venta.nicho

            # Preparar datos para PDF
            urna_data = {
                'numero_urna': urna.numero_urna,
                'nombre_difunto': urna.nombre_difunto,
                'fecha_defuncion': urna.fecha_defuncion.strftime('%d/%m/%Y') if urna.fecha_defuncion else 'N/A',
                'fecha_deposito_urna': urna.fecha_deposito_urna.strftime('%d/%m/%Y') if urna.fecha_deposito_urna else 'N/A',
            }

            venta_data = {
                'numero_contrato': venta.numero_contrato,
                'saldo_restante': venta.saldo_restante,
            }

            cliente_data = {
                'nombre': cliente.nombre,
                'apellido': cliente.apellido,
                'cedula': cliente.cedula,
            }

            nicho_data = {
                'numero': nicho.numero,
                'seccion': nicho.seccion,
                'fila': nicho.fila,
                'columna': nicho.columna,
            }

            # Generar PDF de consentimiento
            consentimiento_path = self.pdf_generator.generar_consentimiento_urna(
                urna_data, venta_data, cliente_data, nicho_data
            )

            # Abrir el archivo PDF generado
            import subprocess
            import os
            if os.name == 'nt':  # Windows
                os.startfile(consentimiento_path)
            else:  # Linux y macOS
                subprocess.Popen(['xdg-open', consentimiento_path])

            messagebox.showinfo("Éxito", f"Consentimiento generado e impreso:\n{consentimiento_path}")
            db.close()

        except Exception as e:
            messagebox.showerror("Error", f"Error al imprimir consentimiento: {str(e)}")

    def update_info_display(self, info_frame):
        """Actualizar información de resumen"""
        db = get_db_session()
        total_urnas = db.query(Urna).count()
        db.close()

        # Limpiar frame
        for widget in info_frame.winfo_children():
            widget.destroy()

        # Crear etiqueta de información
        info_text = f"Total de urnas registradas: {total_urnas}"
        ttk.Label(info_frame, text=info_text).pack(side=tk.LEFT, padx=10)


class UrnasDialog:
    """Diálogo para crear/editar urnas"""

    def __init__(self, parent, title, mode="new", urna=None):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("600x700")
        self.result = None
        self.urna = urna
        self.mode = mode

        # Frame principal
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Venta
        ttk.Label(main_frame, text="Venta (Contrato):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.venta_var = tk.StringVar()

        if mode == "edit" and urna:
            venta_text = f"{urna.venta.numero_contrato} - {urna.venta.nicho.numero}"
            self.venta_var.set(venta_text)
            venta_entry = ttk.Entry(main_frame, textvariable=self.venta_var, state="readonly")
        else:
            venta_entry = ttk.Combobox(main_frame, textvariable=self.venta_var)
            self.load_ventas_para_combobox(venta_entry)

        venta_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nombre del difunto
        ttk.Label(main_frame, text="Nombre del Difunto:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.nombre_difunto_var = tk.StringVar(value=urna.nombre_difunto if urna else "")
        ttk.Entry(main_frame, textvariable=self.nombre_difunto_var).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Fecha de defunción
        ttk.Label(main_frame, text="Fecha de Defuncion:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.fecha_defuncion_var = tk.StringVar(
            value=urna.fecha_defuncion.strftime("%d/%m/%Y") if urna else ""
        )
        fecha_defuncion_inicial = datetime.now()
        if urna and urna.fecha_defuncion:
            fecha_defuncion_inicial = urna.fecha_defuncion
        fecha_defuncion_entry = DateEntry(main_frame, textvariable=self.fecha_defuncion_var,
                                          year=fecha_defuncion_inicial.year, month=fecha_defuncion_inicial.month,
                                          day=fecha_defuncion_inicial.day, date_pattern='dd/MM/yyyy',
                                          width=25, background='darkblue', foreground='white',
                                          borderwidth=2, locale='es_ES')
        fecha_defuncion_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Fecha de deposito
        ttk.Label(main_frame, text="Fecha de Deposito de Urna:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.fecha_deposito_var = tk.StringVar(
            value=urna.fecha_deposito_urna.strftime("%d/%m/%Y") if urna else datetime.now().strftime("%d/%m/%Y")
        )
        fecha_deposito_inicial = urna.fecha_deposito_urna if urna else datetime.now()
        fecha_deposito_entry = DateEntry(main_frame, textvariable=self.fecha_deposito_var,
                                         year=fecha_deposito_inicial.year, month=fecha_deposito_inicial.month,
                                         day=fecha_deposito_inicial.day, date_pattern='dd/MM/yyyy',
                                         width=25, background='darkblue', foreground='white',
                                         borderwidth=2, locale='es_ES')
        fecha_deposito_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Fecha de cremación
        ttk.Label(main_frame, text="Fecha de Cremacion:").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.fecha_cremacion_var = tk.StringVar(
            value=urna.fecha_cremacion.strftime("%d/%m/%Y") if urna and urna.fecha_cremacion else ""
        )
        fecha_cremacion_inicial = urna.fecha_cremacion if urna and urna.fecha_cremacion else datetime.now()
        fecha_cremacion_entry = DateEntry(main_frame, textvariable=self.fecha_cremacion_var,
                                          year=fecha_cremacion_inicial.year, month=fecha_cremacion_inicial.month,
                                          day=fecha_cremacion_inicial.day, date_pattern='dd/MM/yyyy',
                                          width=25, background='darkblue', foreground='white',
                                          borderwidth=2, locale='es_ES')
        fecha_cremacion_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nombre del depositante
        ttk.Label(main_frame, text="Nombre del Depositante:").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.nombre_depositante_var = tk.StringVar(value=urna.nombre_depositante if urna else "")
        ttk.Entry(main_frame, textvariable=self.nombre_depositante_var).grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

        # Nombre del crematorio
        ttk.Label(main_frame, text="Nombre del Crematorio:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.nombre_crematorio_var = tk.StringVar(value=urna.nombre_crematorio if urna else "")
        ttk.Entry(main_frame, textvariable=self.nombre_crematorio_var).grid(row=6, column=1, sticky=(tk.W, tk.E), pady=5)

        # Oficialia del Registro Civil
        ttk.Label(main_frame, text="Oficialia del Registro Civil:").grid(row=7, column=0, sticky=tk.W, pady=5)
        self.oficialia_var = tk.StringVar(value=urna.oficialia_registro_civil if urna else "")
        ttk.Entry(main_frame, textvariable=self.oficialia_var).grid(row=7, column=1, sticky=(tk.W, tk.E), pady=5)

        # Libro
        ttk.Label(main_frame, text="Libro:").grid(row=8, column=0, sticky=tk.W, pady=5)
        self.libro_var = tk.StringVar(value=urna.libro if urna else "")
        ttk.Entry(main_frame, textvariable=self.libro_var).grid(row=8, column=1, sticky=(tk.W, tk.E), pady=5)

        # Acta
        ttk.Label(main_frame, text="Acta:").grid(row=9, column=0, sticky=tk.W, pady=5)
        self.acta_var = tk.StringVar(value=urna.acta if urna else "")
        ttk.Entry(main_frame, textvariable=self.acta_var).grid(row=9, column=1, sticky=(tk.W, tk.E), pady=5)

        # Observaciones
        ttk.Label(main_frame, text="Observaciones:").grid(row=10, column=0, sticky=tk.W, pady=5)
        self.observaciones_text = tk.Text(main_frame, height=4, width=40)
        self.observaciones_text.grid(row=10, column=1, sticky=(tk.W, tk.E), pady=5)
        if urna and urna.observaciones:
            self.observaciones_text.insert("1.0", urna.observaciones)

        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=11, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Guardar", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancelar", command=self.cancel).pack(side=tk.LEFT, padx=5)

        main_frame.columnconfigure(1, weight=1)

    def load_ventas_para_combobox(self, combobox):
        """Cargar ventas completamente pagadas en el combobox"""
        try:
            db = get_db_session()
            ventas = db.query(Venta).filter(Venta.pagado_completamente == True).all()

            ventas_list = [f"{v.numero_contrato} - {v.nicho.numero}" for v in ventas]
            combobox['values'] = ventas_list

            db.close()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar ventas: {str(e)}")

    def save(self):
        """Guardar urna"""
        try:
            # Validar campos requeridos
            if not self.nombre_difunto_var.get():
                messagebox.showwarning("Validacion", "El nombre del difunto es requerido")
                return

            if not self.nombre_depositante_var.get():
                messagebox.showwarning("Validacion", "El nombre del depositante es requerido")
                return

            if not self.fecha_defuncion_var.get():
                messagebox.showwarning("Validacion", "La fecha de defuncion es requerida")
                return

            if not self.fecha_deposito_var.get():
                messagebox.showwarning("Validacion", "La fecha de deposito es requerida")
                return

            # Obtener venta_id
            if self.mode == "new":
                venta_texto = self.venta_var.get()
                if not venta_texto:
                    messagebox.showwarning("Validacion", "Debes seleccionar una venta")
                    return

                db = get_db_session()
                numero_contrato = venta_texto.split(" - ")[0]
                venta = db.query(Venta).filter(Venta.numero_contrato == numero_contrato).first()
                if not venta:
                    messagebox.showerror("Error", "Venta no encontrada")
                    db.close()
                    return
                venta_id = venta.id
                db.close()
            else:
                venta_id = self.urna.venta_id

            # Procesar fechas (formato DD/MM/YYYY)
            try:
                fecha_defuncion = datetime.strptime(self.fecha_defuncion_var.get(), "%d/%m/%Y")
                fecha_deposito = datetime.strptime(self.fecha_deposito_var.get(), "%d/%m/%Y")
                fecha_cremacion = None
                if self.fecha_cremacion_var.get():
                    fecha_cremacion = datetime.strptime(self.fecha_cremacion_var.get(), "%d/%m/%Y")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use DD/MM/YYYY")
                return

            self.result = {
                'venta_id': venta_id,
                'nombre_difunto': self.nombre_difunto_var.get(),
                'fecha_defuncion': fecha_defuncion,
                'fecha_deposito_urna': fecha_deposito,
                'fecha_cremacion': fecha_cremacion,
                'nombre_depositante': self.nombre_depositante_var.get(),
                'nombre_crematorio': self.nombre_crematorio_var.get(),
                'oficialia_registro_civil': self.oficialia_var.get(),
                'libro': self.libro_var.get(),
                'acta': self.acta_var.get(),
                'observaciones': self.observaciones_text.get("1.0", "end-1c")
            }

            self.window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar los datos: {str(e)}")

    def cancel(self):
        """Cancelar diálogo"""
        self.window.destroy()
