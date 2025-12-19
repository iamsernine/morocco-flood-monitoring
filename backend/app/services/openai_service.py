"""
============================================================================
OPENAI_SERVICE.PY - Service d'explications IA via OpenAI
============================================================================
Description:
    Service qui utilise l'API OpenAI pour générer des explications en
    langage naturel des prédictions d'inondation et créer des rapports.

Fonctionnalités:
    - Génération d'explications pour les prédictions
    - Création de rapports personnalisés
    - Optimisation des tokens pour minimiser les coûts
    - Support multilingue (français par défaut)

Usage:
    from app.services.openai_service import OpenAIService
    
    service = OpenAIService()
    explanation = service.generate_explanation(prediction_data)
    report = service.generate_report(cities, sensors, metrics, time_range)

Debugging:
    - Vérifier que la clé API OpenAI est configurée
    - Surveiller l'utilisation des tokens
    - Tester avec des données simulées
    - Vérifier les logs d'erreur API
============================================================================
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from openai import OpenAI

from app.services.config_service import get_config_service


class OpenAIService:
    """
    Service d'explications IA via OpenAI.
    """
    
    def __init__(self):
        """Initialise le service OpenAI."""
        self.config = get_config_service()
        
        # Récupérer la clé API
        api_key = self.config.get('openai_api_key', '')
        
        if not api_key or api_key.strip() == '':
            print("⚠️  Clé API OpenAI non configurée")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)
            print("✅ Service OpenAI initialisé")
        
        # Configuration par défaut
        self.model = "gpt-4.1-mini"  # Modèle optimisé coût/performance
        self.max_tokens = 500  # Limite pour minimiser les coûts
        self.temperature = 0.7
    
    def is_available(self) -> bool:
        """
        Vérifie si le service OpenAI est disponible.
        
        Returns:
            True si la clé API est configurée, False sinon
        """
        return self.client is not None
    
    def generate_explanation(self, prediction_data: Dict[str, Any], 
                           language: str = 'fr') -> Optional[str]:
        """
        Génère une explication en langage naturel pour une prédiction.
        
        Args:
            prediction_data: Données de prédiction (probability, risk_level, input_data)
            language: Langue de l'explication ('fr' ou 'en')
        
        Returns:
            Texte d'explication ou None si erreur
        """
        if not self.is_available():
            return self._generate_fallback_explanation(prediction_data, language)
        
        try:
            # Construire le prompt
            prompt = self._build_explanation_prompt(prediction_data, language)
            
            # Appel API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            explanation = response.choices[0].message.content.strip()
            
            # Log de l'utilisation des tokens
            tokens_used = response.usage.total_tokens
            print(f"📊 Tokens utilisés: {tokens_used}")
            
            return explanation
        
        except Exception as e:
            print(f"❌ Erreur lors de la génération de l'explication: {e}")
            return self._generate_fallback_explanation(prediction_data, language)
    
    def _get_system_prompt(self, language: str) -> str:
        """
        Retourne le prompt système selon la langue.
        
        Args:
            language: Langue ('fr' ou 'en')
        
        Returns:
            Prompt système
        """
        if language == 'fr':
            return """Tu es un expert en hydrologie et gestion des risques d'inondation au Maroc.
            Tu dois expliquer les prédictions d'inondation de manière claire et concise pour 
            des gestionnaires municipaux. Utilise un langage professionnel mais accessible.
            Limite tes réponses à 2-3 phrases maximum."""
        else:
            return """You are an expert in hydrology and flood risk management in Morocco.
            You must explain flood predictions clearly and concisely for municipal managers.
            Use professional but accessible language. Limit your responses to 2-3 sentences maximum."""
    
    def _build_explanation_prompt(self, prediction_data: Dict[str, Any], 
                                 language: str) -> str:
        """
        Construit le prompt pour l'explication.
        
        Args:
            prediction_data: Données de prédiction
            language: Langue
        
        Returns:
            Prompt formaté
        """
        sensor_id = prediction_data.get('sensor_id', 'N/A')
        city = prediction_data.get('city_name', 'N/A')
        probability = prediction_data.get('probability', 0)
        risk_level = prediction_data.get('risk_level', 'Low')
        
        input_data = prediction_data.get('input_data', {})
        water_level = input_data.get('water_level_avg', 0)
        rainfall = input_data.get('rainfall', 0)
        river_level = input_data.get('river_level', 0)
        
        if language == 'fr':
            prompt = f"""Explique cette prédiction d'inondation:
            
