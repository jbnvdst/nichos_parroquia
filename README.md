# Sistema de Administración de Criptas

## 📋 Descripción

Sistema completo desarrollado en Python para la administración de criptas en parroquias. Permite gestionar nichos, ventas, pagos, generar recibos y títulos de propiedad, crear reportes y mantener respaldos automáticos de la información.

## ✨ Características Principales

### 🏛️ Gestión de Nichos
- Administración del inventario total de nichos disponibles
- Creación individual o en lote de nichos
- Organización por secciones, filas y columnas
- Control de disponibilidad y precios
- Búsqueda y filtrado avanzado

### 💰 Gestión de Ventas
- Registro de ventas a contado o crédito
- Gestión de clientes y beneficiarios (hasta 2 por nicho)
- Control de contratos y documentación
- Seguimiento de estados de pago
- Historial completo de transacciones

### 💳 Sistema de Pagos
- Registro de pagos y abonos
- Múltiples métodos de pago
- Cálculo automático de saldos
- Generación automática de recibos PDF
- Control de vencimientos

### 📄 Generación de Documentos
- **Recibos de Pago**: Generación automática en PDF con toda la información
- **Títulos de Propiedad**: Documentos legales cuando se completa el pago
- **Reportes**: Múltiples tipos y formatos (PDF, Excel, CSV)
- Personalización con información de la parroquia

### 🔍 Búsqueda Avanzada
- Búsqueda por número de contrato
- Búsqueda por número de cripta
- Búsqueda por nombre del cliente
- Filtros múltiples y búsqueda combinada
- Resultados organizados y exportables

### 📊 Sistema de Reportes
- Reportes de movimientos diarios, mensuales, anuales
- Resúmenes financieros
- Estados de cuenta
- Saldos pendientes
- Reportes de nichos disponibles
- Exportación en múltiples formatos

### 💾 Respaldos Automáticos
- Respaldos programados automáticamente
- Respaldos manuales bajo demanda
- Compresión y cifrado opcional
- Restauración completa del sistema
- Gestión de versiones de respaldo

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **Tkinter**: Interfaz gráfica de usuario
- **SQLAlchemy**: ORM para base de datos
- **SQLite**: Base de datos local
- **ReportLab**: Generación de PDFs
- **Schedule**: Tareas programadas
- **Requests**: Actualizaciones HTTP desde GitHub
- **PyInstaller**: Creación del ejecutable
- **Inno Setup**: Creación del instalador Windows
- **GitHub Actions**: CI/CD automatizado

## 📦 Instalación

### 🎯 Para Usuarios Finales (Windows)

#### Opción 1: Instalador (Recomendado)
1. Descarga `SistemaCriptas_Setup_v1.0.0.exe` desde [Releases](../../releases)
2. Ejecuta el instalador
3. Sigue el asistente de instalación
4. ¡Listo! Usa el acceso directo en tu escritorio

#### Opción 2: Versión Portable (Sin instalación)
1. Descarga `SistemaCriptas_Portable_v1.0.0.zip`
2. Descomprime en cualquier carpeta
3. Ejecuta `SistemaCriptas.exe`

### 💻 Para Desarrolladores

