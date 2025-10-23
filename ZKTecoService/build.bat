@echo off
echo Construction du Service ZKTeco en Java...

REM Créer les dossiers
if not exist build mkdir build
if not exist dist mkdir dist

REM Compiler les sources
echo Compilation des fichiers Java...
javac -d build -encoding UTF-8 src/com/zkteco/*.java

if errorlevel 1 (
    echo ❌ Erreur de compilation!
    pause
    exit /b 1
)

REM Créer le JAR exécutable
echo Création du JAR...
jar cfe dist/ZKTecoService.jar com.zkteco.Main -C build .

REM Copier la configuration par défaut
if not exist dist\config.properties (
    echo Création de la configuration par défaut...
    echo zkteco_ip=192.168.43.33> dist\config.properties
    echo zkteco_port=4370>> dist\config.properties
    echo api_url=http://localhost:8000/api/pointages>> dist\config.properties
    echo polling_interval=180>> dist\config.properties
)

echo.
echo ✅ Construction terminée avec succès!
echo.
echo Fichiers créés dans le dossier 'dist':
echo   - ZKTecoService.jar (Application principale)
echo   - config.properties (Configuration)
echo.
echo Pour exécuter:
echo   java -jar dist\ZKTecoService.jar          (Mode GUI)
echo   java -jar dist\ZKTecoService.jar start    (Mode service)
echo   java -jar dist\ZKTecoService.jar test     (Test connexion)
echo.

REM Créer un lanceur Windows
echo Création du lanceur Windows...
echo @echo off > dist\LancerService.bat
echo java -jar ZKTecoService.jar >> dist\LancerService.bat

echo Lanceur 'LancerService.bat' créé dans le dossier dist.
echo.

pause