@echo off
echo =================================
echo BUILD APPLICATION PORTABLE ZKTeco
echo =================================

echo.
echo 📦 Installation des dependances...
pip install pyinstaller pystray pillow

echo.
echo 🔨 Construction de l'application portable...

:: Version avec interface
pyinstaller --onefile --windowed --name "ZKTecoService" ^
    --add-data "config.py;." ^
    --add-data "zkteco_config.json;." ^
    --icon=zkteco.ico ^
    main_portable.py

:: Version silencieuse (sans fenêtre)
pyinstaller --onefile --windowed --name "ZKTecoBackground" ^
    --add-data "config.py;." ^
    --add-data "zkteco_config.json;." ^
    --icon=zkteco.ico ^
    service_only.py

echo.
echo 📁 Copie des fichiers de configuration...
copy zkteco_config.json dist\ 2>nul
copy config.py dist\ 2>nul

echo.
echo ✅ BUILD TERMINE !
echo.
echo 📂 Fichiers crees dans 'dist\' :
echo   1. ZKTecoService.exe - Avec interface
echo   2. ZKTecoBackground.exe - Silencieux
echo.
echo 🚀 Utilisation :
echo   - Double-cliquez sur ZKTecoService.exe
echo   - Le service demarre automatiquement
echo   - Les logs sont dans zkteco_service.log
echo.
pause