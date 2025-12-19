# 📥 Import de capteurs au format plat

## Vue d'ensemble

Si vous avez un JSON avec une **liste plate de capteurs** (sans structure de villes), utilisez cette méthode. Les villes seront créées automatiquement et leurs coordonnées calculées comme la moyenne des capteurs.

---

## 🎯 Format JSON

### Votre format (liste plate)

```json
[
    {
        "sensor_id": "CAS_1",
        "city": "Casablanca",
        "lat": 33.5731,
        "lon": -7.5898
    },
    {
        "sensor_id": "CAS_2",
        "city": "Casablanca",
        "lat": 33.5850,
        "lon": -7.6100
    },
    {
        "sensor_id": "RAB_1",
        "city": "Rabat",
        "lat": 34.0209,
        "lon": -6.8416
    }
]
```

### Ce qui se passe automatiquement

1. **Détection des villes** : Les villes sont extraites automatiquement depuis le champ `city`
2. **Calcul des coordonnées** : Les coordonnées de chaque ville = moyenne des coordonnées de ses capteurs
3. **Création automatique** : Villes et capteurs créés en une seule commande

**Exemple** :
- Casablanca aura les coordonnées : `(33.5790, -7.6249)` (moyenne de CAS_1 et CAS_2)
- Rabat aura les coordonnées : `(34.0209, -6.8416)` (coordonnées de RAB_1)

---

## 🚀 Méthodes d'import

### Méthode 1 : Script Python (Recommandé)

```bash
cd backend
python scripts/import_sensors_flat.py your_sensors.json
```

**Avec remplacement des données existantes :**
```bash
python scripts/import_sensors_flat.py --file your_sensors.json --replace
```

### Méthode 2 : API REST

```bash
curl -X POST http://localhost:5000/api/sensors/import-flat \
  -H "Content-Type: application/json" \
  -d @your_sensors.json
```

**Avec remplacement :**
```bash
curl -X POST "http://localhost:5000/api/sensors/import-flat?replace=true" \
  -H "Content-Type: application/json" \
  -d @your_sensors.json
```

---

## 📝 Champs requis

Pour chaque capteur :

| Champ | Type | Description | Requis |
|-------|------|-------------|--------|
| `sensor_id` | string | Identifiant unique du capteur | ✅ Oui |
| `city` | string | Nom de la ville | ✅ Oui |
| `lat` | number | Latitude (-90 à 90) | ✅ Oui |
| `lon` | number | Longitude (-180 à 180) | ✅ Oui |
| `description` | string | Description du capteur | ❌ Non |

---

## 🧪 Exemple complet

### 1. Créer votre fichier JSON

Fichier `my_sensors.json` :

```json
[
    {
        "sensor_id": "MAR_1",
        "city": "Marrakech",
        "lat": 31.6295,
        "lon": -7.9811
    },
    {
        "sensor_id": "MAR_2",
        "city": "Marrakech",
        "lat": 31.6400,
        "lon": -7.9900
    },
    {
        "sensor_id": "AGA_1",
        "city": "Agadir",
        "lat": 30.4278,
        "lon": -9.5981
    }
]
```

### 2. Importer

```bash
cd backend
python scripts/import_sensors_flat.py my_sensors.json
```

### 3. Résultat

```
📊 Initialisation de la base de données...

📥 Import depuis my_sensors.json...
✅ 3 capteurs valides trouvés
✅ 2 villes détectées: Marrakech, Agadir

📍 Ville: Marrakech
   Coordonnées: (31.63475, -7.98555)
   Capteurs: 2
   ✅ Ville créée
      ✅ MAR_1
      ✅ MAR_2

📍 Ville: Agadir
   Coordonnées: (30.42780, -9.59810)
   Capteurs: 1
   ✅ Ville créée
      ✅ AGA_1

============================================================
✅ Import terminé!
   Villes créées: 2
   Capteurs importés: 3
============================================================
```

---

## 🌐 Via l'API REST

### Endpoint

```
POST /api/sensors/import-flat
```

### Query Parameters

- `replace` (optionnel) : `true` pour remplacer les données existantes

### Body

Liste de capteurs au format JSON :

```json
[
    {
        "sensor_id": "...",
        "city": "...",
        "lat": ...,
        "lon": ...
    }
]
```

### Réponse

```json
{
  "success": true,
  "data": {
    "cities_created": 2,
    "sensors_imported": 3,
    "total_cities": 2,
    "errors": []
  }
}
```

### Exemple avec curl

```bash
curl -X POST http://localhost:5000/api/sensors/import-flat \
  -H "Content-Type: application/json" \
  -d '[
    {
      "sensor_id": "TEST_1",
      "city": "TestCity",
      "lat": 30.0,
      "lon": -8.0
    }
  ]'
```

---

## ⚙️ Avantages du format plat

1. **Simplicité** : Pas besoin de structurer par ville
2. **Automatique** : Les villes sont créées automatiquement
3. **Coordonnées intelligentes** : Calculées automatiquement
4. **Flexible** : Ajouter des capteurs à différentes villes dans le même fichier

---

## 🔧 Dépannage

### Erreur : "Capteur existe déjà"

**Solution** : Utilisez `--replace` ou `?replace=true`

```bash
# Script
python scripts/import_sensors_flat.py --file sensors.json --replace

# API
curl -X POST "http://localhost:5000/api/sensors/import-flat?replace=true" \
  -H "Content-Type: application/json" \
  -d @sensors.json
```

### Erreur : "No valid sensors found"

**Causes possibles** :
- Champs manquants (`sensor_id`, `city`, `lat`, `lon`)
- Coordonnées invalides (hors plage)
- Format JSON incorrect

**Solution** : Vérifiez votre JSON sur https://jsonlint.com/

### Coordonnées de ville incorrectes

Les coordonnées de la ville sont calculées comme la **moyenne** des capteurs. Si vous voulez des coordonnées précises :

1. Utilisez le format hiérarchique (voir `IMPORT_JSON.md`)
2. Ou placez un capteur au centre exact de la ville

---

## 📊 Fichier exemple

Un fichier exemple est fourni :

```bash
backend/data/user_sensors.json
```

Il contient 40 capteurs répartis dans 6 villes.

---

## 🆚 Différence avec le format hiérarchique

| Caractéristique | Format plat | Format hiérarchique |
|----------------|-------------|---------------------|
| **Structure** | Liste de capteurs | Villes → Capteurs |
| **Coordonnées villes** | Calculées (moyenne) | Définies manuellement |
| **Simplicité** | ✅ Plus simple | ❌ Plus complexe |
| **Précision villes** | ❌ Approximative | ✅ Exacte |
| **Usage recommandé** | Import rapide | Configuration précise |

---

## ✅ Résumé

**Commande rapide :**

```bash
cd backend
python scripts/import_sensors_flat.py your_sensors.json
```

**Format minimal :**

```json
[
  {
    "sensor_id": "ID",
    "city": "Ville",
    "lat": 30.0,
    "lon": -8.0
  }
]
```

**Résultat :** Villes et capteurs créés automatiquement ! 🎉

---

## 📚 Ressources

- **Script** : `backend/scripts/import_sensors_flat.py`
- **Exemple** : `backend/data/user_sensors.json`
- **API** : `POST /api/sensors/import-flat`
- **Format hiérarchique** : `docs/IMPORT_JSON.md`
