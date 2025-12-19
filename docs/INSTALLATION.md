# 📦 Guide d'installation - Morocco Flood Monitoring System

Guide complet pour installer et démarrer le système de surveillance des inondations.

## 📋 Prérequis

### Logiciels requis

- **Python 3.8+** (pour le backend)
- **Node.js 16+** (pour le frontend)
- **pnpm** (gestionnaire de paquets Node.js)
- **Broker MQTT** (ex: Mosquitto)

### Clés API requises

- **OpenWeatherMap API** : [https://openweathermap.org/api](https://openweathermap.org/api)
- **OpenAI API** : [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)

## 🔧 Installation du Backend

### 1. Cloner le dépôt

```bash
git clone https://github.com/iamsernine/morocco-flood-monitoring.git
cd morocco-flood-monitoring
```

### 2. Installer les dépendances Python

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configuration

Copier le fichier d'exemple et le remplir :

```bash
cp .env.example .env
nano .env
```

Remplir les valeurs :

```env
# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_BROKER_USERNAME=
MQTT_BROKER_PASSWORD=

# OpenWeather API
OPENWEATHER_API_KEY=votre_cle_ici

# OpenAI API
OPENAI_API_KEY=votre_cle_ici

# SMTP Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SENDER=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe
```

### 4. Initialiser la base de données

```bash
python app/models/database.py
```

### 5. Démarrer le backend

```bash
python app/main.py
```

Le backend sera accessible sur `http://localhost:5000`

## 🎨 Installation du Frontend

### 1. Installer les dépendances

```bash
cd frontend
pnpm install
```

### 2. Démarrer le frontend

```bash
pnpm dev
```

Le frontend sera accessible sur `http://localhost:3000`

## 🦟 Installation de Mosquitto (Broker MQTT)

### Ubuntu/Debian

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
```

### macOS

```bash
brew install mosquitto
brew services start mosquitto
```

### Windows

Télécharger depuis [https://mosquitto.org/download/](https://mosquitto.org/download/)

### Tester le broker

```bash
# Terminal 1: Subscriber
mosquitto_sub -h localhost -t test

# Terminal 2: Publisher
mosquitto_pub -h localhost -t test -m "Hello MQTT"
```

## 🧪 Tester le système

### 1. Vérifier le backend

```bash
curl http://localhost:5000/api/health
```

Réponse attendue :
```json
{
  "success": true,
  "message": "API is healthy",
  "timestamp": "2024-01-01T12:00:00.000000"
}
```

### 2. Démarrer le client MQTT

```bash
curl -X POST http://localhost:5000/api/mqtt/start
```

### 3. Simuler un capteur

```bash
cd simulators
python sensor_simulator.py --sensor-id CAS_1 --city Casablanca
```

### 4. Accéder au frontend

Ouvrir `http://localhost:3000` dans le navigateur.

Au premier lancement, le **Setup Wizard** s'affichera pour configurer le système.

## 📊 Vérification de l'installation

### Backend

- ✅ API accessible sur port 5000
- ✅ Base de données SQLite créée dans `backend/data/sqlite/`
- ✅ Client MQTT connecté au broker
- ✅ Endpoints API fonctionnels

### Frontend

- ✅ Application React accessible sur port 3000
- ✅ Communication avec l'API backend
- ✅ Setup Wizard affiché au premier lancement
- ✅ Navigation entre les pages fonctionnelle

### MQTT

- ✅ Broker Mosquitto en cours d'exécution
- ✅ Client MQTT backend connecté
- ✅ Simulateur de capteur publiant des données
- ✅ Données reçues et agrégées

## 🐛 Dépannage

### Le backend ne démarre pas

- Vérifier que Python 3.8+ est installé : `python --version`
- Vérifier que toutes les dépendances sont installées : `pip list`
- Vérifier les logs d'erreur dans la console

### Le frontend ne démarre pas

- Vérifier que Node.js 16+ est installé : `node --version`
- Vérifier que pnpm est installé : `pnpm --version`
- Supprimer `node_modules` et réinstaller : `rm -rf node_modules && pnpm install`

### Le client MQTT ne se connecte pas

- Vérifier que Mosquitto est en cours d'exécution : `systemctl status mosquitto`
- Vérifier le port 1883 : `netstat -an | grep 1883`
- Vérifier la configuration dans `.env`

### Les données ne s'affichent pas

- Vérifier que le client MQTT est démarré : `POST /api/mqtt/start`
- Vérifier qu'un simulateur est en cours d'exécution
- Vérifier les logs du backend pour les erreurs
- Vérifier la console du navigateur pour les erreurs API

## 🚀 Déploiement en production

**⚠️ ATTENTION** : Ce système est conçu pour une démonstration locale uniquement.

Pour un déploiement en production, ajoutez :

1. **Authentification** : JWT, OAuth, ou système de login
2. **HTTPS** : Certificats SSL/TLS
3. **Base de données** : PostgreSQL ou MySQL au lieu de SQLite
4. **Reverse proxy** : Nginx ou Apache
5. **Monitoring** : Prometheus, Grafana
6. **Logs** : Centralisation avec ELK stack
7. **Backup** : Sauvegarde automatique de la base de données
8. **Scaling** : Load balancing, Redis pour le cache

## 📞 Support

Pour toute question ou problème :

- Créer une issue sur GitHub
- Consulter la documentation dans `/docs`
- Vérifier les logs du backend et frontend

## 📄 Licence

Projet développé pour la Coupe du Monde 2030 au Maroc.
