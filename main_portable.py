import sys
import os
import time
import threading
from service import ZKTecoService
import logging

def setup_logging():
    """Configurer le logging pour l'app portable"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('zkteco_service.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def run_service_in_background():
    """Lancer le service en arrière-plan"""
    logger = logging.getLogger(__name__)
    
    try:
        service = ZKTecoService()
        service.start()
        logger.info("🚀 Service ZKTeco démarré en arrière-plan")
        
        # Garder le service actif
        while service.is_running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"💥 Erreur critique: {e}")
    finally:
        if 'service' in locals():
            service.stop()
        logger.info("✅ Service arrêté")

def show_system_tray_notification():
    """Afficher une notification dans la zone de notification"""
    try:
        import pystray
        from PIL import Image, ImageDraw
        import threading
        
        # Créer une icône simple
        def create_image():
            image = Image.new('RGB', (64, 64), color='white')
            dc = ImageDraw.Draw(image)
            dc.rectangle([16, 16, 48, 48], fill='green')
            return image
        
        def on_quit(icon, item):
            icon.stop()
            os._exit(0)
        
        # Menu de l'icône
        menu = pystray.Menu(
            pystray.MenuItem("Quitter", on_quit)
        )
        
        # Créer et afficher l'icône
        icon = pystray.Icon("ZKTeco", create_image(), "Service ZKTeco", menu)
        
        # Lancer dans un thread séparé
        def run_icon():
            icon.run()
        
        thread = threading.Thread(target=run_icon, daemon=True)
        thread.start()
        
    except ImportError:
        # Si pystray n'est pas installé, on continue sans l'icône
        pass

def main():
    """Fonction principale de l'app portable"""
    print("=" * 50)
    print("🚀 ZKTeco Service - Version Portable")
    print("=" * 50)
    print("Le service de pointage démarre en arrière-plan...")
    print("")
    print("📝 Logs: zkteco_service.log")
    print("🌐 IP Device: 192.168.43.33")
    print("🔄 Synchronisation automatique toutes les 5 minutes")
    print("")
    print("💡 Pour arrêter: Fermez cette fenêtre")
    print("=" * 50)
    print("")
    
    # Configurer le logging
    setup_logging()
    
    # Démarrer l'icône système (optionnel)
    show_system_tray_notification()
    
    # Lancer le service en arrière-plan
    run_service_in_background()

if __name__ == "__main__":
    # Si lancé avec --gui, ouvrir l'interface
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        from gui import main as gui_main
        gui_main()
    else:
        # Sinon, lancer en mode service automatique
        main()