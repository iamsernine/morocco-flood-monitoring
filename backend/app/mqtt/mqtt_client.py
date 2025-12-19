"""
============================================================================
MQTT_CLIENT.PY - Client MQTT pour réception des données capteurs
============================================================================
Description:
    Client MQTT qui s'abonne aux topics des capteurs et collecte les données
    en temps réel. Implémente un système de buffers roulants par ville et
    agrège les données périodiquement.

Topics MQTT:
    - sensors/{city}/{sensor_id}/water_level
    - sensors/{city}/{sensor_id}/humidity
    - actuators/{city}/{sensor_id}/pump (pour contrôle)

Fonctionnalités:
    - Connexion au broker MQTT
    - Souscription automatique aux topics
    - Buffers roulants par ville
    - Agrégation périodique (moyenne, max, pente)
    - Sauvegarde en Parquet
    - Récupération données météo externes
    - Simulation river_level et soil_moisture

Usage:
    from app.mqtt.mqtt_client import MQTTClient
    
    client = MQTTClient()
    client.start()  # Démarre en arrière-plan
    client.stop()   # Arrête proprement

Debugging:
    - Vérifier la connexion au broker MQTT
    - Surveiller les logs de connexion/déconnexion
    - Vérifier que les topics sont corrects
    - Inspecter les buffers avec get_buffer_status()
============================================================================
"""

import paho.mqtt.client as mqtt
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
import pandas as pd
import os

from app.services.config_service import get_config_service
from app.services.sensor_service import SensorService


