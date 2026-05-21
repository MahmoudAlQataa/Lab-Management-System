[Setup]
AppName=R Medical Laboratory
AppVersion=1.0
PrivilegesRequired=admin
DefaultDirName={sd}\RLab
DefaultGroupName=R Lab
OutputBaseFilename=RLabSetup_v2.6
OutputDir=F:\Mahmoud\Projects\WEP\Lap_System\LapApp\dist
Compression=lzma
SolidCompression=yes
SetupIconFile=F:\Mahmoud\Projects\WEP\Lap_System\LapApp\AppIcon.ico

[Files]
Source: "F:\Mahmoud\Projects\WEP\Lap_System\LapApp\dist\RLab.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\R Medical Laboratory"; Filename: "{app}\RLab.exe"
Name: "{group}\R Medical Laboratory"; Filename: "{app}\RLab.exe"

[Run]
Filename: "{app}\RLab.exe"; Description: "تشغيل البرنامج"; Flags: nowait postinstall skipifsilent