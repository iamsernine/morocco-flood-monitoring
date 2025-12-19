# 📖 Guide d'utilisation - Morocco Flood Monitoring System

Guide complet pour utiliser le système de surveillance des inondations.

## 🚀 Démarrage rapide

### 1. Premier lancement

Après l'installation (voir `INSTALLATION.md`), suivez ces étapes:

```bash
# Terminal 1: Démarrer le broker MQTT
mosquitto

# Terminal 2: Démarrer le backend
cd backend
python app/main.py

# Terminal 3: Démarrer le frontend
cd frontend
pnpm dev
```

### 2. Configuration initiale

Au premier accès à `http://localhost:3000`, le **Setup Wizard** s'affiche automatiquement.

#### Étape 1: Configuration API

Remplir les clés API et paramètres MQTT:

- **Broker MQTT**: `localhost:1883` (par défaut)
- **OpenWeather API**: Votre clé API
- **OpenAI API**: Votre clé API
- **SMTP**: Configuration email pour les alertes

Vous pouvez cliquer sur **Passer** pour configurer plus tard.

#### Étape 2: Premier capteur

Ajouter au moins un capteur pour commencer:

- **Identifiant**: Ex: `CAS_1`
- **Ville**: Ex: `Casablanca`
- **Latitude**: Ex: `33.5731`
- **Longitude**: Ex: `-7.5898`
- **Description**: Optionnel

Cliquer sur **Terminer la configuration**.

### 3. Démarrer le client MQTT

```bash
curl -X POST http://localhost:5000/api/mqtt/start
```

### 4. Simuler un capteur

```bash
cd simulators
python sensor_simulator.py --sensor-id CAS_1 --city Casablanca
```

## 🖥️ Interface utilisateur

### Page d'accueil

**URL**: `http://localhost:3000/`

**Contenu**:
- Grille de toutes les villes surveillées
- Statistiques par ville (nombre de capteurs, niveau de risque)
- Carte "+ Ajouter" pour nouvelle ville/capteur

**Actions**:
- Cliquer sur une ville → Accéder à la page ville
- Cliquer sur "+ Ajouter" → Ouvrir le Setup Wizard

### Page ville

**URL**: `http://localhost:3000/city/:cityName`

**Contenu**:
- Grille de tous les capteurs de la ville
- Statut de chaque capteur (en ligne, hors ligne, inactif)
- Dernière activité
- Carte "+ Ajouter capteur"

**Actions**:
- Cliquer sur un capteur → Accéder à la page capteur
- Cliquer sur "+ Ajouter capteur" → Ouvrir le Setup Wizard

### Page capteur

**URL**: `http://localhost:3000/sensor/:sensorId`

**Contenu**:
- Prédiction IA en temps réel
- Probabilité d'inondation
- Niveau de risque (Low / Medium / High)
- Explication IA
- Historique des 10 dernières prédictions
- Informations du capteur

**Actions**:
- **Informer**: Envoyer une notification (à implémenter)
- **Pompe ON/OFF**: Contrôler la pompe via MQTT
- **Modifier**: Modifier les paramètres du capteur
- **Supprimer**: Supprimer le capteur

### Page carte

**URL**: `http://localhost:3000/map`

**Contenu**:
- Carte interactive du Maroc (Leaflet + OpenStreetMap)
- Marqueurs colorés selon le niveau de risque:
  - 🟢 Vert: Risque faible
  - 🟠 Orange: Risque modéré
  - 🔴 Rouge: Risque élevé
  - ⚫ Gris: Capteur inactif

**Actions**:
- Cliquer sur un marqueur → Popup avec détails
- Depuis le popup:
  - Voir les détails
  - Informer
  - Contrôler la pompe (ON/OFF)

### Setup Wizard

**URL**: `http://localhost:3000/setup`

**Contenu**:
- Configuration des API
- Ajout de villes et capteurs

**Accès**:
- Automatique au premier lancement
- Via le menu "Configuration"
- Via les cartes "+ Ajouter"

## 🔧 Fonctionnalités avancées

### Contrôle des pompes

Le système peut envoyer des commandes MQTT pour contrôler des pompes de drainage.

**Via l'interface**:
1. Accéder à la page capteur
2. Cliquer sur "Pompe ON" ou "Pompe OFF"

**Via l'API**:
```bash
curl -X POST http://localhost:5000/api/pump/control \
  -H "Content-Type: application/json" \
  -d '{
    "city": "Casablanca",
    "sensor_id": "CAS_1",
    "command": "ON"
  }'
```

**Topic MQTT**:
```
morocco/flood/pump/Casablanca/CAS_1
Payload: {"command": "ON", "timestamp": "2024-01-01T12:00:00"}
```

### Génération de rapports

Le système peut générer des rapports PDF avec OpenAI.

**Via l'API**:
```bash
curl -X POST http://localhost:5000/api/reports/generate \
  -H "Content-Type: application/json" \
  -d '{
    "cities": ["Casablanca", "Rabat"],
    "sensors": ["CAS_1", "RAB_1"],
    "metrics": ["water_level", "humidity"],
    "time_range": "7d",
    "language": "fr"
  }'
```

