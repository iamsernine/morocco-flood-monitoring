# ⚡ Quick Start - Morocco Flood Monitoring System

Démarrage rapide en 5 minutes pour tester le système localement.

## 📋 Prérequis

- Python 3.8+
- Node.js 16+
- pnpm (`npm install -g pnpm`)
- Mosquitto MQTT broker

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/iamsernine/morocco-flood-monitoring.git
cd morocco-flood-monitoring
```

### 2. Backend

```bash
cd backend

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python app/models/database.py

# Entraîner le modèle ML
python scripts/train_model.py

# Générer des données de test
python scripts/generate_test_data.py

# Démarrer le backend
python app/main.py
```

Le backend sera accessible sur `http://localhost:5000`

### 3. Frontend (nouveau terminal)

```bash
cd frontend

# Installer les dépendances
pnpm install

# Démarrer le frontend
pnpm dev
```

Le frontend sera accessible sur `http://localhost:3000`

### 4. MQTT (nouveau terminal)

```bash
# Démarrer Mosquitto
mosquitto

# OU sur Ubuntu/Debian
sudo systemctl start mosquitto
```

### 5. Démarrer le client MQTT

```bash
curl -X POST http://localhost:5000/api/mqtt/start
```

### 6. Simuler un capteur (nouveau terminal)

```bash
cd simulators
python sensor_simulator.py --sensor-id CAS_1 --city Casablanca
```

## 🎯 Tester le système

1. **Ouvrir le navigateur** : `http://localhost:3000`

2. **Page d'accueil** : Voir les 5 villes avec leurs statistiques

3. **Cliquer sur Casablanca** : Voir les capteurs de la ville

4. **Cliquer sur CAS_1** : Voir les prédictions en temps réel

5. **Aller sur la carte** : Voir tous les capteurs sur la carte du Maroc

## 📊 Données de test

Le script `generate_test_data.py` a créé:

- **5 villes** : Casablanca, Rabat, Marrakech, Fès, Tanger
- **15-20 capteurs** : 2-4 par ville
- **~1000 prédictions** : 7 jours d'historique

## 🔧 Commandes utiles

### Backend

```bash
# Health check
curl http://localhost:5000/api/health

# Voir les villes
curl http://localhost:5000/api/cities

# Voir les capteurs
curl http://localhost:5000/api/sensors

# Voir le résumé des prédictions
curl http://localhost:5000/api/predictions/summary
```

### MQTT

```bash
# Écouter tous les messages
mosquitto_sub -h localhost -t "morocco/flood/#" -v

# Publier un message de test
mosquitto_pub -h localhost -t "morocco/flood/sensors/CAS_1" \
  -m '{"water_level": 75, "humidity": 80, "timestamp": "2024-01-01T12:00:00"}'
```

### Frontend

```bash
# Build production
pnpm build

# Preview production
pnpm preview
```

## 🐛 Problèmes courants

### Port 5000 déjà utilisé

```bash
# Changer le port dans backend/app/main.py
# Ligne: uvicorn.run(app, host="0.0.0.0", port=5001)
```

### Port 3000 déjà utilisé

```bash
# Changer le port dans frontend/vite.config.ts
# Ligne: server: { port: 3001 }
```

### Mosquitto ne démarre pas

```bash
# Ubuntu/Debian
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto

# macOS
brew install mosquitto
brew services start mosquitto
```

### Les données ne s'affichent pas

1. Vérifier que le backend est démarré
2. Vérifier que le client MQTT est démarré (`POST /api/mqtt/start`)
3. Vérifier qu'un simulateur publie des données
4. Vérifier les logs du backend

## 📚 Documentation complète

- **Installation** : `docs/INSTALLATION.md`
- **Guide d'utilisation** : `docs/USER_GUIDE.md`
- **Scripts** : `backend/scripts/README.md`
- **Frontend** : `frontend/README.md`

## 🎉 Prochaines étapes

1. **Explorer l'interface** : Naviguer entre les pages
2. **Tester les actions** : Contrôler les pompes, voir les prédictions
3. **Ajouter des capteurs** : Via le Setup Wizard
4. **Personnaliser** : Modifier les configurations, entraîner le modèle

## 📞 Support

Créer une issue sur GitHub : https://github.com/iamsernine/morocco-flood-monitoring/issues

---

**Bon test ! 🌊**
