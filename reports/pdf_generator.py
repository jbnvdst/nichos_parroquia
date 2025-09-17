# reports/pdf_generator.py
"""
Generador de PDFs para recibos de pago y títulos de propiedad
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
        # Configuración de la parroquia (esto podría venir de la base de datos)
        self.parish_config = {
            "nombre": "Parroquia San José",
            "direccion": "Calle Principal #123, Ciudad",
            "telefono": "+1 (555) 123-4567",
            "email": "info@parroquiasanjose.org",
            "logo_path": "assets/logo_parroquia.png"  # Si existe
        }
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        ))
        
        # Estilo para texto de información
        self.styles.add(ParagraphStyle(
            name='InfoText',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_LEFT
        ))
        
        # Estilo para texto centrado
        self.styles.add(ParagraphStyle(
            name='CenteredText',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER
        ))
    
    def generar_recibo_pago(self, pago_data, venta_data, cliente_data, nicho_data, output_path=None):
        """
        Generar recibo de pago en PDF
        
        Args:
            pago_data: Diccionario con datos del pago
            venta_data: Diccionario con datos de la venta
            cliente_data: Diccionario con datos del cliente
            nicho_data: Diccionario con datos del nicho
            output_path: Ruta del archivo de salida
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"recibos/recibo_{pago_data['numero_recibo']}_{timestamp}.pdf"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=18)
        
        # Contenido del documento
        story = []
        
        # Encabezado con información de la parroquia
        story.extend(self._crear_encabezado_parroquia())
        
        # Título del documento
        story.append(Paragraph("RECIBO DE PAGO", self.styles['CustomTitle']))
        story.append(Spacer(1, 20))
        
        # Información del recibo
        info_recibo = [
            ["Número de Recibo:", pago_data['numero_recibo']],
            ["Fecha de Pago:", pago_data['fecha_pago'].strftime("%d/%m/%Y")],
            ["Número de Contrato:", venta_data['numero_contrato']],
        ]
        
        tabla_info = Table(info_recibo, colWidths=[2*inch, 3*inch])
        tabla_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        story.append(tabla_info)
        story.append(Spacer(1, 20))
        
        # Información del cliente
        story.append(Paragraph("DATOS DEL CLIENTE", self.styles['CustomSubtitle']))
        
        cliente_info = [
            ["Nombre:", f"{cliente_data['nombre']} {cliente_data['apellido']}"],
            ["Cédula:", cliente_data['cedula']],
            ["Teléfono:", cliente_data.get('telefono', 'No registrado')],
            ["Dirección:", cliente_data.get('direccion', 'No registrada')],
        ]
        
        tabla_cliente = Table(cliente_info, colWidths=[1.5*inch, 4*inch])
        tabla_cliente.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        story.append(tabla_cliente)
        story.append(Spacer(1, 20))
        
        # Información del nicho
        story.append(Paragraph("INFORMACIÓN DEL NICHO", self.styles['CustomSubtitle']))
        
        nicho_info = [
            ["Número de Nicho:", nicho_data['numero']],
            ["Sección:", nicho_data['seccion']],
            ["Ubicación:", f"Fila {nicho_data['fila']}, Columna {nicho_data['columna']}"],
            ["Precio Total:", f"${venta_data['precio_total']:,.2f}"],
        ]
        
        tabla_nicho = Table(nicho_info, colWidths=[1.5*inch, 4*inch])
        tabla_nicho.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
        ]))
        story.append(tabla_nicho)
        story.append(Spacer(1, 20))
        
        # Detalles del pago
        story.append(Paragraph("DETALLE DEL PAGO", self.styles['CustomSubtitle']))
        
        pago_info = [
            ["Concepto:", pago_data['concepto']],
            ["Método de Pago:", pago_data['metodo_pago']],
            ["Monto Pagado:", f"${pago_data['monto']:,.2f}"],
            ["Saldo Anterior:", f"${venta_data['saldo_anterior']:,.2f}"],
            ["Saldo Restante:", f"${venta_data['saldo_restante']:,.2f}"],
        ]
        
        tabla_pago = Table(pago_info, colWidths=[1.5*inch, 4*inch])
        tabla_pago.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            # Resaltar el monto pagado
            ('BACKGROUND', (0, 2), (-1, 2), colors.lightblue),
            ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
        ]))
        story.append(tabla_pago)
        story.append(Spacer(1, 30))
        
        # Observaciones si existen
        if pago_data.get('observaciones'):
            story.append(Paragraph("OBSERVACIONES", self.styles['CustomSubtitle']))
            story.append(Paragraph(pago_data['observaciones'], self.styles['InfoText']))
            story.append(Spacer(1, 20))
        
        # Pie de página con firmas
        story.extend(self._crear_pie_firmas())
        
        # Generar PDF
        doc.build(story)
        return output_path
    
    def generar_titulo_propiedad(self, venta_data, cliente_data, nicho_data, beneficiarios_data=None, output_path=None):
        """
        Generar título de propiedad en PDF
        
        Args:
            venta_data: Diccionario con datos de la venta
            cliente_data: Diccionario con datos del cliente
            nicho_data: Diccionario con datos del nicho
            beneficiarios_data: Lista de beneficiarios
            output_path: Ruta del archivo de salida
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"titulos/titulo_{venta_data['numero_contrato']}_{timestamp}.pdf"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=72, leftMargin=72,
                              topMargin=72, bottomMargin=72)
        
        # Contenido del documento
        story = []
        
        # Encabezado con información de la parroquia
        story.extend(self._crear_encabezado_parroquia())
        
        # Título del documento
        story.append(Paragraph("TÍTULO DE PROPIEDAD", self.styles['CustomTitle']))
        story.append(Paragraph("CRIPTA FAMILIAR", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 30))
        
        # Texto legal del título
        texto_legal = f"""
        Por medio del presente documento, {self.parish_config['nombre']} certifica que 
        <b>{cliente_data['nombre']} {cliente_data['apellido']}</b>, identificado(a) con cédula de 
        ciudadanía número <b>{cliente_data['cedula']}</b>, ha adquirido en plena propiedad 
        el derecho de uso y goce del nicho número <b>{nicho_data['numero']}</b>, ubicado en 
        la sección <b>{nicho_data['seccion']}</b>, fila <b>{nicho_data['fila']}</b>, 
        columna <b>{nicho_data['columna']}</b> del cementerio de esta parroquia.
        """
        
        story.append(Paragraph(texto_legal, self.styles['InfoText']))
        story.append(Spacer(1, 20))
        
        # Información del contrato
        contrato_info = [
            ["Número de Contrato:", venta_data['numero_contrato']],
            ["Fecha de Venta:", venta_data['fecha_venta'].strftime("%d de %B de %Y")],
            ["Precio Total:", f"${venta_data['precio_total']:,.2f}"],
            ["Estado:", "PAGADO COMPLETAMENTE" if venta_data['pagado_completamente'] else "PENDIENTE"],
        ]
        
        tabla_contrato = Table(contrato_info, colWidths=[2*inch, 3.5*inch])
        tabla_contrato.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(tabla_contrato)
        story.append(Spacer(1, 30))
        
        # Beneficiarios si existen
        if beneficiarios_data:
            story.append(Paragraph("BENEFICIARIOS DESIGNADOS", self.styles['CustomSubtitle']))
            
            beneficiarios_texto = "En caso de fallecimiento del titular, los derechos sobre este nicho serán transferidos a los siguientes beneficiarios en el orden establecido:"
            story.append(Paragraph(beneficiarios_texto, self.styles['InfoText']))
            story.append(Spacer(1, 10))
            
            for i, beneficiario in enumerate(beneficiarios_data, 1):
                beneficiario_texto = f"<b>{i}. {beneficiario['nombre']} {beneficiario['apellido']}</b> - Cédula: {beneficiario['cedula']}"
                story.append(Paragraph(beneficiario_texto, self.styles['InfoText']))
            
            story.append(Spacer(1, 20))
        
        # Condiciones y términos
        condiciones_texto = """
        <b>CONDICIONES Y TÉRMINOS:</b><br/>
        1. Este título otorga el derecho de uso y goce del nicho mencionado a perpetuidad.<br/>
        2. El titular se compromete a respetar las normas del cementerio y la parroquia.<br/>
        3. Cualquier modificación o transferencia debe ser autorizada por la administración.<br/>
        4. El nicho debe ser utilizado únicamente para los fines establecidos.<br/>
        5. La parroquia se reserva el derecho de supervisar el mantenimiento del nicho.
        """
        
        story.append(Paragraph(condiciones_texto, self.styles['InfoText']))
        story.append(Spacer(1, 40))
        
        # Firmas
        story.extend(self._crear_pie_firmas_titulo())
        
        # Generar PDF
        doc.build(story)
        return output_path
    
    def _crear_encabezado_parroquia(self):
        """Crear encabezado con información de la parroquia"""
        elementos = []
        
        # Logo si existe
        if os.path.exists(self.parish_config.get('logo_path', '')):
            logo = Image(self.parish_config['logo_path'], width=1*inch, height=1*inch)
            elementos.append(logo)
        
        # Información de la parroquia
        info_parroquia = f"""
        <b>{self.parish_config['nombre']}</b><br/>
        {self.parish_config['direccion']}<br/>
        Tel: {self.parish_config['telefono']} | Email: {self.parish_config['email']}
        """
        
        elementos.append(Paragraph(info_parroquia, self.styles['CenteredText']))
        elementos.append(Spacer(1, 20))
        
        # Línea separadora
        line_data = [['_' * 80]]
        line_table = Table(line_data)
        line_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        elementos.append(line_table)
        elementos.append(Spacer(1, 20))
        
        return elementos
    
    def _crear_pie_firmas(self):
        """Crear pie de página con firmas para recibos"""
        elementos = []
        
        elementos.append(Spacer(1, 40))
        
        # Fecha y hora de emisión
        fecha_emision = datetime.now().strftime("Emitido el %d de %B de %Y a las %H:%M")
        elementos.append(Paragraph(fecha_emision, self.styles['CenteredText']))
        elementos.append(Spacer(1, 30))
        
        # Líneas de firma
        firmas_data = [
            ['_' * 25, '_' * 25],
            ['Administrador', 'Cliente'],
            ['Firma y Sello', 'Firma']
        ]
        
        tabla_firmas = Table(firmas_data, colWidths=[2.5*inch, 2.5*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
        ]))
        elementos.append(tabla_firmas)
        
        return elementos
    
    def _crear_pie_firmas_titulo(self):
        """Crear pie de página con firmas para títulos"""
        elementos = []
        
        elementos.append(Spacer(1, 40))
        
        # Fecha de expedición
        fecha_expedicion = datetime.now().strftime("Expedido en la ciudad el %d de %B de %Y")
        elementos.append(Paragraph(fecha_expedicion, self.styles['CenteredText']))
        elementos.append(Spacer(1, 50))
        
        # Líneas de firma
        firmas_data = [
            ['_' * 30, '_' * 30],
            ['Párroco', 'Administrador'],
            ['Firma y Sello', 'Firma y Sello']
        ]
        
        tabla_firmas = Table(firmas_data, colWidths=[3*inch, 3*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 20),
        ]))
        elementos.append(tabla_firmas)
        
        return elementos
    
    def generar_reporte_movimientos(self, movimientos_data, fecha_inicio, fecha_fin, output_path=None):
        """Generar reporte de movimientos en PDF"""
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"reportes/reporte_movimientos_{timestamp}.pdf"
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Crear documento
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                              rightMargin=50, leftMargin=50,
                              topMargin=50, bottomMargin=50)
        
        story = []
        
        # Encabezado
        story.extend(self._crear_encabezado_parroquia())
        
        # Título
        story.append(Paragraph("REPORTE DE MOVIMIENTOS", self.styles['CustomTitle']))
        periodo = f"Período: {fecha_inicio.strftime('%d/%m/%Y')} - {fecha_fin.strftime('%d/%m/%Y')}"
        story.append(Paragraph(periodo, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 30))
        
        # Tabla de movimientos
        if movimientos_data:
            # Encabezados de la tabla
            headers = ['Fecha', 'Tipo', 'Contrato', 'Cliente', 'Monto', 'Estado']
            data = [headers]
            
            # Agregar datos
            for mov in movimientos_data:
                data.append([
                    mov['fecha'].strftime('%d/%m/%Y'),
                    mov['tipo'],
                    mov['contrato'],
                    mov['cliente'],
                    f"${mov['monto']:,.2f}",
                    mov['estado']
                ])
            
            # Crear tabla
            tabla = Table(data, colWidths=[1*inch, 1*inch, 1.2*inch, 2*inch, 1*inch, 1*inch])
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
            ]))
            story.append(tabla)
        else:
            story.append(Paragraph("No se encontraron movimientos en el período seleccionado.", 
                                 self.styles['InfoText']))
        
        # Generar PDF
        doc.build(story)
        return output_path