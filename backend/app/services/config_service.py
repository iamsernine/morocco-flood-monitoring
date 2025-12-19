"""
============================================================================
CONFIG_SERVICE.PY - Service de gestion de la configuration
============================================================================
Description:
    Gère la configuration système stockée dans SQLite.
    Fournit des méthodes pour lire/écrire les paramètres de configuration.

Configuration gérée:
    - MQTT: broker_host, broker_port, broker_username, broker_password
    - OpenWeather API: openweather_api_key
    - OpenAI API: openai_api_key
    - SMTP: smtp_host, smtp_port, smtp_sender, smtp_password
    - Système: setup_completed, aggregation_interval

Usage:
    from app.services.config_service import ConfigService
    
    config = ConfigService()
    config.set('mqtt_broker_host', 'localhost')
    host = config.get('mqtt_broker_host')
    
    if not config.is_setup_complete():
        # Rediriger vers le wizard

Debugging:
    - Vérifier que la table 'config' existe dans la DB
    - Utiliser get_all() pour voir toutes les configurations
    - Les valeurs sensibles ne sont jamais loggées
============================================================================
"""

from typing import Optional, Dict, Any
from app.models import Config, get_db_session
from datetime import datetime


class ConfigService:
    """
    Service de gestion de la configuration système.
    """
    
    # Clés de configuration par défaut
    DEFAULT_CONFIG = {
        'setup_completed': 'false',
        'aggregation_interval': '300',  # 5 minutes en secondes
        'mqtt_broker_host': '',
        'mqtt_broker_port': '1883',
        'mqtt_broker_username': '',
        'mqtt_broker_password': '',
        'openweather_api_key': '',
        'openai_api_key': '',
        'smtp_host': '',
        'smtp_port': '587',
        'smtp_sender': '',
        'smtp_password': '',
        'buffer_window_minutes': '30',  # Fenêtre de buffer pour agrégation
        'model_version': 'v1.0',
    }
    
    def __init__(self):
        """Initialise le service de configuration."""
        self._ensure_defaults()
    
    def _ensure_defaults(self):
        """
        S'assure que toutes les clés par défaut existent dans la DB.
        Crée les clés manquantes avec leurs valeurs par défaut.
        """
        session = get_db_session()
        try:
            for key, default_value in self.DEFAULT_CONFIG.items():
                existing = session.query(Config).filter_by(key=key).first()
                if not existing:
                    config_entry = Config(
                        key=key,
                        value=default_value,
                        description=self._get_description(key)
                    )
                    session.add(config_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de l'initialisation de la configuration: {e}")
        finally:
            session.close()
    
    def _get_description(self, key: str) -> str:
        """Retourne une description pour une clé de configuration."""
        descriptions = {
            'setup_completed': 'Indique si le setup wizard a été complété',
            'aggregation_interval': 'Intervalle d\'agrégation des données en secondes',
            'mqtt_broker_host': 'Adresse du broker MQTT',
            'mqtt_broker_port': 'Port du broker MQTT',
            'mqtt_broker_username': 'Nom d\'utilisateur MQTT',
            'mqtt_broker_password': 'Mot de passe MQTT',
            'openweather_api_key': 'Clé API OpenWeatherMap',
            'openai_api_key': 'Clé API OpenAI',
            'smtp_host': 'Serveur SMTP pour l\'envoi d\'emails',
            'smtp_port': 'Port SMTP',
            'smtp_sender': 'Adresse email expéditeur',
            'smtp_password': 'Mot de passe email',
            'buffer_window_minutes': 'Fenêtre de buffer en minutes',
            'model_version': 'Version du modèle ML',
        }
        return descriptions.get(key, '')
    
    def _clean_value(self, value: Optional[str]) -> Optional[str]:
        """
        Nettoie une valeur de configuration en enlevant les guillemets.
        
        Args:
            value: Valeur à nettoyer
        
        Returns:
            Valeur nettoyée
        """
        if value is None:
            return None
        # Enlever les guillemets simples et doubles au début/fin
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            value = value[1:-1]
        return value
    
    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Récupère une valeur de configuration.
        
        Args:
            key: Clé de configuration
            default: Valeur par défaut si la clé n'existe pas
        
        Returns:
            Valeur de configuration ou default (nettoyée)
        """
        session = get_db_session()
        try:
            config = session.query(Config).filter_by(key=key).first()
            if config:
                return self._clean_value(config.value)
            return default
        finally:
            session.close()
    
    def set(self, key: str, value: str, description: Optional[str] = None) -> bool:
        """
        Définit une valeur de configuration.
        
        Args:
            key: Clé de configuration
            value: Valeur à stocker
            description: Description optionnelle
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            config = session.query(Config).filter_by(key=key).first()
            if config:
                config.value = value
                config.updated_at = datetime.utcnow()
                if description:
                    config.description = description
            else:
                config = Config(
                    key=key,
                    value=value,
                    description=description or self._get_description(key)
                )
                session.add(config)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la sauvegarde de la configuration {key}: {e}")
            return False
        finally:
            session.close()
    
    def get_all(self) -> Dict[str, str]:
        """
        Récupère toutes les configurations.
        
        Returns:
            Dictionnaire {key: value}
        """
        session = get_db_session()
        try:
            configs = session.query(Config).all()
            return {config.key: config.value for config in configs}
        finally:
            session.close()
    
    def delete(self, key: str) -> bool:
        """
        Supprime une configuration.
        
        Args:
            key: Clé à supprimer
        
        Returns:
            True si succès, False sinon
        """
        session = get_db_session()
        try:
            config = session.query(Config).filter_by(key=key).first()
            if config:
                session.delete(config)
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            print(f"❌ Erreur lors de la suppression de la configuration {key}: {e}")
            return False
        finally:
            session.close()
    
    def is_setup_complete(self) -> bool:
        """
        Vérifie si le setup wizard a été complété.
        
        Returns:
            True si le setup est complet, False sinon
        """
        value = self.get('setup_completed', 'false')
        return value.lower() == 'true'
    
    def mark_setup_complete(self) -> bool:
        """
        Marque le setup comme complété.
        
        Returns:
            True si succès
        """
        return self.set('setup_completed', 'true')
    
    def get_mqtt_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration MQTT.
        
        Returns:
            Dictionnaire avec host, port, username, password
        """
        return {
            'host': self.get('mqtt_broker_host', 'localhost'),
            'port': int(self.get('mqtt_broker_port', '1883')),
            'username': self.get('mqtt_broker_username', ''),
            'password': self.get('mqtt_broker_password', ''),
        }
    
    def get_smtp_config(self) -> Dict[str, Any]:
        """
        Récupère la configuration SMTP.
        
        Returns:
            Dictionnaire avec host, port, sender, password
        """
        return {
            'host': self.get('smtp_host', ''),
            'port': int(self.get('smtp_port', '587')),
            'sender': self.get('smtp_sender', ''),
            'password': self.get('smtp_password', ''),
        }
    
    def validate_required_config(self) -> tuple[bool, list[str]]:
        """
        Valide que toutes les configurations requises sont présentes.
        
        Returns:
            (is_valid, missing_keys)
        """
        required_keys = [
            'mqtt_broker_host',
            'openweather_api_key',
            'openai_api_key',
        ]
        
        missing = []
        for key in required_keys:
            value = self.get(key)
            if not value or value.strip() == '':
                missing.append(key)
        
        return (len(missing) == 0, missing)


# ============================================================================
# INSTANCE GLOBALE (Singleton pattern)
# ============================================================================

_config_service_instance = None

def get_config_service() -> ConfigService:
    """
    Retourne l'instance singleton du ConfigService.
    
    Usage:
        config = get_config_service()
        api_key = config.get('openai_api_key')
    """
    global _config_service_instance
    if _config_service_instance is None:
        _config_service_instance = ConfigService()
    return _config_service_instance


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    # Test du service de configuration
    from app.models import init_db
    
    print("Initialisation de la base de données...")
    init_db()
    
    print("\nTest du ConfigService...")
    config = ConfigService()
    
    # Test set/get
    config.set('test_key', 'test_value', 'Clé de test')
    print(f"test_key = {config.get('test_key')}")
    
    # Test get_all
    print(f"\nToutes les configurations: {len(config.get_all())} clés")
    
    # Test validation
    is_valid, missing = config.validate_required_config()
    print(f"\nConfiguration valide: {is_valid}")
    if not is_valid:
        print(f"Clés manquantes: {missing}")
    
    print("\n✅ Tests terminés!")
