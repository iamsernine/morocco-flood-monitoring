"""
============================================================================
SENSOR_SIMULATOR.PY - Simulateur de capteur IoT
============================================================================
Description:
    Simule un capteur IoT qui publie des données sur MQTT.
    Utile pour tester le système sans capteurs physiques.

Fonctionnalités:
    - Simulation de water_level et humidity
    - Publication périodique sur MQTT
    - Variation réaliste des valeurs
    - Support multi-capteurs

Usage:
    python sensor_simulator.py --sensor-id CAS_1 --city Casablanca

Arguments:
    --sensor-id: Identifiant du capteur (ex: CAS_1)
    --city: Nom de la ville (ex: Casablanca)
    --broker: Adresse du broker MQTT (défaut: localhost)
    --port: Port du broker MQTT (défaut: 1883)
    --interval: Intervalle de publication en secondes (défaut: 5)

Debugging:
    - Vérifier la connexion au broker MQTT
    - Surveiller les logs de publication
    - Vérifier les topics avec mosquitto_sub
============================================================================
"""

import paho.mqtt.client as mqtt
import json
import time
import random
import argparse
from datetime import datetime


class SensorSimulator:
    """
    Simulateur de capteur IoT.
    """
    
    def __init__(self, sensor_id: str, city: str, broker_host: str = 'localhost',
                 broker_port: int = 1883, interval: int = 5):
        """
        Initialise le simulateur.
        
        Args:
            sensor_id: Identifiant du capteur
            city: Nom de la ville
            broker_host: Adresse du broker MQTT
            broker_port: Port du broker MQTT
            interval: Intervalle de publication en secondes
        """
        self.sensor_id = sensor_id
        self.city = city
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.interval = interval
        
        # État du capteur
        self.water_level = random.uniform(20, 60)  # cm
        self.humidity = random.uniform(40, 80)  # %
        
        # Client MQTT
        self.client = mqtt.Client(client_id=f"simulator_{sensor_id}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        
        # Topics
        self.topic_water_level = f"sensors/{city}/{sensor_id}/water_level"
        self.topic_humidity = f"sensors/{city}/{sensor_id}/humidity"
        
        print(f"📡 Simulateur initialisé: {sensor_id} ({city})")
        print(f"   Broker: {broker_host}:{broker_port}")
        print(f"   Intervalle: {interval}s")
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback de connexion."""
        if rc == 0:
            print(f"✅ Connecté au broker MQTT")
        else:
            print(f"❌ Échec de connexion (code: {rc})")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback de déconnexion."""
        if rc != 0:
            print(f"⚠️  Déconnexion inattendue (code: {rc})")
    
    def _simulate_water_level(self) -> float:
        """
        Simule le niveau d'eau avec variation réaliste.
        
        Returns:
            Niveau d'eau en cm
        """
        # Variation aléatoire (-2 à +2 cm)
        variation = random.uniform(-2, 2)
        self.water_level += variation
        
        # Limiter entre 0 et 100 cm
        self.water_level = max(0, min(100, self.water_level))
        
        # Ajouter un peu de bruit
        noise = random.uniform(-0.5, 0.5)
        
        return round(self.water_level + noise, 2)
    
    def _simulate_humidity(self) -> float:
        """
        Simule l'humidité avec variation réaliste.
        
        Returns:
            Humidité en %
        """
        # Variation aléatoire (-1 à +1 %)
        variation = random.uniform(-1, 1)
        self.humidity += variation
        
        # Limiter entre 0 et 100 %
        self.humidity = max(0, min(100, self.humidity))
        
        # Ajouter un peu de bruit
        noise = random.uniform(-0.3, 0.3)
        
        return round(self.humidity + noise, 2)
    
    def _publish_data(self):
        """Publie les données sur MQTT."""
        # Simuler les valeurs
        water_level = self._simulate_water_level()
        humidity = self._simulate_humidity()
        
        timestamp = datetime.utcnow().isoformat()
        
        # Publier water_level
        payload_water = json.dumps({
            'value': water_level,
            'unit': 'cm',
            'timestamp': timestamp
        })
        self.client.publish(self.topic_water_level, payload_water)
        
        # Publier humidity
        payload_humidity = json.dumps({
            'value': humidity,
            'unit': '%',
            'timestamp': timestamp
        })
        self.client.publish(self.topic_humidity, payload_humidity)
        
        print(f"📊 [{timestamp}] {self.sensor_id}: water_level={water_level}cm, humidity={humidity}%")
    
    def start(self):
        """Démarre le simulateur."""
        try:
            # Connexion au broker
            print(f"\n🔌 Connexion au broker {self.broker_host}:{self.broker_port}...")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            print(f"🚀 Simulateur démarré")
            print(f"   Topics:")
            print(f"     - {self.topic_water_level}")
            print(f"     - {self.topic_humidity}")
            print(f"\n📡 Publication en cours (Ctrl+C pour arrêter)...\n")
            
            # Boucle de publication
            while True:
                self._publish_data()
                time.sleep(self.interval)
        
        except KeyboardInterrupt:
            print("\n\n🛑 Arrêt du simulateur...")
            self.stop()
        
        except Exception as e:
            print(f"\n❌ Erreur: {e}")
            self.stop()
    
    def stop(self):
        """Arrête le simulateur."""
        self.client.loop_stop()
        self.client.disconnect()
        print("✅ Simulateur arrêté")


def main():
    """Fonction principale."""
    parser = argparse.ArgumentParser(
        description='Simulateur de capteur IoT pour le système de surveillance des inondations'
    )
    
    parser.add_argument(
        '--sensor-id',
        type=str,
        required=True,
        help='Identifiant du capteur (ex: CAS_1)'
    )
    
    parser.add_argument(
        '--city',
        type=str,
        required=True,
        help='Nom de la ville (ex: Casablanca)'
    )
    
    parser.add_argument(
        '--broker',
        type=str,
        default='localhost',
        help='Adresse du broker MQTT (défaut: localhost)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=1883,
        help='Port du broker MQTT (défaut: 1883)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Intervalle de publication en secondes (défaut: 5)'
    )
    
    args = parser.parse_args()
    
    # Créer et démarrer le simulateur
    simulator = SensorSimulator(
        sensor_id=args.sensor_id,
        city=args.city,
        broker_host=args.broker,
        broker_port=args.port,
        interval=args.interval
    )
    
    simulator.start()


if __name__ == '__main__':
    main()
