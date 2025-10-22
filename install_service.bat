@echo off
echo =================================
echo INSTALLATION SERVICE ZKTeco
echo =================================

echo.
echo 1. Installation des dependances...
pip install pywin32

echo.
echo 2. Creation du service...
python install_windows_service.py install

echo.
echo 3. Demarrage du service...
python install_windows_service.py start

echo.
echo ✅ Service installe et demarre!
echo.
echo Commandes disponibles:
echo   python install_windows_service.py start
echo   python install_windows_service.py stop
echo   python install_windows_service.py restart
echo   python install_windows_service.py remove
echo.
pause