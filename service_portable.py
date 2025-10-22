import time
import threading
import logging
from datetime import datetime, timedelta
from config import Config
from zkteco_client import ZKTecoClient
from api_client import APIClient

class ZKTecoPortableService:
    def __init__(self):
        self.config = Config()
        self.is_running = False
        self.thread = None
        self.last_check = None
        self.last_successful_sync = None
        self.error_count = 0
        self.max_errors = 5
        
        # Configuration du logging pour portable
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - ZKTecoService - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('zkteco_service.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Log de démarrage
        self.logger.info("=" * 50)
        self.logger.info("🚀 SERVICE ZKTECO PORTABLE DÉMARRÉ")
        self.logger.info("=" * 50)
    
    def start(self):
        """Démarrer le service"""
        if self.is_running:
            self.logger.warning("Service déjà en cours d'exécution")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("Service démarré avec succès")
    
    def stop(self):
        """Arrêter le service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.logger.info("Service arrêté")
    
    def _run_loop(self):
        """Boucle principale du service"""
        self.logger.info("Démarrage de la surveillance automatique")
        
        while self.is_running:
            try:
                self._check_attendance()
                
                # Attendre l'intervalle configuré
                sleep_time = self.config.get('polling_interval', 300)
                
                # Vérifier toutes les secondes si on doit s'arrêter
                for _ in range(sleep_time):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"Erreur dans la boucle principale: {e}")
                
                if self.error_count >= self.max_errors:
                    self.logger.error("Trop d'erreurs, arrêt du service")
                    self.stop()
                    break
                
                time.sleep(60)
    
    def _check_attendance(self):
        """Vérifier et envoyer les pointages"""
        try:
            since_date = self.last_successful_sync or (datetime.now() - timedelta(hours=24))
            
            zk_client = ZKTecoClient(
                self.config.get('zkteco_ip', '192.168.43.33'),
                self.config.get('zkteco_port', 4370)
            )
            
            attendances = zk_client.get_attendance_since(since_date)
            
            if attendances:
                self.logger.info(f"{len(attendances)} nouveaux pointages à envoyer")
                
                api_client = APIClient(self.config.get('api_url', 'http://localhost:8000/api/pointages'))
                success = api_client.send_attendance(attendances)
                
                if success:
                    self.last_successful_sync = datetime.now()
                    self.last_check = datetime.now()
                    self.error_count = 0
                    self.logger.info("Pointages envoyés avec succès")
                else:
                    self.error_count += 1
                    self.logger.error("Échec de l'envoi des pointages")
            else:
                self.last_check = datetime.now()
                self.logger.debug("Aucun nouveau pointage")
        
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"Erreur lors de la vérification: {e}")
    
    def get_status(self):
        """Obtenir le statut pour les logs"""
        return {
            'running': self.is_running,
            'last_check': self.last_check,
            'last_sync': self.last_successful_sync,
            'error_count': self.error_count
        }