# Instrucciones para Construir el Instalador

Este documento explica cómo construir el instalador del Sistema de Administración de Criptas desde el código fuente.

## Tabla de Contenidos

1. [Requisitos Previos](#requisitos-previos)
2. [Instalación de Herramientas](#instalación-de-herramientas)
3. [Construcción Manual](#construcción-manual)
4. [Construcción Automatizada](#construcción-automatizada)
5. [Creación de Release en GitHub](#creación-de-release-en-github)
6. [Solución de Problemas](#solución-de-problemas)

---

## Requisitos Previos

### Software Necesario

- **Python 3.8 o superior**
- **Git** (para clonar el repositorio)
- **PyInstaller** (se instala automáticamente)
- **Inno Setup 6.0 o superior** (para crear el instalador)

### Dependencias de Python

Todas las dependencias del proyecto deben estar instaladas:

```bash
pip install -r requirements.txt
pip install pyinstaller
```

---

## Instalación de Herramientas

### 1. Instalar Inno Setup

Inno Setup es necesario para crear el instalador de Windows.

**Pasos:**

1. Descarga Inno Setup desde: https://jrsoftware.org/isdl.php
2. Ejecuta el instalador
3. Instala en la ubicación predeterminada: `C:\Program Files (x86)\Inno Setup 6\`
4. Durante la instalación, asegúrate de incluir el compilador de línea de comandos (ISCC.exe)

**Verificación:**

```bash
# Verifica que ISCC.exe esté disponible
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /?
```

### 2. Instalar PyInstaller

```bash
pip install pyinstaller
```

**Verificación:**

```bash
pyinstaller --version
```

### 3. Clonar el Repositorio

```bash
git clone https://github.com/jbnvdst/nichos_parroquia.git
cd nichos_parroquia
```

---

## Construcción Manual

Si prefieres construir paso a paso:

### Paso 1: Construir el Ejecutable

```bash
# Crear archivo .spec
pyi-makespec main.py --name=SistemaCriptas --windowed --icon=assets/icon.ico

# Compilar
pyinstaller --clean --noconfirm SistemaCriptas.spec
```

El ejecutable se creará en: `dist/SistemaCriptas.exe`

### Paso 2: Preparar Archivos de Documentación

Asegúrate de que existan estos archivos en la raíz del proyecto:

- `README.txt`
- `LICENSE.txt`
- `INSTALACION.txt`

### Paso 3: Compilar el Instalador

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

El instalador se creará en: `dist/installer/SistemaCriptas_Setup_v1.0.0.exe`

---

## Construcción Automatizada

Usa el script `build_installer.py` para automatizar todo el proceso:

### Uso Básico

```bash
# Construcción completa (ejecutable + instalador)
python build_installer.py --version 1.0.0
```

### Opciones Avanzadas

```bash
# Solo construir ejecutable (sin instalador)
python build_installer.py --version 1.0.0 --skip-installer

# Especificar versión diferente
python build_installer.py --version 1.2.3

# Ver ayuda
python build_installer.py --help
```

### Proceso Automatizado

El script `build_installer.py` realiza las siguientes acciones:

1. ✅ Verifica requisitos (Python, PyInstaller, Inno Setup)
2. ✅ Limpia directorios de construcción anteriores
3. ✅ Crea archivo de información de versión de Windows
4. ✅ Genera archivo .spec de PyInstaller
5. ✅ Compila el ejecutable con PyInstaller
6. ✅ Prepara archivos de documentación
7. ✅ Compila el instalador con Inno Setup
8. ✅ Genera notas de versión

### Salida Esperada

```
======================================================================
  CONSTRUCCIÓN DE SistemaCriptas v1.0.0
======================================================================

[Paso 1] Verificando requisitos
----------------------------------------------------------------------
✓ Python 3.10.0
✓ PyInstaller instalado
✓ Inno Setup encontrado: C:\Program Files (x86)\Inno Setup 6\ISCC.exe
✓ Archivo principal encontrado: main.py
✓ Script de Inno Setup encontrado

[Paso 2] Limpiando directorios de construcción
----------------------------------------------------------------------
  ✓ dist eliminado
  ✓ build eliminado
✓ Directorios recreados

...

======================================================================
  RESUMEN DE LA COMPILACIÓN
======================================================================
Versión: 1.0.0
Fecha: 19/10/2025 14:30:00

Archivos generados:
  • Ejecutable: dist\SistemaCriptas.exe
    Tamaño: 45.23 MB
  • Instalador: dist\installer\SistemaCriptas_Setup_v1.0.0.exe
    Tamaño: 42.15 MB
```

---

## Creación de Release en GitHub

### Método 1: Interfaz Web de GitHub

1. Ve a tu repositorio en GitHub
2. Haz clic en **"Releases"** → **"Draft a new release"**
3. Crea un nuevo tag: `v1.0.0`
4. Título del release: `Versión 1.0.0`
5. Descripción: Copia el contenido de `Release_Notes_v1.0.0.md`
6. Sube el archivo: `SistemaCriptas_Setup_v1.0.0.exe`
7. Marca como "Latest release"
8. Haz clic en **"Publish release"**

### Método 2: GitHub CLI (Automatizado)

Si tienes instalado GitHub CLI (`gh`):

```bash
# Crear release y subir instalador
gh release create v1.0.0 \
  "dist/installer/SistemaCriptas_Setup_v1.0.0.exe" \
  --title "Versión 1.0.0" \
  --notes-file "dist/installer/Release_Notes_v1.0.0.md"
```

### Método 3: GitHub Actions (Recomendado)

Usa el workflow automatizado que se ejecuta al crear un tag:

```bash
# Crear y subir tag
git tag v1.0.0
git push origin v1.0.0
```

El workflow de GitHub Actions se encargará de:
- Construir el ejecutable
- Crear el instalador
- Publicar el release automáticamente

---

## Actualización del Sistema desde GitHub

El sistema incluye un módulo de actualización automática (`github_updater.py`) que:

1. Verifica si hay nuevas versiones en GitHub Releases
2. Compara la versión actual con la última disponible
3. Descarga e instala actualizaciones automáticamente
4. Muestra notas de la versión antes de actualizar

### Integración en el Código

```python
# En main.py
from github_updater import GitHubUpdater

# Verificar actualizaciones al iniciar
updater = GitHubUpdater(current_version="1.0.0")
updater.check_updates_on_startup(self.root)

# O verificar manualmente (desde menú Ayuda)
has_update, release = updater.check_for_updates(silent=False)
```

---

## Solución de Problemas

### Error: "PyInstaller no encontrado"

**Solución:**
```bash
pip install pyinstaller
```

### Error: "Inno Setup no encontrado"

**Solución:**
1. Instala Inno Setup desde https://jrsoftware.org/isdl.php
2. O especifica la ruta manualmente en `build_installer.py`:
   ```python
   self.inno_compiler = r"C:\ruta\a\ISCC.exe"
   ```

### Error: "No module named 'X'"

**Solución:**
```bash
# Instala todas las dependencias
pip install -r requirements.txt

# O agrega el módulo faltante a hiddenimports en el .spec
hiddenimports=['X', ...]
```

### El ejecutable es muy grande

**Soluciones:**
1. Excluye módulos innecesarios en el archivo .spec:
   ```python
   excludes=['pytest', 'test', 'matplotlib', ...]
   ```

2. Desactiva UPX (puede aumentar tamaño pero mejorar compatibilidad):
   ```python
   upx=False,
   ```

### El instalador no detecta archivos

**Solución:**
Verifica que los directorios existan en el proyecto:
- `database/`
- `ui/`
- `reports/`
- `backup/`
- `assets/`

### Error al ejecutar en otra PC

**Soluciones:**
1. Incluye Microsoft Visual C++ Redistributable:
   - Descarga: https://aka.ms/vs/17/release/vc_redist.x64.exe
   - Agrégalo al instalador de Inno Setup

2. Verifica dependencias en el .spec:
   ```python
   hiddenimports=[
       'tkinter',
       'sqlite3',
       'PIL',
       ...
   ]
   ```

---

## Versionado

Este proyecto usa **Semantic Versioning** (https://semver.org/):

- **MAJOR.MINOR.PATCH** (ej: 1.2.3)
  - **MAJOR**: Cambios incompatibles con versiones anteriores
  - **MINOR**: Nueva funcionalidad compatible con versiones anteriores
  - **PATCH**: Correcciones de bugs

### Actualizar Versión

1. Actualiza el número de versión en:
   - `build_installer.py` (argumento `--version`)
   - `version_info.py`
   - `main.py` (en `GitHubUpdater`)
   - `installer_script.iss` (se actualiza automáticamente)

2. Construye con la nueva versión:
   ```bash
   python build_installer.py --version 1.2.3
   ```

3. Crea el release en GitHub:
   ```bash
   git tag v1.2.3
   git push origin v1.2.3
   ```

---

## Checklist de Release

Antes de publicar una nueva versión:

- [ ] Todas las pruebas pasan
- [ ] Actualizar número de versión en todos los archivos
- [ ] Actualizar CHANGELOG.md o notas de versión
- [ ] Construir instalador con `build_installer.py`
- [ ] Probar instalador en máquina limpia
- [ ] Verificar que la aplicación funciona correctamente
- [ ] Crear tag de git: `git tag v1.0.0`
- [ ] Push del tag: `git push origin v1.0.0`
- [ ] Crear release en GitHub
- [ ] Subir instalador al release
- [ ] Publicar notas de versión

---

## Recursos Adicionales

- **PyInstaller Documentation**: https://pyinstaller.org/en/stable/
- **Inno Setup Documentation**: https://jrsoftware.org/ishelp/
- **GitHub Releases**: https://docs.github.com/en/repositories/releasing-projects-on-github
- **Semantic Versioning**: https://semver.org/

---

## Contacto y Soporte

Para preguntas o problemas con la construcción:

- **Issues**: https://github.com/jbnvdst/nichos_parroquia/issues
- **Discussions**: https://github.com/jbnvdst/nichos_parroquia/discussions

---

**Última actualización**: 19/10/2025
