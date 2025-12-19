"""
============================================================================
DATABASE.PY - Configuration de la base de données SQLite
============================================================================
Description:
    Ce module configure la connexion à la base de données SQLite et définit
    tous les modèles de données pour le système de surveillance des inondations.

Tables:
    - config: Configuration système (MQTT, API keys, SMTP)
    - cities: Villes surveillées
    - sensors: Capteurs IoT déployés
    - alerts: Historique des alertes d'inondation
    - predictions: Historique des prédictions IA

Usage:
    from app.models.database import init_db, get_db_session
    init_db()  # Initialiser la base de données
    session = get_db_session()  # Obtenir une session

Debugging:
    - Vérifier que le fichier flood_monitoring.db est créé dans data/sqlite/
    - Utiliser SQLite Browser pour inspecter les tables
    - Activer echo=True dans create_engine pour voir les requêtes SQL
============================================================================
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chemin de la base de données
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, 'data', 'sqlite')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'flood_monitoring.db')

# Configuration SQLAlchemy
DATABASE_URL = f'sqlite:///{DB_PATH}'
engine = create_engine(DATABASE_URL, echo=False)  # echo=True pour debug SQL
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# MODÈLES DE DONNÉES
# ============================================================================

class Config(Base):
    """
    Table de configuration système.
    Stocke les clés API, paramètres MQTT, SMTP, etc.
    """
    __tablename__ = 'config'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Config(key='{self.key}', value='{self.value[:20]}...')>"


class City(Base):
    """
    Table des villes surveillées.
    Une ville peut contenir plusieurs capteurs.
    """
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<City(name='{self.name}', lat={self.latitude}, lon={self.longitude})>"


class Sensor(Base):
    """
    Table des capteurs IoT.
    Chaque capteur appartient à une ville et publie sur MQTT.
    
    Note: Les canaux (water_level, humidity) sont partagés par tous les capteurs.
    Ne pas stocker les canaux ici, ils sont définis globalement.
    """
    __tablename__ = 'sensors'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(50), unique=True, nullable=False, index=True)
    city_name = Column(String(100), nullable=False, index=True)  # Foreign key vers cities.name
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    active = Column(Boolean, default=True)
    last_seen = Column(DateTime, nullable=True)  # Dernière réception de données
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Sensor(sensor_id='{self.sensor_id}', city='{self.city_name}')>"


class Alert(Base):
    """
    Table des alertes d'inondation.
    Enregistre toutes les alertes générées par le système.
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    city_name = Column(String(100), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)  # 'flood_detected', 'flood_predicted'
    risk_level = Column(String(20), nullable=False)  # 'Low', 'Medium', 'High'
    probability = Column(Float, nullable=True)  # 0-100
    message = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Alert(sensor='{self.sensor_id}', type='{self.alert_type}', risk='{self.risk_level}')>"


class Prediction(Base):
    """
    Table des prédictions IA.
    Stocke l'historique de toutes les prédictions pour analyse et amélioration.
    """
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(String(50), nullable=False, index=True)
    city_name = Column(String(100), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Données d'entrée (JSON pour flexibilité)
    input_data = Column(JSON, nullable=True)
    
    # Résultats de prédiction
    flood_probability = Column(Float, nullable=False)  # 0-100
    risk_level = Column(String(20), nullable=False)  # 'Low', 'Medium', 'High'
    
    # Explication IA (optionnelle)
    explanation = Column(Text, nullable=True)
    
    # Métadonnées
    model_version = Column(String(50), nullable=True)
    
    def __repr__(self):
        return f"<Prediction(sensor='{self.sensor_id}', prob={self.flood_probability}%, risk='{self.risk_level}')>"


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def init_db():
    """
    Initialise la base de données.
    Crée toutes les tables si elles n'existent pas.
    
    Usage:
        init_db()
    
    Debugging:
        - Vérifier que flood_monitoring.db existe dans data/sqlite/
        - Vérifier les permissions du dossier
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de données initialisée: {DB_PATH}")


def get_db_session():
    """
    Retourne une nouvelle session de base de données.
    
    Usage:
        session = get_db_session()
        try:
            # Utiliser la session
            pass
        finally:
            session.close()
    
    Returns:
        Session SQLAlchemy
    """
    return SessionLocal()


def drop_all_tables():
    """
    DANGER: Supprime toutes les tables de la base de données.
    À utiliser uniquement pour le développement/test.
    
    Usage:
        drop_all_tables()
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  Toutes les tables ont été supprimées!")


# ============================================================================
# INITIALISATION AU DÉMARRAGE
# ============================================================================

if __name__ == "__main__":
    print("Initialisation de la base de données...")
    init_db()
    print("Base de données prête!")