#### Ejecutar desde Código Fuente

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/tu-usuario/nichos_parroquia.git
   cd nichos_parroquia
   ```

2. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación**
   ```bash
   python main.py
   ```

#### Crear Instalador de Windows

**Método automatizado (Recomendado):**
```bash
# Construir ejecutable + instalador completo
python build_installer.py --version 1.0.0
```

**Solo el ejecutable (sin instalador):**
```bash
python build_installer.py --version 1.0.0 --skip-installer
```

**Publicar release en GitHub:**
```bash
# Crear tag de versión
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions construirá y publicará automáticamente
```

Ver [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) para instrucciones detalladas.

### Requisitos del Sistema
- Windows 10 o superior
- 4GB RAM mínimo
- 500MB espacio libre en disco
- Impresora (opcional, para recibos y títulos)

## 🚀 Uso del Sistema

### Primera Configuración

1. **Ejecutar el sistema** por primera vez
2. **Configurar información de la parroquia** en Configuración
3. **Crear nichos iniciales** desde Gestión de Nichos
4. **Configurar respaldos** según necesidades

### Flujo de Trabajo Típico

1. **Crear Nichos**
   - Ir a "Gestión de Nichos"
   - Agregar nichos individualmente o en lote
   - Configurar precios y ubicaciones

2. **Registrar Venta**
   - Ir a "Ventas" → "Nueva Venta"
   - Ingresar datos del cliente
   - Seleccionar nicho disponible
   - Definir tipo de pago (contado/crédito)
   - Agregar beneficiarios si es necesario

3. **Procesar Pagos**
   - Ir a "Pagos" → "Nuevo Pago"
   - Buscar por número de contrato
   - Registrar monto y método de pago
   - El sistema genera automáticamente el recibo

4. **Generar Título de Propiedad**
   - Ir a "Títulos de Propiedad"
   - Seleccionar venta pagada completamente
   - Generar título en PDF

5. **Crear Reportes**
   - Ir a "Reportes"
   - Seleccionar tipo y período
   - Generar vista previa
   - Exportar en formato deseado

### Búsquedas Rápidas

- **Por Contrato**: Ingresar número en búsqueda rápida
- **Por Cripta**: Buscar por número de nicho
- **Por Cliente**: Buscar por nombre o cédula

## 📁 Estructura de Archivos

```
sistema-criptas/
├── main.py                    # Archivo principal
├── requirements.txt           # Dependencias
├── app_config.json           # Configuración
├── criptas.db                # Base de datos SQLite
├── 
├── database/
│   └── models.py             # Modelos de datos
├── 
├── ui/
│   ├── main_window.py        # Ventana principal
│   ├── nichos_manager.py     # Gestión de nichos
│   ├── ventas_manager.py     # Gestión de ventas
│   ├── pagos_manager.py      # Gestión de pagos
│   ├── titulos_manager.py    # Gestión de títulos
│   ├── reportes_manager.py   # Gestión de reportes
│   └── busqueda_manager.py   # Búsquedas
├── 
├── reports/
│   └── pdf_generator.py      # Generador de PDFs
├── 
├── backup/
│   └── backup_manager.py     # Gestor de respaldos
├── 
├── config/
│   ├── app_config.py         # Configuración
│   ├── logger_config.py      # Logging
│   └── constants.py          # Constantes
├── 
├── recibos/                  # PDFs de recibos
├── titulos/                  # PDFs de títulos
├── reportes/                 # Reportes generados
├── backups/                  # Respaldos automáticos
├── assets/                   # Recursos (logos, etc.)
└── logs/                     # Archivos de log
```

## ⚙️ Configuración

### Configuración de la Parroquia

```json
{
  "parroquia": {
    "nombre": "Parroquia Nuestra Señora del Consuelo de los Afligidos",
    "direccion": "Calle Principal #123",
    "telefono": "+1 (555) 123-4567",
    "email": "info@parroquia.org",
    "parroco": "Padre José María",
    "administrador": "Juan Pérez"
  }
}
```

### Configuración de Respaldos

```json
{
  "backup": {
    "directory": "backups",
    "max_backups": 10,
    "auto_backup": true,
    "schedule_time": "23:00",
    "compression_level": 6
  }
}
```

### Configuración de PDFs

```json
{
  "pdf": {
    "output_dir_recibos": "recibos",
    "output_dir_titulos": "titulos",
    "include_logo": true,
    "font_size": 11,
    "page_size": "letter"
  }
}
```

## 🔒 Respaldos y Seguridad

### Respaldos Automáticos
- Se ejecutan automáticamente cada sábado a las 12:00 PM
- Incluyen base de datos, configuración y archivos generados
- Se mantienen las últimas 10 copias por defecto
- Compresión automática para ahorrar espacio

### Respaldos Manuales
- Disponibles desde el menú "Respaldos"
- Se pueden crear en cualquier momento
- Útiles antes de actualizaciones importantes

### Restauración
- Seleccionar archivo de respaldo desde el menú
- El sistema restaura automáticamente todos los datos
- Se crea respaldo de seguridad antes de restaurar

## 📊 Tipos de Reportes

### Reportes de Movimientos
- Todas las transacciones en un período
- Incluye ventas y pagos
- Filtrable por fechas y tipos

### Reportes Financieros
- Resumen de ingresos y saldos
- Estados de cuenta por cliente
- Saldos pendientes de cobro

### Reportes de Inventario
- Nichos disponibles y vendidos
- Distribución por secciones
- Histórico de ventas por ubicación

### Reportes de Clientes
- Lista completa de clientes
- Historial de compras por cliente
- Información de contacto actualizada

## 🆘 Solución de Problemas

### El programa no inicia
1. Verificar que todos los archivos estén en la misma carpeta
2. Ejecutar como administrador
3. Verificar que no haya antivirus bloqueando
4. Revisar archivo de log en `logs/criptas_app.log`

### Error de base de datos
1. Verificar permisos de escritura en la carpeta
2. Restaurar desde respaldo reciente
3. Recrear base de datos (se perderán datos)

### Problemas de impresión
1. Verificar configuración de impresora
2. Verificar que el PDF se genere correctamente
3. Intentar imprimir desde otro programa

### Archivos PDF corruptos
1. Verificar espacio libre en disco
2. Verificar permisos de escritura
3. Reinstalar ReportLab: `pip install --upgrade reportlab`

## 🔄 Actualizaciones Automáticas desde GitHub

### Sistema de Actualización Integrado
El sistema incluye un módulo de actualización automática que:
- ✅ Verifica actualizaciones automáticamente al iniciar
- ✅ Compara la versión actual con la última en GitHub Releases
- ✅ Muestra las notas de versión antes de actualizar
- ✅ Descarga e instala actualizaciones con un clic
- ✅ No requiere intervención manual del usuario

### Verificación Manual de Actualizaciones
Desde el menú:
```
Ayuda → Verificar Actualizaciones
```

### Instalación de Actualizaciones
1. El sistema detecta automáticamente la nueva versión
2. Muestra un diálogo con las novedades
3. Haz clic en "Descargar e Instalar"
4. El instalador se descarga automáticamente
5. Cierra la aplicación actual
6. Ejecuta el instalador descargado
7. ¡Listo! Ya tienes la última versión

## 📞 Soporte Técnico

### Información de Contacto
- **GitHub Issues**: [Reportar problemas](https://github.com/jbnvdst/nichos_parroquia/issues)
- **GitHub Discussions**: [Hacer preguntas](https://github.com/jbnvdst/nichos_parroquia/discussions)
- **Releases**: [Descargar versiones](https://github.com/jbnvdst/nichos_parroquia/releases)

### Antes de Contactar Soporte
1. Revisar este README completamente
2. Verificar archivos de log en `logs/`
3. Intentar restaurar desde respaldo reciente
4. Tener a mano información del error específico

### Información Necesaria para Soporte
- Versión del sistema
- Sistema operativo
- Descripción detallada del problema
- Mensaje de error exacto
- Pasos para reproducir el problema
- Archivos de log recientes

## 📝 Registro de Cambios

### Versión 1.0.0 (2024-08-21)
#### Nuevas Características
- ✅ Gestión completa de nichos y inventario
- ✅ Sistema de ventas con clientes y beneficiarios
- ✅ Procesamiento de pagos y control de saldos
- ✅ Generación automática de recibos PDF
- ✅ Creación de títulos de propiedad
- ✅ Sistema de reportes múltiples formatos
- ✅ Búsqueda avanzada y filtros
- ✅ Respaldos automáticos programados
- ✅ Interfaz gráfica intuitiva
- ✅ Configuración personalizable

#### Características Técnicas
- Base de datos SQLite integrada
- Generación de PDFs con ReportLab
- Interfaz Tkinter multiplataforma
- Sistema de logging detallado
- Respaldos comprimidos automáticos

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE.txt](LICENSE.txt) para más detalles.

```
MIT License

Copyright (c) 2024 Parroquia Nuestra Señora del Consuelo de los Afligidos

Por la presente se concede permiso, libre de cargos, a cualquier persona
que obtenga una copia de este software...
```

## 🤝 Créditos

Desarrollado por [Tu Nombre/Empresa] para la administración eficiente de criptas parroquiales.

---

**© 2024 Sistema de Administración de Criptas. Todos los derechos reservados.**