"""
============================================================================
APP __init__.py - Initialisation de l'application
============================================================================
Description:
    Point d'entrée du package app.

Usage:
    from app import create_app
============================================================================
"""

from .api import create_app

__all__ = ['create_app']
