@echo off
echo Ajout au demarrage Windows...

:: Créer un raccourci dans le dossier Startup
powershell "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ZKTecoService.lnk'); $Shortcut.TargetPath = '%~dp0windows_service.py'; $Shortcut.WorkingDirectory = '%~dp0'; $Shortcut.Save()"

echo ✅ Ajoute au demarrage de Windows!
echo Le service se lancera automatiquement a chaque connexion.
pause