**Paramètres**:
- `cities`: Liste des villes
- `sensors`: Liste des capteurs
- `metrics`: Métriques à inclure
- `time_range`: Période (ex: "7d", "30d", "1h")
- `language`: Langue du rapport ("fr" ou "en")

### Alertes par email

Le système peut envoyer des alertes par email en cas de risque élevé.

**Configuration SMTP** (dans le Setup Wizard ou `.env`):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=votre@email.com
SMTP_PASSWORD=votre_mot_de_passe
```

**Déclenchement automatique**:
- Lorsqu'une prédiction atteint un risque "High"
- Email envoyé aux destinataires configurés

## 📊 Données et prédictions

### Comment fonctionnent les prédictions ?

1. **Collecte**: Les capteurs publient des données via MQTT
2. **Agrégation**: Le backend agrège les données toutes les 5 minutes
3. **Prédiction**: Le modèle ML calcule la probabilité d'inondation
4. **Stockage**: Les prédictions sont sauvegardées dans la base de données
5. **Affichage**: Le frontend affiche les prédictions en temps réel

### Métriques utilisées

Le modèle utilise ces métriques pour prédire:

- **water_level**: Niveau d'eau (0-100%)
- **humidity**: Humidité (0-100%)
- **rainfall**: Précipitations (mm)
- **temperature**: Température (°C)
- **wind_speed**: Vitesse du vent (km/h)
- **river_level**: Niveau de la rivière (0-100%)
- **soil_moisture**: Humidité du sol (0-100%)

### Niveaux de risque

- **Low** (Faible): Probabilité < 40%
- **Medium** (Modéré): Probabilité 40-70%
- **High** (Élevé): Probabilité > 70%

## 🧪 Mode test avec données synthétiques

Pour tester le système sans capteurs réels:

### 1. Générer des données de test

```bash
cd backend
python scripts/generate_test_data.py
```

Cela crée:
- 5 villes (Casablanca, Rabat, Marrakech, Fès, Tanger)
- 15-20 capteurs
- 7 jours d'historique de prédictions

### 2. Simuler des capteurs

```bash
# Simuler un capteur avec risque élevé
python simulators/sensor_simulator.py --sensor-id CAS_1 --city Casablanca --high-risk

# Simuler plusieurs capteurs en parallèle
python simulators/sensor_simulator.py --sensor-id CAS_1 --city Casablanca &
python simulators/sensor_simulator.py --sensor-id RAB_1 --city Rabat &
python simulators/sensor_simulator.py --sensor-id MAR_1 --city Marrakech &
```

## 🔍 Monitoring et logs

### Logs du backend

Les logs sont affichés dans la console où le backend est lancé:

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5000
```

### Logs MQTT

Pour voir les messages MQTT en temps réel:

```bash
mosquitto_sub -h localhost -t "morocco/flood/#" -v
```

### Vérifier l'état du système

```bash
# Health check
curl http://localhost:5000/api/health

# Statut MQTT
curl http://localhost:5000/api/mqtt/status

# Configuration
curl http://localhost:5000/api/config
```

## ⚠️ Limitations

### Version actuelle (v1.0)

- **Pas d'authentification**: Système local uniquement
- **Base de données SQLite**: Non adapté pour production
- **Modèle ML synthétique**: Entraîné sur données simulées
- **Pas de clustering**: Un seul serveur backend

### Pour la production

Il faudrait ajouter:
- Authentification JWT ou OAuth
- Base de données PostgreSQL/MySQL
- Modèle ML entraîné sur données réelles
- Load balancing et scaling
- Monitoring avancé (Prometheus, Grafana)
- Logs centralisés (ELK stack)
- Backup automatique
- HTTPS avec certificats SSL/TLS

## 🆘 Problèmes courants

### Les données ne s'affichent pas

1. Vérifier que le backend est démarré
2. Vérifier que le client MQTT est démarré (`POST /api/mqtt/start`)
3. Vérifier qu'un simulateur publie des données
4. Vérifier les logs du backend pour les erreurs

### Les prédictions sont toujours à 0%

1. Vérifier que le modèle ML est entraîné (`python scripts/train_model.py`)
2. Vérifier que `ml_models/flood_model.pkl` existe
3. Redémarrer le backend

### Le Setup Wizard ne se ferme pas

1. Vérifier qu'au moins un capteur a été ajouté
2. Vérifier que la configuration a été sauvegardée
3. Vider le cache du navigateur et recharger

### La carte ne s'affiche pas

1. Vérifier que Leaflet CSS est chargé
2. Vérifier la console du navigateur pour les erreurs
3. Vérifier que les capteurs ont des coordonnées valides

## 📞 Support

Pour toute question ou problème:

- Consulter la documentation dans `/docs`
- Vérifier les logs du backend et frontend
- Créer une issue sur GitHub

## 📄 Licence

Projet développé pour la Coupe du Monde 2030 au Maroc.
