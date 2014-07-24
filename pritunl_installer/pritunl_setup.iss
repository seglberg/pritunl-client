#define MyAppName "Pritunl"
#define MyAppVersion "0.10.1"
#define MyAppPublisher "Pritunl"
#define MyAppURL "http://pritunl.com/"
#define MyAppExeName "pritunl_client.exe"

[Setup]
AppId={{80EC2557-82C8-4ECB-9E02-B7DB1B8F6BC7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
PrivilegesRequired=admin
DisableProgramGroupPage=yes
OutputDir=.\
OutputBaseFilename=pritunl_client-setup
SetupIconFile=logo.ico
Compression=lzma
SolidCompression=yes
CloseApplications=yes
CloseApplicationsFilter=*.exe,*.dll,*.chm

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\pritunl_client\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Flags: nowait

[UninstallRun]
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "taskkill.exe"; Parameters: "/F /IM {#MyAppExeName}"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "timeout.exe"; Parameters: "/t 3"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "taskkill.exe"; Parameters: "/F /IM openvpn.exe"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "taskkill.exe"; Parameters: "/F /IM openvpn.exe"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "taskkill.exe"; Parameters: "/F /IM openvpn.exe"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "timeout.exe"; Parameters: "/t 3"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "{app}\pritunl_client_clean.exe"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "timeout.exe"; Parameters: "/t 1"; Flags: runascurrentuser runhidden skipifdoesntexist
Filename: "cmd.exe"; Parameters: "/C ""del """"{app}/MPR.dll"""""""; Flags: runascurrentuser runhidden skipifdoesntexist

[UninstallDelete]
Type: filesandordirs; Name: "{app}"
