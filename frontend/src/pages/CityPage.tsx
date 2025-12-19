/**
 * ============================================================================
 * CITYPAGE.TSX - Page ville avec grille des capteurs
 * ============================================================================
 * Description: Affiche tous les capteurs d'une ville avec leurs statuts.
 * Fil d'Ariane: Accueil > Ville
 * ============================================================================
 */

import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ChevronRight, Home, Plus, AlertCircle, Activity } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import api from '@/services/api'
import { formatDate } from '@/lib/utils'

interface Sensor {
  sensor_id: string
  city_name: string
  latitude: number
  longitude: number
  description: string | null
  active: boolean
  last_seen: string | null
}

export default function CityPage() {
  const { cityName } = useParams<{ cityName: string }>()
  const [sensors, setSensors] = useState<Sensor[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (cityName) {
      loadSensors()
      const interval = setInterval(loadSensors, 30000)
      return () => clearInterval(interval)
    }
  }, [cityName])

  const loadSensors = async () => {
    try {
      const response = await api.getSensors(cityName)
      if (response.success) {
        setSensors(response.data)
      }
    } catch (error) {
      console.error('Failed to load sensors:', error)
    } finally {
      setLoading(false)
    }
  }

  const getSensorStatus = (sensor: Sensor): { label: string; variant: "success" | "warning" | "danger" } => {
    if (!sensor.active) {
      return { label: 'Inactif', variant: 'danger' }
    }

    if (!sensor.last_seen) {
      return { label: 'Jamais vu', variant: 'warning' }
    }

    const lastSeen = new Date(sensor.last_seen)
    const now = new Date()
    const diffMinutes = (now.getTime() - lastSeen.getTime()) / 1000 / 60

    if (diffMinutes > 30) {
      return { label: 'Hors ligne', variant: 'danger' }
    } else if (diffMinutes > 10) {
      return { label: 'Inactif', variant: 'warning' }
    } else {
      return { label: 'En ligne', variant: 'success' }
    }
  }

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement des capteurs...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Fil d'Ariane */}
      <nav className="flex items-center gap-2 text-sm text-muted-foreground mb-6">
        <Link to="/" className="hover:text-foreground flex items-center gap-1">
          <Home className="w-4 h-4" />
          Accueil
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-foreground font-medium">{cityName}</span>
      </nav>

      {/* En-tête */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">Capteurs - {cityName}</h2>
        <p className="text-muted-foreground">
          {sensors.length} capteur{sensors.length !== 1 ? 's' : ''} déployé{sensors.length !== 1 ? 's' : ''}
        </p>
      </div>

      {/* Grille des capteurs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {sensors.map((sensor) => {
          const status = getSensorStatus(sensor)

          return (
            <Link key={sensor.sensor_id} to={`/sensor/${sensor.sensor_id}`}>
              <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-xl flex items-center gap-2">
                      <Activity className="w-5 h-5 text-primary" />
                      {sensor.sensor_id}
                    </CardTitle>
                    {status.variant === 'danger' && (
                      <AlertCircle className="w-5 h-5 text-red-500" />
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {sensor.description && (
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {sensor.description}
                      </p>
                    )}

                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Statut</span>
                      <Badge variant={status.variant}>{status.label}</Badge>
                    </div>

                    {sensor.last_seen && (
                      <div className="pt-2 border-t">
                        <div className="text-xs text-muted-foreground mb-1">
                          Dernière activité
                        </div>
                        <div className="text-sm font-medium">
                          {formatDate(sensor.last_seen)}
                        </div>
                      </div>
                    )}

                    <div className="text-xs text-muted-foreground">
                      📍 {sensor.latitude.toFixed(4)}, {sensor.longitude.toFixed(4)}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          )
        })}

        {/* Carte "Ajouter capteur" */}
        <Link to="/setup">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer h-full border-dashed border-2 hover:border-primary">
            <CardContent className="flex flex-col items-center justify-center h-full min-h-[200px]">
              <Plus className="w-12 h-12 text-muted-foreground mb-4" />
              <p className="text-lg font-semibold text-muted-foreground">
                Ajouter un capteur
              </p>
            </CardContent>
          </Card>
        </Link>
      </div>

      {sensors.length === 0 && (
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Aucun capteur dans cette ville</h3>
          <p className="text-muted-foreground mb-4">
            Ajoutez un premier capteur pour commencer la surveillance
          </p>
          <Link
            to="/setup"
            className="inline-flex items-center gap-2 px-6 py-3 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Ajouter un capteur
          </Link>
        </div>
      )}
    </div>
  )
}
