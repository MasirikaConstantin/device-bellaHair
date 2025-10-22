import requests
import json
import time
from typing import List, Dict, Any
import logging

class APIClient:
    def __init__(self, api_url: str):
        self.api_url = api_url
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ZKTeco-Service/2.0'
        })
        # Désactiver la vérification SSL pour les tests
        self.session.verify = False
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        self.logger = logging.getLogger(__name__)
    
    def send_attendance(self, attendance_data: List[Dict[str, Any]], max_retries: int = 3) -> bool:
        """Envoyer les pointages à l'API avec système de retry"""
        if not attendance_data:
            self.logger.info("📭 Aucune donnée à envoyer")
            return True
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"📤 Tentative {attempt + 1}/{max_retries} - Envoi de {len(attendance_data)} pointages")
                
                response = self.session.post(
                    self.api_url,
                    json=attendance_data,
                    timeout=30,
                    verify=False
                )
                
                if response.status_code in [200, 201]:
                    try:
                        response_data = response.json()
                        self.logger.info(f"✅ Réponse API: {response_data.get('message', 'Succès')}")
                        self.logger.info(f"📊 {response_data.get('saved_count', 0)} sauvegardés, {response_data.get('duplicates_skipped', 0)} doublons ignorés")
                        return True
                    except ValueError:
                        self.logger.info("✅ Pointages envoyés avec succès")
                        return True
                else:
                    self.logger.warning(f"⚠️  Réponse API {response.status_code}: {response.text}")
                    
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10
                        self.logger.info(f"⏳ Nouvelle tentative dans {wait_time}s...")
                        time.sleep(wait_time)
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"🔌 Erreur connexion API: {e}")
            except requests.exceptions.Timeout as e:
                self.logger.error(f"⏰ Timeout API: {e}")
            except Exception as e:
                self.logger.error(f"💥 Erreur inattendue: {e}")
            
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 10)
        
        self.logger.error(f"🔴 Échec après {max_retries} tentatives")
        return False
    
    def test_connection(self) -> bool:
        """Tester la connexion à l'API de manière plus robuste"""
        try:
            self.logger.info(f"🧪 Test de connexion API: {self.api_url}")
            
            # Méthode 1: Essayer une requête OPTIONS (plus safe)
            try:
                response = self.session.options(self.api_url, timeout=10, verify=False)
                if response.status_code in [200, 204, 405]:  # 405 Method Not Allowed est acceptable
                    self.logger.info("✅ Test OPTIONS réussi")
                    return True
            except:
                pass
            
            # Méthode 2: Essayer une requête HEAD
            try:
                response = self.session.head(self.api_url, timeout=10, verify=False)
                if response.status_code != 404:
                    self.logger.info("✅ Test HEAD réussi")
                    return True
            except:
                pass
            
            # Méthode 3: Essayer l'endpoint racine sans /pointages
            try:
                base_url = self.api_url.rsplit('/pointages', 1)[0]
                if base_url != self.api_url:  # Vérifier qu'on a bien enlevé /pointages
                    response = self.session.get(base_url, timeout=10, verify=False)
                    if response.status_code != 404:
                        self.logger.info("✅ Test endpoint racine réussi")
                        return True
            except:
                pass
            
            # Méthode 4: Essayer avec des données vides
            try:
                response = self.session.post(
                    self.api_url,
                    json=[],
                    timeout=10,
                    verify=False
                )
                # Même une erreur 400 signifie que l'endpoint existe
                if response.status_code != 404:
                    self.logger.info("✅ Test avec données vides réussi")
                    return True
            except requests.exceptions.ConnectionError:
                self.logger.error("🔌 Impossible de se connecter à l'API")
                return False
            except Exception as e:
                # D'autres erreurs peuvent signifier que l'endpoint existe mais refuse les données
                if "404" not in str(e):
                    self.logger.info("✅ Endpoint accessible (erreur autre que 404)")
                    return True
            
            self.logger.error("❌ Aucune méthode de test n'a fonctionné")
            return False
            
        except Exception as e:
            self.logger.error(f"❌ Test connexion API échoué: {e}")
            return False