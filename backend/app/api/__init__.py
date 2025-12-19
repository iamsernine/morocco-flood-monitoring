"""
============================================================================
API __init__.py - Initialisation du module API
============================================================================
Description:
    Expose les fonctions de création de l'application Flask.

Usage:
    from app.api import create_app
============================================================================
"""

from .routes import create_app

__all__ = ['create_app']
