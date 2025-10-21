import time
import threading
import logging
from datetime import datetime, timedelta
from config import Config
from zkteco_client import ZKTecoClient
from api_client import APIClient

class ZKTecoService:
    def __init__(self):
        self.config = Config()
        self.is_running = False
        self.thread = None
        self.last_check = None
        self.last_successful_sync = None
        self.error_count = 0
        self.max_errors = 5
        
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('zkteco_service.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        """Démarrer le service"""
        if self.is_running:
            self.logger.warning("⚠️ Service déjà en cours d'exécution")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        self.logger.info("🚀 Service ZKTeco démarré")
    
    def stop(self):
        """Arrêter le service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=10)
        self.logger.info("🛑 Service ZKTeco arrêté")
    
    def _run_loop(self):
        """Boucle principale du service"""
        self.logger.info("🔄 Démarrage de la boucle de surveillance")
        
        while self.is_running:
            try:
                self._check_attendance()
                
                # Attendre l'intervalle configuré
                sleep_time = self.config.get('polling_interval', 300)
                self.logger.debug(f"⏰ Attente de {sleep_time} secondes")
                
                # Vérifier toutes les secondes si on doit s'arrêter
                for _ in range(sleep_time):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.error_count += 1
                self.logger.error(f"💥 Erreur dans la boucle principale: {e}")
                
                if self.error_count >= self.max_errors:
                    self.logger.error("🔴 Trop d'erreurs, arrêt du service")
                    self.stop()
                    break
                
                time.sleep(60)  # Attendre 1 minute en cas d'erreur
    
    def _check_attendance(self):
        """Vérifier et envoyer les pointages"""
        self.logger.info("🔍 Vérification des pointages...")
        
        try:
            # Récupérer les pointages depuis la dernière synchronisation
            since_date = self.last_successful_sync or (
                datetime.now() - timedelta(hours=24)  # Par défaut, dernières 24h
            )
            
            # Récupérer les pointages
            zk_client = ZKTecoClient(
                self.config.get('zkteco_ip', '192.168.41.155'),
                self.config.get('zkteco_port', 4370),
                self.config.get('timeout', 5)
            )
            
            attendances = zk_client.get_attendance_since(since_date)
            
            if attendances:
                self.logger.info(f"📥 {len(attendances)} nouveaux pointages à envoyer")
                
                # Envoyer à l'API
                api_client = APIClient(self.config.get('api_url', 'http://localhost:8000/api/pointages'))
                success = api_client.send_attendance(attendances)
                
                if success:
                    self.last_successful_sync = datetime.now()
                    self.last_check = datetime.now()
                    self.error_count = 0  # Réinitialiser le compteur d'erreurs
                    self.logger.info("✅ Pointages envoyés avec succès")
                else:
                    self.error_count += 1
                    self.logger.error("❌ Échec de l'envoi des pointages")
            else:
                self.last_check = datetime.now()
                self.logger.info("📭 Aucun nouveau pointage")
        
        except Exception as e:
            self.error_count += 1
            self.logger.error(f"💥 Erreur lors de la vérification: {e}")
    
    def test_connection(self, ip: str = None) -> dict:
        """Tester la connectivité complète"""
        test_ip = ip or self.config.get('zkteco_ip', '192.168.41.155')
        results = {'zkteco': False, 'api': False, 'device_info': {}}
        
        try:
            # Test connexion ZKTeco
            zk_client = ZKTecoClient(test_ip, self.config.get('zkteco_port', 4370))
            results['zkteco'] = zk_client.test_connection()
            
            if results['zkteco']:
                results['device_info'] = zk_client.get_device_info()
            
            # Test connexion API
            api_client = APIClient(self.config.get('api_url', 'http://localhost:8000/api/pointages'))
            results['api'] = api_client.test_connection()
            
        except Exception as e:
            self.logger.error(f"❌ Erreur test connexion: {e}")
        
        return results
    
    def update_config(self, new_config: dict) -> bool:
        """Mettre à jour la configuration"""
        success = self.config.save_config(new_config)
        if success:
            self.logger.info("✅ Configuration mise à jour")
        else:
            self.logger.error("❌ Erreur mise à jour configuration")
        return success
    
    def get_status(self) -> dict:
        """Obtenir le statut détaillé du service"""
        return {
            'running': self.is_running,
            'last_check': self.last_check.isoformat() if self.last_check else None,
            'last_successful_sync': self.last_successful_sync.isoformat() if self.last_successful_sync else None,
            'error_count': self.error_count,
            'config': self.config.get_all()
        }
    
    def force_sync(self) -> bool:
        """Forcer une synchronisation immédiate"""
        self.logger.info("🔀 Synchronisation forcée demandée")
        self._check_attendance()
        return self.error_count == 0