class MQTTClient:
    """
    Client MQTT pour la collecte de données des capteurs.
    """
    
    # Canaux partagés par tous les capteurs
    SENSOR_CHANNELS = ['water_level', 'humidity']
    ACTUATOR_CHANNELS = ['pump']
    
    def __init__(self):
        """Initialise le client MQTT."""
        self.config = get_config_service()
        self.sensor_service = SensorService()
        
        # Configuration MQTT
        mqtt_config = self.config.get_mqtt_config()
        self.broker_host = mqtt_config['host']
        self.broker_port = mqtt_config['port']
        self.broker_username = mqtt_config['username']
        self.broker_password = mqtt_config['password']
        
        # Client MQTT
        self.client = mqtt.Client(client_id="flood_monitoring_receiver")
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        # Authentification si nécessaire
        if self.broker_username and self.broker_password:
            self.client.username_pw_set(self.broker_username, self.broker_password)
        
        # Buffers roulants par ville
        # Structure: {city_name: {parameter: deque([{timestamp, sensor_id, value}])}}
        self.buffers = defaultdict(lambda: defaultdict(lambda: deque(maxlen=1000)))
        
        # Configuration agrégation
        self.aggregation_interval = int(self.config.get('aggregation_interval', '300'))  # secondes
        self.buffer_window_minutes = int(self.config.get('buffer_window_minutes', '30'))
        
        # Thread d'agrégation
        self.aggregation_thread = None
        self.running = False
        
        # Répertoire de stockage Parquet
        self.parquet_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'data', 'parquet'
        )
        os.makedirs(self.parquet_dir, exist_ok=True)
        
        print(f"📡 Client MQTT initialisé (broker: {self.broker_host}:{self.broker_port})")
    
    # ========================================================================
    # CALLBACKS MQTT
    # ========================================================================
    
    def _on_connect(self, client, userdata, flags, rc):
        """
        Callback appelé lors de la connexion au broker.
        
        Args:
            rc: Code de retour (0 = succès)
        """
        if rc == 0:
            print("✅ Connecté au broker MQTT")
            self._subscribe_to_sensors()
        else:
            print(f"❌ Échec de connexion au broker MQTT (code: {rc})")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback appelé lors de la déconnexion."""
        if rc != 0:
            print(f"⚠️  Déconnexion inattendue du broker MQTT (code: {rc})")
        else:
            print("📡 Déconnecté du broker MQTT")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback appelé lors de la réception d'un message.
        
        Args:
            msg: Message MQTT avec topic et payload
        """
        try:
            # Parser le topic: sensors/{city}/{sensor_id}/{parameter}
            parts = msg.topic.split('/')
            if len(parts) != 4 or parts[0] != 'sensors':
                print(f"⚠️  Topic invalide: {msg.topic}")
                return
            
            city = parts[1]
            sensor_id = parts[2]
            parameter = parts[3]
            
            # Parser le payload (JSON ou valeur simple)
            try:
                payload = json.loads(msg.payload.decode())
                if isinstance(payload, dict):
                    value = payload.get('value')
                else:
                    value = payload
            except json.JSONDecodeError:
                value = float(msg.payload.decode())
            
            # Ajouter au buffer
            self._add_to_buffer(city, parameter, sensor_id, value)
            
            # Mettre à jour last_seen du capteur
            self.sensor_service.update_sensor_last_seen(sensor_id)
            
            # Log (optionnel, peut être verbeux)
            # print(f"📊 {sensor_id} ({city}) - {parameter}: {value}")
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement du message: {e}")
    
    # ========================================================================
    # SOUSCRIPTION AUX TOPICS
    # ========================================================================
    
    def _subscribe_to_sensors(self):
        """
        S'abonne aux topics de tous les capteurs actifs.
        """
        sensors = self.sensor_service.get_all_sensors(active_only=True)
        
        if not sensors:
            print("⚠️  Aucun capteur actif trouvé")
            return
        
        for sensor in sensors:
            for channel in self.SENSOR_CHANNELS:
                topic = f"sensors/{sensor.city_name}/{sensor.sensor_id}/{channel}"
                self.client.subscribe(topic)
                print(f"📡 Souscription: {topic}")
    
    def subscribe_to_sensor(self, city: str, sensor_id: str):
        """
        S'abonne aux topics d'un capteur spécifique.
        
        Args:
            city: Nom de la ville
            sensor_id: Identifiant du capteur
        """
        for channel in self.SENSOR_CHANNELS:
            topic = f"sensors/{city}/{sensor_id}/{channel}"
            self.client.subscribe(topic)
            print(f"📡 Souscription: {topic}")
    
    def unsubscribe_from_sensor(self, city: str, sensor_id: str):
        """
        Se désabonne des topics d'un capteur.
        
        Args:
            city: Nom de la ville
            sensor_id: Identifiant du capteur
        """
        for channel in self.SENSOR_CHANNELS:
            topic = f"sensors/{city}/{sensor_id}/{channel}"
            self.client.unsubscribe(topic)
            print(f"📡 Désinscription: {topic}")
    
    # ========================================================================
    # GESTION DES BUFFERS
    # ========================================================================
    
    def _add_to_buffer(self, city: str, parameter: str, sensor_id: str, value: float):
        """
        Ajoute une valeur au buffer.
        
        Args:
            city: Nom de la ville
            parameter: Nom du paramètre (water_level, humidity, etc.)
            sensor_id: Identifiant du capteur
            value: Valeur mesurée
        """
        data_point = {
            'timestamp': datetime.utcnow(),
            'sensor_id': sensor_id,
            'value': value
        }
        self.buffers[city][parameter].append(data_point)
    
    def get_buffer_status(self) -> Dict[str, Any]:
        """
        Retourne le statut des buffers.
        
        Returns:
            Dictionnaire avec statistiques des buffers
        """
        status = {}
        for city, parameters in self.buffers.items():
            status[city] = {}
            for parameter, buffer in parameters.items():
                status[city][parameter] = {
                    'count': len(buffer),
                    'oldest': buffer[0]['timestamp'].isoformat() if buffer else None,
                    'newest': buffer[-1]['timestamp'].isoformat() if buffer else None,
                }
        return status
    
    def clear_old_buffer_data(self, city: str):
        """
        Nettoie les données du buffer plus anciennes que la fenêtre.
        
        Args:
            city: Nom de la ville
        """
        cutoff_time = datetime.utcnow() - timedelta(minutes=self.buffer_window_minutes)
        
        for parameter, buffer in self.buffers[city].items():
            # Filtrer les données récentes
            recent_data = deque(
                [dp for dp in buffer if dp['timestamp'] > cutoff_time],
                maxlen=1000
            )
            self.buffers[city][parameter] = recent_data
    
    # ========================================================================
    # AGRÉGATION ET SAUVEGARDE
    # ========================================================================
    
    def _aggregation_loop(self):
        """
        Boucle d'agrégation périodique (exécutée dans un thread).
        """
        print(f"🔄 Démarrage de l'agrégation (intervalle: {self.aggregation_interval}s)")
        
        while self.running:
            try:
                time.sleep(self.aggregation_interval)
                self._aggregate_and_save()
            except Exception as e:
                print(f"❌ Erreur dans la boucle d'agrégation: {e}")
    
    def _aggregate_and_save(self):
        """
        Agrège les données des buffers et sauvegarde en Parquet.
        """
        timestamp = datetime.utcnow()
        
        for city in list(self.buffers.keys()):
            try:
                # Agréger les données
                aggregated = self._aggregate_city_data(city)
                
                if aggregated:
                    # Ajouter timestamp
                    aggregated['timestamp'] = timestamp
                    
                    # Sauvegarder en Parquet
                    self._save_to_parquet(city, aggregated)
                    
                    # Nettoyer les anciennes données du buffer
                    self.clear_old_buffer_data(city)
                    
                    print(f"💾 Données agrégées sauvegardées pour {city}")
            
            except Exception as e:
                print(f"❌ Erreur lors de l'agrégation pour {city}: {e}")
    
    def _aggregate_city_data(self, city: str) -> Dict[str, Any]:
        """
        Agrège les données d'une ville.
        
        Args:
            city: Nom de la ville
        
        Returns:
            Dictionnaire avec données agrégées
        """
        aggregated = {'city': city}
        
        for parameter, buffer in self.buffers[city].items():
            if not buffer:
                continue
            
            values = [dp['value'] for dp in buffer]
            timestamps = [dp['timestamp'] for dp in buffer]
            
            # Calculs d'agrégation
            aggregated[f'{parameter}_avg'] = sum(values) / len(values)
            aggregated[f'{parameter}_max'] = max(values)
            aggregated[f'{parameter}_min'] = min(values)
            
            # Calcul de la pente (tendance)
            if len(values) >= 2:
                time_diff = (timestamps[-1] - timestamps[0]).total_seconds()
                if time_diff > 0:
                    value_diff = values[-1] - values[0]
                    aggregated[f'{parameter}_slope'] = value_diff / time_diff
                else:
                    aggregated[f'{parameter}_slope'] = 0.0
            else:
                aggregated[f'{parameter}_slope'] = 0.0
        
        # Ajouter données externes (météo)
        external_data = self._fetch_external_data(city)
        aggregated.update(external_data)
        
        # Simuler river_level et soil_moisture si manquants
        if 'river_level' not in aggregated:
            aggregated['river_level'] = self._simulate_river_level()
        if 'soil_moisture' not in aggregated:
            aggregated['soil_moisture'] = self._simulate_soil_moisture()
        
        return aggregated
    
    def _fetch_external_data(self, city: str) -> Dict[str, Any]:
        """
        Récupère les données météo externes pour une ville.
        
        Args:
            city: Nom de la ville
        
        Returns:
            Dictionnaire avec rainfall, temperature, wind_speed, wind_direction
        """
        # TODO: Implémenter l'appel à OpenWeatherMap API
        # Pour l'instant, retourner des valeurs simulées
        import random
        
        return {
            'rainfall': random.uniform(0, 50),  # mm
            'temperature': random.uniform(10, 35),  # °C
            'wind_speed': random.uniform(0, 30),  # km/h
            'wind_direction': random.uniform(0, 360),  # degrés
        }
    
    def _simulate_river_level(self) -> float:
        """Simule le niveau de la rivière."""
        import random
        return random.uniform(0, 100)  # cm
    
    def _simulate_soil_moisture(self) -> float:
        """Simule l'humidité du sol."""
        import random
        return random.uniform(0, 100)  # %
    
    def _save_to_parquet(self, city: str, data: Dict[str, Any]):
        """
        Sauvegarde les données agrégées en Parquet.
        
        Args:
            city: Nom de la ville
            data: Données à sauvegarder
        """
        # Nom du fichier Parquet
        filename = f"{city}_{datetime.utcnow().strftime('%Y%m')}.parquet"
        filepath = os.path.join(self.parquet_dir, filename)
        
        # Convertir en DataFrame
        df_new = pd.DataFrame([data])
        
        # Ajouter au fichier existant ou créer nouveau
        if os.path.exists(filepath):
            df_existing = pd.read_parquet(filepath)
            df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            df_combined.to_parquet(filepath, index=False)
        else:
            df_new.to_parquet(filepath, index=False)
    
    # ========================================================================
    # CONTRÔLE DES ACTIONNEURS
    # ========================================================================
    
    def publish_pump_command(self, city: str, sensor_id: str, command: str):
        """
        Publie une commande de pompe.
        
        Args:
            city: Nom de la ville
            sensor_id: Identifiant du capteur
            command: 'ON' ou 'OFF'
        """
        topic = f"actuators/{city}/{sensor_id}/pump"
        payload = json.dumps({'command': command, 'timestamp': datetime.utcnow().isoformat()})
        self.client.publish(topic, payload)
        print(f"🚰 Commande pompe envoyée: {sensor_id} -> {command}")
    
    # ========================================================================
    # DÉMARRAGE/ARRÊT
    # ========================================================================
    
    def start(self):
        """Démarre le client MQTT et la boucle d'agrégation."""
        if self.running:
            print("⚠️  Le client MQTT est déjà démarré")
            return
        
        try:
            # Connexion au broker
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Démarrer le thread d'agrégation
            self.running = True
            self.aggregation_thread = threading.Thread(target=self._aggregation_loop, daemon=True)
            self.aggregation_thread.start()
            
            print("✅ Client MQTT démarré")
        
        except Exception as e:
            print(f"❌ Erreur lors du démarrage du client MQTT: {e}")
            self.running = False
    
    def stop(self):
        """Arrête le client MQTT proprement."""
        if not self.running:
            print("⚠️  Le client MQTT n'est pas démarré")
            return
        
        print("🛑 Arrêt du client MQTT...")
        self.running = False
        
        # Arrêter la boucle MQTT
        self.client.loop_stop()
        self.client.disconnect()
        
        # Attendre la fin du thread d'agrégation
        if self.aggregation_thread:
            self.aggregation_thread.join(timeout=5)
        
        print("✅ Client MQTT arrêté")


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    from app.models import init_db
    
    print("Initialisation de la base de données...")
    init_db()
    
    print("\nTest du MQTTClient...")
    client = MQTTClient()
    
    # Simuler l'ajout de données au buffer
    client._add_to_buffer('Casablanca', 'water_level', 'CAS_1', 45.5)
    client._add_to_buffer('Casablanca', 'water_level', 'CAS_1', 46.2)
    client._add_to_buffer('Casablanca', 'humidity', 'CAS_1', 65.0)
    
    # Vérifier le statut des buffers
    status = client.get_buffer_status()
    print(f"\nStatut des buffers: {json.dumps(status, indent=2, default=str)}")
    
    # Test agrégation
    aggregated = client._aggregate_city_data('Casablanca')
    print(f"\nDonnées agrégées: {json.dumps(aggregated, indent=2, default=str)}")
    
    print("\n✅ Tests terminés!")
