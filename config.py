import json
import os
from pathlib import Path
import sys

class Config:
    def __init__(self):
        # Utiliser le répertoire de l'exécutable pour la portabilité
        if getattr(sys, 'frozen', False):
            # Si on est dans un exécutable PyInstaller
            base_path = Path(sys.executable).parent
        else:
            # Si on est en développement
            base_path = Path(__file__).parent
            
        self.config_file = base_path / "zkteco_config.json"
        self.default_config = {
            "zkteco_ip": "192.168.41.155",
            "zkteco_port": 4370,
            "timeout": 5,
            # CHANGER localhost par l'IP RÉELLE de ton serveur Laravel
            "api_url": "http://192.168.1.100:8000/api/pointages",  # ← IP de ton serveur
            "polling_interval": 300,
            "timezone": "Africa/Casablanca",
            "max_retries": 3,
            "retry_delay": 30
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
                # Créer le fichier avec la config par défaut
                self.save_config(self.default_config)
        else:
            print("ℹ️  Fichier config non trouvé, création avec config par défaut")
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
        return self.default_config.get(key, default)
    
    def get_all(self):
        return self.default_config.copy()