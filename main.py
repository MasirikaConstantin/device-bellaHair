import sys
import os
import logging

def setup_logging():
    """Configurer le logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('zkteco_service.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "start":
            # Mode service uniquement (sans GUI)
            from service import ZKTecoService
            setup_logging()
            print("🚀 Démarrage du service ZKTeco en mode service...")
            service = ZKTecoService()
            service.start()
            
            # Garder le programme actif
            try:
                while True:
                    user_input = input("Tapez 'stop' pour arrêter le service: ")
                    if user_input.lower() == 'stop':
                        break
            except KeyboardInterrupt:
                print("\n🛑 Arrêt demandé...")
            finally:
                service.stop()
                
        elif command == "test":
            # Mode test
            from service import ZKTecoService
            setup_logging()
            print("🧪 Test de connexion...")
            
            service = ZKTecoService()
            results = service.test_connection()
            
            print("\n📊 Résultats du test:")
            print(f"ZKTeco Device: {'✅ OK' if results['zkteco'] else '❌ ERREUR'}")
            print(f"API: {'✅ OK' if results['api'] else '❌ ERREUR'}")
            
            if results['zkteco'] and results['device_info']:
                print("\n📟 Informations du device:")
                for key, value in results['device_info'].items():
                    print(f"  {key}: {value}")
            
        elif command == "simple":
            # Test simple
            from test_simple import test_simple
            test_simple()
            
        else:
            print("Commandes disponibles:")
            print("  start  - Démarrer le service en mode console")
            print("  gui    - Interface graphique (recommandé)")
            print("  test   - Tester la connexion")
            print("  simple - Test simple de connexion")
    else:
        # PAR DÉFAUT: Lancer le GUI
        from gui import main as gui_main
        gui_main()

if __name__ == "__main__":
    main()