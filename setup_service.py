# setup_service.py - Pour créer l'exécutable du service
import sys
from cx_Freeze import setup, Executable

build_options = {
    "packages": ["os", "sys", "time", "threading", "logging", "datetime", "requests", "zk"],
    "excludes": [],
    "include_files": ["config.py", "zkteco_config.json"]
}

base = None
if sys.platform == "win32":
    base = "Win32Service"  # Pour un service Windows

setup(
    name="ZKTecoService",
    version="1.0",
    description="Service de pointage ZKTeco",
    options={"build_exe": build_options},
    executables=[Executable("windows_service.py", base=base, target_name="ZKTecoService.exe")]
)