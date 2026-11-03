; Inno Setup definition for the per-user Windows installer. The build script or
; GitHub Actions supplies MyAppVersion; local builds fall back to 0.0.0.
#ifndef MyAppVersion
  #define MyAppVersion "0.0.0"
#endif

[Setup]
; A stable AppId lets upgrades replace the same installation. PrivilegesRequired
; keeps installation inside the user's profile and avoids an administrator prompt.
AppId={{A6088AB5-D894-47E4-B625-A354B75C7802}
AppName=LEDD Calculator
AppVersion={#MyAppVersion}
AppPublisher=Biomedical Signal Processing
DefaultDirName={code:GetDefaultDir}
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=releases
OutputBaseFilename=LEDD-Calculator-Windows-x64-Setup
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\LEDD Calculator.exe
CloseApplications=yes
RestartApplications=no

[Files]
; Install the complete PyInstaller onedir output, including native libraries.
Source: "dist\LEDD Calculator\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Create a Start menu shortcut and, when selected, an optional desktop shortcut.
Name: "{code:GetStartMenuDir}\LEDD Calculator"; Filename: "{app}\LEDD Calculator.exe"
Name: "{code:GetDesktopDir}\LEDD Calculator"; Filename: "{app}\LEDD Calculator.exe"; Tasks: desktopicon

[Tasks]
; Desktop shortcut creation is deliberately opt-in.
Name: "desktopicon"; Description: "Create a desktop shortcut"; GroupDescription: "Additional shortcuts:"; Flags: unchecked

[Run]
; Offer to launch the calculator after an interactive installation.
Filename: "{app}\LEDD Calculator.exe"; Description: "Launch LEDD Calculator"; Flags: nowait postinstall skipifsilent

[Code]
{ Resolve writable per-user folders explicitly. These fallbacks support managed
  Windows profiles where one or more standard environment variables are absent. }
function GetDefaultDir(Param: String): String;
var
  BaseDir: String;
begin
  { Prefer LocalAppData because the application contains machine-specific files. }
  BaseDir := GetEnv('LOCALAPPDATA');
  if BaseDir = '' then
  begin
    BaseDir := GetEnv('USERPROFILE');
    if BaseDir <> '' then
      BaseDir := AddBackslash(BaseDir) + 'AppData\Local';
  end;
  if BaseDir = '' then
    BaseDir := GetTempDir;
  Result := AddBackslash(BaseDir) + 'Programs\LEDD Calculator';
end;

function GetStartMenuDir(Param: String): String;
var
  BaseDir: String;
begin
  { Start menu shortcuts belong in the user's roaming application data. }
  BaseDir := GetEnv('APPDATA');
  if BaseDir = '' then
  begin
    BaseDir := GetEnv('USERPROFILE');
    if BaseDir <> '' then
      BaseDir := AddBackslash(BaseDir) + 'AppData\Roaming';
  end;
  if BaseDir = '' then
    BaseDir := GetDefaultDir('');
  Result := AddBackslash(BaseDir) + 'Microsoft\Windows\Start Menu\Programs\LEDD Calculator';
end;

function GetDesktopDir(Param: String): String;
var
  BaseDir: String;
begin
  { Fall back to the calculated install location only for unusual profiles. }
  BaseDir := GetEnv('USERPROFILE');
  if BaseDir = '' then
    BaseDir := GetDefaultDir('');
  Result := AddBackslash(BaseDir) + 'Desktop';
end;
