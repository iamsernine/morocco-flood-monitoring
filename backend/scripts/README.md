# Scripts - Morocco Flood Monitoring System

Scripts utilitaires pour l'entraînement du modèle et la génération de données de test.

## 📜 Scripts disponibles

### `train_model.py`

Entraîne le modèle de prédiction d'inondation.

**Usage:**
```bash
cd backend
python scripts/train_model.py
```

**Fonctionnalités:**
- Génère des données synthétiques pour démonstration
- Entraîne un RandomForestClassifier
- Évalue les performances avec validation croisée
- Sauvegarde le modèle dans `ml_models/flood_model.pkl`

**Output:**
- Modèle entraîné: `ml_models/flood_model.pkl`
- Métriques de performance affichées dans la console

### `generate_test_data.py`

Peuple la base de données avec des données de démonstration.

**Usage:**
```bash
cd backend
python scripts/generate_test_data.py
```

**Données générées:**
- 5 villes marocaines (Casablanca, Rabat, Marrakech, Fès, Tanger)
- 2-4 capteurs par ville (15-20 capteurs au total)
- 7 jours d'historique de prédictions (4 prédictions/jour)

**⚠️ Note:** Ce script remplace les données existantes pour les villes et capteurs.

## 🔄 Workflow recommandé

### Premier démarrage

1. **Initialiser la base de données:**
   ```bash
   python app/models/database.py
   ```

2. **Entraîner le modèle:**
   ```bash
   python scripts/train_model.py
   ```

3. **Générer des données de test:**
   ```bash
   python scripts/generate_test_data.py
   ```

4. **Démarrer le backend:**
   ```bash
   python app/main.py
   ```

### Réentraînement du modèle

Si vous avez collecté de nouvelles données réelles:

1. Modifier `train_model.py` pour charger vos données
2. Réentraîner le modèle
3. Redémarrer le backend

## 📊 Données synthétiques

Les données générées par `train_model.py` sont purement synthétiques et basées sur des règles simplifiées:

**Features utilisées:**
- `water_level_avg`: Niveau d'eau moyen
- `water_level_max`: Niveau d'eau maximum
- `water_level_slope`: Tendance du niveau d'eau
- `humidity_avg`: Humidité moyenne
- `humidity_max`: Humidité maximum
- `humidity_slope`: Tendance de l'humidité
- `rainfall`: Précipitations
- `temperature`: Température
- `wind_speed`: Vitesse du vent
- `river_level`: Niveau de la rivière
- `soil_moisture`: Humidité du sol

**Règles de classification:**
- Inondation si niveau d'eau > 70%
- Inondation si précipitations > 40mm
- Inondation si combinaison de facteurs (eau + pluie, rivière + sol, etc.)

## 🔧 Personnalisation

### Utiliser vos propres données

Pour entraîner le modèle avec vos données réelles:

1. Préparer un fichier CSV avec les colonnes:
   - Features (voir liste ci-dessus)
   - `flood` (0 ou 1)

2. Modifier `train_model.py`:
   ```python
   # Remplacer generate_synthetic_data() par:
   df = pd.read_csv('path/to/your/data.csv')
   ```

3. Réentraîner le modèle

### Ajouter des features

1. Modifier la liste `feature_cols` dans `train_model.py`
2. Modifier `PredictionService` pour calculer les nouvelles features
3. Réentraîner le modèle

## 📝 Notes

- Le modèle par défaut est un **RandomForestClassifier**
- Les hyperparamètres peuvent être ajustés dans `train_model.py`
- Le scaler est sauvegardé avec le modèle pour normaliser les données
- Les métriques de performance sont incluses dans le fichier `.pkl`

## 🐛 Dépannage

### Erreur: "No module named 'sklearn'"

```bash
pip install scikit-learn
```

### Erreur: "No module named 'joblib'"

```bash
pip install joblib
```

### Le modèle ne se charge pas

- Vérifier que `ml_models/flood_model.pkl` existe
- Vérifier les permissions du fichier
- Réentraîner le modèle avec `train_model.py`
