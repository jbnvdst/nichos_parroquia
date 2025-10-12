# Guía para Crear el Instalador de Windows

Esta guía te ayudará a crear un instalador profesional de Windows para el Sistema de Criptas.

## 📋 Requisitos Previos

### 1. Python y Dependencias
```bash
# Instalar PyInstaller si no lo tienes
pip install pyinstaller

# Instalar todas las dependencias del proyecto
pip install -r requirements.txt
```

### 2. Inno Setup (Opcional, para crear instalador .exe)
- Descargar de: https://jrsoftware.org/isdl.php
- Instalar en la ruta por defecto: `C:\Program Files (x86)\Inno Setup 6\`
- Si lo instalas en otra ubicación, actualiza la ruta en `create_installer.py`

## 🚀 Métodos de Creación

### Método 1: Script Automatizado (Recomendado)

Este método crea todo automáticamente: ejecutable, instalador y versión portable.

```bash
python create_installer.py
```

**Resultado:**
- ✅ `dist/SistemaCriptas.exe` - Ejecutable standalone
- ✅ `installer_output/SistemaCriptas_Setup_v1.0.0.exe` - Instalador completo
- ✅ `SistemaCriptas_Portable_v1.0.0.zip` - Versión portable

### Método 2: Solo Ejecutable

Si solo necesitas el .exe sin instalador:

```bash
python build_executable.py
```

**Resultado:**
- ✅ `dist/SistemaCriptas.exe` - Ejecutable listo para usar

### Método 3: Manual con PyInstaller

Si prefieres usar PyInstaller directamente:

```bash
# Primero, crear el archivo .spec
python -c "from build_executable import ExecutableBuilder; builder = ExecutableBuilder(); builder.create_spec_file()"

# Luego, construir con PyInstaller
pyinstaller --clean --noconfirm SistemaCriptas.spec
```

### Método 4: Solo Instalador (si ya tienes el .exe)

Si ya tienes el ejecutable y solo quieres crear el instalador:

1. Asegúrate de tener `dist/SistemaCriptas.exe`
2. Abre `installer_config.iss` con Inno Setup
3. Presiona **F9** o click en **Build → Compile**

## 📁 Estructura de Archivos Generados

```
nichos_parroquia/
├── dist/
│   └── SistemaCriptas.exe              # Ejecutable principal
├── installer_output/
│   └── SistemaCriptas_Setup_v1.0.0.exe # Instalador completo
├── SistemaCriptas_Portable_v1.0.0.zip  # Versión portable
├── build/                              # Archivos temporales de compilación
└── SistemaCriptas.spec                 # Configuración de PyInstaller
```

## 🔧 Personalización

### Cambiar Versión

Edita en `create_installer.py` y `build_executable.py`:
```python
self.version = "1.0.0"  # Cambiar a tu versión
```

También actualiza en `installer_config.iss`:
```ini
#define MyAppVersion "1.0.0"
```

### Cambiar Icono

1. Coloca tu icono (.ico) en `assets/icon.ico`
2. El script lo usará automáticamente
3. Si está en otra ubicación, actualiza `self.icon_path` en `build_executable.py`

### Agregar Archivos al Instalador

Edita `installer_config.iss`, sección `[Files]`:
```ini
Source: "mi_archivo.txt"; DestDir: "{app}"; Flags: ignoreversion
```

### Modificar Información de Versión

Edita el método `create_version_file()` en `build_executable.py`:
```python
StringStruct(u'CompanyName', u'Tu Empresa'),
StringStruct(u'FileDescription', u'Tu Descripción'),
```

## 🐛 Solución de Problemas

### Error: "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### Error: "Inno Setup no encontrado"
- Instala Inno Setup desde: https://jrsoftware.org/isdl.php
- O actualiza la ruta en `create_installer.py`:
```python
self.inno_setup_path = r"C:\ruta\a\tu\ISCC.exe"
```

### Error: "No se puede importar módulo X"
Agrega el módulo a `hiddenimports` en `build_executable.py`:
```python
hiddenimports=[
    'sqlalchemy.dialects.sqlite',
    'tu_modulo_faltante',  # <-- Agregar aquí
    ...
]
```

### El ejecutable no inicia
1. Prueba con `console=True` en el archivo .spec para ver errores
2. Verifica que todas las dependencias estén en `requirements.txt`
3. Revisa los `hiddenimports` en el archivo .spec

### Ejecutable muy grande
- Desactiva UPX si causa problemas: `upx=False` en el .spec
- Usa `--exclude-module` para módulos innecesarios

## 📦 Distribución

### Para usuarios finales:

**Opción 1: Instalador (Recomendado)**
- Distribuye: `SistemaCriptas_Setup_v1.0.0.exe`
- El usuario hace doble click y sigue el asistente
- Se crea automáticamente acceso directo en el escritorio

**Opción 2: Versión Portable**
- Distribuye: `SistemaCriptas_Portable_v1.0.0.zip`
- El usuario descomprime y ejecuta `SistemaCriptas.exe`
- No requiere instalación

### Para desarrolladores:

1. **Código fuente:**
```bash
git clone https://github.com/tuusuario/nichos_parroquia.git
cd nichos_parroquia
pip install -r requirements.txt
python main.py
```

2. **Crear ejecutable:**
```bash
python create_installer.py
```

## 🔐 Firma Digital (Opcional)

Para firmar el ejecutable e instalador:

1. Obtén un certificado de firma de código
2. Usa `signtool` de Windows SDK:
```bash
signtool sign /f "certificado.pfx" /p "password" /t "http://timestamp.digicert.com" dist\SistemaCriptas.exe
```

3. Para el instalador, agrega en `installer_config.iss`:
```ini
[Setup]
SignTool=signtool
SignedUninstaller=yes
```

## 📊 Comparación de Métodos

| Método | Velocidad | Flexibilidad | Resultado |
|--------|-----------|--------------|-----------|
| Script Automatizado | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Instalador + Portable + EXE |
| Solo Ejecutable | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Solo EXE |
| Manual PyInstaller | ⭐⭐ | ⭐⭐⭐⭐⭐ | Solo EXE |
| Solo Instalador | ⭐⭐⭐ | ⭐⭐ | Solo Instalador |

## 🎯 Comandos Rápidos

```bash
# Todo en uno (recomendado)
python create_installer.py

# Solo ejecutable
python build_executable.py

# Limpiar archivos temporales
rmdir /s /q build dist __pycache__

# Instalar dependencias
pip install -r requirements.txt

# Verificar ejecutable
dist\SistemaCriptas.exe
```

## 📝 Checklist de Pre-lanzamiento

- [ ] Todas las dependencias en `requirements.txt`
- [ ] Versión actualizada en todos los archivos
- [ ] Icono personalizado en `assets/icon.ico`
- [ ] Prueba del ejecutable en computadora limpia
- [ ] Documentación actualizada (README.txt, etc.)
- [ ] LICENSE.txt incluido
- [ ] Prueba de instalación completa
- [ ] Prueba de desinstalación
- [ ] Verificar que se crean todas las carpetas necesarias
- [ ] Probar respaldos y restauración

## 🆘 Soporte

Si encuentras problemas:

1. Revisa esta guía
2. Verifica los logs en la carpeta `build/`
3. Consulta la documentación de PyInstaller: https://pyinstaller.org/
4. Consulta la documentación de Inno Setup: https://jrsoftware.org/ishelp/

---

**¡Listo!** Ahora puedes distribuir tu aplicación profesionalmente. 🎉
