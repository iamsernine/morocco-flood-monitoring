"""
============================================================================
IMPORT_SENSORS_FLAT.PY - Import de capteurs depuis JSON plat
============================================================================
Description:
    Importe des capteurs depuis un JSON au format plat (liste de capteurs).
    Les villes sont créées automatiquement et leurs coordonnées sont
    calculées comme la moyenne des capteurs de chaque ville.

Format JSON attendu:
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
        }
    ]

Usage:
    python scripts/import_sensors_flat.py sensors.json
    python scripts/import_sensors_flat.py --file sensors.json
    python scripts/import_sensors_flat.py --file sensors.json --replace

Arguments:
    file: Chemin vers le fichier JSON
    --replace: Remplacer les villes/capteurs existants

Debugging:
    - Vérifier le format JSON (doit être une liste)
    - Vérifier que les coordonnées sont valides
    - Vérifier les IDs uniques des capteurs
============================================================================
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any
from collections import defaultdict

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import init_db
from app.services.sensor_service import SensorService


def validate_sensor(sensor: Dict[str, Any]) -> bool:
    """
    Valide les données d'un capteur.
    
    Args:
        sensor: Dictionnaire de données capteur
    
    Returns:
        True si valide, False sinon
    """
    required_fields = ['sensor_id', 'city', 'lat', 'lon']
    for field in required_fields:
        if field not in sensor:
            print(f"❌ Capteur invalide: champ '{field}' manquant")
            return False
    
    # Valider les coordonnées
    try:
        lat = float(sensor['lat'])
        lon = float(sensor['lon'])
        
        if not (-90 <= lat <= 90):
            print(f"❌ Latitude invalide pour {sensor['sensor_id']}: {lat}")
            return False
        
        if not (-180 <= lon <= 180):
            print(f"❌ Longitude invalide pour {sensor['sensor_id']}: {lon}")
            return False
    except (ValueError, TypeError):
        print(f"❌ Coordonnées invalides pour {sensor['sensor_id']}")
        return False
    
    return True


def group_sensors_by_city(sensors: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Groupe les capteurs par ville.
    
    Args:
        sensors: Liste de capteurs
    
    Returns:
        Dictionnaire {ville: [capteurs]}
    """
    cities = defaultdict(list)
    for sensor in sensors:
        city_name = sensor['city']
        cities[city_name].append(sensor)
    return dict(cities)


def calculate_city_coordinates(sensors: List[Dict[str, Any]]) -> tuple[float, float]:
    """
    Calcule les coordonnées d'une ville comme la moyenne de ses capteurs.
    
    Args:
        sensors: Liste des capteurs de la ville
    
    Returns:
        (latitude, longitude)
    """
    if not sensors:
        return (0.0, 0.0)
    
    total_lat = sum(float(s['lat']) for s in sensors)
    total_lon = sum(float(s['lon']) for s in sensors)
    
    avg_lat = total_lat / len(sensors)
    avg_lon = total_lon / len(sensors)
    
    return (avg_lat, avg_lon)


def import_from_flat_json(json_file: str, replace: bool = False) -> tuple[int, int]:
    """
    Importe des capteurs depuis un fichier JSON plat.
    
    Args:
        json_file: Chemin vers le fichier JSON
        replace: Si True, remplace les données existantes
    
    Returns:
        (nombre_villes_créées, nombre_capteurs_importés)
    """
    # Lire le fichier JSON
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Fichier non trouvé: {json_file}")
        return (0, 0)
    except json.JSONDecodeError as e:
        print(f"❌ Erreur de parsing JSON: {e}")
        return (0, 0)
    
    # Valider la structure
    if not isinstance(data, list):
        print("❌ Le JSON doit être une liste de capteurs")
        return (0, 0)
    
    # Valider tous les capteurs
    valid_sensors = []
    for sensor in data:
        if validate_sensor(sensor):
            valid_sensors.append(sensor)
    
    if not valid_sensors:
        print("❌ Aucun capteur valide trouvé")
        return (0, 0)
    
    print(f"✅ {len(valid_sensors)} capteurs valides trouvés")
    
    # Grouper par ville
    cities_sensors = group_sensors_by_city(valid_sensors)
    print(f"✅ {len(cities_sensors)} villes détectées: {', '.join(cities_sensors.keys())}")
    
    # Initialiser le service
    sensor_service = SensorService()
    
    cities_count = 0
    sensors_count = 0
    
    # Créer les villes et leurs capteurs
    for city_name, city_sensors in cities_sensors.items():
        # Calculer les coordonnées de la ville
        city_lat, city_lon = calculate_city_coordinates(city_sensors)
        
        print(f"\n📍 Ville: {city_name}")
        print(f"   Coordonnées: ({city_lat:.5f}, {city_lon:.5f})")
        print(f"   Capteurs: {len(city_sensors)}")
        
        # Vérifier si la ville existe déjà
        existing_city = sensor_service.get_city(city_name)
        if existing_city and not replace:
            print(f"   ⚠️  Ville existe déjà (utilisez --replace pour écraser)")
        else:
            # Créer ou mettre à jour la ville
            city = sensor_service.create_city(
                name=city_name,
                latitude=city_lat,
                longitude=city_lon,
                description=f"Ville avec {len(city_sensors)} capteur(s)"
            )
            
            if city:
                cities_count += 1
                print(f"   ✅ Ville créée")
            else:
                print(f"   ❌ Échec création ville")
                continue
        
        # Importer les capteurs de cette ville
        for sensor_data in city_sensors:
            sensor_id = sensor_data['sensor_id']
            
            # Vérifier si le capteur existe déjà
            existing_sensor = sensor_service.get_sensor(sensor_id)
            if existing_sensor and not replace:
                print(f"      ⚠️  Capteur '{sensor_id}' existe déjà")
                continue
            
            # Créer ou mettre à jour le capteur
            sensor = sensor_service.create_sensor(
                sensor_id=sensor_id,
                city_name=city_name,
                latitude=float(sensor_data['lat']),
                longitude=float(sensor_data['lon']),
                description=sensor_data.get('description', f"Capteur {sensor_id}")
            )
            
            if sensor:
                sensors_count += 1
                print(f"      ✅ {sensor_id}")
            else:
                print(f"      ❌ Échec: {sensor_id}")
    
    return (cities_count, sensors_count)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description='Importe des capteurs depuis un fichier JSON plat'
    )
    parser.add_argument(
        'file',
        nargs='?',
        help='Chemin vers le fichier JSON'
    )
    parser.add_argument(
        '--file',
        dest='json_file',
        help='Chemin vers le fichier JSON (alternative)'
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        help='Remplacer les villes/capteurs existants'
    )
    
    args = parser.parse_args()
    
    # Déterminer le fichier JSON
    json_file = args.file or args.json_file
    
    if not json_file:
        print("❌ Veuillez spécifier un fichier JSON")
        print("Usage: python import_sensors_flat.py sensors.json")
        print("   ou: python import_sensors_flat.py --file sensors.json")
        sys.exit(1)
    
    # Initialiser la base de données
    print("📊 Initialisation de la base de données...")
    init_db()
    
    # Importer les données
    print(f"\n📥 Import depuis {json_file}...")
    if args.replace:
        print("⚠️  Mode remplacement activé")
    
    cities_count, sensors_count = import_from_flat_json(json_file, args.replace)
    
    # Résumé
    print(f"\n{'='*60}")
    print(f"✅ Import terminé!")
    print(f"   Villes créées: {cities_count}")
    print(f"   Capteurs importés: {sensors_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
