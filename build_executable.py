# build_executable.py
# Script para crear el ejecutable con PyInstaller

import os
import sys
import subprocess
import shutil
from pathlib import Path

class ExecutableBuilder:
    def __init__(self):
        self.app_name = "SistemaCriptas"
        self.main_script = "main.py"
        self.icon_path = "assets/icon.ico"  # Si tienes un icono
        self.version = "1.0.0"
        
    def create_spec_file(self):
        """Crear archivo .spec personalizado para PyInstaller"""
        spec_content = f'''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{self.main_script}'],
    pathex=[],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('database', 'database'),
        ('ui', 'ui'),
        ('reports', 'reports'),
        ('backup', 'backup'),
    ],
    hiddenimports=[
        'sqlalchemy.dialects.sqlite',
        'reportlab.pdfgen',
        'reportlab.lib',
        'tkinter',
        'tkinter.ttk',
        'schedule',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
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
    console=False,  # Cambiar a True si necesitas consola para debug
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{self.icon_path if os.path.exists(self.icon_path) else None}',
)
'''
        
        with open(f'{self.app_name}.spec', 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"Archivo {self.app_name}.spec creado")
    
    def build_executable(self):
        """Construir el ejecutable"""
        print("Iniciando construcción del ejecutable...")
        
        # Verificar que PyInstaller esté instalado
        try:
            import PyInstaller
        except ImportError:
            print("PyInstaller no está instalado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        
        # Crear archivo .spec si no existe
        if not os.path.exists(f'{self.app_name}.spec'):
            self.create_spec_file()
        
        # Ejecutar PyInstaller
        cmd = [
            'pyinstaller',
            '--clean',
            '--noconfirm',
            f'{self.app_name}.spec'
        ]
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("Construcción exitosa!")
            print(f"Ejecutable creado en: dist/{self.app_name}.exe")
            
            # Crear directorio de distribución
            self.create_distribution_package()
            
        except subprocess.CalledProcessError as e:
            print(f"Error durante la construcción: {e}")
            print(f"Salida: {e.stdout}")
            print(f"Error: {e.stderr}")
    
    def create_distribution_package(self):
        """Crear paquete de distribución completo"""
        dist_dir = f"dist/{self.app_name}"
        package_dir = f"SistemaCriptas_v{self.version}"
        
        if os.path.exists(package_dir):
            shutil.rmtree(package_dir)
        
        os.makedirs(package_dir, exist_ok=True)
        
        # Copiar ejecutable
        if os.path.exists(f"{dist_dir}.exe"):
            shutil.copy2(f"{dist_dir}.exe", package_dir)
        elif os.path.exists(dist_dir):
            shutil.copytree(dist_dir, f"{package_dir}/{self.app_name}")
        
        # Crear archivos adicionales
        self.create_readme(package_dir)
        self.create_installation_guide(package_dir)
        
        # Crear directorio para base de datos
        os.makedirs(f"{package_dir}/database", exist_ok=True)
        
        # Crear directorios para archivos generados
        for dir_name in ["reportes", "recibos", "titulos", "backups"]:
            os.makedirs(f"{package_dir}/{dir_name}", exist_ok=True)
        
        print(f"Paquete de distribución creado en: {package_dir}")
    
    def create_readme(self, package_dir):
        """Crear archivo README"""
        readme_content = f"""
# Sistema de Administración de Criptas - v{self.version}

## Descripción
Sistema completo para la administración de criptas en parroquias, que incluye:
- Gestión de nichos disponibles
- Registro de ventas (contado/crédito)
- Control de pagos y abonos
- Generación de recibos e impresión
- Títulos de propiedad
- Reportes exportables
- Búsqueda avanzada
- Respaldos automáticos

## Instalación
1. Extraer todos los archivos en una carpeta
2. Ejecutar {self.app_name}.exe
3. El sistema creará automáticamente la base de datos en el primer uso

## Requisitos del Sistema
- Windows 10 o superior
- Mínimo 4GB de RAM
- 500MB de espacio libre en disco
- Impresora (para generar recibos y títulos)

## Respaldos
- Respaldos automáticos cada domingo a las 23:00
- Respaldos manuales disponibles desde el menú
- Los respaldos se guardan en la carpeta "backups"

## Soporte
Para soporte técnico o reportar problemas, contactar al administrador del sistema.

## Versión
{self.version} - {datetime.now().strftime('%B %Y')}
"""
        
        with open(f"{package_dir}/README.txt", 'w', encoding='utf-8') as f:
            f.write(readme_content)
    
    def create_installation_guide(self, package_dir):
        """Crear guía de instalación"""
        install_guide = """
# GUÍA DE INSTALACIÓN - Sistema de Criptas

## PASO 1: Extracción
1. Extraer todos los archivos del ZIP en una carpeta (ej: C:\\SistemaCriptas)
2. Asegurarse de que todos los archivos estén en la misma carpeta

## PASO 2: Primera Ejecución
1. Hacer doble clic en SistemaCriptas.exe
2. El sistema iniciará y creará la base de datos automáticamente
3. Aparecerá la ventana principal del sistema

## PASO 3: Configuración Inicial
1. Ir a "Configuración" en el menú principal
2. Configurar el nombre de la parroquia
3. Agregar nichos disponibles desde "Gestión de Nichos"

## PASO 4: Uso del Sistema
1. Crear clientes desde "Ventas"
2. Registrar ventas de nichos
3. Gestionar pagos desde "Pagos"
4. Generar reportes desde "Reportes"

## RESPALDOS IMPORTANTES
- El sistema crea respaldos automáticos
- También puede crear respaldos manuales
- Guardar los respaldos en una ubicación segura
- En caso de problemas, usar "Restaurar desde Respaldo"

## SOLUCIÓN DE PROBLEMAS

### El programa no inicia:
- Verificar que todos los archivos estén en la misma carpeta
- Ejecutar como administrador
- Verificar que no haya antivirus bloqueando el archivo

### Error de base de datos:
- Verificar permisos de escritura en la carpeta
- Restaurar desde un respaldo reciente

### Problemas de impresión:
- Verificar que la impresora esté configurada
- Intentar imprimir desde otro programa para verificar funcionamiento

## CONTACTO
Para soporte adicional, contactar al administrador del sistema.
"""
        
        with open(f"{package_dir}/INSTALACION.txt", 'w', encoding='utf-8') as f:
            f.write(install_guide)

if __name__ == "__main__":
    from datetime import datetime
    
    builder = ExecutableBuilder()
    
    print("=== Constructor de Ejecutable - Sistema de Criptas ===")
    print(f"Versión: {builder.version}")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print()
    
    # Verificar que el archivo principal existe
    if not os.path.exists(builder.main_script):
        print(f"Error: No se encuentra el archivo {builder.main_script}")
        sys.exit(1)
    
    # Construir ejecutable
    builder.build_executable()
    
    print("¡Construcción completada!")
    print("El ejecutable está listo para distribuir.")