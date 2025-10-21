#!/bin/bash

echo "🔨 Construction des exécutables ZKTeco pour Linux..."

# Créer le répertoire de distribution si il n'existe pas
mkdir -p dist

# Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt

# Créer l'exécutable principal (GUI)
echo "🖥️  Construction de l'interface graphique..."
pyinstaller --onefile --windowed --name "ZKTecoService" \
    --add-data "config.py:." \
    --add-data "zkteco_config.json:." \
    --icon=zkteco.ico \
    main.py

# Créer l'exécutable pour le service en arrière-plan
echo "🔄 Construction du service en arrière-plan..."
pyinstaller --onefile --console --name "ZKTecoBackgroundService" \
    --add-data "config.py:." \
    --add-data "zkteco_config.json:." \
    windows_service.py

# Créer un script de lancement simple
echo "📝 Création des scripts de lancement..."

# Script pour l'interface graphique
cat > dist/start_gui.sh << 'EOF'
#!/bin/bash
echo "🚀 Lancement de l'interface ZKTeco..."
./ZKTecoService
EOF

# Script pour le service en arrière-plan
cat > dist/start_service.sh << 'EOF'
#!/bin/bash
echo "🚀 Lancement du service ZKTeco en arrière-plan..."
./ZKTecoBackgroundService
EOF

# Script de test
cat > dist/test_connection.sh << 'EOF'
#!/bin/bash
echo "🧪 Test de connexion..."
./ZKTecoService test
EOF

# Rendre les scripts exécutables
chmod +x dist/start_gui.sh
chmod +x dist/start_service.sh
chmod +x dist/test_connection.sh

# Copier les fichiers de configuration
echo "📄 Copie des fichiers de configuration..."
cp zkteco_config.json dist/ 2>/dev/null || true
cp config.py dist/ 2>/dev/null || true

# Créer un README pour Linux
cat > dist/README_LINUX.md << 'EOF'
# Service ZKTeco pour Linux

## Fichiers disponibles :

- **ZKTecoService** : Interface graphique (configuration + service)
- **ZKTecoBackgroundService** : Service en arrière-plan uniquement
- **start_gui.sh** : Script pour lancer l'interface
- **start_service.sh** : Script pour le service en arrière-plan
- **test_connection.sh** : Script pour tester la connexion

## Utilisation :

### Première configuration :
```bash
./start_gui.sh