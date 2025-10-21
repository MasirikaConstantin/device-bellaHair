from zkteco_client import ZKTecoClient
from api_client import APIClient
from config import Config
import logging

def test_with_api():
    # Configuration du logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    config = Config()
    
    print("🧪 Test complet avec envoi API...")
    
    # Test connexion ZKTeco
    zk_client = ZKTecoClient(
        config.get('zkteco_ip'),
        config.get('zkteco_port')
    )
    
    if zk_client.test_connection():
        print("✅ Connexion ZKTeco réussie!")
        
        # Récupérer les pointages
        attendances = zk_client.get_attendance()
        print(f"📊 {len(attendances)} pointages récupérés")
        
        if attendances:
            # Afficher les 3 premiers pour vérifier le format
            print("\n📝 Format des données (3 premiers):")
            for i, att in enumerate(attendances[:3]):
                print(f"  {i+1}. UID: {att['uid']}, ID: {att['id']}, Time: {att['timestamp']}")
            
            # Envoyer à l'API
            api_client = APIClient(config.get('api_url'))
            print(f"\n📤 Envoi à l'API: {config.get('api_url')}")
            
            success = api_client.send_attendance(attendances)
            
            if success:
                print("✅ Pointages envoyés avec succès à l'API!")
            else:
                print("❌ Échec de l'envoi à l'API")
        else:
            print("📭 Aucun pointage à envoyer")
    else:
        print("❌ Échec connexion ZKTeco")

if __name__ == "__main__":
    test_with_api()