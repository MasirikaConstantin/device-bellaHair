@echo off
echo Déploiement de l'application ZKTeco...

REM Créer l'exécutable principal (GUI)
pyinstaller --onefile --windowed --name "ZKTecoService" ^
    --add-data "config.py;." ^
    --add-data "zkteco_config.json;." ^
    --icon=zkteco.ico ^
    main.py

REM Créer l'exécutable pour le service en arrière-plan
pyinstaller --onefile --console --name "ZKTecoBackgroundService" ^
    --add-data "config.py;." ^
    --add-data "zkteco_config.json;." ^
    windows_service.py

echo.
echo Déploiement terminé!
echo.
echo Fichiers créés:
echo   - dist\ZKTecoService.exe (Interface graphique)
echo   - dist\ZKTecoBackgroundService.exe (Service en arrière-plan)
echo.
pause