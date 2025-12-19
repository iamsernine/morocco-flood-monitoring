"""
============================================================================
IMPORT_FROM_JSON.PY - Import de villes et capteurs depuis JSON
============================================================================
Description:
    Importe des villes et capteurs depuis un fichier JSON au lieu de les
    ajouter un par un manuellement.

Format JSON attendu:
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
            }
          ]
        }
      ]
    }

Usage:
    python scripts/import_from_json.py data.json
    python scripts/import_from_json.py --file data.json
    python scripts/import_from_json.py --file data.json --replace

Arguments:
    file: Chemin vers le fichier JSON
    --replace: Remplacer les villes/capteurs existants

Debugging:
    - Vérifier le format JSON
    - Vérifier que les coordonnées sont valides
    - Vérifier les IDs uniques des capteurs
============================================================================
"""

import sys
import os
import json
import argparse
from typing import Dict, List, Any

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.database import init_db
from app.services.sensor_service import SensorService


def validate_city(city: Dict[str, Any]) -> bool:
    """
    Valide les données d'une ville.
    
    Args:
        city: Dictionnaire de données ville
    
    Returns:
        True si valide, False sinon
    """
    required_fields = ['name', 'latitude', 'longitude']
    for field in required_fields:
        if field not in city:
            print(f"❌ Ville invalide: champ '{field}' manquant")
            return False
    
    # Valider les coordonnées
    if not (-90 <= city['latitude'] <= 90):
        print(f"❌ Latitude invalide pour {city['name']}: {city['latitude']}")
        return False
    
    if not (-180 <= city['longitude'] <= 180):
        print(f"❌ Longitude invalide pour {city['name']}: {city['longitude']}")
        return False
    
    return True


def validate_sensor(sensor: Dict[str, Any], city_name: str) -> bool:
    """
    Valide les données d'un capteur.
    
    Args:
        sensor: Dictionnaire de données capteur
        city_name: Nom de la ville parente
    
    Returns:
        True si valide, False sinon
    """
    required_fields = ['sensor_id', 'latitude', 'longitude']
    for field in required_fields:
        if field not in sensor:
            print(f"❌ Capteur invalide dans {city_name}: champ '{field}' manquant")
            return False
    
    # Valider les coordonnées
    if not (-90 <= sensor['latitude'] <= 90):
        print(f"❌ Latitude invalide pour capteur {sensor['sensor_id']}: {sensor['latitude']}")
        return False
    
    if not (-180 <= sensor['longitude'] <= 180):
        print(f"❌ Longitude invalide pour capteur {sensor['sensor_id']}: {sensor['longitude']}")
        return False
    
    return True


def import_from_json(json_file: str, replace: bool = False) -> tuple[int, int]:
    """
    Importe des villes et capteurs depuis un fichier JSON.
    
    Args:
        json_file: Chemin vers le fichier JSON
        replace: Si True, remplace les données existantes
    
    Returns:
        (nombre_villes_importées, nombre_capteurs_importés)
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
    if 'cities' not in data:
        print("❌ Le JSON doit contenir un champ 'cities'")
        return (0, 0)
    
    cities = data['cities']
    if not isinstance(cities, list):
        print("❌ Le champ 'cities' doit être une liste")
        return (0, 0)
    
    # Initialiser le service
    sensor_service = SensorService()
    
    cities_count = 0
    sensors_count = 0
    
    # Importer chaque ville
    for city_data in cities:
        if not validate_city(city_data):
            continue
        
        city_name = city_data['name']
        
        # Vérifier si la ville existe déjà
        existing_city = sensor_service.get_city(city_name)
        if existing_city and not replace:
            print(f"⚠️  Ville '{city_name}' existe déjà (utilisez --replace pour écraser)")
            continue
        
        # Créer ou mettre à jour la ville
        city = sensor_service.create_city(
            name=city_name,
            latitude=city_data['latitude'],
            longitude=city_data['longitude'],
            description=city_data.get('description', '')
        )
        
        if city:
            cities_count += 1
            print(f"✅ Ville importée: {city_name}")
            
            # Importer les capteurs de cette ville
            sensors = city_data.get('sensors', [])
            for sensor_data in sensors:
                if not validate_sensor(sensor_data, city_name):
                    continue
                
                sensor_id = sensor_data['sensor_id']
                
                # Vérifier si le capteur existe déjà
                existing_sensor = sensor_service.get_sensor(sensor_id)
                if existing_sensor and not replace:
                    print(f"   ⚠️  Capteur '{sensor_id}' existe déjà")
                    continue
                
                # Créer ou mettre à jour le capteur
                sensor = sensor_service.create_sensor(
                    sensor_id=sensor_id,
                    city_name=city_name,
                    latitude=sensor_data['latitude'],
                    longitude=sensor_data['longitude'],
                    description=sensor_data.get('description', '')
                )
                
                if sensor:
                    sensors_count += 1
                    print(f"   ✅ Capteur importé: {sensor_id}")
                else:
                    print(f"   ❌ Échec import capteur: {sensor_id}")
        else:
            print(f"❌ Échec import ville: {city_name}")
    
    return (cities_count, sensors_count)


def main():
    """Point d'entrée principal."""
    parser = argparse.ArgumentParser(
        description='Importe des villes et capteurs depuis un fichier JSON'
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
        print("Usage: python import_from_json.py data.json")
        print("   ou: python import_from_json.py --file data.json")
        sys.exit(1)
    
    # Initialiser la base de données
    print("📊 Initialisation de la base de données...")
    init_db()
    
    # Importer les données
    print(f"\n📥 Import depuis {json_file}...")
    if args.replace:
        print("⚠️  Mode remplacement activé")
    
    cities_count, sensors_count = import_from_json(json_file, args.replace)
    
    # Résumé
    print(f"\n{'='*60}")
    print(f"✅ Import terminé!")
    print(f"   Villes importées: {cities_count}")
    print(f"   Capteurs importés: {sensors_count}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