Ville: {city}
Capteur: {sensor_id}
Probabilité d'inondation: {probability}%
Niveau de risque: {risk_level}

Données clés:
- Niveau d'eau: {water_level} cm
- Précipitations: {rainfall} mm
- Niveau de la rivière: {river_level} cm

Fournis une explication concise (2-3 phrases) des facteurs de risque et recommandations."""
        else:
            prompt = f"""Explain this flood prediction:
            
City: {city}
Sensor: {sensor_id}
Flood probability: {probability}%
Risk level: {risk_level}

Key data:
- Water level: {water_level} cm
- Rainfall: {rainfall} mm
- River level: {river_level} cm

Provide a concise explanation (2-3 sentences) of risk factors and recommendations."""
        
        return prompt
    
    def _generate_fallback_explanation(self, prediction_data: Dict[str, Any], 
                                      language: str) -> str:
        """
        Génère une explication simple sans OpenAI (fallback).
        
        Args:
            prediction_data: Données de prédiction
            language: Langue
        
        Returns:
            Explication générée
        """
        probability = prediction_data.get('probability', 0)
        risk_level = prediction_data.get('risk_level', 'Low')
        
        if language == 'fr':
            if risk_level == 'High':
                return f"Risque élevé d'inondation détecté ({probability}%). Surveillance accrue recommandée et activation des mesures préventives."
            elif risk_level == 'Medium':
                return f"Risque modéré d'inondation ({probability}%). Maintenir la surveillance et préparer les équipes d'intervention."
            else:
                return f"Risque faible d'inondation ({probability}%). Situation normale, surveillance de routine."
        else:
            if risk_level == 'High':
                return f"High flood risk detected ({probability}%). Increased monitoring and preventive measures recommended."
            elif risk_level == 'Medium':
                return f"Moderate flood risk ({probability}%). Maintain monitoring and prepare response teams."
            else:
                return f"Low flood risk ({probability}%). Normal situation, routine monitoring."
    
    def generate_report(self, cities: List[str], sensors: List[str], 
                       metrics: List[str], time_range: str,
                       summary_data: Dict[str, Any],
                       language: str = 'fr') -> Optional[str]:
        """
        Génère un rapport personnalisé.
        
        Args:
            cities: Liste des villes à inclure
            sensors: Liste des capteurs à inclure
            metrics: Liste des métriques à analyser
            time_range: Période du rapport
            summary_data: Données de synthèse
            language: Langue du rapport
        
        Returns:
            Texte du rapport ou None si erreur
        """
        if not self.is_available():
            return self._generate_fallback_report(cities, sensors, time_range, summary_data, language)
        
        try:
            # Construire le prompt
            prompt = self._build_report_prompt(cities, sensors, metrics, time_range, summary_data, language)
            
            # Appel API OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_report_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=1000,  # Plus de tokens pour un rapport complet
                temperature=0.7,
            )
            
            report = response.choices[0].message.content.strip()
            
            # Log de l'utilisation des tokens
            tokens_used = response.usage.total_tokens
            print(f"📊 Tokens utilisés pour le rapport: {tokens_used}")
            
            return report
        
        except Exception as e:
            print(f"❌ Erreur lors de la génération du rapport: {e}")
            return self._generate_fallback_report(cities, sensors, time_range, summary_data, language)
    
    def _get_report_system_prompt(self, language: str) -> str:
        """Retourne le prompt système pour les rapports."""
        if language == 'fr':
            return """Tu es un expert en analyse de données hydrologiques et gestion des risques.
            Tu dois créer des rapports professionnels pour les autorités municipales marocaines.
            Structure le rapport avec des sections claires: Résumé, Analyse, Recommandations."""
        else:
            return """You are an expert in hydrological data analysis and risk management.
            You must create professional reports for Moroccan municipal authorities.
            Structure the report with clear sections: Summary, Analysis, Recommendations."""
    
    def _build_report_prompt(self, cities: List[str], sensors: List[str],
                            metrics: List[str], time_range: str,
                            summary_data: Dict[str, Any], language: str) -> str:
        """Construit le prompt pour le rapport."""
        if language == 'fr':
            prompt = f"""Génère un rapport de surveillance des inondations:

