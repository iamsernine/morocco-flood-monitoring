# 📥 Import de villes et capteurs depuis JSON

## Vue d'ensemble

Au lieu d'ajouter les villes et capteurs un par un via l'interface, vous pouvez les importer en masse depuis un fichier JSON.

---

## 🎯 Méthodes d'import

### Méthode 1 : Script Python (Recommandé)

```bash
cd backend
python scripts/import_from_json.py data/example_cities_sensors.json
```

**Avec remplacement des données existantes :**
```bash
python scripts/import_from_json.py --file data/example_cities_sensors.json --replace
```

### Méthode 2 : API REST

```bash
curl -X POST http://localhost:5000/api/sensors/import \
  -H "Content-Type: application/json" \
  -d @data/example_cities_sensors.json
```

---

## 📝 Format JSON

### Structure complète

```json
{
  "cities": [
    {
      "name": "Casablanca",
      "latitude": 33.5731,
      "longitude": -7.5898,
      "description": "Plus grande ville du Maroc",
      "sensors": [
        {
          "sensor_id": "CAS_1",
          "latitude": 33.5731,
          "longitude": -7.5898,
          "description": "Capteur zone portuaire"
        },
        {
          "sensor_id": "CAS_2",
          "latitude": 33.5850,
          "longitude": -7.6100,
          "description": "Capteur quartier Aïn Diab"
        }
      ]
    },
    {
      "name": "Rabat",
      "latitude": 34.0209,
      "longitude": -6.8416,
      "description": "Capitale du Maroc",
      "sensors": [
        {
          "sensor_id": "RAB_1",
          "latitude": 34.0209,
          "longitude": -6.8416,
          "description": "Capteur Bouregreg"
        }
      ]
    }
  ]
}
```

### Champs requis

#### Pour une ville :
- `name` (string) : Nom unique de la ville
- `latitude` (number) : Latitude (-90 à 90)
- `longitude` (number) : Longitude (-180 à 180)
- `description` (string, optionnel) : Description de la ville
- `sensors` (array, optionnel) : Liste des capteurs

#### Pour un capteur :
- `sensor_id` (string) : Identifiant unique du capteur
- `latitude` (number) : Latitude (-90 à 90)
- `longitude` (number) : Longitude (-180 à 180)
- `description` (string, optionnel) : Description du capteur

---

## 🚀 Exemple d'utilisation

### 1. Créer votre fichier JSON

Créez un fichier `my_cities.json` :

```json
{
  "cities": [
    {
      "name": "Agadir",
      "latitude": 30.4278,
      "longitude": -9.5981,
      "description": "Ville côtière du sud",
      "sensors": [
        {
          "sensor_id": "AGA_1",
          "latitude": 30.4278,
          "longitude": -9.5981,
          "description": "Capteur plage"
        }
      ]
    }
  ]
}
```

### 2. Importer les données

```bash
cd backend
python scripts/import_from_json.py my_cities.json
```

### 3. Vérifier l'import

```bash
# Via l'API
curl http://localhost:5000/api/cities

# Via le frontend
# Ouvrir http://localhost:3000
```

---

## ⚙️ Options avancées

### Mode remplacement

Par défaut, l'import ignore les villes/capteurs existants. Utilisez `--replace` pour les écraser :

```bash
python scripts/import_from_json.py --file data.json --replace
```

### Validation automatique

Le script valide automatiquement :
- ✅ Présence des champs requis
- ✅ Coordonnées GPS valides
- ✅ Format JSON correct
- ✅ IDs uniques

### Gestion des erreurs

Le script continue même en cas d'erreur et affiche un résumé :

```
✅ Import terminé!
   Villes importées: 4
   Capteurs importés: 12
   Erreurs: 2
```

---

## 🔧 Dépannage

### Erreur : "Ville existe déjà"

**Solution** : Utilisez `--replace` pour écraser les données existantes.

### Erreur : "Latitude invalide"

**Solution** : Vérifiez que les coordonnées sont dans les plages valides :
- Latitude : -90 à 90
- Longitude : -180 à 180

### Erreur : "Champ manquant"

**Solution** : Vérifiez que tous les champs requis sont présents dans votre JSON.

### Erreur : "JSON invalide"

**Solution** : Validez votre JSON sur https://jsonlint.com/

---

## 📊 Fichier exemple

Un fichier exemple complet est fourni :

```bash
backend/data/example_cities_sensors.json
```

Il contient 5 villes (Casablanca, Rabat, Marrakech, Fès, Tanger) avec 15 capteurs au total.

---

## 🌐 Via l'API REST

### Endpoint

```
POST /api/sensors/import
```

### Body

```json
{
  "cities": [...],
  "replace": false
}
```

### Réponse

```json
{
  "success": true,
  "data": {
    "cities_imported": 5,
    "sensors_imported": 15,
    "errors": []
  }
}
```

### Exemple avec curl

```bash
curl -X POST http://localhost:5000/api/sensors/import \
  -H "Content-Type: application/json" \
  -d '{
    "cities": [
      {
        "name": "Test City",
        "latitude": 30.0,
        "longitude": -8.0,
        "sensors": [
          {
            "sensor_id": "TEST_1",
            "latitude": 30.0,
            "longitude": -8.0
          }
        ]
      }
    ]
  }'
```

---

## ✅ Avantages de l'import JSON

1. **Rapidité** : Importer des dizaines de villes/capteurs en une seule commande
2. **Réutilisabilité** : Garder vos configurations dans des fichiers versionnés
3. **Partage** : Partager facilement vos configurations avec d'autres
4. **Automatisation** : Intégrer dans des scripts de déploiement
5. **Validation** : Validation automatique des données avant import

---

## 📚 Ressources

- **Script** : `backend/scripts/import_from_json.py`
- **Exemple** : `backend/data/example_cities_sensors.json`
- **API** : `POST /api/sensors/import`
- **Documentation API** : `docs/API.md`
