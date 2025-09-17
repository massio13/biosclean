; Inno Setup Script
[Setup]
AppName=BIOS Scanner Full Extended
AppVersion=0.1.0
DefaultDirName={pf}\BIOS Scanner Full Extended
DisableProgramGroupPage=yes
OutputBaseFilename=bios_scanner_setup
Compression=lzma
SolidCompression=yes

[Files]
Source: "target\release\bios_scanner_full_extended.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "python_gui\dist\gui.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "db\sample_signatures.json"; DestDir: "{app}\db"; Flags: preservepath

[Icons]
Name: "{group}\BIOS Scanner Full Extended"; Filename: "{app}\gui.exe"
Name: "{userdesktop}\BIOS Scanner Full Extended"; Filename: "{app}\gui.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\gui.exe"; Description: "Launch BIOS Scanner"; Flags: nowait postinstall skipifsilent
