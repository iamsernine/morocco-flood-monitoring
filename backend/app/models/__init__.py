"""
============================================================================
MODELS __init__.py - Initialisation du module models
============================================================================
Description:
    Expose les modèles de base de données et les fonctions utilitaires.

Usage:
    from app.models import Config, City, Sensor, Alert, Prediction
    from app.models import init_db, get_db_session
============================================================================
"""

from .database import (
    Base,
    Config,
    City,
    Sensor,
    Alert,
    Prediction,
    init_db,
    get_db_session,
    drop_all_tables
)

__all__ = [
    'Base',
    'Config',
    'City',
    'Sensor',
    'Alert',
    'Prediction',
    'init_db',
    'get_db_session',
    'drop_all_tables'
]
