"""
============================================================================
APP __init__.py - Initialisation de l'application
============================================================================
Description:
    Point d'entrée du package app.
    
    Note: Les imports sont lazy pour éviter les dépendances circulaires
    et permettre l'utilisation de modules individuels (comme database)
    sans charger toute l'application.

Usage:
    from app import create_app
    from app.models.database import get_db_connection
============================================================================
"""

# Pas d'import automatique pour éviter les dépendances circulaires
# Les imports se font à la demande

__all__ = ['create_app']


def create_app():
    """
    Lazy import de create_app pour éviter de charger Flask
    si on veut juste utiliser la base de données.
    """
    from .api import create_app as _create_app
    return _create_app()
