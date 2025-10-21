@echo off
echo Construction de l'application ZKTeco...

pip install -r requirements.txt

pyinstaller --onefile --windowed --name "ZKTecoService" ^
    --add-data "config.py;." ^
    --icon=zkteco.ico ^
    main.py

echo.
echo Construction terminee!
echo Fichier executable: dist\ZKTecoService.exe
pause