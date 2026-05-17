[Setup]
AppName=Nebras Medical Laboratory
AppVersion=1.0
PrivilegesRequired=admin
DefaultDirName={sd}\NebrasLab
DefaultGroupName=Nebras Lab
OutputBaseFilename=NebrasLabSetup_v2.6
OutputDir=F:\Mahmoud\Projects\WEP\Lap_System\LapApp\dist
Compression=lzma
SolidCompression=yes
SetupIconFile=F:\Mahmoud\Projects\WEP\Lap_System\LapApp\AppIcon.ico

[Files]
Source: "F:\Mahmoud\Projects\WEP\Lap_System\LapApp\dist\NebrasLab.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{commondesktop}\Nebras Medical Laboratory"; Filename: "{app}\NebrasLab.exe"
Name: "{group}\Nebras Medical Laboratory"; Filename: "{app}\NebrasLab.exe"

[Run]
Filename: "{app}\NebrasLab.exe"; Description: "تشغيل البرنامج"; Flags: nowait postinstall skipifsilent