#define AppName "AI Gatterka Szabadkez"
[Setup]
AppId={{A8D5CA4B-3A1F-4A80-A40D-F3F79F9DB1E3}
AppName={#AppName}
AppVersion=0.1
DefaultDirName={autopf}\AI Gatterka Szabadkez
DefaultGroupName={#AppName}
OutputDir=dist
OutputBaseFilename=AI_Gatterka_Szabadkez_Telepito_0.1
Compression=lzma
SolidCompression=yes
WizardStyle=modern
[Files]
Source: "dist\AI_Gatterka_Szabadkez.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\AI Gatterka Szabadkez"; Filename: "{app}\AI_Gatterka_Szabadkez.exe"
[Run]
Filename: "{app}\AI_Gatterka_Szabadkez.exe"; Flags: nowait postinstall skipifsilent
