; Script de Inno Setup para Sistema de Criptas
; Este script crea un instalador profesional para Windows

#define MyAppName "Sistema de Criptas"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Parroquia Nuestra Señora del Consuelo de los Afligidos"
#define MyAppExeName "SistemaCriptas.exe"
#define MyAppURL "https://github.com/tuusuario/nichos_parroquia"

[Setup]
; Información básica
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=LICENSE.txt
InfoBeforeFile=INSTALACION.txt
OutputDir=installer_output
OutputBaseFilename=SistemaCriptas_Setup_v{#MyAppVersion}
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Ejecutable principal
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; Crear directorios necesarios
Source: "README.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "INSTALACION.txt"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
; Crear directorios que la aplicación necesita
Name: "{app}\database"; Permissions: users-full
Name: "{app}\reportes"; Permissions: users-full
Name: "{app}\recibos"; Permissions: users-full
Name: "{app}\titulos"; Permissions: users-full
Name: "{app}\backups"; Permissions: users-full

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
// Código Pascal para funciones personalizadas
function InitializeSetup(): Boolean;
begin
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // Aquí puedes agregar acciones post-instalación
  end;
end;

[UninstallDelete]
Type: filesandordirs; Name: "{app}\database"
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\*.log"

[Messages]
spanish.WelcomeLabel2=Este instalador instalará [name/ver] en su computadora.%n%nSe recomienda cerrar todas las aplicaciones antes de continuar.
spanish.FinishedLabel=La instalación de [name] ha finalizado exitosamente.%n%nPuede ejecutar la aplicación desde el acceso directo en el escritorio o desde el menú de inicio.
