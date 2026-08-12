; Inno Setup betiği — Sözleşme Portföy Paneli kurulum sihirbazı
; Derleme: ISCC.exe installer\installer.iss   (kur_olustur.bat bunu otomatik yapar)
; Önce PyInstaller çıktısı hazır olmalı:  dist\SozlesmePortfoyPaneli\
;
; Yönetici yetkisi GEREKTİRMEZ (kullanıcı bazlı kurulum).

#define MyAppName "Sözleşme Portföy Paneli"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sözleşme Portföy Paneli"
#define MyAppExeName "SozlesmePortfoyPaneli.exe"

[Setup]
; Kararlı, benzersiz uygulama kimliği (güncellemelerin üst üste kurulması için)
AppId={{7A1E9C3C-58B2-4E4E-9E2B-5B0C2D6F9A10}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\SozlesmePortfoyPaneli
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; Yönetici yetkisi istemeden, kullanıcı profiline kur
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=Output
OutputBaseFilename=SozlesmePortfoyPaneli_Setup
SetupIconFile=..\assets\app.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
WizardStyle=modern
Compression=lzma2/max
SolidCompression=yes

[Languages]
Name: "tr"; MessagesFile: "compiler:Languages\Turkish.isl"
Name: "en"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
; PyInstaller onedir çıktısının TAMAMI (exe dahil)
Source: "..\dist\SozlesmePortfoyPaneli\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Örnek Excel'i de kur (kullanıcı deneyebilsin)
Source: "..\sample\ornek_veri.xlsx"; DestDir: "{app}\ornek"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
