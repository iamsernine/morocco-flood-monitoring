"""
============================================================================
SENSOR_SERVICE.PY - Service de gestion des capteurs
============================================================================
Description:
    Gère les opérations CRUD sur les capteurs et les villes.
    Fournit des méthodes pour ajouter, modifier, supprimer et récupérer
    les capteurs et villes.

Fonctionnalités:
    - CRUD complet pour capteurs et villes
    - Validation des données
    - Gestion des relations ville-capteur
    - Import/export JSON

Usage:
    from app.services.sensor_service import SensorService
    
    service = SensorService()
    sensor = service.add_sensor('CAS_1', 'Casablanca', 33.5731, -7.5898)
    sensors = service.get_sensors_by_city('Casablanca')

Debugging:
    - Vérifier que les tables cities et sensors existent
    - Les sensor_id doivent être uniques
    - Les city_name doivent correspondre à des villes existantes
============================================================================
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models import City, Sensor, get_db_session


class SensorService:
    """
    Service de gestion des capteurs et villes.
    """
    
    # ========================================================================
    # GESTION DES VILLES
    # ========================================================================
    
    def add_city(self, name: str, latitude: float, longitude: float, 
                 description: Optional[str] = None) -> Optional[City]:
        """
        Ajoute une nouvelle ville.
        
        Args:
            name: Nom de la ville (unique)
            latitude: Latitude
            longitude: Longitude
            description: Description optionnelle
        
        Returns:
            Objet City créé ou None si erreur
        """
        session = get_db_session()
        try:
            # Vérifier si la ville existe déjà
            existing = session.query(City).filter_by(name=name).first()
            if existing:
                print(f"⚠️  La ville {name} existe déjà")
                return existing
            
            city = City(
                name=name,
                latitude=latitude,
                longitude=longitude,
                description=description,
                active=True
            )
            session.add(city)
            session.commit()
            session.refresh(city)
            print(f"✅ Ville ajoutée: {name}")
            return city
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de l'ajout de la ville {name}: {e}")
            return None
        finally:
            session.close()
    
    def get_city(self, name: str) -> Optional[City]:
        """
        Récupère une ville par son nom.
        
        Args:
            name: Nom de la ville
        
        Returns:
            Objet City ou None
        """
        session = get_db_session()
        try:
            return session.query(City).filter_by(name=name).first()
        finally:
            session.close()
    
    def get_all_cities(self, active_only: bool = True) -> List[City]:
        """
        Récupère toutes les villes.
        
        Args:
            active_only: Si True, ne retourne que les villes actives
        
        Returns:
            Liste des villes
        """
        session = get_db_session()
        try:
            query = session.query(City)
            if active_only:
                query = query.filter_by(active=True)
            return query.all()
        finally:
            session.close()
    
    def update_city(self, name: str, **kwargs) -> bool:
        """
        Met à jour une ville.
        
        Args:
            name: Nom de la ville
            **kwargs: Champs à mettre à jour
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            city = session.query(City).filter_by(name=name).first()
            if not city:
                print(f"⚠️  Ville {name} non trouvée")
                return False
            
            for key, value in kwargs.items():
                if hasattr(city, key):
                    setattr(city, key, value)
            
            city.updated_at = datetime.utcnow()
            session.commit()
            print(f"✅ Ville mise à jour: {name}")
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la mise à jour de la ville {name}: {e}")
            return False
        finally:
            session.close()
    
    def delete_city(self, name: str, force: bool = False) -> bool:
        """
        Supprime une ville.
        
        Args:
            name: Nom de la ville
            force: Si True, supprime même si des capteurs existent
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            city = session.query(City).filter_by(name=name).first()
            if not city:
                print(f"⚠️  Ville {name} non trouvée")
                return False
            
            # Vérifier s'il y a des capteurs
            sensors = session.query(Sensor).filter_by(city_name=name).count()
            if sensors > 0 and not force:
                print(f"⚠️  La ville {name} contient {sensors} capteur(s). Utilisez force=True pour supprimer.")
                return False
            
            # Supprimer les capteurs si force=True
            if force and sensors > 0:
                session.query(Sensor).filter_by(city_name=name).delete()
            
            session.delete(city)
            session.commit()
            print(f"✅ Ville supprimée: {name}")
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression de la ville {name}: {e}")
            return False
        finally:
            session.close()
    
    # ========================================================================
    # GESTION DES CAPTEURS
    # ========================================================================
    
    def add_sensor(self, sensor_id: str, city_name: str, latitude: float, 
                   longitude: float, description: Optional[str] = None) -> Optional[Sensor]:
        """
        Ajoute un nouveau capteur.
        
        Args:
            sensor_id: Identifiant unique du capteur
            city_name: Nom de la ville
            latitude: Latitude
            longitude: Longitude
            description: Description optionnelle
        
        Returns:
            Objet Sensor créé ou None si erreur
        """
        session = get_db_session()
        try:
            # Vérifier si le capteur existe déjà
            existing = session.query(Sensor).filter_by(sensor_id=sensor_id).first()
            if existing:
                print(f"⚠️  Le capteur {sensor_id} existe déjà")
                return existing
            
            # Vérifier si la ville existe
            city = session.query(City).filter_by(name=city_name).first()
            if not city:
                # Créer la ville automatiquement
                print(f"ℹ️  Création automatique de la ville {city_name}")
                city = City(
                    name=city_name,
                    latitude=latitude,
                    longitude=longitude,
                    active=True
                )
                session.add(city)
                session.flush()
            
            sensor = Sensor(
                sensor_id=sensor_id,
                city_name=city_name,
                latitude=latitude,
                longitude=longitude,
                description=description,
                active=True
            )
            session.add(sensor)
            session.commit()
            session.refresh(sensor)
            print(f"✅ Capteur ajouté: {sensor_id} ({city_name})")
            return sensor
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de l'ajout du capteur {sensor_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_sensor(self, sensor_id: str) -> Optional[Sensor]:
        """
        Récupère un capteur par son ID.
        
        Args:
            sensor_id: Identifiant du capteur
        
        Returns:
            Objet Sensor ou None
        """
        session = get_db_session()
        try:
            return session.query(Sensor).filter_by(sensor_id=sensor_id).first()
        finally:
            session.close()
    
    def get_all_sensors(self, active_only: bool = True) -> List[Sensor]:
        """
        Récupère tous les capteurs.
        
        Args:
            active_only: Si True, ne retourne que les capteurs actifs
        
        Returns:
            Liste des capteurs
        """
        session = get_db_session()
        try:
            query = session.query(Sensor)
            if active_only:
                query = query.filter_by(active=True)
            return query.all()
        finally:
            session.close()
    
    def get_sensors_by_city(self, city_name: str, active_only: bool = True) -> List[Sensor]:
        """
        Récupère tous les capteurs d'une ville.
        
        Args:
            city_name: Nom de la ville
            active_only: Si True, ne retourne que les capteurs actifs
        
        Returns:
            Liste des capteurs
        """
        session = get_db_session()
        try:
            query = session.query(Sensor).filter_by(city_name=city_name)
            if active_only:
                query = query.filter_by(active=True)
            return query.all()
        finally:
            session.close()
    
    def update_sensor(self, sensor_id: str, **kwargs) -> bool:
        """
        Met à jour un capteur.
        
        Args:
            sensor_id: Identifiant du capteur
            **kwargs: Champs à mettre à jour
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            sensor = session.query(Sensor).filter_by(sensor_id=sensor_id).first()
            if not sensor:
                print(f"⚠️  Capteur {sensor_id} non trouvé")
                return False
            
            for key, value in kwargs.items():
                if hasattr(sensor, key):
                    setattr(sensor, key, value)
            
            sensor.updated_at = datetime.utcnow()
            session.commit()
            print(f"✅ Capteur mis à jour: {sensor_id}")
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la mise à jour du capteur {sensor_id}: {e}")
            return False
        finally:
            session.close()
    
    def update_sensor_last_seen(self, sensor_id: str) -> bool:
        """
        Met à jour le timestamp last_seen d'un capteur.
        
        Args:
            sensor_id: Identifiant du capteur
        
        Returns:
            True si succès, False sinon
        """
        return self.update_sensor(sensor_id, last_seen=datetime.utcnow())
    
    def delete_sensor(self, sensor_id: str) -> bool:
        """
        Supprime un capteur.
        
        Args:
            sensor_id: Identifiant du capteur
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            sensor = session.query(Sensor).filter_by(sensor_id=sensor_id).first()
            if not sensor:
                print(f"⚠️  Capteur {sensor_id} non trouvé")
                return False
            
            session.delete(sensor)
            session.commit()
            print(f"✅ Capteur supprimé: {sensor_id}")
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression du capteur {sensor_id}: {e}")
            return False
        finally:
            session.close()
    
    # ========================================================================
    # IMPORT/EXPORT
    # ========================================================================
    
    def import_sensor_from_json(self, data: Dict[str, Any]) -> Optional[Sensor]:
        """
        Importe un capteur depuis un dictionnaire JSON.
        
        Args:
            data: Dictionnaire avec sensor_id, city, lat, lon
        
        Returns:
            Objet Sensor créé ou None
        """
        required_fields = ['sensor_id', 'city', 'lat', 'lon']
        for field in required_fields:
            if field not in data:
                print(f"❌ Champ requis manquant: {field}")
                return None
        
        return self.add_sensor(
            sensor_id=data['sensor_id'],
            city_name=data['city'],
            latitude=float(data['lat']),
            longitude=float(data['lon']),
            description=data.get('description')
        )
    
    def export_sensor_to_json(self, sensor_id: str) -> Optional[Dict[str, Any]]:
        """
        Exporte un capteur vers un dictionnaire JSON.
        
        Args:
            sensor_id: Identifiant du capteur
        
        Returns:
            Dictionnaire JSON ou None
        """
        sensor = self.get_sensor(sensor_id)
        if not sensor:
            return None
        
        return {
            'sensor_id': sensor.sensor_id,
            'city': sensor.city_name,
            'lat': sensor.latitude,
            'lon': sensor.longitude,
            'description': sensor.description,
            'active': sensor.active,
            'last_seen': sensor.last_seen.isoformat() if sensor.last_seen else None,
        }
    
    def get_city_stats(self, city_name: str) -> Dict[str, Any]:
        """
        Récupère les statistiques d'une ville.
        
        Args:
            city_name: Nom de la ville
        
        Returns:
            Dictionnaire avec statistiques
        """
        session = get_db_session()
        try:
            city = session.query(City).filter_by(name=city_name).first()
            if not city:
                return {}
            
            total_sensors = session.query(Sensor).filter_by(city_name=city_name).count()
            active_sensors = session.query(Sensor).filter_by(city_name=city_name, active=True).count()
            
            return {
                'city_name': city_name,
                'total_sensors': total_sensors,
                'active_sensors': active_sensors,
                'latitude': city.latitude,
                'longitude': city.longitude,
            }
        finally:
            session.close()


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    from app.models import init_db
    
    print("Initialisation de la base de données...")
    init_db()
    
    print("\nTest du SensorService...")
    service = SensorService()
    
    # Test ajout ville
    service.add_city('Casablanca', 33.5731, -7.5898, 'Capitale économique')
    
    # Test ajout capteur
    service.add_sensor('CAS_1', 'Casablanca', 33.5731, -7.5898, 'Capteur centre-ville')
    service.add_sensor('CAS_2', 'Casablanca', 33.5800, -7.5900, 'Capteur port')
    
    # Test récupération
    sensors = service.get_sensors_by_city('Casablanca')
    print(f"\nCapteurs à Casablanca: {len(sensors)}")
    for sensor in sensors:
        print(f"  - {sensor.sensor_id}")
    
    # Test stats
    stats = service.get_city_stats('Casablanca')
    print(f"\nStats Casablanca: {stats}")
    
    print("\n✅ Tests terminés!")
