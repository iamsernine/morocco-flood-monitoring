# 🌊 Smart Flood Monitoring System - Morocco World Cup 2030

## 📋 Vue d'ensemble

Système intelligent de surveillance des inondations pour le Maroc dans le contexte de la Coupe du Monde 2030. Cette application web combine des capteurs IoT en temps réel, des données météorologiques externes, et l'intelligence artificielle pour prédire et expliquer les risques d'inondation urbaine.

**Approche AI-first** : L'IA est au cœur du système, l'IoT n'est qu'une source de données parmi d'autres.

## 🎯 Fonctionnalités principales

- **Surveillance en temps réel** : Collecte de données via MQTT depuis des capteurs IoT (niveau d'eau, humidité)
- **Prédiction IA** : Modèle ML local pour calculer la probabilité d'inondation (0-100%) et le niveau de risque
- **Explications intelligentes** : Génération de rapports en langage naturel via OpenAI API
- **Visualisation cartographique** : Carte interactive du Maroc avec marqueurs de capteurs et état des risques
- **Actions automatisées** : Activation de pompes via MQTT, notifications par email
- **Données externes** : Intégration OpenWeatherMap pour précipitations, température, vent
- **Simulation** : Génération de données river_level et soil_moisture si non disponibles

## 🏗️ Architecture technique

### Stack technologique

- **Frontend** : React + shadcn/ui (design minimal et professionnel)
- **Backend** : Flask (API REST + client MQTT)
- **Base de données** :
  - SQLite : configuration, métadonnées, capteurs, villes
  - Parquet : séries temporelles agrégées
- **IA** :
  - Modèle ML local (fichier remplaçable)
  - OpenAI API pour explications et rapports
- **Protocoles** : MQTT pour capteurs et actionneurs
- **Cartographie** : Leaflet ou Mapbox

### Structure du projet

```
morocco-flood-monitoring/
├── backend/                 # API Flask et logique métier
│   ├── app/                # Code principal de l'application
│   ├── data/               # Stockage SQLite et Parquet
│   ├── models/             # Modèles ML
│   ├── scripts/            # Scripts utilitaires
│   └── requirements.txt    # Dépendances Python
├── frontend/               # Application React
│   ├── src/               # Code source React
│   └── package.json       # Dépendances Node.js
├── docs/                  # Documentation
├── simulators/            # Simulateurs de capteurs IoT
└── README.md             # Ce fichier
```

## 🚀 Installation et démarrage

### Prérequis

- Python 3.8+
- Node.js 16+
- Broker MQTT (ex: Mosquitto)
- Clés API : OpenWeatherMap, OpenAI

### Installation Backend

```bash
cd backend
pip install -r requirements.txt
python app/main.py
```

### Installation Frontend

```bash
cd frontend
npm install
npm start
```

### Configuration initiale

Au premier lancement, un **Setup Wizard** vous guidera pour :

1. **Configuration API** : MQTT broker, OpenWeather API, OpenAI API, SMTP email
2. **Premier capteur** : Ajout obligatoire d'au moins un capteur (via formulaire ou JSON)

## 📊 Paramètres surveillés

### Capteurs MQTT (par ville/capteur)
- `water_level` : Niveau d'eau
- `humidity` : Humidité

### Données externes (par ville, cachées)
- `rainfall` : Précipitations
- `temperature` : Température
- `wind_speed` : Vitesse du vent
- `wind_direction` : Direction du vent

### Données simulées (si non disponibles)
- `river_level` : Niveau de la rivière
- `soil_moisture` : Humidité du sol

### Actionneurs
- `pump` : Pompe (ON/OFF) via MQTT

## 🧠 Couche IA

### Prédiction ML
- **Entrée** : Agrégation des paramètres (moyenne, max, pente)
- **Sortie** : Probabilité d'inondation (0-100%), niveau de risque (Low/Medium/High)

### Explications OpenAI
- Génération de texte en langage naturel pour expliquer les prédictions
- Rapports personnalisés (sélection de villes, capteurs, métriques, période)
- Optimisation des tokens pour minimiser les coûts

## 🗺️ Interface utilisateur

### Page d'accueil - Grille des villes
- Nom de la ville, nombre de capteurs, statut de risque IA
- Icône de notification (point rouge si inondation détectée/prédite)
- Carte "+ Ajouter ville/capteur"

### Page ville - Grille des capteurs
- Fil d'Ariane : Accueil > Ville
- Cartes de capteurs : ID, statut, icône d'alerte
- Carte "+ Ajouter capteur"

### Page capteur - Vue détaillée
- Fil d'Ariane : Accueil > Ville > Capteur
- Métriques en temps réel et agrégées
- Prédiction IA (probabilité, risque, explication)
- Boutons d'action : Informer, Activer pompe, Modifier, Supprimer

### Vue cartographique
- Maroc complet + Sahara Occidental
- Marqueurs de capteurs avec état actuel et prédit
- Vert = sûr, Rouge = risque d'inondation
- Clic sur marqueur → modal avec actions (informer/pompe)

## 📡 Flux de données

```
Capteurs/ESP32 → MQTT → Flask Receiver → Buffer → Agrégation → Parquet
                                       ↓
                                  OpenWeather API
                                       ↓
                                  Modèle ML → Prédiction
                                       ↓
                                  OpenAI API → Explication
                                       ↓
                                  Frontend React
```

### Topics MQTT

**Capteurs** :
- `sensors/{city}/{sensor_id}/water_level`
- `sensors/{city}/{sensor_id}/humidity`

**Actionneurs** :
- `actuators/{city}/{sensor_id}/pump`

## ⚙️ Règles importantes

- ✅ Pas d'authentification (démo locale uniquement)
- ✅ Tous les capteurs partagent les mêmes canaux (ne pas stocker les canaux dans sensors.json ou DB)
- ✅ Pas de duplication de canaux de capteurs
- ✅ Séparation backend/frontend stricte
- ✅ Architecture modulaire et extensible
- ✅ Focus sur l'IA, pas sur l'IoT

## 📝 Licence

Ce projet est développé dans le cadre de la préparation de la Coupe du Monde 2030 au Maroc.

## 👥 Contribution

Projet développé par un ingénieur full-stack IA senior pour démonstration et usage local.

---

**Note** : Ce système est conçu pour une démonstration locale. Pour un déploiement en production, ajoutez l'authentification, la sécurité, et l'évolutivité nécessaires.
