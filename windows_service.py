import sys
import os
import time
from service import ZKTecoService

def run_as_service():
    """Fonction pour exécuter le service en arrière-plan"""
    service = ZKTecoService()
    
    print("🚀 Démarrage du service ZKTeco en arrière-plan...")
    print("📝 Logs enregistrés dans: zkteco_service.log")
    print("🛑 Pour arrêter: Ctrl+C ou fermer cette fenêtre")
    
    service.start()
    
    try:
        # Maintenir le service actif
        while service.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du service...")
    finally:
        service.stop()

if __name__ == "__main__":
    run_as_service()