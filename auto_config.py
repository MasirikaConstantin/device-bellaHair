import json
import os
from pathlib import Path

def setup_auto_config():
    """Créer la configuration automatiquement si elle n'existe pas"""
    config_file = Path("zkteco_config.json")
    
    if not config_file.exists():
        default_config = {
            "zkteco_ip": "192.168.43.33",
            "zkteco_port": 4370,
            "api_url": "http://localhost:8000/api/pointages",
            "polling_interval": 300,
            "auto_start": True
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2, ensure_ascii=False)
        
        print("✅ Configuration créée automatiquement")
    
    return config_file.exists()

# Exécuter à l'import
setup_auto_config()