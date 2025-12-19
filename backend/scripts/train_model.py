"""
============================================================================
TRAIN_MODEL.PY - Script d'entraînement du modèle ML
============================================================================
Description:
    Entraîne un modèle de prédiction d'inondation basé sur des données
    historiques. Utilise RandomForestClassifier pour la classification
    binaire (inondation / pas d'inondation).

Fonctionnalités:
    - Génération de données synthétiques pour démonstration
    - Entraînement du modèle avec validation croisée
    - Sauvegarde du modèle et du scaler
    - Évaluation des performances

Usage:
    python scripts/train_model.py

Debugging:
    - Vérifier que scikit-learn est installé
    - Vérifier que le dossier ml_models/ existe
    - Inspecter les métriques de performance
============================================================================
"""

import os
import sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import joblib

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def generate_synthetic_data(n_samples=10000):
    """
    Génère des données synthétiques pour l'entraînement.
    
    En production, ces données seraient remplacées par des données
    historiques réelles collectées par les capteurs.
    
    Args:
        n_samples: Nombre d'échantillons à générer
    
    Returns:
        DataFrame avec features et target
    """
    print(f"Génération de {n_samples} échantillons synthétiques...")
    
    np.random.seed(42)
    
    # Features
    data = {
        'water_level_avg': np.random.uniform(0, 100, n_samples),
        'water_level_max': np.random.uniform(0, 100, n_samples),
        'water_level_slope': np.random.uniform(-5, 5, n_samples),
        'humidity_avg': np.random.uniform(0, 100, n_samples),
        'humidity_max': np.random.uniform(0, 100, n_samples),
        'humidity_slope': np.random.uniform(-2, 2, n_samples),
        'rainfall': np.random.uniform(0, 100, n_samples),
        'temperature': np.random.uniform(5, 45, n_samples),
        'wind_speed': np.random.uniform(0, 50, n_samples),
        'river_level': np.random.uniform(0, 100, n_samples),
        'soil_moisture': np.random.uniform(0, 100, n_samples),
    }
    
    df = pd.DataFrame(data)
    
    # Logique de génération du target (inondation)
    # Règles simplifiées pour la démonstration
    flood = (
        (df['water_level_avg'] > 70) |
        (df['rainfall'] > 40) |
        ((df['water_level_avg'] > 50) & (df['rainfall'] > 25)) |
        ((df['river_level'] > 70) & (df['soil_moisture'] > 80)) |
        ((df['water_level_slope'] > 2) & (df['water_level_avg'] > 40))
    ).astype(int)
    
    df['flood'] = flood
    
    # Ajouter du bruit pour rendre les données plus réalistes
    noise_indices = np.random.choice(len(df), size=int(len(df) * 0.1), replace=False)
    df.loc[noise_indices, 'flood'] = 1 - df.loc[noise_indices, 'flood']
    
    print(f"✅ Données générées: {len(df)} échantillons")
    print(f"   - Inondations: {df['flood'].sum()} ({df['flood'].mean()*100:.1f}%)")
    print(f"   - Pas d'inondation: {(1-df['flood']).sum()} ({(1-df['flood']).mean()*100:.1f}%)")
    
    return df


def train_model(df):
    """
    Entraîne le modèle de prédiction.
    
    Args:
        df: DataFrame avec features et target
    
    Returns:
        Tuple (model, scaler, metrics)
    """
    print("\n🔧 Entraînement du modèle...")
    
    # Séparer features et target
    feature_cols = [
        'water_level_avg', 'water_level_max', 'water_level_slope',
        'humidity_avg', 'humidity_max', 'humidity_slope',
        'rainfall', 'temperature', 'wind_speed',
        'river_level', 'soil_moisture'
    ]
    
    X = df[feature_cols]
    y = df['flood']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"   - Train: {len(X_train)} échantillons")
    print(f"   - Test: {len(X_test)} échantillons")
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entraînement
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train_scaled, y_train)
    
    # Validation croisée
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
    print(f"\n📊 Validation croisée (ROC-AUC): {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    
    # Évaluation sur le test set
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    print("\n📈 Performances sur le test set:")
    print(classification_report(y_test, y_pred, target_names=['Pas d\'inondation', 'Inondation']))
    
    print("\nMatrice de confusion:")
    print(confusion_matrix(y_test, y_pred))
    
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    print(f"\nROC-AUC Score: {roc_auc:.4f}")
    
    # Feature importance
    print("\n🔍 Importance des features:")
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.iterrows():
        print(f"   {row['feature']:25s}: {row['importance']:.4f}")
    
    metrics = {
        'cv_roc_auc': cv_scores.mean(),
        'test_roc_auc': roc_auc,
        'feature_importance': feature_importance.to_dict('records')
    }
    
    return model, scaler, metrics


def save_model(model, scaler, metrics):
    """
    Sauvegarde le modèle et le scaler.
    
    Args:
        model: Modèle entraîné
        scaler: Scaler pour normalisation
        metrics: Métriques de performance
    """
    print("\n💾 Sauvegarde du modèle...")
    
    # Créer le dossier ml_models
    model_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'ml_models'
    )
    os.makedirs(model_dir, exist_ok=True)
    
    # Sauvegarder le modèle
    model_path = os.path.join(model_dir, 'flood_model.pkl')
    
    model_data = {
        'classifier': model,
        'scaler': scaler,
        'metrics': metrics,
        'is_default': False
    }
    
    joblib.dump(model_data, model_path)
    
    print(f"✅ Modèle sauvegardé: {model_path}")
    print(f"   - Taille: {os.path.getsize(model_path) / 1024:.2f} KB")


def main():
    """Fonction principale."""
    print("=" * 80)
    print("🌊 ENTRAÎNEMENT DU MODÈLE DE PRÉDICTION D'INONDATION")
    print("=" * 80)
    
    # Générer des données synthétiques
    df = generate_synthetic_data(n_samples=10000)
    
    # Entraîner le modèle
    model, scaler, metrics = train_model(df)
    
    # Sauvegarder le modèle
    save_model(model, scaler, metrics)
    
    print("\n" + "=" * 80)
    print("✅ ENTRAÎNEMENT TERMINÉ AVEC SUCCÈS")
    print("=" * 80)
    print("\nLe modèle est prêt à être utilisé par le service de prédiction.")
    print("Redémarrez le backend pour charger le nouveau modèle.")


if __name__ == '__main__':
    main()
