/**
 * ============================================================================
 * HOMEPAGE.TSX - Page d'accueil avec grille des villes
 * ============================================================================
 * Description: Affiche toutes les villes surveillées avec leurs statistiques
 * et niveau de risque. Dernière carte pour ajouter une ville/capteur.
 * 
 * Fonctionnalités:
 * - Grille responsive des villes
 * - Statut de risque par ville
 * - Nombre de capteurs
 * - Icône de notification si risque élevé
 * - Carte "+ Ajouter" pour nouvelle ville/capteur
 * ============================================================================
 */

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, AlertCircle, MapPin } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import api from '@/services/api'
import { getRiskBadgeColor } from '@/lib/utils'

interface City {
  name: string
  latitude: number
  longitude: number
  total_sensors: number
  active_sensors: number
}

interface RiskSummary {
  [cityName: string]: {
    total_sensors: number
    high_risk: number
    medium_risk: number
    low_risk: number
    avg_probability: number
    max_probability: number
  }
}

export default function HomePage() {
  const [cities, setCities] = useState<City[]>([])
  const [riskSummary, setRiskSummary] = useState<RiskSummary>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    // Rafraîchir toutes les 30 secondes
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [citiesResponse, riskResponse] = await Promise.all([
        api.getCities(),
        api.getPredictionsSummary(),
      ])

      if (citiesResponse.success) {
        setCities(citiesResponse.data)
      }

      if (riskResponse.success) {
        setRiskSummary(riskResponse.data)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const getCityRiskLevel = (cityName: string): string => {
    const risk = riskSummary[cityName]
    if (!risk) return 'Low'

    if (risk.high_risk > 0) return 'High'
    if (risk.medium_risk > 0) return 'Medium'
    return 'Low'
  }

  const getCityRiskVariant = (riskLevel: string): "success" | "warning" | "danger" => {
    switch (riskLevel) {
      case 'High':
        return 'danger'
      case 'Medium':
        return 'warning'
      default:
        return 'success'
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement des villes...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Villes surveillées</h2>
        <p className="text-muted-foreground">
          Sélectionnez une ville pour voir ses capteurs et prédictions
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {/* Cartes des villes */}
        {cities.map((city) => {
          const riskLevel = getCityRiskLevel(city.name)
          const hasAlert = riskLevel === 'High'

          return (
            <Link key={city.name} to={`/city/${encodeURIComponent(city.name)}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <CardTitle className="text-xl flex items-center gap-2">
                        <MapPin className="w-5 h-5 text-primary" />
                        {city.name}
                      </CardTitle>
                    </div>
                    {hasAlert && (
                      <AlertCircle className="w-5 h-5 text-red-500 animate-pulse" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Capteurs actifs</span>
                      <span className="font-semibold">
                        {city.active_sensors} / {city.total_sensors}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Niveau de risque</span>
                      <Badge variant={getCityRiskVariant(riskLevel)}>
                        {riskLevel}
                      </Badge>
                    </div>

                    {riskSummary[city.name] && (
                      <div className="pt-2 border-t">
                        <div className="text-xs text-muted-foreground mb-1">
                          Probabilité moyenne
                        </div>
                        <div className="text-lg font-bold text-primary">
                          {riskSummary[city.name].avg_probability.toFixed(1)}%
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}

        {/* Carte "Ajouter" */}
        <Link to="/setup">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full border-dashed border-2 hover:border-primary">
            <CardContent className="flex flex-col items-center justify-center h-full min-h-[200px]">
              <Plus className="w-12 h-12 text-muted-foreground mb-4" />
              <p className="text-lg font-semibold text-muted-foreground">
                Ajouter une ville
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                ou un capteur
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {cities.length === 0 && (
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Aucune ville configurée</h3>
          <p className="text-muted-foreground mb-4">
            Commencez par ajouter une ville et un capteur
          </p>
          <Link
            to="/setup"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Ajouter une ville
          </Link>
        </div>
      )}
    </div>
  )
}
