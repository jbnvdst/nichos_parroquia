# build_installer.py
# Script automatizado para construir el ejecutable y el instalador
# Integra PyInstaller + Inno Setup para crear un instalador completo

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
import json

class InstallerBuilder:
    """
    Clase para automatizar la construcción del instalador completo
    Incluye compilación del ejecutable y creación del instalador
    """

    def __init__(self, version="1.0.5"):
        """
        Inicializar el constructor

        Args:
            version: Versión de la aplicación (formato: X.Y.Z)
        """
        self.version = version
        self.app_name = "SistemaCriptas"
        self.main_script = "main.py"
        self.icon_path = "assets/icon.ico"

        # Rutas
        self.project_root = Path.cwd()
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"
        self.installer_dir = self.dist_dir / "installer"

        # Archivos
        self.spec_file = self.project_root / f"{self.app_name}.spec"
        self.iss_file = self.project_root / "installer_script.iss"
        self.version_file = self.project_root / "version_info.txt"

    def print_header(self, text):
        """Imprimir encabezado formateado"""
        print("\n" + "=" * 70)
        print(f"  {text}")
        print("=" * 70 + "\n")

    def print_step(self, step_number, text):
        """Imprimir paso formateado"""
        print(f"\n[Paso {step_number}] {text}")
        print("-" * 70)

    def check_requirements(self):
        """Verificar que todas las herramientas necesarias estén instaladas"""
        self.print_step(1, "Verificando requisitos")

        # Verificar Python
        print(f"[OK] Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

        # Verificar PyInstaller
        try:
            import PyInstaller
            print(f"[OK] PyInstaller instalado")
        except ImportError:
            print("[INFO] PyInstaller no encontrado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("[OK] PyInstaller instalado")

        # Verificar Inno Setup
        self.inno_compiler = None

        # Primero intentar encontrarlo en PATH
        try:
            result = subprocess.run(
                ["where", "ISCC.exe"],
                capture_output=True,
                text=True,
                check=True
            )
            if result.stdout:
                self.inno_compiler = result.stdout.strip().split('\n')[0]
                print(f"[OK] Inno Setup encontrado en PATH: {self.inno_compiler}")
        except:
            pass

        # Si no está en PATH, buscar en ubicaciones comunes
        if not self.inno_compiler:
            inno_paths = [
                r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                r"C:\Program Files\Inno Setup 6\ISCC.exe",
                r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
                r"C:\Program Files\Inno Setup 5\ISCC.exe",
            ]

            for path in inno_paths:
                if os.path.exists(path):
                    self.inno_compiler = path
                    print(f"[OK] Inno Setup encontrado: {path}")
                    break

        # Último intento: buscar recursivamente
        if not self.inno_compiler:
            print("Buscando Inno Setup en Program Files...")
            import glob
            for pattern in [r"C:\Program Files*\Inno Setup*\ISCC.exe"]:
                matches = glob.glob(pattern)
                if matches:
                    self.inno_compiler = matches[0]
                    print(f"[OK] Inno Setup encontrado: {self.inno_compiler}")
                    break

        if not self.inno_compiler:
            print("[WARNING] Inno Setup no encontrado en las ubicaciones comunes")
            print("  Descargalo desde: https://jrsoftware.org/isdl.php")
            print("  O especifica la ruta manualmente en el codigo")
            return False

        # Verificar archivo principal
        if not os.path.exists(self.main_script):
            print(f"[ERROR] No se encuentra el archivo {self.main_script}")
            return False
        print(f"[OK] Archivo principal encontrado: {self.main_script}")

        # Verificar archivo de script de instalador
        if not os.path.exists(self.iss_file):
            print(f"[ERROR] No se encuentra el script de Inno Setup: {self.iss_file}")
            return False
        print(f"[OK] Script de Inno Setup encontrado")

        return True

    def clean_build_dirs(self):
        """Limpiar directorios de construcción anteriores"""
        self.print_step(2, "Limpiando directorios de construcción")

        dirs_to_clean = [self.dist_dir, self.build_dir]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                print(f"  Eliminando: {dir_path}")
                shutil.rmtree(dir_path)
                print(f"  [OK] {dir_path} eliminado")

        # Recrear directorios
        self.dist_dir.mkdir(exist_ok=True)
        self.installer_dir.mkdir(parents=True, exist_ok=True)
        print("[OK] Directorios recreados")

    def create_version_file(self):
        """Crear archivo de información de versión para Windows"""
        self.print_step(3, "Creando archivo de versión")

        # Parsear versión
        version_parts = self.version.split('.')
        while len(version_parts) < 4:
            version_parts.append('0')

        version_content = f'''VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    prodvers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Parroquia Nuestra Señora del Consuelo de los Afligidos'),
        StringStruct(u'FileDescription', u'Sistema de Administración de Criptas'),
        StringStruct(u'FileVersion', u'{self.version}'),
        StringStruct(u'InternalName', u'{self.app_name}'),
        StringStruct(u'LegalCopyright', u'© {datetime.now().year} Parroquia Nuestra Señora del Consuelo de los Afligidos'),
        StringStruct(u'OriginalFilename', u'{self.app_name}.exe'),
        StringStruct(u'ProductName', u'Sistema de Criptas'),
        StringStruct(u'ProductVersion', u'{self.version}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''

        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(version_content)

        print(f"[OK] Archivo de versión creado: {self.version_file}")

    def create_spec_file(self):
        """Crear archivo .spec para PyInstaller"""
        self.print_step(4, "Creando archivo .spec de PyInstaller")

        # Convertir rutas a formato POSIX (/) para evitar problemas con backslash
        def normalize_path(path):
            """Convertir Path a string con barras normales"""
            return str(path).replace('\\', '/')

        # Verificar si existe icono
        if os.path.exists(self.icon_path):
            icon_param = f"icon=r'{normalize_path(self.icon_path)}'"
        else:
            icon_param = "icon=None"

        # Construir lista de datas solo con directorios que existen
        datas_list = []
        data_dirs = ['database', 'ui', 'reports', 'backup']
        for dir_name in data_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                datas_list.append(f"        ('{dir_name}', '{dir_name}'),")
                print(f"  [INFO] Incluyendo directorio: {dir_name}")
            else:
                print(f"  [WARNING] Directorio no encontrado, omitiendo: {dir_name}")

        # Si no hay datas, usar lista vacía
        datas_content = "\n".join(datas_list) if datas_list else "        # No data directories found"

        # Normalizar ruta del archivo de versión
        version_file_path = normalize_path(self.version_file)
        version_param = f"version=r'{version_file_path}'" if self.version_file.exists() else "version=None"

        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
# Archivo .spec generado automaticamente para {self.app_name}

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[
{datas_content}
    ],
    hiddenimports=[
        # Modulos criticos - TODOS listados explicitamente
        'schedule',
        'schedule.job',

        # SQLAlchemy - completo
        'sqlalchemy',
        'sqlalchemy.dialects',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.pool',
        'sqlalchemy.ext',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.sql',
        'sqlalchemy.sql.default_comparator',
        'sqlalchemy.orm',
        'sqlalchemy.engine',

        # ReportLab - completo
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.pdfgen.canvas',
        'reportlab.lib',
        'reportlab.lib.pagesizes',
        'reportlab.lib.units',
        'reportlab.lib.colors',
        'reportlab.lib.styles',
        'reportlab.platypus',
        'reportlab.graphics',

        # Pillow
        'PIL',
        'PIL.Image',

        # Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',

        # Requests - completo
        'requests',
        'requests.adapters',
        'requests.exceptions',
        'requests.auth',
        'requests.models',
        'requests.sessions',
        'urllib3',
        'urllib3.util',
        'urllib3.util.retry',

        # Pandas y dependencias
        'pandas',
        'numpy',
        'openpyxl',
        'openpyxl.writer',
        'openpyxl.writer.excel',
        'et_xmlfile',

        # Python-dateutil
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',

        # Otros modulos necesarios
        'shortuuid',
        'packaging',
        'packaging.version',
        'threading',
        'json',
        'pathlib',
        'zipfile',
        'datetime',
        'time',
        'os',
        'shutil',
        'tempfile',
        'webbrowser',
        'sqlite3',

        # Modulos del sistema
        'greenlet',
        'charset_normalizer',
        'pytz',
        'six',
        'typing_extensions',
        'tzdata',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=['pytest', 'test', 'tests', 'setuptools'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.app_name}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Sin consola para aplicacion GUI
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    {icon_param},
    {version_param},
)
'''

        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)

        print(f"[OK] Archivo .spec creado: {self.spec_file}")

    def build_executable(self):
        """Construir el ejecutable con PyInstaller"""
        self.print_step(5, "Compilando ejecutable con PyInstaller")

        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            '--log-level=DEBUG',  # Agregar logging detallado
            str(self.spec_file)
        ]

        print(f"  Ejecutando: {' '.join(cmd)}")
        print()

        try:
            # Capturar salida para poder mostrarla en caso de error
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'  # Manejar caracteres problemáticos
            )

            # Mostrar salida de PyInstaller
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)

            # Verificar que el ejecutable fue creado
            exe_path = self.dist_dir / f"{self.app_name}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                print(f"\n[OK] Ejecutable creado exitosamente")
                print(f"  Ubicacion: {exe_path}")
                print(f"  Tamano: {size_mb:.2f} MB")
                return True
            else:
                print(f"[ERROR] No se encontro el ejecutable en: {exe_path}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error durante la compilacion con PyInstaller")
            print(f"Codigo de salida: {e.returncode}")
            if e.stdout:
                print("\n--- STDOUT ---")
                print(e.stdout)
            if e.stderr:
                print("\n--- STDERR ---")
                print(e.stderr)
            return False
        except Exception as e:
            print(f"[ERROR] Excepcion inesperada: {type(e).__name__}: {str(e)}")
            return False

    def prepare_installer_files(self):
        """Preparar archivos necesarios para el instalador"""
        self.print_step(6, "Preparando archivos para el instalador")

        # Crear directorio de assets si no existe
        assets_dir = self.project_root / "assets"
        assets_dir.mkdir(exist_ok=True)

        # Crear icono placeholder si no existe
        if not (assets_dir / "icon.ico").exists():
            print("  [WARNING] No se encontró icon.ico, creando placeholder...")
            # Aquí podrías generar un icono básico o simplemente notificar

        # Crear archivos de documentación si no existen
        docs = {
            "README.txt": self.create_readme_content(),
            "LICENSE.txt": self.create_license_content(),
            "INSTALACION.txt": self.create_installation_guide_content()
        }

        for filename, content in docs.items():
            file_path = self.project_root / filename
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  [OK] Creado: {filename}")
            else:
                print(f"  [OK] Encontrado: {filename}")

        print("[OK] Archivos preparados")

    def create_readme_content(self):
        """Generar contenido del README"""
        return f"""
Sistema de Administración de Criptas - v{self.version}
{'=' * 70}

DESCRIPCIÓN
-----------
Sistema completo para la administración de criptas en parroquias, que incluye:

• Gestión de nichos disponibles
• Registro de ventas (contado/crédito)
• Control de pagos y abonos
• Generación de recibos e impresión
• Títulos de propiedad
• Reportes exportables
• Búsqueda avanzada
• Respaldos automáticos
• Sistema de actualizaciones desde GitHub

REQUISITOS DEL SISTEMA
----------------------
• Windows 10 o superior (64-bit recomendado)
• Mínimo 4GB de RAM
• 500MB de espacio libre en disco
• Impresora (para generar recibos y títulos)
• Conexión a internet (para verificar actualizaciones)

CARACTERÍSTICAS PRINCIPALES
---------------------------
[OK] Interfaz gráfica intuitiva
[OK] Base de datos SQLite integrada
[OK] Generación automática de PDFs
[OK] Respaldos automáticos programables
[OK] Sistema de actualización integrado
[OK] Búsqueda y filtrado avanzado
[OK] Reportes personalizables

ACTUALIZACIONES
---------------
El sistema verifica automáticamente si hay nuevas versiones disponibles
al iniciar. Las actualizaciones se descargan desde GitHub y pueden
instalarse directamente desde la aplicación.

Para verificar manualmente: Menú → Ayuda → Verificar Actualizaciones

SOPORTE
-------
Para reportar problemas o solicitar nuevas funcionalidades:
https://github.com/jbnvdst/nichos_parroquia/issues

VERSIÓN: {self.version}
FECHA: {datetime.now().strftime('%d/%m/%Y')}
"""

    def create_license_content(self):
        """Generar contenido de la licencia"""
        return f"""
MIT License

Copyright (c) {datetime.now().year} Parroquia Nuestra Señora del Consuelo de los Afligidos

Por la presente se concede permiso, libre de cargos, a cualquier persona que obtenga una
copia de este software y de los archivos de documentación asociados (el "Software"), para
utilizar el Software sin restricción, incluyendo sin limitación los derechos a usar, copiar,
modificar, fusionar, publicar, distribuir, sublicenciar, y/o vender copias del Software, y a
permitir a las personas a las que se les proporcione el Software a hacer lo mismo, sujeto a
las siguientes condiciones:

El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o
porciones sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "TAL CUAL", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA,
INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO
PARTICULAR Y NO INFRACCIÓN. EN NINGÚN CASO LOS AUTORES O TITULARES DEL COPYRIGHT SERÁN
RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES, YA SEA EN UNA ACCIÓN
DE CONTRATO, AGRAVIO O CUALQUIER OTRO MOTIVO, QUE SURJA DE O EN CONEXIÓN CON EL SOFTWARE O
EL USO U OTRO TIPO DE ACCIONES EN EL SOFTWARE.
"""

    def create_installation_guide_content(self):
        """Generar contenido de la guía de instalación"""
        return """
GUÍA DE INSTALACIÓN
Sistema de Administración de Criptas
====================================

REQUISITOS PREVIOS
------------------
[OK] Windows 10 o superior
[OK] Permisos de administrador (para instalación)
[OK] 500 MB de espacio libre en disco

INSTALACIÓN
-----------

Paso 1: Ejecutar el Instalador
   • Haz doble clic en el archivo de instalación (.exe)
   • Si aparece un aviso de Windows Defender, haz clic en "Más información"
     y luego en "Ejecutar de todas formas"

Paso 2: Asistente de Instalación
   • Acepta los términos de la licencia
   • Selecciona la carpeta de instalación (por defecto: C:\\Program Files\\Sistema de Criptas)
   • Selecciona la carpeta donde se guardarán los datos
   • Elige si quieres crear un icono en el escritorio

Paso 3: Completar la Instalación
   • Haz clic en "Instalar"
   • Espera a que se copien todos los archivos
   • Marca "Ejecutar Sistema de Criptas" si quieres iniciarlo inmediatamente
   • Haz clic en "Finalizar"

PRIMER USO
----------

1. Configuración Inicial:
   • La primera vez que ejecutes el programa, se creará automáticamente
     la base de datos
   • Ve a Configuración para personalizar el nombre de la parroquia

2. Agregar Nichos:
   • Ve a "Gestión de Nichos" para agregar los nichos disponibles
   • Puedes importar desde un archivo CSV o agregarlos manualmente

3. Comenzar a Usar:
   • Registra clientes desde "Ventas"
   • Gestiona pagos desde "Pagos"
   • Genera reportes desde "Reportes"

RESPALDOS
---------
• El sistema crea respaldos automáticos semanalmente
• También puedes crear respaldos manuales desde Archivo → Crear Respaldo
• Los respaldos se guardan en: %APPDATA%\\Sistema de Criptas\\backups
• IMPORTANTE: Guarda los respaldos en una ubicación externa (USB, nube, etc.)

ACTUALIZACIONES
---------------
• El sistema verifica automáticamente actualizaciones al iniciar
• Para verificar manualmente: Ayuda → Verificar Actualizaciones
• Las actualizaciones se descargan e instalan automáticamente

DESINSTALACIÓN
--------------
• Panel de Control → Programas → Desinstalar un programa
• Busca "Sistema de Administración de Criptas"
• Haz clic en "Desinstalar"
• NOTA: Esto NO eliminará tus datos (base de datos y respaldos)

SOLUCIÓN DE PROBLEMAS
---------------------

Problema: El programa no inicia
Solución:
   • Verifica que tienes permisos suficientes
   • Ejecuta como administrador (clic derecho → Ejecutar como administrador)
   • Verifica que no haya antivirus bloqueando el programa

Problema: Error de base de datos
Solución:
   • Verifica permisos de escritura en la carpeta de datos
   • Restaura desde un respaldo reciente

Problema: No se pueden generar PDF
Solución:
   • Verifica que la carpeta de reportes tenga permisos de escritura
   • Reinstala el programa

CONTACTO Y SOPORTE
------------------
Para soporte técnico o reportar problemas:
https://github.com/jbnvdst/nichos_parroquia/issues
"""

    def build_installer(self):
        """Compilar el instalador con Inno Setup"""
        self.print_step(7, "Compilando instalador con Inno Setup")

        if not self.inno_compiler:
            print("[ERROR] Inno Setup no está disponible")
            return False

        # Actualizar versión en el archivo .iss
        self.update_iss_version()

        cmd = [
            self.inno_compiler,
            str(self.iss_file),
            f"/O{self.installer_dir}",  # Output directory
            f"/F{self.app_name}_Setup_v{self.version}"  # Output filename
        ]

        print(f"  Ejecutando: {' '.join(cmd)}")
        print()

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True
            )

            print(result.stdout)

            # Verificar que el instalador fue creado
            installer_path = self.installer_dir / f"{self.app_name}_Setup_v{self.version}.exe"
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"\n[OK] Instalador creado exitosamente")
                print(f"  Ubicación: {installer_path}")
                print(f"  Tamaño: {size_mb:.2f} MB")
                return True
            else:
                print(f"[ERROR] No se encontró el instalador en: {installer_path}")
                return False

        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error durante la compilación del instalador")
            print(e.stdout)
            print(e.stderr)
            return False

    def update_iss_version(self):
        """Actualizar versión en el archivo .iss"""
        with open(self.iss_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Actualizar línea de versión
        import re
        content = re.sub(
            r'#define MyAppVersion ".*"',
            f'#define MyAppVersion "{self.version}"',
            content
        )

        with open(self.iss_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def create_release_notes(self):
        """Crear archivo con notas de la versión"""
        self.print_step(8, "Creando notas de versión")

        notes_content = f"""# Release Notes v{self.version}

## Fecha de Compilación
{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

## Archivos Incluidos
- {self.app_name}_Setup_v{self.version}.exe (Instalador completo)

## Novedades en esta versión
- Sistema de actualización automática desde GitHub
- Instalador mejorado con Inno Setup
- [Agrega aquí las características específicas de esta versión]

## Instalación
1. Descarga el archivo {self.app_name}_Setup_v{self.version}.exe
2. Ejecuta el instalador
3. Sigue las instrucciones del asistente de instalación

## Actualización desde versión anterior
El instalador detectará automáticamente versiones anteriores y las actualizará.
Se recomienda hacer un respaldo antes de actualizar.

## Requisitos del Sistema
- Windows 10 o superior
- 4GB RAM mínimo
- 500MB espacio en disco

## Soporte
Reporta problemas en: https://github.com/jbnvdst/nichos_parroquia/issues
"""

        notes_file = self.installer_dir / f"Release_Notes_v{self.version}.md"
        with open(notes_file, 'w', encoding='utf-8') as f:
            f.write(notes_content)

        print(f"[OK] Notas de versión creadas: {notes_file}")

    def create_build_summary(self):
        """Crear resumen de la compilación"""
        self.print_header("RESUMEN DE LA COMPILACIÓN")

        exe_path = self.dist_dir / f"{self.app_name}.exe"
        installer_path = self.installer_dir / f"{self.app_name}_Setup_v{self.version}.exe"

        print(f"Versión: {self.version}")
        print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print()
        print("Archivos generados:")
        print(f"  • Ejecutable: {exe_path}")
        if exe_path.exists():
            print(f"    Tamaño: {exe_path.stat().st_size / (1024*1024):.2f} MB")
        print(f"  • Instalador: {installer_path}")
        if installer_path.exists():
            print(f"    Tamaño: {installer_path.stat().st_size / (1024*1024):.2f} MB")
        print()
        print("Próximos pasos:")
        print("  1. Prueba el instalador en una máquina limpia")
        print("  2. Crea un nuevo Release en GitHub")
        print("  3. Sube el archivo del instalador al Release")
        print("  4. Actualiza las Release Notes con las novedades")
        print()
        print("Comando para crear release en GitHub (con gh CLI):")
        print(f'  gh release create v{self.version} "{installer_path}" --title "Versión {self.version}" --notes "Ver Release_Notes_v{self.version}.md"')
        print()

    def build_all(self):
        """Ejecutar todo el proceso de construcción"""
        self.print_header(f"CONSTRUCCIÓN DE {self.app_name} v{self.version}")

        # Verificar requisitos
        if not self.check_requirements():
            print("\n[ERROR] Faltan requisitos necesarios. Abortando.")
            return False

        # Limpiar directorios
        self.clean_build_dirs()

        # Crear archivos de versión
        self.create_version_file()
        self.create_spec_file()

        # Preparar archivos
        self.prepare_installer_files()

        # Construir ejecutable
        if not self.build_executable():
            print("\n[ERROR] Error al construir el ejecutable. Abortando.")
            return False

        # Construir instalador
        if not self.build_installer():
            print("\n[ERROR] Error al construir el instalador.")
            print("  El ejecutable está disponible en:", self.dist_dir)
            return False

        # Crear notas de versión
        self.create_release_notes()

        # Mostrar resumen
        self.create_build_summary()

        return True


def main():
    """Función principal"""
    import argparse

    parser = argparse.ArgumentParser(description="Constructor de instalador para Sistema de Criptas")
    parser.add_argument(
        "--version",
        "-v",
        default="1.0.5",
        help="Versión de la aplicación (formato: X.Y.Z)"
    )
    parser.add_argument(
        "--skip-installer",
        action="store_true",
        help="Solo construir ejecutable, sin crear instalador"
    )

    args = parser.parse_args()

    builder = InstallerBuilder(version=args.version)

    if args.skip_installer:
        # Solo construir ejecutable
        if builder.check_requirements():
            builder.clean_build_dirs()
            builder.create_version_file()
            builder.create_spec_file()
            builder.build_executable()
    else:
        # Construcción completa
        success = builder.build_all()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
