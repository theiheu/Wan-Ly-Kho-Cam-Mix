; Professional Inno Setup Installer for Chicken Farm Manager
; Modern wizard with complete Windows integration

#define AppName "Phần mềm Quản lý Cám - Trại Gà"
#define AppNameShort "ChickenFarmManager"
#define AppVersion "2.0.0"
#define AppPublisher "Minh-Tan_Phat"
#define AppURL "https://github.com/Minh-Tan_Phat"
#define AppDescription "Professional Chicken Farm Management System"
#define AppCopyright "© 2025 Minh-Tan_Phat. All rights reserved."
#define AppExeName "ChickenFarmManager.exe"

[Setup]
; Application Information
AppId={{8B5F4B2A-9C3D-4E5F-8A7B-1C2D3E4F5A6B}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
AppCopyright={#AppCopyright}
VersionInfoVersion={#AppVersion}
VersionInfoCompany={#AppPublisher}
VersionInfoDescription={#AppDescription}
VersionInfoCopyright={#AppCopyright}

; Installation Settings
DefaultDirName={autopf}\{#AppNameShort}
DefaultGroupName={#AppName}
AllowNoIcons=yes
LicenseFile=..\resources\license.txt
InfoBeforeFile=..\resources\readme.txt
OutputDir=..\output
OutputBaseFilename={#AppNameShort}_Setup
SetupIconFile=..\resources\app_icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; System Requirements
MinVersion=10.0
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

; Visual Settings
DisableProgramGroupPage=no
DisableReadyPage=no
DisableFinishedPage=no
DisableWelcomePage=no
ShowLanguageDialog=no
WizardImageFile=..\resources\welcome_image.bmp
WizardSmallImageFile=..\resources\header_image.bmp

; Uninstall Settings
UninstallDisplayIcon={app}\{#AppExeName}
UninstallDisplayName={#AppName}
CreateUninstallRegKey=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1

[Files]
Source: "..\output\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\output\*.dll"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"
Name: "{group}\{cm:ProgramOnTheWeb,{#AppName}}"; Filename: "{#AppURL}"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#AppName}"; Filename: "{app}\{#AppExeName}"; Tasks: quicklaunchicon

[Registry]
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppNameShort}"; ValueType: string; ValueName: "InstallPath"; ValueData: "{app}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppNameShort}"; ValueType: string; ValueName: "Version"; ValueData: "{#AppVersion}"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\{#AppPublisher}\{#AppNameShort}"; ValueType: string; ValueName: "Publisher"; ValueData: "{#AppPublisher}"; Flags: uninsdeletekey

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(AppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{localappdata}\{#AppNameShort}"
Type: filesandordirs; Name: "{userappdata}\{#AppNameShort}"

[Code]
var
  DataDirPage: TInputDirWizardPage;

function InitializeSetup(): Boolean;
var
  Version: TWindowsVersion;
begin
  GetWindowsVersionEx(Version);

  // Check Windows 10 or later
  if Version.Major < 10 then
  begin
    MsgBox('Phần mềm này yêu cầu Windows 10 hoặc mới hơn.', mbError, MB_OK);
    Result := False;
    Exit;
  end;

  // Check if application is running
  if CheckForMutexes('{#AppNameShort}Mutex') then
  begin
    if MsgBox('{#AppName} đang chạy. Vui lòng đóng ứng dụng trước khi tiếp tục cài đặt.',
              mbConfirmation, MB_OKCANCEL) = IDCANCEL then
    begin
      Result := False;
      Exit;
    end;
  end;

  Result := True;
end;

procedure InitializeWizard();
begin
  // Create custom page for data directory selection
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Chọn thư mục dữ liệu', 'Chọn nơi lưu trữ dữ liệu ứng dụng',
    'Chọn thư mục để lưu trữ dữ liệu, cài đặt và báo cáo của ứng dụng, sau đó nhấn Tiếp tục.',
    False, '');
  DataDirPage.Add('Thư mục dữ liệu:');
  DataDirPage.Values[0] := ExpandConstant('{localappdata}\{#AppNameShort}');
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  if CurPageID = DataDirPage.ID then
  begin
    if not DirExists(DataDirPage.Values[0]) then
    begin
      if not CreateDir(DataDirPage.Values[0]) then
      begin
        MsgBox('Không thể tạo thư mục dữ liệu. Vui lòng chọn thư mục khác.', mbError, MB_OK);
        Result := False;
        Exit;
      end;
    end;
  end;
  Result := True;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Create data directory
    CreateDir(DataDirPage.Values[0]);

    // Set permissions for data directory
    Exec('icacls', '"' + DataDirPage.Values[0] + '" /grant Users:(OI)(CI)F', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Create registry entry for data directory
    RegWriteStringValue(HKLM, 'Software\{#AppPublisher}\{#AppNameShort}', 'DataPath', DataDirPage.Values[0]);
  end;
end;

function PrepareToInstall(var NeedsRestart: Boolean): String;
var
  ResultCode: Integer;
begin
  // Stop the application if running
  Exec('taskkill', '/F /IM "{#AppExeName}"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  Result := '';
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  DataPath: String;
  ResultCode: Integer;
begin
  if CurUninstallStep = usUninstall then
  begin
    // Stop the application
    Exec('taskkill', '/F /IM "{#AppExeName}"', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

    // Ask about user data
    if RegQueryStringValue(HKLM, 'Software\{#AppPublisher}\{#AppNameShort}', 'DataPath', DataPath) then
    begin
      if MsgBox('Bạn có muốn xóa dữ liệu người dùng không?' + #13#10 +
                '(Bao gồm cài đặt, báo cáo và dữ liệu đã lưu)' + #13#10#13#10 +
                'Thư mục: ' + DataPath, mbConfirmation, MB_YESNO) = IDYES then
      begin
        DelTree(DataPath, True, True, True);
      end;
    end;
  end;
end;
