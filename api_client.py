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
        self.logger = logging.getLogger(__name__)
    
    def send_attendance(self, attendance_data: List[Dict[str, Any]], max_retries: int = 3) -> bool:
        """Envoyer les pointages à l'API avec système de retry"""
        if not attendance_data:
            self.logger.info("📭 Aucune donnée à envoyer")
            return True
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"📤 Tentative {attempt + 1}/{max_retries} - Envoi de {len(attendance_data)} pointages")
                
                # Préparer les données pour l'API Laravel
                payload = attendance_data  # Déjà formaté correctement
                
                self.logger.debug(f"📦 Données envoyées: {json.dumps(payload[:2], indent=2)}")  # Log des 2 premiers pour debug
                
                response = self.session.post(
                    self.api_url,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code in [200, 201]:
                    # Analyser la réponse de l'API
                    try:
                        response_data = response.json()
                        self.logger.info(f"✅ Réponse API: {response_data.get('message', 'Succès')}")
                        self.logger.info(f"📊 Statistiques: {response_data.get('saved_count', 0)} sauvegardés, "
                                       f"{response_data.get('duplicates_skipped', 0)} doublons ignorés")
                        
                        if response_data.get('errors'):
                            self.logger.warning(f"⚠️  Erreurs partielles: {len(response_data['errors'])} erreurs")
                            for error in response_data['errors'][:3]:  # Log seulement les 3 premières erreurs
                                self.logger.warning(f"   - {error}")
                        
                        return True
                    except ValueError:
                        self.logger.info("✅ Pointages envoyés (réponse non JSON)")
                        return True
                else:
                    self.logger.warning(f"⚠️  Réponse API {response.status_code}: {response.text}")
                    
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 10  # Backoff exponentiel
                        self.logger.info(f"⏳ Nouvelle tentative dans {wait_time}s...")
                        time.sleep(wait_time)
                    
            except requests.exceptions.ConnectionError as e:
                self.logger.error(f"🔌 Erreur connexion API (tentative {attempt + 1}): {e}")
            except requests.exceptions.Timeout as e:
                self.logger.error(f"⏰ Timeout API (tentative {attempt + 1}): {e}")
            except requests.exceptions.RequestException as e:
                self.logger.error(f"❌ Erreur requête API (tentative {attempt + 1}): {e}")
            except Exception as e:
                self.logger.error(f"💥 Erreur inattendue (tentative {attempt + 1}): {e}")
            
            if attempt < max_retries - 1:
                time.sleep((attempt + 1) * 10)  # Attendre avant nouvelle tentative
        
        self.logger.error(f"🔴 Échec après {max_retries} tentatives")
        return False
    
    def test_connection(self) -> bool:
        """Tester la connexion à l'API"""
        try:
            # Tester avec une requête HEAD ou GET simple
            test_payload = [{
                'uid': 'test',
                'id': 9999,
                'state': 0,
                'timestamp': '2024-01-01 00:00:00',
                'type': 0,
                'verify_mode': 0,
                'work_code': 0,
                'device_ip': '192.168.1.1'
            }]
            
            response = self.session.post(
                self.api_url,
                json=test_payload,
                timeout=10
            )
            
            # Même si ça retourne une erreur 400 (mauvaises données), ça signifie que l'API est accessible
            return response.status_code != 404  # Si c'est pas 404, l'endpoint existe
            
        except requests.exceptions.ConnectionError:
            self.logger.error("🔌 Impossible de se connecter à l'API")
            return False
        except Exception as e:
            self.logger.error(f"❌ Test connexion API échoué: {e}")
            return False