Période: {time_range}
Villes: {', '.join(cities)}
Nombre de capteurs: {len(sensors)}
Métriques analysées: {', '.join(metrics)}

Données de synthèse:
{self._format_summary_data(summary_data, language)}

Crée un rapport structuré avec:
1. Résumé exécutif
2. Analyse des risques par ville
3. Recommandations d'action"""
        else:
            prompt = f"""Generate a flood monitoring report:

Period: {time_range}
Cities: {', '.join(cities)}
Number of sensors: {len(sensors)}
Analyzed metrics: {', '.join(metrics)}

Summary data:
{self._format_summary_data(summary_data, language)}

Create a structured report with:
1. Executive summary
2. Risk analysis by city
3. Action recommendations"""
        
        return prompt
    
    def _format_summary_data(self, summary_data: Dict[str, Any], language: str) -> str:
        """Formate les données de synthèse pour le prompt."""
        formatted = []
        for city, data in summary_data.items():
            if language == 'fr':
                formatted.append(f"- {city}: {data.get('total_sensors', 0)} capteurs, "
                               f"risque moyen {data.get('avg_probability', 0)}%, "
                               f"{data.get('high_risk', 0)} alertes élevées")
            else:
                formatted.append(f"- {city}: {data.get('total_sensors', 0)} sensors, "
                               f"average risk {data.get('avg_probability', 0)}%, "
                               f"{data.get('high_risk', 0)} high alerts")
        return '\n'.join(formatted)
    
    def _generate_fallback_report(self, cities: List[str], sensors: List[str],
                                 time_range: str, summary_data: Dict[str, Any],
                                 language: str) -> str:
        """Génère un rapport simple sans OpenAI."""
        if language == 'fr':
            report = f"""RAPPORT DE SURVEILLANCE DES INONDATIONS
Période: {time_range}
Généré le: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

RÉSUMÉ
Villes surveillées: {', '.join(cities)}
Nombre de capteurs: {len(sensors)}

ANALYSE PAR VILLE
"""
            for city, data in summary_data.items():
                report += f"\n{city}:\n"
                report += f"  - Capteurs actifs: {data.get('total_sensors', 0)}\n"
                report += f"  - Probabilité moyenne: {data.get('avg_probability', 0)}%\n"
                report += f"  - Alertes élevées: {data.get('high_risk', 0)}\n"
            
            report += "\nRECOMMANDATIONS\n"
            report += "- Maintenir la surveillance continue\n"
            report += "- Vérifier l'état des équipements\n"
            report += "- Préparer les équipes d'intervention\n"
        else:
            report = f"""FLOOD MONITORING REPORT
Period: {time_range}
Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}

SUMMARY
Monitored cities: {', '.join(cities)}
Number of sensors: {len(sensors)}

ANALYSIS BY CITY
"""
            for city, data in summary_data.items():
                report += f"\n{city}:\n"
                report += f"  - Active sensors: {data.get('total_sensors', 0)}\n"
                report += f"  - Average probability: {data.get('avg_probability', 0)}%\n"
                report += f"  - High alerts: {data.get('high_risk', 0)}\n"
            
            report += "\nRECOMMENDATIONS\n"
            report += "- Maintain continuous monitoring\n"
            report += "- Check equipment status\n"
            report += "- Prepare response teams\n"
        
        return report


# ============================================================================
# TESTS
# ============================================================================

if __name__ == "__main__":
    print("Test du OpenAIService...")
    service = OpenAIService()
    
    if service.is_available():
        # Test explication
        test_prediction = {
            'sensor_id': 'CAS_1',
            'city_name': 'Casablanca',
            'probability': 75.5,
            'risk_level': 'High',
            'input_data': {
                'water_level_avg': 80.0,
                'rainfall': 35.0,
                'river_level': 70.0,
            }
        }
        
        explanation = service.generate_explanation(test_prediction, 'fr')
        print(f"\nExplication générée:\n{explanation}")
    else:
        print("⚠️  Service OpenAI non disponible (clé API manquante)")
        
        # Test fallback
        test_prediction = {
            'probability': 75.5,
            'risk_level': 'High',
        }
        explanation = service._generate_fallback_explanation(test_prediction, 'fr')
        print(f"\nExplication fallback:\n{explanation}")
    
    print("\n✅ Tests terminés!")
