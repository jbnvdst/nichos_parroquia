#!/usr/bin/env python3
# create_installer.py
# Script automatizado para crear el instalador completo de Windows

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

class InstallerCreator:
    def __init__(self):
        self.app_name = "SistemaCriptas"
        self.version = "1.0.0"
        self.inno_setup_path = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

    def check_requirements(self):
        """Verificar que todas las herramientas necesarias estén instaladas"""
        print("=== Verificando requisitos ===\n")

        # Verificar Python
        print(f"✓ Python {sys.version.split()[0]} encontrado")

        # Verificar PyInstaller
        try:
            import PyInstaller
            print(f"✓ PyInstaller encontrado")
        except ImportError:
            print("✗ PyInstaller no encontrado. Instalando...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✓ PyInstaller instalado")

        # Verificar Inno Setup (opcional)
        if os.path.exists(self.inno_setup_path):
            print(f"✓ Inno Setup encontrado en {self.inno_setup_path}")
            return True
        else:
            print(f"⚠ Inno Setup no encontrado en {self.inno_setup_path}")
            print("  Puedes descargarlo de: https://jrsoftware.org/isdl.php")
            print("  O especificar la ruta manualmente")
            return False

    def build_executable(self):
        """Construir el ejecutable usando PyInstaller"""
        print("\n=== Paso 1: Construyendo ejecutable con PyInstaller ===\n")

        # Importar el builder existente
        from build_executable import ExecutableBuilder

        builder = ExecutableBuilder()
        builder.build_executable()

        print("\n✓ Ejecutable creado exitosamente")

    def prepare_installer_files(self):
        """Preparar archivos necesarios para el instalador"""
        print("\n=== Paso 2: Preparando archivos del instalador ===\n")

        # Crear README.txt si no existe
        if not os.path.exists("README.txt"):
            readme_content = f"""
Sistema de Administración de Criptas - v{self.version}

DESCRIPCIÓN:
Sistema completo para la administración de criptas en parroquias.

CARACTERÍSTICAS:
- Gestión de nichos disponibles
- Registro de ventas (contado/crédito)
- Control de pagos y abonos
- Generación de recibos e impresión
- Títulos de propiedad
- Reportes exportables
- Búsqueda avanzada
- Respaldos automáticos

REQUISITOS DEL SISTEMA:
- Windows 10 o superior
- Mínimo 4GB de RAM
- 500MB de espacio libre en disco
- Impresora (opcional, para generar recibos y títulos)

SOPORTE:
Para soporte técnico o reportar problemas, contactar al administrador.

Versión {self.version} - {datetime.now().strftime('%B %Y')}
"""
            with open("README.txt", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print("✓ README.txt creado")

        # Crear INSTALACION.txt si no existe
        if not os.path.exists("INSTALACION.txt"):
            install_content = """
GUÍA DE INSTALACIÓN - Sistema de Criptas

INSTALACIÓN:
1. Ejecute el instalador SistemaCriptas_Setup_v1.0.0.exe
2. Siga las instrucciones del asistente de instalación
3. Elija el directorio de instalación (recomendado: dejar por defecto)
4. Opcionalmente, cree accesos directos en el escritorio

PRIMERA EJECUCIÓN:
1. Ejecute el Sistema de Criptas desde el acceso directo
2. El sistema creará automáticamente la base de datos
3. Configure el nombre de la parroquia en Configuración
4. Agregue nichos disponibles desde Gestión de Nichos

USO DEL SISTEMA:
1. Crear clientes desde "Ventas"
2. Registrar ventas de nichos
3. Gestionar pagos desde "Pagos"
4. Generar reportes desde "Reportes"
5. Crear respaldos desde "Respaldos"

RESPALDOS:
- El sistema crea respaldos automáticos semanales
- También puede crear respaldos manuales cuando lo necesite
- Los respaldos se guardan en la carpeta "backups"
- Guarde copias en ubicaciones seguras

SOLUCIÓN DE PROBLEMAS:

El programa no inicia:
- Verifique que todos los archivos estén instalados
- Ejecute como administrador
- Verifique que no haya antivirus bloqueando

Error de base de datos:
- Verifique permisos de escritura
- Restaure desde un respaldo reciente

Problemas de impresión:
- Configure correctamente su impresora
- Verifique drivers actualizados

CONTACTO:
Para soporte adicional, contactar al administrador del sistema.
"""
            with open("INSTALACION.txt", 'w', encoding='utf-8') as f:
                f.write(install_content)
            print("✓ INSTALACION.txt creado")

        # Crear LICENSE.txt si no existe
        if not os.path.exists("LICENSE.txt"):
            license_content = f"""
LICENCIA DE USO - Sistema de Administración de Criptas

Copyright (c) {datetime.now().year} Parroquia Nuestra Señora del Consuelo de los Afligidos

Este software es proporcionado "tal cual", sin garantía de ningún tipo,
expresa o implícita, incluyendo pero no limitado a garantías de
comercialización, idoneidad para un propósito particular y no infracción.

En ningún caso los autores o titulares del Copyright serán responsables
de ningún reclamo, daños u otras responsabilidades, ya sea en una acción
de contrato, agravio o cualquier otro motivo, que surja de o en conexión
con el software o el uso u otros tratos en el software.

PERMISOS:
- Uso interno en la parroquia
- Modificación para necesidades específicas
- Distribución con permiso explícito

RESTRICCIONES:
- No se permite uso comercial
- No se permite redistribución sin autorización
- Se debe mantener este aviso de copyright

Versión {self.version}
"""
            with open("LICENSE.txt", 'w', encoding='utf-8') as f:
                f.write(license_content)
            print("✓ LICENSE.txt creado")

        print("\n✓ Archivos preparados")

    def create_installer(self):
        """Crear el instalador con Inno Setup"""
        print("\n=== Paso 3: Creando instalador con Inno Setup ===\n")

        if not os.path.exists(self.inno_setup_path):
            print("✗ Inno Setup no encontrado")
            print(f"  Buscado en: {self.inno_setup_path}")
            print("\nPara crear el instalador manualmente:")
            print("1. Descarga Inno Setup de: https://jrsoftware.org/isdl.php")
            print("2. Instala Inno Setup")
            print("3. Abre installer_config.iss con Inno Setup")
            print("4. Presiona F9 o click en 'Compile'")
            return False

        # Compilar el instalador
        try:
            cmd = [self.inno_setup_path, "installer_config.iss"]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✓ Instalador creado exitosamente")
            print(f"✓ Ubicación: installer_output\\SistemaCriptas_Setup_v{self.version}.exe")
            return True
        except subprocess.CalledProcessError as e:
            print(f"✗ Error al crear el instalador: {e}")
            print(f"Salida: {e.stdout}")
            print(f"Error: {e.stderr}")
            return False

    def create_portable_version(self):
        """Crear versión portable (ZIP)"""
        print("\n=== Paso 4: Creando versión portable ===\n")

        portable_dir = f"SistemaCriptas_Portable_v{self.version}"

        if os.path.exists(portable_dir):
            shutil.rmtree(portable_dir)

        os.makedirs(portable_dir, exist_ok=True)

        # Copiar ejecutable
        exe_path = f"dist\\{self.app_name}.exe"
        if os.path.exists(exe_path):
            shutil.copy2(exe_path, portable_dir)
            print(f"✓ Ejecutable copiado")

        # Copiar archivos de documentación
        for file in ["README.txt", "INSTALACION.txt", "LICENSE.txt"]:
            if os.path.exists(file):
                shutil.copy2(file, portable_dir)

        # Crear directorios necesarios
        for dir_name in ["database", "reportes", "recibos", "titulos", "backups"]:
            os.makedirs(f"{portable_dir}\\{dir_name}", exist_ok=True)

        # Crear archivo ZIP
        try:
            shutil.make_archive(portable_dir, 'zip', portable_dir)
            print(f"✓ Versión portable creada: {portable_dir}.zip")
        except Exception as e:
            print(f"✗ Error al crear ZIP: {e}")

        print("\n✓ Versión portable lista")

    def run(self):
        """Ejecutar todo el proceso"""
        print("╔════════════════════════════════════════════════════════╗")
        print("║   CREADOR DE INSTALADOR - Sistema de Criptas          ║")
        print(f"║   Versión: {self.version:<43} ║")
        print(f"║   Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M'):<45} ║")
        print("╚════════════════════════════════════════════════════════╝\n")

        # Verificar requisitos
        has_inno_setup = self.check_requirements()

        # Construir ejecutable
        try:
            self.build_executable()
        except Exception as e:
            print(f"\n✗ Error al construir ejecutable: {e}")
            return

        # Preparar archivos
        self.prepare_installer_files()

        # Crear instalador si Inno Setup está disponible
        if has_inno_setup:
            installer_created = self.create_installer()
        else:
            print("\n⚠ Saltando creación de instalador (Inno Setup no encontrado)")
            installer_created = False

        # Crear versión portable
        self.create_portable_version()

        # Resumen final
        print("\n" + "="*60)
        print("RESUMEN DE CONSTRUCCIÓN")
        print("="*60)
        print(f"✓ Ejecutable: dist\\{self.app_name}.exe")
        if installer_created:
            print(f"✓ Instalador: installer_output\\SistemaCriptas_Setup_v{self.version}.exe")
        print(f"✓ Portable: SistemaCriptas_Portable_v{self.version}.zip")
        print("\n¡Proceso completado exitosamente!")
        print("\nPara distribuir:")
        if installer_created:
            print("1. Usa el instalador .exe para instalación tradicional")
        print("2. Usa el .zip para versión portable (sin instalación)")

if __name__ == "__main__":
    creator = InstallerCreator()
    creator.run()
