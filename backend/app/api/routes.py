"""
============================================================================
ROUTES.PY - Routes API REST Flask
============================================================================
Description:
    Définit toutes les routes de l'API REST pour le système de surveillance
    des inondations. Fournit des endpoints pour la configuration, les capteurs,
    les prédictions, et les rapports.

Endpoints principaux:
    - GET  /api/config : Récupérer la configuration
    - POST /api/config : Mettre à jour la configuration
    - GET  /api/cities : Lister les villes
    - POST /api/cities : Ajouter une ville
    - GET  /api/sensors : Lister les capteurs
    - POST /api/sensors : Ajouter un capteur
    - GET  /api/predictions/:sensor_id : Prédictions pour un capteur
    - POST /api/pump/control : Contrôler une pompe
    - POST /api/reports/generate : Générer un rapport

Usage:
    from app.api.routes import create_app
    
    app = create_app()
    app.run(host='0.0.0.0', port=5000)

Debugging:
    - Activer FLASK_DEBUG=1 pour voir les erreurs détaillées
    - Vérifier les logs de requêtes
    - Tester avec curl ou Postman
    - Vérifier les CORS pour le frontend
============================================================================
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Dict, Any
import traceback

from app.models import init_db
from app.services.config_service import get_config_service
from app.services.sensor_service import SensorService
from app.services.prediction_service import PredictionService
from app.services.openai_service import OpenAIService
from app.mqtt.mqtt_client import MQTTClient


# ============================================================================
# CRÉATION DE L'APPLICATION FLASK
# ============================================================================

def create_app() -> Flask:
    """
    Crée et configure l'application Flask.
    
    Returns:
        Application Flask configurée
    """
    app = Flask(__name__)
    
    # Configuration CORS (permissif pour démo locale)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Initialiser la base de données
    init_db()
    
    # Services
    config_service = get_config_service()
    sensor_service = SensorService()
    prediction_service = PredictionService()
    openai_service = OpenAIService()
    
    # Client MQTT (global)
    mqtt_client = None
    
    # ========================================================================
    # ROUTES DE CONFIGURATION
    # ========================================================================
    
    @app.route('/api/config', methods=['GET'])
    def get_config():
        """
        Récupère la configuration système.
        
        Returns:
            JSON avec toutes les configurations (masque les mots de passe)
        """
        try:
            config = config_service.get_all()
            
            # Masquer les données sensibles
            sensitive_keys = ['mqtt_broker_password', 'smtp_password', 
                            'openweather_api_key', 'openai_api_key']
            for key in sensitive_keys:
                if key in config and config[key]:
                    config[key] = '***MASKED***'
            
            return jsonify({
                'success': True,
                'data': config
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/config', methods=['POST'])
    def update_config():
        """
        Met à jour la configuration système.
        
        Body:
            {
                "key": "value",
                ...
            }
        
        Returns:
            JSON avec succès/erreur
        """
        try:
            data = request.get_json()
            
            if not data:
                return jsonify({
                    'success': False,
                    'error': 'No data provided'
                }), 400
            
            # Mettre à jour chaque clé
            for key, value in data.items():
                config_service.set(key, str(value))
            
            return jsonify({
                'success': True,
                'message': f'{len(data)} configuration(s) updated'
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/config/setup-status', methods=['GET'])
    def get_setup_status():
        """
        Vérifie si le setup wizard a été complété.
        
        Returns:
            JSON avec setup_completed et missing_config
        """
        try:
            is_complete = config_service.is_setup_complete()
            is_valid, missing = config_service.validate_required_config()
            
            return jsonify({
                'success': True,
                'data': {
                    'setup_completed': is_complete,
                    'config_valid': is_valid,
                    'missing_keys': missing
                }
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/config/complete-setup', methods=['POST'])
    def complete_setup():
        """
        Marque le setup comme complété.
        
        Returns:
            JSON avec succès
        """
        try:
            config_service.mark_setup_complete()
            
            return jsonify({
                'success': True,
                'message': 'Setup completed'
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES DES VILLES
    # ========================================================================
    
    @app.route('/api/cities', methods=['GET'])
    def get_cities():
        """
        Récupère toutes les villes.
        
        Returns:
            JSON avec liste des villes
        """
        try:
            cities = sensor_service.get_all_cities()
            
            cities_data = []
            for city in cities:
                stats = sensor_service.get_city_stats(city.name)
                cities_data.append({
                    'name': city.name,
                    'latitude': city.latitude,
                    'longitude': city.longitude,
                    'description': city.description,
                    'active': city.active,
                    'total_sensors': stats.get('total_sensors', 0),
                    'active_sensors': stats.get('active_sensors', 0),
                })
            
            return jsonify({
                'success': True,
                'data': cities_data
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/cities', methods=['POST'])
    def add_city():
        """
        Ajoute une nouvelle ville.
        
        Body:
            {
                "name": "Casablanca",
                "latitude": 33.5731,
                "longitude": -7.5898,
                "description": "Capitale économique"
            }
        
        Returns:
            JSON avec ville créée
        """
        try:
            data = request.get_json()
            
            required_fields = ['name', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            city = sensor_service.add_city(
                name=data['name'],
                latitude=float(data['latitude']),
                longitude=float(data['longitude']),
                description=data.get('description')
            )
            
            if city:
                return jsonify({
                    'success': True,
                    'data': {
                        'name': city.name,
                        'latitude': city.latitude,
                        'longitude': city.longitude,
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to create city'
                }), 500
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES DES CAPTEURS
    # ========================================================================
    
    @app.route('/api/sensors', methods=['GET'])
    def get_sensors():
        """
        Récupère tous les capteurs.
        
        Query params:
            - city: Filtrer par ville (optionnel)
        
        Returns:
            JSON avec liste des capteurs
        """
        try:
            city_filter = request.args.get('city')
            
            if city_filter:
                sensors = sensor_service.get_sensors_by_city(city_filter)
            else:
                sensors = sensor_service.get_all_sensors()
            
            sensors_data = []
            for sensor in sensors:
                sensors_data.append({
                    'sensor_id': sensor.sensor_id,
                    'city_name': sensor.city_name,
                    'latitude': sensor.latitude,
                    'longitude': sensor.longitude,
                    'description': sensor.description,
                    'active': sensor.active,
                    'last_seen': sensor.last_seen.isoformat() if sensor.last_seen else None,
                })
            
            return jsonify({
                'success': True,
                'data': sensors_data
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/sensors', methods=['POST'])
    def add_sensor():
        """
        Ajoute un nouveau capteur.
        
        Body:
            {
                "sensor_id": "CAS_1",
                "city": "Casablanca",
                "lat": 33.5731,
                "lon": -7.5898,
                "description": "Capteur centre-ville"
            }
        
        Returns:
            JSON avec capteur créé
        """
        try:
            data = request.get_json()
            
            required_fields = ['sensor_id', 'city', 'lat', 'lon']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            sensor = sensor_service.add_sensor(
                sensor_id=data['sensor_id'],
                city_name=data['city'],
                latitude=float(data['lat']),
                longitude=float(data['lon']),
                description=data.get('description')
            )
            
            if sensor:
                # S'abonner au capteur dans MQTT si le client est actif
                nonlocal mqtt_client
                if mqtt_client:
                    mqtt_client.subscribe_to_sensor(data['city'], data['sensor_id'])
                
                return jsonify({
                    'success': True,
                    'data': {
                        'sensor_id': sensor.sensor_id,
                        'city_name': sensor.city_name,
                    }
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to create sensor'
                }), 500
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/sensors/<sensor_id>', methods=['DELETE'])
    def delete_sensor(sensor_id: str):
        """
        Supprime un capteur.
        
        Returns:
            JSON avec succès
        """
        try:
            success = sensor_service.delete_sensor(sensor_id)
            
            if success:
                return jsonify({
                    'success': True,
                    'message': f'Sensor {sensor_id} deleted'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'Sensor not found'
                }), 404
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES DES PRÉDICTIONS
    # ========================================================================
    
    @app.route('/api/predictions/<sensor_id>', methods=['GET'])
    def get_predictions(sensor_id: str):
        """
        Récupère l'historique des prédictions pour un capteur.
        
        Query params:
            - limit: Nombre de prédictions (défaut: 100)
        
        Returns:
            JSON avec liste des prédictions
        """
        try:
            limit = int(request.args.get('limit', 100))
            predictions = prediction_service.get_prediction_history(sensor_id, limit)
            
            return jsonify({
                'success': True,
                'data': predictions
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/predictions/summary', methods=['GET'])
    def get_predictions_summary():
        """
        Récupère le résumé des risques actuels.
        
        Returns:
            JSON avec résumé par ville
        """
        try:
            summary = prediction_service.get_current_risk_summary()
            
            return jsonify({
                'success': True,
                'data': summary
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES DE CONTRÔLE
    # ========================================================================
    
    @app.route('/api/pump/control', methods=['POST'])
    def control_pump():
        """
        Contrôle une pompe via MQTT.
        
        Body:
            {
                "city": "Casablanca",
                "sensor_id": "CAS_1",
                "command": "ON" | "OFF"
            }
        
        Returns:
            JSON avec succès
        """
        try:
            data = request.get_json()
            
            required_fields = ['city', 'sensor_id', 'command']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'error': f'Missing required field: {field}'
                    }), 400
            
            if data['command'] not in ['ON', 'OFF']:
                return jsonify({
                    'success': False,
                    'error': 'Invalid command. Must be ON or OFF'
                }), 400
            
            nonlocal mqtt_client
            if mqtt_client:
                mqtt_client.publish_pump_command(
                    data['city'],
                    data['sensor_id'],
                    data['command']
                )
                
                return jsonify({
                    'success': True,
                    'message': f"Pump command sent: {data['command']}"
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'MQTT client not available'
                }), 503
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES DES RAPPORTS
    # ========================================================================
    
    @app.route('/api/reports/generate', methods=['POST'])
    def generate_report():
        """
        Génère un rapport personnalisé.
        
        Body:
            {
                "cities": ["Casablanca", "Rabat"],
                "sensors": ["CAS_1", "RAB_1"],
                "metrics": ["water_level", "rainfall"],
                "time_range": "Last 24 hours",
                "language": "fr"
            }
        
        Returns:
            JSON avec le rapport généré
        """
        try:
            data = request.get_json()
            
            cities = data.get('cities', [])
            sensors = data.get('sensors', [])
            metrics = data.get('metrics', [])
            time_range = data.get('time_range', 'Last 24 hours')
            language = data.get('language', 'fr')
            
            # Récupérer les données de synthèse
            summary_data = prediction_service.get_current_risk_summary()
            
            # Filtrer par villes sélectionnées
            if cities:
                summary_data = {k: v for k, v in summary_data.items() if k in cities}
            
            # Générer le rapport
            report = openai_service.generate_report(
                cities, sensors, metrics, time_range, summary_data, language
            )
            
            return jsonify({
                'success': True,
                'data': {
                    'report': report,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTES MQTT
    # ========================================================================
    
    @app.route('/api/mqtt/start', methods=['POST'])
    def start_mqtt():
        """
        Démarre le client MQTT.
        
        Returns:
            JSON avec succès
        """
        try:
            nonlocal mqtt_client
            
            if mqtt_client is None:
                mqtt_client = MQTTClient()
            
            mqtt_client.start()
            
            return jsonify({
                'success': True,
                'message': 'MQTT client started'
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/mqtt/stop', methods=['POST'])
    def stop_mqtt():
        """
        Arrête le client MQTT.
        
        Returns:
            JSON avec succès
        """
        try:
            nonlocal mqtt_client
            
            if mqtt_client:
                mqtt_client.stop()
            
            return jsonify({
                'success': True,
                'message': 'MQTT client stopped'
            }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/mqtt/status', methods=['GET'])
    def get_mqtt_status():
        """
        Récupère le statut du client MQTT.
        
        Returns:
            JSON avec statut et buffers
        """
        try:
            nonlocal mqtt_client
            
            if mqtt_client:
                status = mqtt_client.get_buffer_status()
                return jsonify({
                    'success': True,
                    'data': {
                        'running': mqtt_client.running,
                        'buffers': status
                    }
                }), 200
            else:
                return jsonify({
                    'success': True,
                    'data': {
                        'running': False,
                        'buffers': {}
                    }
                }), 200
        
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # ========================================================================
    # ROUTE DE SANTÉ
    # ========================================================================
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """
        Vérifie la santé de l'API.
        
        Returns:
            JSON avec statut
        """
        return jsonify({
            'success': True,
            'message': 'API is healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    
    # ========================================================================
    # GESTION DES ERREURS
    # ========================================================================
    
    @app.errorhandler(404)
    def not_found(error):
        """Gestion des erreurs 404."""
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Gestion des erreurs 500."""
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


# ============================================================================
# POINT D'ENTRÉE
# ============================================================================

if __name__ == '__main__':
    from datetime import datetime
    
    app = create_app()
    print(f"\n🚀 Démarrage de l'API Flask...")
    print(f"📅 {datetime.utcnow().isoformat()}")
    print(f"🌐 http://localhost:5000")
    print(f"📚 Documentation API: http://localhost:5000/api/health\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
