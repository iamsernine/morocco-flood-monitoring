"""
============================================================================
GENERATE_TEST_DATA.PY - Génération de données de test
============================================================================
Description:
    Génère des données de test pour peupler la base de données avec
    des villes, capteurs, et prédictions de démonstration.

Usage:
    python scripts/generate_test_data.py

Debugging:
    - Vérifier que la base de données existe
    - Vérifier les logs pour les erreurs d'insertion
============================================================================
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import get_db_connection


def generate_cities():
    """Génère des villes de test."""
    cities = [
        {
            'name': 'Casablanca',
            'latitude': 33.5731,
            'longitude': -7.5898,
            'description': 'Capitale économique du Maroc'
        },
        {
            'name': 'Rabat',
            'latitude': 34.0209,
            'longitude': -6.8416,
            'description': 'Capitale administrative du Maroc'
        },
        {
            'name': 'Marrakech',
            'latitude': 31.6295,
            'longitude': -7.9811,
            'description': 'Ville touristique majeure'
        },
        {
            'name': 'Fès',
            'latitude': 34.0181,
            'longitude': -5.0078,
            'description': 'Ville historique et culturelle'
        },
        {
            'name': 'Tanger',
            'latitude': 35.7595,
            'longitude': -5.8340,
            'description': 'Ville portuaire du nord'
        },
    ]
    
    return cities


def generate_sensors(cities):
    """Génère des capteurs de test pour chaque ville."""
    sensors = []
    
    for city in cities:
        # 2-4 capteurs par ville
        num_sensors = random.randint(2, 4)
        
        for i in range(num_sensors):
            sensor_id = f"{city['name'][:3].upper()}_{i+1}"
            
            # Position légèrement décalée par rapport au centre de la ville
            lat_offset = random.uniform(-0.05, 0.05)
            lon_offset = random.uniform(-0.05, 0.05)
            
            sensors.append({
                'sensor_id': sensor_id,
                'city_name': city['name'],
                'latitude': city['latitude'] + lat_offset,
                'longitude': city['longitude'] + lon_offset,
                'description': f"Capteur {i+1} - {city['name']}",
                'active': random.choice([True, True, True, False]),  # 75% actifs
            })
    
    return sensors


def generate_predictions(sensors, days=7):
    """Génère des prédictions historiques pour les capteurs."""
    predictions = []
    
    now = datetime.now()
    
    for sensor in sensors:
        if not sensor['active']:
            continue
        
        # Générer des prédictions pour les N derniers jours
        for day in range(days):
            timestamp = now - timedelta(days=day)
            
            # 4 prédictions par jour (toutes les 6 heures)
            for hour in [0, 6, 12, 18]:
                pred_time = timestamp.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Probabilité aléatoire avec tendance
                base_prob = random.uniform(10, 40)
                
                # Augmenter la probabilité pour certains capteurs (simulation de risque)
                if sensor['sensor_id'].endswith('_1'):
                    base_prob += random.uniform(20, 40)
                
                probability = min(100, base_prob)
                
                # Déterminer le niveau de risque
                if probability >= 70:
                    risk_level = 'High'
                elif probability >= 40:
                    risk_level = 'Medium'
                else:
                    risk_level = 'Low'
                
                predictions.append({
                    'sensor_id': sensor['sensor_id'],
                    'timestamp': pred_time.isoformat(),
                    'probability': probability,
                    'risk_level': risk_level,
                    'model_version': 'v1.0',
                })
    
    return predictions


def populate_database():
    """Peuple la base de données avec des données de test."""
    print("=" * 80)
    print("🌊 GÉNÉRATION DE DONNÉES DE TEST")
    print("=" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Générer les villes
    print("\n📍 Génération des villes...")
    cities = generate_cities()
    
    for city in cities:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO cities (name, latitude, longitude, description)
                VALUES (?, ?, ?, ?)
            """, (city['name'], city['latitude'], city['longitude'], city['description']))
            print(f"   ✅ {city['name']}")
        except Exception as e:
            print(f"   ❌ Erreur pour {city['name']}: {e}")
    
    conn.commit()
    print(f"\n✅ {len(cities)} villes ajoutées")
    
    # Générer les capteurs
    print("\n📡 Génération des capteurs...")
    sensors = generate_sensors(cities)
    
    for sensor in sensors:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO sensors 
                (sensor_id, city_name, latitude, longitude, description, active, last_seen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                sensor['sensor_id'],
                sensor['city_name'],
                sensor['latitude'],
                sensor['longitude'],
                sensor['description'],
                sensor['active'],
                datetime.now().isoformat() if sensor['active'] else None
            ))
            print(f"   ✅ {sensor['sensor_id']} ({sensor['city_name']})")
        except Exception as e:
            print(f"   ❌ Erreur pour {sensor['sensor_id']}: {e}")
    
    conn.commit()
    print(f"\n✅ {len(sensors)} capteurs ajoutés")
    
    # Générer les prédictions
    print("\n🔮 Génération des prédictions (7 derniers jours)...")
    predictions = generate_predictions(sensors, days=7)
    
    for pred in predictions:
        try:
            cursor.execute("""
                INSERT INTO predictions 
                (sensor_id, timestamp, probability, risk_level, model_version)
                VALUES (?, ?, ?, ?, ?)
            """, (
                pred['sensor_id'],
                pred['timestamp'],
                pred['probability'],
                pred['risk_level'],
                pred['model_version']
            ))
        except Exception as e:
            print(f"   ❌ Erreur pour {pred['sensor_id']}: {e}")
    
    conn.commit()
    print(f"✅ {len(predictions)} prédictions ajoutées")
    
    # Statistiques
    print("\n" + "=" * 80)
    print("📊 STATISTIQUES")
    print("=" * 80)
    
    cursor.execute("SELECT COUNT(*) FROM cities")
    print(f"Villes: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM sensors")
    print(f"Capteurs: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM sensors WHERE active = 1")
    print(f"Capteurs actifs: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM predictions")
    print(f"Prédictions: {cursor.fetchone()[0]}")
    
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE risk_level = 'High'")
    print(f"Prédictions à risque élevé: {cursor.fetchone()[0]}")
    
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ GÉNÉRATION TERMINÉE AVEC SUCCÈS")
    print("=" * 80)
    print("\nVous pouvez maintenant démarrer le frontend et voir les données.")


if __name__ == '__main__':
    populate_database()
