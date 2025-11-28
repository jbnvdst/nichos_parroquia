# reports/pdf_generator.py
"""
Generador de PDFs para recibos de pago y títulos de propiedad
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, Frame, PageTemplate, BaseDocTemplate, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os
from config.paths import AppPaths

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        
        # Configuración de la parroquia (esto podría venir de la base de datos)
        self.parish_config = {
            "nombre": "Parroquia Nuestra Señora del Consuelo de los Afligidos",
            "direccion": "Calle Girasoles #960, Zapopan, Jalisco",
            "telefono": "3347345288",
            "email": "parroquiaconsuelozap@hotmail.com",
            "logo_path": "assets/logo_parroquia.webp"  # Si existe
        }
    
    def setup_custom_styles(self):
        """Configurar estilos personalizados"""
        # Estilo para títulos principales
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=16,
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

        # Estilo para etiqueta de copia
        self.styles.add(ParagraphStyle(
            name='CopyLabel',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=10
        ))

    def _crear_contenido_recibo(self, pago_data, venta_data, cliente_data, nicho_data, etiqueta_copia):
        """
        Crear contenido de un recibo individual

        Args:
            pago_data: Diccionario con datos del pago
            venta_data: Diccionario con datos de la venta
            cliente_data: Diccionario con datos del cliente
            nicho_data: Diccionario con datos del nicho
            etiqueta_copia: Texto para identificar la copia (ej: "COPIA PARROQUIA")

        Returns:
            Lista de elementos Platypus para el recibo
        """
        elementos = []

        # Etiqueta de la copia
        copy_style = ParagraphStyle(
            name='CompactCopyLabel',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=5
        )
        elementos.append(Paragraph(f"<b>{etiqueta_copia}</b>", copy_style))

        # Encabezado con información de la parroquia (versión compacta)
        header_style = ParagraphStyle(
            name='CompactHeader',
            parent=self.styles['Normal'],
            fontSize=8,
            alignment=TA_CENTER
        )
        info_parroquia = f"""
        <b>{self.parish_config['nombre']}</b><br/>
        {self.parish_config['direccion']}<br/>
        Tel: {self.parish_config['telefono']}
        """
        elementos.append(Paragraph(info_parroquia, header_style))

        # Línea separadora
        line_data = [['_' * 60]]
        line_table = Table(line_data)
        line_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
        ]))
        elementos.append(line_table)
        elementos.append(Spacer(1, 3))

        # Título del documento
        title_style = ParagraphStyle(
            name='CompactTitle',
            parent=self.styles['Title'],
            fontSize=12,
            spaceAfter=5,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        elementos.append(Paragraph("RECIBO DE PAGO", title_style))
        elementos.append(Spacer(1, 5))

        # Información del recibo (compacta)
        info_recibo = [
            ["N° Recibo:", pago_data['numero_recibo'], "Fecha:", pago_data['fecha_pago'].strftime("%d/%m/%Y")],
            ["Contrato:", venta_data['numero_contrato'], "", ""],
        ]

        tabla_info = Table(info_recibo, colWidths=[0.9*inch, 1.4*inch, 0.6*inch, 1*inch])
        tabla_info.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]))
        elementos.append(tabla_info)
        elementos.append(Spacer(1, 5))

        # TABLA ÚNICA CON TODA LA INFORMACIÓN
        datos_completos = [
            # Datos del titular
            ["Titular:", f"{cliente_data['nombre']} {cliente_data['apellido']}"],
            # Información del nicho
            ["Nicho:", nicho_data['numero']],
            ["Sección:", nicho_data['seccion']],
            ["Ubicación:", f"F{nicho_data['fila']}, C{nicho_data['columna']}"],
            # Detalles del pago
            ["Concepto:", pago_data['concepto']],
            ["Método:", pago_data['metodo_pago']],
            ["Monto Pagado:", f"${pago_data['monto']:,.2f}"],
            ["Saldo Restante:", f"${venta_data['saldo_restante']:,.2f}"],
        ]

        tabla_completa = Table(datos_completos, colWidths=[1.1*inch, 3*inch])
        tabla_completa.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
            # Resaltar el monto pagado
            ('BACKGROUND', (0, 6), (-1, 6), colors.lightblue),
            ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
        ]))
        elementos.append(tabla_completa)
        elementos.append(Spacer(1, 8))

        # Fecha de emisión
        fecha_style = ParagraphStyle(
            name='CompactDate',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER
        )
        fecha_emision = datetime.now().strftime("Emitido el %d/%m/%Y a las %H:%M")
        elementos.append(Paragraph(f"<i>{fecha_emision}</i>", fecha_style))
        elementos.append(Spacer(1, 6))

        # Línea de firma solo del administrador
        firmas_data = [
            ['_' * 30],
            ['Administrador'],
        ]

        tabla_firmas = Table(firmas_data, colWidths=[2.5*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ]))
        elementos.append(tabla_firmas)

        return elementos

    def generar_recibo_pago(self, pago_data, venta_data, cliente_data, nicho_data, output_path=None):
        """
        Generar recibo de pago en PDF con dos copias en una hoja carta
        (Una para la parroquia y otra para el titular)

        Args:
            pago_data: Diccionario con datos del pago
            venta_data: Diccionario con datos de la venta
            cliente_data: Diccionario con datos del cliente
            nicho_data: Diccionario con datos del nicho
            output_path: Ruta del archivo de salida
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            recibos_dir = AppPaths.get_recibos_dir()
            output_path = os.path.join(recibos_dir, f"recibo_{pago_data['numero_recibo']}_{timestamp}.pdf")

        # Crear documento con BaseDocTemplate para usar múltiples frames
        doc = BaseDocTemplate(output_path, pagesize=letter)

        # Definir dimensiones de la página
        page_width, page_height = letter
        margin = 25

        # Crear dos frames: uno para la mitad superior y otro para la inferior
        # Frame superior (COPIA PARROQUIA)
        frame_superior = Frame(
            margin,  # x1
            page_height / 2 + 10,  # y1 (mitad inferior de la mitad superior para dejar espacio)
            page_width - 2 * margin,  # width
            page_height / 2 - margin - 10,  # height
            id='superior',
            showBoundary=0  # 0 para no mostrar bordes, 1 para debug
        )

        # Frame inferior (COPIA TITULAR)
        frame_inferior = Frame(
            margin,  # x1
            margin,  # y1
            page_width - 2 * margin,  # width
            page_height / 2 - 10,  # height
            id='inferior',
            showBoundary=0
        )

        # Crear template de página con ambos frames
        template = PageTemplate(id='recibo_doble', frames=[frame_superior, frame_inferior])
        doc.addPageTemplates([template])

        # Crear contenido del documento
        story = []

        # Primer recibo (COPIA PARROQUIA) - se renderiza en frame superior
        contenido_parroquia = self._crear_contenido_recibo(
            pago_data, venta_data, cliente_data, nicho_data,
            "═══ COPIA PARROQUIA ═══"
        )
        story.extend(contenido_parroquia)

        # Frame break para pasar al siguiente frame (frame inferior)
        story.append(Spacer(1, 0))  # Esto forzará el cambio de frame

        # Segundo recibo (COPIA TITULAR) - se renderiza en frame inferior
        contenido_titular = self._crear_contenido_recibo(
            pago_data, venta_data, cliente_data, nicho_data,
            "═══ COPIA TITULAR ═══"
        )
        story.extend(contenido_titular)

        # Generar PDF
        doc.build(story)
        return output_path

    def generar_consentimiento_urna(self, urna_data, venta_data, cliente_data, nicho_data, output_path=None):
        """
        Generar documento de consentimiento para depósito de urna en nicho

        Args:
            urna_data: Diccionario con datos de la urna
            venta_data: Diccionario con datos de la venta
            cliente_data: Diccionario con datos del cliente titular
            nicho_data: Diccionario con datos del nicho
            output_path: Ruta del archivo de salida

        Returns:
            Ruta del archivo PDF generado
        """
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            consentimientos_dir = AppPaths.get_recibos_dir()  # Usar mismo directorio de recibos
            output_path = os.path.join(consentimientos_dir, f"consentimiento_urna_{urna_data.get('numero_urna', 'xxx')}_{timestamp}.pdf")

        # Crear documento con márgenes más estrechos
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=0.5*inch, leftMargin=0.5*inch,
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []

        # Encabezado de la parroquia
        header_style = ParagraphStyle(
            name='Header',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            spaceAfter=3
        )

        story.append(Paragraph(f"<b>{self.parish_config['nombre']}</b>", header_style))
        story.append(Paragraph(self.parish_config['direccion'], header_style))
        story.append(Paragraph(f"Tel: {self.parish_config['telefono']}", header_style))
        story.append(Spacer(1, 0.2*inch))

        # Título del documento
        title_style = ParagraphStyle(
            name='DocumentTitle',
            parent=self.styles['Title'],
            fontSize=10,
            alignment=TA_CENTER,
            textColor=colors.darkblue,
            spaceAfter=5,
            fontName='Helvetica-Bold'
        )
        story.append(Paragraph("CONSENTIMIENTO INFORMADO", title_style))
        story.append(Paragraph("Depósito de Urna en Nicho", title_style))
        story.append(Spacer(1, 0.1*inch))

        # Contenido del consentimiento
        body_style = ParagraphStyle(
            name='BodyJustified',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
            leading=12
        )

        # Información del titular y urna
        info_data = [
            ['INFORMACIÓN DEL TITULAR Y URNA', ''],
            ['Titular:', f"{cliente_data.get('nombre', '')} {cliente_data.get('apellido', '')}"],
            ['Nicho:', f"{nicho_data.get('numero', 'N/A')} - Sección {nicho_data.get('seccion', 'N/A')}"],
            ['Nombre del Difunto:', urna_data.get('nombre_difunto', 'N/A')],
            ['Fecha de Defunción:', urna_data.get('fecha_defuncion', 'N/A')],
            ['Fecha de Depósito:', urna_data.get('fecha_deposito_urna', 'N/A')],
        ]

        tabla_info = Table(info_data, colWidths=[1.5*inch, 3.5*inch])
        tabla_info.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ]))

        story.append(tabla_info)
        story.append(Spacer(1, 0.1*inch))

        # Texto del consentimiento
        consentimiento_text = f"""<b>DECLARACIÓN DE CONSENTIMIENTO INFORMADO</b><br/><br/>
Yo, <b>{cliente_data.get('nombre', '')} {cliente_data.get('apellido', '')}</b>, titular del nicho ubicado en <b>{nicho_data.get('numero', 'N/A')} - Sección {nicho_data.get('seccion', 'N/A')}</b>, en esta <b>{self.parish_config['nombre']}</b>, por este medio <b>AUTORIZO Y CONSIENTO</b> el depósito de la urna conteniendo los restos de <b>{urna_data.get('nombre_difunto', 'N/A')}</b> (fallecido el <b>{urna_data.get('fecha_defuncion', 'N/A')}</b>) en el nicho de mi propiedad, de conformidad con la normatividad vigente y los términos establecidos en el contrato de venta del nicho.<br/><br/>
<b>DECLARO QUE:</b><br/>
• He sido informado completamente sobre el proceso de depósito de la urna en el nicho.<br/>
• Conozco mis derechos y responsabilidades como titular del nicho.<br/>
• Confirmo que los restos a depositar corresponden a la persona identificada en este documento.<br/>
• He recibido una copia de este consentimiento para mis registros personales.<br/><br/>
<b>RECONOZCO:</b><br/>
La parroquia no se responsabiliza por daños causados por eventos naturales, accidentes, o fuerza mayor que afecten la integridad del nicho. El titular o sus herederos asumen toda responsabilidad en estos casos, conforme a lo establecido en el contrato de venta."""

        story.append(Paragraph(consentimiento_text, body_style))
        story.append(Spacer(1, 0.15*inch))

        # Sección de firmas
        firmas_style = ParagraphStyle(
            name='FirmasStyle',
            parent=self.styles['Normal'],
            fontSize=9,
            alignment=TA_CENTER,
            spaceAfter=6
        )

        story.append(Paragraph("AUTORIZACIONES Y FIRMAS", ParagraphStyle(
            name='FirmasTitle',
            parent=self.styles['Normal'],
            fontSize=10,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            spaceAfter=10
        )))

        firmas_data = [
            ['_' * 35, '', '_' * 35],
            ['Firma del Titular', '', 'Sello de la Parroquia'],
            ['', '', ''],
            [f"{cliente_data.get('nombre', '')} {cliente_data.get('apellido', '')}",
             '', 'Sello Parroquia'],
            [f"Fecha: {datetime.now().strftime('%d/%m/%Y')}"],
        ]

        tabla_firmas = Table(firmas_data, colWidths=[2*inch, 0.5*inch, 2*inch])
        tabla_firmas.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'BOTTOM'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 25),
        ]))

        story.append(tabla_firmas)
        story.append(Spacer(1, 0.15*inch))

        # Pie de página con información de emisión
        footer_style = ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=7,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=3
        )

        fecha_emision = datetime.now().strftime("%d de %B de %Y a las %H:%M")
        story.append(Paragraph(f"<i>Documento emitido: {fecha_emision}</i>", footer_style))
        story.append(Paragraph("Este documento es válido como constancia de autorización para el depósito de urna", footer_style))

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
            titulos_dir = AppPaths.get_titulos_dir()
            output_path = os.path.join(titulos_dir, f"titulo_{venta_data['numero_contrato']}_{timestamp}.pdf")
        
        # Crear documento
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=25, leftMargin=25,
                              topMargin=25, bottomMargin=25)
        
        # Contenido del documento
        story = []
        
        # Encabezado con información de la parroquia
        story.extend(self._crear_encabezado_parroquia())
        
        # Título del documento
        story.append(Paragraph("TÍTULO DE PROPIEDAD", self.styles['CustomTitle']))
        story.append(Paragraph("CRIPTA FAMILIAR", self.styles['CustomSubtitle']))
        story.append(Spacer(1, 10))
        
        # Texto legal del título
        texto_legal = f"""
        Por medio del presente documento, {self.parish_config['nombre']} certifica que 
        <b>{cliente_data['nombre']} {cliente_data['apellido']}</b>, identificado(a) con cédula de 
        ciudadanía número <b>{cliente_data['cedula']}</b>, ha adquirido en plena propiedad 
        el derecho de uso y goce del nicho número <b>{nicho_data['numero']}</b>, ubicado en 
        la sección <b>{nicho_data['seccion']}</b>, fila <b>{nicho_data['fila']}</b>, 
        columna <b>{nicho_data['columna']}</b> de las criptas de esta parroquia.
        """
        
        story.append(Paragraph(texto_legal, self.styles['InfoText']))
        story.append(Spacer(1, 10))
        
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
        story.append(Spacer(1, 10))
        
        # Beneficiarios si existen
        if beneficiarios_data:
            story.append(Paragraph("BENEFICIARIOS DESIGNADOS", self.styles['CustomSubtitle']))
            
            beneficiarios_texto = "En caso de fallecimiento del titular, los derechos sobre este nicho serán transferidos a los siguientes beneficiarios en el orden establecido:"
            story.append(Paragraph(beneficiarios_texto, self.styles['InfoText']))
            story.append(Spacer(1, 10))
            
            for i, beneficiario in enumerate(beneficiarios_data, 1):
                beneficiario_texto = f"<b>{i}. {beneficiario['nombre']} {beneficiario['apellido']}</b> - Cédula: {beneficiario['cedula']}"
                story.append(Paragraph(beneficiario_texto, self.styles['InfoText']))
            
            story.append(Spacer(1, 10))
        
        # Condiciones y términos
        condiciones_texto = """
        <b>CONDICIONES Y TÉRMINOS:</b><br/>
        1. Este título otorga el derecho de uso y goce del nicho mencionado a perpetuidad.<br/>
        2. El titular se compromete a respetar las normas del espacio de criptas y la parroquia.<br/>
        3. El nicho es intransferible.<br/>
        4. El nicho debe ser utilizado únicamente para los fines establecidos.<br/>
        """
        
        story.append(Paragraph(condiciones_texto, self.styles['InfoText']))
        story.append(Spacer(1, 10))
        
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
        elementos.append(Spacer(1, 10))
        
        return elementos
    
    def _crear_pie_firmas(self):
        """Crear pie de página con firmas para recibos"""
        elementos = []
        
        elementos.append(Spacer(1, 10))
        
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
        
        elementos.append(Spacer(1, 10))
        
        # Fecha de expedición
        fecha_expedicion = datetime.now().strftime("Expedido en Zapopan, Jalisco el %d de %B de %Y")
        elementos.append(Paragraph(fecha_expedicion, self.styles['CenteredText']))
        elementos.append(Spacer(1, 40))
        
        # Líneas de firma
        firmas_data = [
            ['_' * 30, '_' * 30],
            ['Párroco', 'Dueño del nicho'],
            ['Firma y Sello', 'Firma y Nombre']
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
            reportes_dir = AppPaths.get_reportes_dir()
            output_path = os.path.join(reportes_dir, f"reporte_movimientos_{timestamp}.pdf")

        # Crear documento
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                              rightMargin=25, leftMargin=25,
                              topMargin=25, bottomMargin=25)

        story = []

        # Encabezado
        story.extend(self._crear_encabezado_parroquia())

        # Título
        story.append(Paragraph("REPORTE DE MOVIMIENTOS", self.styles['CustomTitle']))
        # Formatear fechas solo si son objetos date/datetime
        fecha_inicio_str = fecha_inicio.strftime('%d/%m/%Y') if hasattr(fecha_inicio, 'strftime') else str(fecha_inicio)
        fecha_fin_str = fecha_fin.strftime('%d/%m/%Y') if hasattr(fecha_fin, 'strftime') else str(fecha_fin)
        periodo = f"Período: {fecha_inicio_str} - {fecha_fin_str}"
        story.append(Paragraph(periodo, self.styles['CustomSubtitle']))
        story.append(Spacer(1, 30))

        # Tabla de movimientos
        if movimientos_data:
            # Encabezados de la tabla - usar las claves del primer registro
            first_item = movimientos_data[0]
            headers = list(first_item.keys())

            # Crear tabla con encabezados formateados
            tabla_data = [[h.replace('_', ' ').title() for h in headers]]

            # Agregar datos
            for mov in movimientos_data:
                row = [str(mov.get(key, '')) for key in headers]
                tabla_data.append(row)

            # Calcular anchos de columnas dinámicamente
            num_cols = len(headers)
            col_width = 6.5 * inch / num_cols

            # Crear tabla
            tabla = Table(tabla_data, colWidths=[col_width] * num_cols)
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