import sys
import os
import time
import logging
from service import ZKTecoService

def setup_logging():
    """Configurer le logging sans console"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('zkteco_service.log', encoding='utf-8')
            # Pas de StreamHandler pour éviter la console
        ]
    )

def main():
    """Lancement silencieux du service"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        service = ZKTecoService()
        service.start()
        logger.info("🚀 Service ZKTeco démarré silencieusement")
        
        # Boucle infinie silencieuse
        while service.is_running:
            time.sleep(60)  # Vérifier toutes les minutes
            
    except Exception as e:
        logger.error(f"💥 Erreur critique: {e}")
    finally:
        if 'service' in locals():
            service.stop()
        logger.info("✅ Service arrêté")

if __name__ == "__main__":
    main()