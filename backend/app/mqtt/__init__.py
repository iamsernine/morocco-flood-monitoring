"""
============================================================================
MQTT __init__.py - Initialisation du module MQTT
============================================================================
Description:
    Expose le client MQTT.

Usage:
    from app.mqtt import MQTTClient
============================================================================
"""

from .mqtt_client import MQTTClient

__all__ = ['MQTTClient']
