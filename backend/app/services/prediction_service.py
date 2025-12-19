"""
============================================================================
PREDICTION_SERVICE.PY - Service de prédiction d'inondation par IA
============================================================================
Description:
    Service qui utilise un modèle ML local pour prédire les risques
    d'inondation basé sur les données agrégées des capteurs et données
    externes.

Fonctionnalités:
    - Chargement du modèle ML (fichier .pkl remplaçable)
    - Préparation des features pour prédiction
    - Calcul de probabilité d'inondation (0-100%)
    - Détermination du niveau de risque (Low/Medium/High)
    - Sauvegarde des prédictions dans la DB
    - Génération d'explications via OpenAI

Usage:
    from app.services.prediction_service import PredictionService
    
    service = PredictionService()
    result = service.predict(sensor_id, input_data)
    # result = {'probability': 75.5, 'risk_level': 'High', 'explanation': '...'}

Debugging:
    - Vérifier que le modèle ML existe dans ml_models/
    - Vérifier que les features correspondent au modèle
    - Surveiller les logs de prédiction
    - Tester avec des données simulées
============================================================================
"""

import os
import joblib
import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.models import Prediction, get_db_session
from app.services.config_service import get_config_service


class PredictionService:
    """
    Service de prédiction d'inondation par IA.
    """
    
    # Seuils de risque
    RISK_THRESHOLDS = {
        'Low': (0, 30),
        'Medium': (30, 70),
        'High': (70, 100),
    }
    
    # Features attendues par le modèle (ordre important)
    FEATURE_NAMES = [
        'water_level_avg',
        'water_level_max',
        'water_level_slope',
        'humidity_avg',
        'humidity_max',
        'humidity_slope',
        'rainfall',
        'temperature',
        'wind_speed',
        'river_level',
        'soil_moisture',
    ]
    
    def __init__(self):
        """Initialise le service de prédiction."""
        self.config = get_config_service()
        self.model = None
        self.model_version = self.config.get('model_version', 'v1.0')
        
        # Chemin du modèle
        self.model_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'ml_models'
        )
        self.model_path = os.path.join(self.model_dir, 'flood_model.pkl')
        
        # Charger le modèle
        self._load_model()
    
    def _load_model(self):
        """
        Charge le modèle ML depuis le fichier.
        Si le modèle n'existe pas, utilise un modèle par défaut simple.
        """
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                print(f"✅ Modèle ML chargé: {self.model_path}")
            except Exception as e:
                print(f"❌ Erreur lors du chargement du modèle: {e}")
                self._create_default_model()
        else:
            print(f"⚠️  Modèle ML non trouvé, création d'un modèle par défaut")
            self._create_default_model()
    
    def _create_default_model(self):
        """
        Crée un modèle par défaut simple basé sur des règles.
        Ce modèle sera remplacé par un vrai modèle ML entraîné.
        """
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.preprocessing import StandardScaler
        
        # Créer un modèle simple (sera entraîné avec de vraies données plus tard)
        self.model = {
            'classifier': RandomForestClassifier(n_estimators=10, random_state=42),
            'scaler': StandardScaler(),
            'is_default': True
        }
        
        # Sauvegarder le modèle par défaut
        os.makedirs(self.model_dir, exist_ok=True)
        joblib.dump(self.model, self.model_path)
        print(f"💾 Modèle par défaut créé: {self.model_path}")
    
    def reload_model(self) -> bool:
        """
        Recharge le modèle ML (utile après mise à jour).
        
        Returns:
            True si succès, False sinon
        """
        try:
            self._load_model()
            return True
        except Exception as e:
            print(f"❌ Erreur lors du rechargement du modèle: {e}")
            return False
    
    def _prepare_features(self, input_data: Dict[str, Any]) -> np.ndarray:
        """
        Prépare les features pour la prédiction.
        
        Args:
            input_data: Dictionnaire avec les données d'entrée
        
        Returns:
            Array numpy avec les features dans le bon ordre
        """
        features = []
        for feature_name in self.FEATURE_NAMES:
            value = input_data.get(feature_name, 0.0)
            features.append(float(value))
        
        return np.array([features])
    
    def _calculate_probability_rule_based(self, input_data: Dict[str, Any]) -> float:
        """
        Calcule la probabilité d'inondation avec des règles simples.
        Utilisé comme fallback si le modèle ML n'est pas disponible.
        
        Args:
            input_data: Dictionnaire avec les données d'entrée
        
        Returns:
            Probabilité entre 0 et 100
        """
        probability = 0.0
        
        # Niveau d'eau (poids: 40%)
        water_level = input_data.get('water_level_avg', 0)
        if water_level > 80:
            probability += 40
        elif water_level > 60:
            probability += 30
        elif water_level > 40:
            probability += 15
        
        # Pente du niveau d'eau (poids: 20%)
        water_slope = input_data.get('water_level_slope', 0)
        if water_slope > 1.0:
            probability += 20
        elif water_slope > 0.5:
            probability += 10
        
        # Précipitations (poids: 20%)
        rainfall = input_data.get('rainfall', 0)
        if rainfall > 30:
            probability += 20
        elif rainfall > 15:
            probability += 10
        
        # Niveau de la rivière (poids: 10%)
        river_level = input_data.get('river_level', 0)
        if river_level > 70:
            probability += 10
        elif river_level > 50:
            probability += 5
        
        # Humidité du sol (poids: 10%)
        soil_moisture = input_data.get('soil_moisture', 0)
        if soil_moisture > 80:
            probability += 10
        elif soil_moisture > 60:
            probability += 5
        
        return min(probability, 100.0)
    
    def _determine_risk_level(self, probability: float) -> str:
        """
        Détermine le niveau de risque basé sur la probabilité.
        
        Args:
            probability: Probabilité d'inondation (0-100)
        
        Returns:
            'Low', 'Medium', ou 'High'
        """
        for risk_level, (min_prob, max_prob) in self.RISK_THRESHOLDS.items():
            if min_prob <= probability < max_prob:
                return risk_level
        return 'High'  # Par défaut si >= 70
    
    def predict(self, sensor_id: str, city_name: str, 
                input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Effectue une prédiction d'inondation.
        
        Args:
            sensor_id: Identifiant du capteur
            city_name: Nom de la ville
            input_data: Données d'entrée (features)
        
        Returns:
            Dictionnaire avec probability, risk_level, explanation
        """
        try:
            # Préparer les features
            features = self._prepare_features(input_data)
            
            # Prédiction
            if self.model and not self.model.get('is_default'):
                # Utiliser le modèle ML
                scaler = self.model.get('scaler')
                classifier = self.model.get('classifier')
                
                if scaler and classifier:
                    features_scaled = scaler.transform(features)
                    probability = float(classifier.predict_proba(features_scaled)[0][1] * 100)
                else:
                    probability = self._calculate_probability_rule_based(input_data)
            else:
                # Utiliser les règles simples
                probability = self._calculate_probability_rule_based(input_data)
            
            # Déterminer le niveau de risque
            risk_level = self._determine_risk_level(probability)
            
            # Résultat
            result = {
                'sensor_id': sensor_id,
                'city_name': city_name,
                'probability': round(probability, 2),
                'risk_level': risk_level,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Sauvegarder la prédiction dans la DB
            self._save_prediction(sensor_id, city_name, input_data, probability, risk_level)
            
            return result
        
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction pour {sensor_id}: {e}")
            return {
                'sensor_id': sensor_id,
                'city_name': city_name,
                'probability': 0.0,
                'risk_level': 'Low',
                'error': str(e),
            }
    
    def _save_prediction(self, sensor_id: str, city_name: str, 
                        input_data: Dict[str, Any], probability: float, 
                        risk_level: str):
        """
        Sauvegarde une prédiction dans la base de données.
        
        Args:
            sensor_id: Identifiant du capteur
            city_name: Nom de la ville
            input_data: Données d'entrée
            probability: Probabilité calculée
            risk_level: Niveau de risque
        """
        session = get_db_session()
        try:
            prediction = Prediction(
                sensor_id=sensor_id,
                city_name=city_name,
                timestamp=datetime.utcnow(),
                input_data=input_data,
                flood_probability=probability,
                risk_level=risk_level,
                model_version=self.model_version,
            )
            session.add(prediction)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la sauvegarde de la prédiction: {e}")
        finally:
            session.close()
    
    def get_prediction_history(self, sensor_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Récupère l'historique des prédictions pour un capteur.
        
        Args:
            sensor_id: Identifiant du capteur
            limit: Nombre maximum de prédictions à retourner
        
        Returns:
            Liste de prédictions
        """
        session = get_db_session()
        try:
            predictions = session.query(Prediction)\
                .filter_by(sensor_id=sensor_id)\
                .order_by(Prediction.timestamp.desc())\
                .limit(limit)\
                .all()
            
            return [
                {
                    'timestamp': p.timestamp.isoformat(),
                    'probability': p.flood_probability,
                    'risk_level': p.risk_level,
                    'model_version': p.model_version,
                }
                for p in predictions
            ]
        finally:
            session.close()
    
    def get_current_risk_summary(self) -> Dict[str, Any]:
        """
        Récupère un résumé des risques actuels pour toutes les villes.
        
        Returns:
            Dictionnaire avec statistiques par ville
        """
        session = get_db_session()
        try:
            # Récupérer les dernières prédictions par capteur
            from sqlalchemy import func
            
            subquery = session.query(
                Prediction.sensor_id,
                func.max(Prediction.timestamp).label('max_timestamp')
            ).group_by(Prediction.sensor_id).subquery()
            
            latest_predictions = session.query(Prediction).join(
                subquery,
                (Prediction.sensor_id == subquery.c.sensor_id) &
                (Prediction.timestamp == subquery.c.max_timestamp)
            ).all()
            
            # Grouper par ville
            summary = {}
            for pred in latest_predictions:
                city = pred.city_name
                if city not in summary:
                    summary[city] = {
                        'total_sensors': 0,
                        'high_risk': 0,
                        'medium_risk': 0,
                        'low_risk': 0,
                        'avg_probability': 0.0,
                        'max_probability': 0.0,
                    }
                
                summary[city]['total_sensors'] += 1
                summary[city][f'{pred.risk_level.lower()}_risk'] += 1
                summary[city]['avg_probability'] += pred.flood_probability
                summary[city]['max_probability'] = max(
                    summary[city]['max_probability'],
                    pred.flood_probability
                )
            
            # Calculer les moyennes
            for city in summary:
                if summary[city]['total_sensors'] > 0:
                    summary[city]['avg_probability'] /= summary[city]['total_sensors']
                    summary[city]['avg_probability'] = round(summary[city]['avg_probability'], 2)
            
            return summary
        
        finally:
            session.close()


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    from app.models import init_db
    
    print("Initialisation de la base de données...")
    init_db()
    
    print("\nTest du PredictionService...")
    service = PredictionService()
    
    # Données de test
    test_data = {
        'water_level_avg': 75.0,
        'water_level_max': 80.0,
        'water_level_slope': 1.5,
        'humidity_avg': 70.0,
        'humidity_max': 75.0,
        'humidity_slope': 0.5,
        'rainfall': 35.0,
        'temperature': 22.0,
        'wind_speed': 15.0,
        'river_level': 65.0,
        'soil_moisture': 80.0,
    }
    
    # Test prédiction
    result = service.predict('CAS_1', 'Casablanca', test_data)
    print(f"\nRésultat de prédiction:")
    print(f"  Probabilité: {result['probability']}%")
    print(f"  Niveau de risque: {result['risk_level']}")
    
    # Test résumé des risques
    summary = service.get_current_risk_summary()
    print(f"\nRésumé des risques: {summary}")
    
    print("\n✅ Tests terminés!")
