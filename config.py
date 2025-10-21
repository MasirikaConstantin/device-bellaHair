import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_file = Path(__file__).parent / "zkteco_config.json"
        self.default_config = {
            "zkteco_ip": "192.168.41.155",
            "zkteco_port": 4370,
            "timeout": 5,
            "api_url": "http://localhost:8000/api/pointages",
            "polling_interval": 300,  # 5 minutes
            "timezone": "Africa/Casablanca",
            "max_retries": 3,
            "retry_delay": 30,
            "sync_on_startup": True
        }
        self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                self.default_config.update(user_config)
                print(f"✅ Configuration chargée: {self.config_file}")
            except Exception as e:
                print(f"❌ Erreur lecture config: {e}")
        else:
            print("ℹ️  Fichier config non trouvé, utilisation config par défaut")
            self.save_config(self.default_config)
    
    def save_config(self, new_config):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=2, ensure_ascii=False)
            self.default_config.update(new_config)
            print(f"✅ Configuration sauvegardée: {self.config_file}")
            return True
        except Exception as e:
            print(f"❌ Erreur sauvegarde config: {e}")
            return False
    
    def get(self, key, default=None):
        """Méthode get corrigée avec valeur par défaut"""
        return self.default_config.get(key, default)
    
    def get_all(self):
        return self.default_config.copy()