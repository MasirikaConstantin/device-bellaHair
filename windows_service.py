import sys
import os
import time
import subprocess
from service import ZKTecoService

def run_as_windows_service():
    """Version adaptée pour Windows avec gestion de session"""
    service = ZKTecoService()
    
    print("=" * 50)
    print("🚀 SERVICE ZKTeco - Mode Windows")
    print("=" * 50)
    print("Ce service tourne en arrière-plan et synchronise")
    print("automatiquement les pointages toutes les 5 minutes.")
    print("")
    print("📝 Logs: zkteco_service.log")
    print("🛑 Pour arreter: Fermez cette fenetre ou Ctrl+C")
    print("=" * 50)
    print("")
    
    # Démarrer le service
    service.start()
    
    try:
        # Garder la fenêtre ouverte mais minimisée
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 6)  # SW_MINIMIZE
        
        # Boucle principale
        while service.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt demandé...")
    finally:
        service.stop()
        print("✅ Service arrêté")

def create_task_scheduler():
    """Créer une tâche planifiée Windows"""
    script_path = os.path.abspath(__file__)
    working_dir = os.path.dirname(script_path)
    
    # Commande PowerShell pour créer la tâche
    ps_script = f"""
$Action = New-ScheduledTaskAction -Execute 'python' -Argument '{script_path}' -WorkingDirectory '{working_dir}'
$Trigger = New-ScheduledTaskTrigger -AtStartup
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable
$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName "ZKTecoAttendanceService" -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Description "Service de synchronisation des pointages ZKTeco"
"""
    
    with open("create_scheduled_task.ps1", "w") as f:
        f.write(ps_script)
    
    print("📋 Script PowerShell créé: create_scheduled_task.ps1")
    print("💡 Exécutez-le en tant qu'administrateur pour installer le service")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        create_task_scheduler()
    else:
        run_as_windows_service()