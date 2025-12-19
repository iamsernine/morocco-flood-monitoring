"""
============================================================================
MAIN.PY - Point d'entrée principal du backend
============================================================================
Description:
    Point d'entrée principal de l'application backend Flask.
    Initialise tous les services et démarre le serveur.

Usage:
    python app/main.py

Debugging:
    - Vérifier que la base de données est initialisée
    - Vérifier les logs de démarrage
    - Tester avec curl http://localhost:5000/api/health
============================================================================
"""

import os
import sys
from datetime import datetime

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.api.routes import create_app
from app.models import init_db


def main():
    """
    Fonction principale de démarrage.
    """
    print("=" * 80)
    print("🌊 SMART FLOOD MONITORING SYSTEM - MOROCCO WORLD CUP 2030")
    print("=" * 80)
    print(f"📅 Démarrage: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print()
    
    # Initialiser la base de données
    print("🔧 Initialisation de la base de données...")
    try:
        init_db()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation de la DB: {e}")
        sys.exit(1)
    
    # Créer l'application Flask
    print("\n🔧 Création de l'application Flask...")
    try:
        app = create_app()
        print("✅ Application Flask créée")
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'app: {e}")
        sys.exit(1)
    
    # Informations de démarrage
    print("\n" + "=" * 80)
    print("🚀 SERVEUR PRÊT")
    print("=" * 80)
    print("🌐 URL: http://localhost:5000")
    print("📚 Health check: http://localhost:5000/api/health")
    print("📡 MQTT: Démarrer avec POST /api/mqtt/start")
    print()
    print("⚠️  Mode démo locale - Pas d'authentification")
    print("=" * 80)
    print()
    
    # Démarrer le serveur
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=False  # Éviter le double démarrage en mode debug
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Arrêt du serveur...")
    except Exception as e:
        print(f"\n❌ Erreur lors du démarrage du serveur: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
