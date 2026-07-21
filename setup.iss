[Setup]
AppName=R Medical Laboratory
AppVersion=2.0
PrivilegesRequired=admin
DefaultDirName={sd}\RLab
DefaultGroupName=R Lab
OutputBaseFilename=RLabSetup_v2.0
OutputDir=F:\Mahmoud\Projects\WEP\Lap_System\Demo_Lap_System_ToGit\Lap_System\dist
Compression=lzma
SolidCompression=yes
SetupIconFile=F:\Mahmoud\Projects\WEP\Lap_System\Demo_Lap_System_ToGit\Lap_System\AppIcon.ico

[Files]
Source: "F:\Mahmoud\Projects\WEP\Lap_System\Demo_Lap_System_ToGit\Lap_System\dist\RLab.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\R Medical Laboratory"; Filename: "{app}\RLab.exe"
Name: "{group}\R Medical Laboratory"; Filename: "{app}\RLab.exe"

[Run]
Filename: "{app}\RLab.exe"; Description: "تشغيل البرنامج"; Flags: nowait postinstall skipifsilent