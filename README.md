# 🌊 Morocco Flood Monitoring System

**Système intelligent de surveillance des inondations pour la Coupe du Monde 2030 au Maroc**

[![GitHub](https://img.shields.io/badge/GitHub-iamsernine%2Fmorocco--flood--monitoring-blue)](https://github.com/iamsernine/morocco-flood-monitoring)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18-blue)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)

---

## 📋 Description

Système de surveillance en temps réel des inondations conçu pour protéger les infrastructures et la population lors de la Coupe du Monde 2030 au Maroc. Le système combine IoT, IA prédictive, et visualisation cartographique pour une gestion proactive des risques d'inondation.

### 🎯 Objectifs

- **Prévention** : Anticiper les inondations avec des prédictions IA
- **Réaction rapide** : Alertes en temps réel et contrôle automatisé des pompes
- **Visualisation** : Interface intuitive avec carte interactive
- **Scalabilité** : Architecture modulaire pour déploiement multi-villes

### ✨ Fonctionnalités principales

#### 🔮 Prédiction IA
- Modèle ML (RandomForest) entraîné sur données historiques
- Prédictions toutes les 5 minutes
- Niveaux de risque : Low, Medium, High
- Explications générées par OpenAI

#### 📡 IoT & MQTT
- Collecte temps réel via MQTT
- Support multi-capteurs (niveau d'eau, humidité, etc.)
- Buffers roulants pour agrégation
- Simulateur de capteurs inclus

#### 🗺️ Cartographie
- Carte interactive du Maroc (Leaflet + OpenStreetMap)
- Marqueurs colorés selon le niveau de risque
- Popups avec actions (informer, contrôler pompes)

#### 🎛️ Contrôle automatisé
- Activation/désactivation des pompes via MQTT
- Notifications par email (SMTP)
- Génération de rapports PDF (OpenAI)

#### 💻 Interface moderne
- Design minimal et professionnel (shadcn/ui)
- Grilles responsives (villes → capteurs → détails)
- Setup Wizard pour configuration initiale
- Pas d'authentification (démo locale)

---

## 🏗️ Architecture

### Stack technique

**Backend**
- **Framework** : Flask + FastAPI
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **MQTT** : Paho MQTT Client
- **ML** : scikit-learn (RandomForest)
- **IA** : OpenAI API
- **API météo** : OpenWeatherMap

**Frontend**
- **Framework** : React 18 + TypeScript
- **Bundler** : Vite
- **Styling** : Tailwind CSS
- **UI** : shadcn/ui
- **Routing** : React Router
- **Carte** : Leaflet + React-Leaflet
- **HTTP** : Axios

**Infrastructure**
- **Broker MQTT** : Mosquitto
- **Déploiement** : Local (dev) / Docker (prod)

---

## 🚀 Installation

### Méthode rapide (5 minutes)

Voir **[QUICKSTART.md](QUICKSTART.md)** pour un démarrage rapide.

### Installation complète

Voir **[docs/INSTALLATION.md](docs/INSTALLATION.md)** pour le guide complet.

### Résumé

```bash
# 1. Cloner le dépôt
git clone https://github.com/iamsernine/morocco-flood-monitoring.git
cd morocco-flood-monitoring

# 2. Backend
cd backend
pip install -r requirements.txt
python app/models/database.py
python scripts/train_model.py
python scripts/generate_test_data.py
python app/main.py

# 3. Frontend (nouveau terminal)
cd frontend
pnpm install
pnpm dev

# 4. MQTT (nouveau terminal)
mosquitto

# 5. Démarrer le client MQTT
curl -X POST http://localhost:5000/api/mqtt/start

# 6. Simuler un capteur (nouveau terminal)
cd simulators
python sensor_simulator.py --sensor-id CAS_1 --city Casablanca
```

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** : Démarrage rapide en 5 minutes
- **[docs/INSTALLATION.md](docs/INSTALLATION.md)** : Guide d'installation complet
- **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)** : Guide d'utilisation détaillé
- **[backend/scripts/README.md](backend/scripts/README.md)** : Documentation des scripts
- **[frontend/README.md](frontend/README.md)** : Documentation du frontend

---

## 📁 Structure du projet

```
morocco-flood-monitoring/
├── backend/                    # Backend Flask
│   ├── app/
│   │   ├── api/               # Routes API REST
│   │   ├── models/            # Modèles de base de données
│   │   ├── mqtt/              # Client MQTT
│   │   ├── services/          # Services métier
│   │   └── main.py            # Point d'entrée
│   ├── data/                  # Données (SQLite, Parquet)
│   ├── ml_models/             # Modèles ML entraînés
│   ├── scripts/               # Scripts utilitaires
│   │   ├── train_model.py     # Entraînement du modèle
│   │   └── generate_test_data.py  # Génération de données de test
│   └── requirements.txt       # Dépendances Python
│
├── frontend/                  # Frontend React
│   ├── src/
│   │   ├── components/        # Composants réutilisables
│   │   │   ├── ui/           # Composants UI (shadcn/ui)
│   │   │   └── Layout.tsx    # Layout principal
│   │   ├── pages/            # Pages de l'application
│   │   │   ├── HomePage.tsx
│   │   │   ├── CityPage.tsx
│   │   │   ├── SensorPage.tsx
│   │   │   ├── MapPage.tsx
│   │   │   └── SetupWizard.tsx
│   │   ├── services/         # Services API
│   │   ├── lib/              # Utilitaires
│   │   └── App.tsx           # Composant racine
│   ├── package.json
│   └── vite.config.ts
│
├── simulators/               # Simulateurs de capteurs
│   └── sensor_simulator.py
│
├── docs/                     # Documentation
│   ├── INSTALLATION.md
│   └── USER_GUIDE.md
│
├── README.md                 # Ce fichier
└── QUICKSTART.md            # Guide de démarrage rapide
```

---

## 🧪 Tests et démonstration

### Générer des données de test

```bash
cd backend
python scripts/generate_test_data.py
```

Cela crée :
- 5 villes (Casablanca, Rabat, Marrakech, Fès, Tanger)
- 15-20 capteurs
- 7 jours d'historique de prédictions

### Simuler des capteurs

```bash
# Capteur normal
python simulators/sensor_simulator.py --sensor-id CAS_1 --city Casablanca

# Capteur avec risque élevé
python simulators/sensor_simulator.py --sensor-id CAS_1 --city Casablanca --high-risk

# Plusieurs capteurs en parallèle
python simulators/sensor_simulator.py --sensor-id CAS_1 --city Casablanca &
python simulators/sensor_simulator.py --sensor-id RAB_1 --city Rabat &
python simulators/sensor_simulator.py --sensor-id MAR_1 --city Marrakech &
```

---

## 🔧 API REST

### Endpoints principaux

#### Configuration
- `GET /api/config` - Récupérer la configuration
- `POST /api/config` - Mettre à jour la configuration
- `GET /api/config/setup-status` - Statut du setup
- `POST /api/config/complete-setup` - Marquer le setup comme complété

#### Villes
- `GET /api/cities` - Liste des villes
- `POST /api/cities` - Ajouter une ville

#### Capteurs
- `GET /api/sensors` - Liste des capteurs
- `POST /api/sensors` - Ajouter un capteur
- `DELETE /api/sensors/:id` - Supprimer un capteur

#### Prédictions
- `GET /api/predictions/:sensor_id` - Prédictions d'un capteur
- `GET /api/predictions/summary` - Résumé des prédictions

#### Contrôle
- `POST /api/pump/control` - Contrôler une pompe
- `POST /api/mqtt/start` - Démarrer le client MQTT
- `POST /api/mqtt/stop` - Arrêter le client MQTT
- `GET /api/mqtt/status` - Statut du client MQTT

#### Rapports
- `POST /api/reports/generate` - Générer un rapport PDF

Voir la documentation complète dans **[docs/USER_GUIDE.md](docs/USER_GUIDE.md)**.

---

## 🤖 Modèle ML

### Algorithme

**RandomForestClassifier** (scikit-learn)

### Features

- `water_level_avg` : Niveau d'eau moyen
- `water_level_max` : Niveau d'eau maximum
- `water_level_slope` : Tendance du niveau d'eau
- `humidity_avg` : Humidité moyenne
- `humidity_max` : Humidité maximum
- `humidity_slope` : Tendance de l'humidité
- `rainfall` : Précipitations
- `temperature` : Température
- `wind_speed` : Vitesse du vent
- `river_level` : Niveau de la rivière
- `soil_moisture` : Humidité du sol

### Entraînement

```bash
cd backend
python scripts/train_model.py
```

Le modèle est sauvegardé dans `ml_models/flood_model.pkl`.

### Performances

Sur données synthétiques :
- **ROC-AUC** : ~0.95
- **Précision** : ~90%
- **Rappel** : ~85%

---

## 🌐 Déploiement

### Local (développement)

Voir **[QUICKSTART.md](QUICKSTART.md)**.

### Production

**⚠️ ATTENTION** : Ce système est conçu pour une démonstration locale uniquement.

Pour un déploiement en production, ajoutez :

1. **Authentification** : JWT, OAuth
2. **HTTPS** : Certificats SSL/TLS
3. **Base de données** : PostgreSQL ou MySQL
4. **Reverse proxy** : Nginx ou Apache
5. **Monitoring** : Prometheus, Grafana
6. **Logs** : Centralisation avec ELK stack
7. **Backup** : Sauvegarde automatique
8. **Scaling** : Load balancing, Redis

---

## 🤝 Contribution

Les contributions sont les bienvenues !

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📄 Licence

Projet développé pour la Coupe du Monde 2030 au Maroc.

---

## 👨‍💻 Auteur

Développé par **iamsernine** pour la Coupe du Monde 2030 au Maroc.

---

## 🙏 Remerciements

- **OpenWeatherMap** pour l'API météo
- **OpenAI** pour l'API d'IA générative
- **shadcn/ui** pour les composants UI
- **Leaflet** pour la cartographie
- **Eclipse Mosquitto** pour le broker MQTT

---

## 📞 Support

- **Issues** : [GitHub Issues](https://github.com/iamsernine/morocco-flood-monitoring/issues)
- **Documentation** : [docs/](docs/)

---

**🌊 Protégeons le Maroc ensemble pour la Coupe du Monde 2030 ! ⚽**
