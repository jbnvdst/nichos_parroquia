; Script de Inno Setup para Sistema de Administración de Criptas
; Este script crea un instalador profesional para Windows
; Requiere Inno Setup 6.0 o superior

#define MyAppName "Sistema de Administración de Criptas"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Parroquia Nuestra Señora del Consuelo de los Afligidos"
#define MyAppURL "https://github.com/jbnvdst/nichos_parroquia"
#define MyAppExeName "SistemaCriptas.exe"
#define MyAppAssocName MyAppName + " File"
#define MyAppAssocExt ".cripta"
#define MyAppAssocKey StringChange(MyAppAssocName, " ", "") + MyAppAssocExt

[Setup]
; NOTA: El valor de AppId identifica únicamente esta aplicación.
; No uses el mismo valor de AppId en otros instaladores.
; (Para generar un nuevo GUID, haz clic en Tools|Generate GUID en el IDE de Inno Setup.)
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}/issues
AppUpdatesURL={#MyAppURL}/releases
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
; Quitar el siguiente comentario para ejecutar en modo no administrativo (instalar solo para el usuario actual)
;PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=dist\installer
OutputBaseFilename=SistemaCriptas_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
; Habilitar soporte para 64-bit
ArchitecturesInstallIn64BitMode=x64compatible
; Licencia y documentación
LicenseFile=LICENSE.txt
InfoBeforeFile=README.txt

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Ejecutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; NOTA: No uses "Flags: ignoreversion" en archivos del sistema compartidos

; Directorios de la aplicación
Source: "dist\database\*"; DestDir: "{app}\database"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\ui\*"; DestDir: "{app}\ui"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\reports\*"; DestDir: "{app}\reports"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "dist\backup\*"; DestDir: "{app}\backup"; Flags: ignoreversion recursesubdirs createallsubdirs

; Archivos de assets (iconos, imágenes, etc.)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentación
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme
Source: "LICENSE.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALACION.txt"; DestDir: "{app}"; Flags: ignoreversion

[Dirs]
; Crear directorios para archivos generados por la aplicación
Name: "{app}\reportes"; Permissions: users-full
Name: "{app}\recibos"; Permissions: users-full
Name: "{app}\titulos"; Permissions: users-full
Name: "{app}\backups"; Permissions: users-full
Name: "{app}\database"; Permissions: users-full

; Directorio en AppData para base de datos del usuario
Name: "{userappdata}\{#MyAppName}"; Permissions: users-full
Name: "{userappdata}\{#MyAppName}\backups"; Permissions: users-full

[Icons]
; Iconos del menú inicio
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Manual de Usuario"; Filename: "{app}\README.txt"
Name: "{group}\Guía de Instalación"; Filename: "{app}\INSTALACION.txt"
Name: "{group}\Carpeta de Respaldos"; Filename: "{userappdata}\{#MyAppName}\backups"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Iconos del escritorio
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

; Iconos de inicio rápido
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
var
  DataDirPage: TInputDirWizardPage;

procedure InitializeWizard;
begin
  // Crear página personalizada para seleccionar directorio de datos
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Seleccionar Carpeta de Datos', 'Donde se guardarán los archivos de la base de datos y respaldos?',
    'Selecciona la carpeta donde se guardarán los datos de la aplicación. ' +
    'Se recomienda una ubicación con suficiente espacio y que se respalde regularmente.' +
    #13#10#13#10 +
    'Haz clic en Siguiente para continuar o en Examinar para seleccionar otra carpeta.',
    False, '');

  // Valor predeterminado
  DataDirPage.Add('');
  DataDirPage.Values[0] := ExpandConstant('{userappdata}\{#MyAppName}');
end;

function GetDataDir(Param: String): String;
begin
  // Devolver la carpeta de datos seleccionada
  Result := DataDirPage.Values[0];
end;

// Verificar si se necesita reiniciar el sistema después de la instalación
function NeedRestart(): Boolean;
begin
  Result := False;
end;

// Código para verificar si la aplicación está ejecutándose
function IsAppRunning(): Boolean;
var
  WbemLocator, WbemServices: Variant;
  WbemObjectSet: Variant;
begin
  Result := False;
  try
    WbemLocator := CreateOleObject('WbemScripting.SWbemLocator');
    WbemServices := WbemLocator.ConnectServer('', 'root\CIMV2');
    WbemObjectSet := WbemServices.ExecQuery('SELECT * FROM Win32_Process WHERE Name="' + '{#MyAppExeName}' + '"');
    Result := (WbemObjectSet.Count > 0);
  except
    Result := False;
  end;
end;

function InitializeSetup(): Boolean;
begin
  // Verificar si la aplicación está ejecutándose antes de instalar
  if IsAppRunning() then
  begin
    MsgBox('El Sistema de Criptas está actualmente ejecutándose.' + #13#10#13#10 +
           'Por favor, cierra la aplicación antes de continuar con la instalación.',
           mbError, MB_OK);
    Result := False;
  end
  else
    Result := True;
end;

// Crear archivo de configuración con la ruta de datos
procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigFile: String;
  ConfigContent: TStringList;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigFile := ExpandConstant('{app}\config.ini');
    ConfigContent := TStringList.Create;
    try
      ConfigContent.Add('[Paths]');
      ConfigContent.Add('DataDir=' + GetDataDir(''));
      ConfigContent.Add('BackupDir=' + GetDataDir('') + '\backups');
      ConfigContent.Add('ReportsDir=' + GetDataDir('') + '\reportes');
      ConfigContent.Add('');
      ConfigContent.Add('[Application]');
      ConfigContent.Add('Version={#MyAppVersion}');
      ConfigContent.Add('CheckUpdatesOnStartup=true');
      ConfigContent.Add('AutoBackup=true');
      ConfigContent.SaveToFile(ConfigFile);
    finally
      ConfigContent.Free;
    end;
  end;
end;

[UninstallDelete]
; Opcional: Descomentar para eliminar archivos de configuración al desinstalar
; Type: filesandordirs; Name: "{app}\config.ini"
; Type: filesandordirs; Name: "{app}\*.db"

[Registry]
; Asociar extensión de archivo .cripta con la aplicación (opcional)
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocExt}\OpenWithProgids"; ValueType: string; ValueName: "{#MyAppAssocKey}"; ValueData: ""; Flags: uninsdeletevalue
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}"; ValueType: string; ValueName: ""; ValueData: "{#MyAppAssocName}"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\{#MyAppExeName},0"
Root: HKA; Subkey: "Software\Classes\{#MyAppAssocKey}\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
Root: HKA; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".cripta"; ValueData: ""

[Messages]
; Mensajes personalizados en español
spanish.WelcomeLabel2=Este programa instalará [name/ver] en su computadora.%n%nSe recomienda cerrar todas las demás aplicaciones antes de continuar.
spanish.FinishedHeadingLabel=Completando el Asistente de Instalación de [name]
spanish.FinishedLabelNoIcons=La instalación de [name] se completó exitosamente.
spanish.FinishedLabel=La instalación de [name] se completó exitosamente. La aplicación puede iniciarse desde los iconos instalados.
