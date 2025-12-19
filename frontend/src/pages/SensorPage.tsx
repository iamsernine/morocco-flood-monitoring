/**
 * ============================================================================
 * SENSORPAGE.TSX - Page capteur avec détails et prédictions
 * ============================================================================
 * Description: Affiche les détails d'un capteur, ses métriques en temps réel,
 * et les prédictions IA. Boutons d'action: Informer, Activer pompe, Modifier, Supprimer.
 * Fil d'Ariane: Accueil > Ville > Capteur
 * ============================================================================
 */

import { useEffect, useState } from 'react'
import { Link, useParams, useNavigate } from 'react-router-dom'
import { ChevronRight, Home, Bell, Power, Edit, Trash2, AlertTriangle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import api from '@/services/api'
import { formatDate, getRiskBadgeColor } from '@/lib/utils'

interface Sensor {
  sensor_id: string
  city_name: string
  latitude: number
  longitude: number
  description: string | null
  active: boolean
  last_seen: string | null
}

interface Prediction {
  timestamp: string
  probability: number
  risk_level: string
  model_version: string
}

export default function SensorPage() {
  const { sensorId } = useParams<{ sensorId: string }>()
  const navigate = useNavigate()
  const [sensor, setSensor] = useState<Sensor | null>(null)
  const [predictions, setPredictions] = useState<Prediction[]>([])
  const [loading, setLoading] = useState(true)
  const [pumpLoading, setPumpLoading] = useState(false)

  useEffect(() => {
    if (sensorId) {
      loadData()
      const interval = setInterval(loadData, 30000)
      return () => clearInterval(interval)
    }
  }, [sensorId])

  const loadData = async () => {
    try {
      const [sensorsResponse, predictionsResponse] = await Promise.all([
        api.getSensors(),
        api.getPredictions(sensorId!, 10),
      ])

      if (sensorsResponse.success) {
        const foundSensor = sensorsResponse.data.find((s: Sensor) => s.sensor_id === sensorId)
        setSensor(foundSensor || null)
      }

      if (predictionsResponse.success) {
        setPredictions(predictionsResponse.data)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handlePumpControl = async (command: 'ON' | 'OFF') => {
    if (!sensor) return

    setPumpLoading(true)
    try {
      await api.controlPump(sensor.city_name, sensor.sensor_id, command)
      alert(`Pompe ${command === 'ON' ? 'activée' : 'désactivée'} avec succès`)
    } catch (error) {
      console.error('Failed to control pump:', error)
      alert('Erreur lors du contrôle de la pompe')
    } finally {
      setPumpLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!sensor) return

    if (!confirm(`Êtes-vous sûr de vouloir supprimer le capteur ${sensor.sensor_id} ?`)) {
      return
    }

    try {
      await api.deleteSensor(sensor.sensor_id)
      alert('Capteur supprimé avec succès')
      navigate(`/city/${sensor.city_name}`)
    } catch (error) {
      console.error('Failed to delete sensor:', error)
      alert('Erreur lors de la suppression du capteur')
    }
  }

  const latestPrediction = predictions[0]

  const getRiskVariant = (riskLevel: string): "success" | "warning" | "danger" => {
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
          <p className="text-muted-foreground">Chargement du capteur...</p>
        </div>
      </div>
    )
  }

  if (!sensor) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center py-12">
          <AlertTriangle className="w-16 h-16 text-muted-foreground mx-auto mb-4" />
          <h3 className="text-xl font-semibold mb-2">Capteur non trouvé</h3>
          <p className="text-muted-foreground mb-4">
            Le capteur {sensorId} n'existe pas ou a été supprimé
          </p>
          <Link to="/" className="text-primary hover:underline">
            Retour à l'accueil
          </Link>
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
        <Link to={`/city/${sensor.city_name}`} className="hover:text-foreground">
          {sensor.city_name}
        </Link>
        <ChevronRight className="w-4 h-4" />
        <span className="text-foreground font-medium">{sensor.sensor_id}</span>
      </nav>

      {/* En-tête avec actions */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h2 className="text-3xl font-bold mb-2">{sensor.sensor_id}</h2>
          <p className="text-muted-foreground">{sensor.city_name}</p>
          {sensor.description && (
            <p className="text-sm text-muted-foreground mt-2">{sensor.description}</p>
          )}
        </div>

        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Bell className="w-4 h-4 mr-2" />
            Informer
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePumpControl('ON')}
            disabled={pumpLoading}
          >
            <Power className="w-4 h-4 mr-2" />
            Pompe ON
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handlePumpControl('OFF')}
            disabled={pumpLoading}
          >
            <Power className="w-4 h-4 mr-2" />
            Pompe OFF
          </Button>
          <Button variant="outline" size="sm">
            <Edit className="w-4 h-4 mr-2" />
            Modifier
          </Button>
          <Button variant="destructive" size="sm" onClick={handleDelete}>
            <Trash2 className="w-4 h-4 mr-2" />
            Supprimer
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Prédiction IA */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Prédiction IA</CardTitle>
              <CardDescription>Analyse en temps réel du risque d'inondation</CardDescription>
            </CardHeader>
            <CardContent>
              {latestPrediction ? (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="text-sm text-muted-foreground mb-1">
                        Probabilité d'inondation
                      </div>
                      <div className="text-4xl font-bold text-primary">
                        {latestPrediction.probability.toFixed(1)}%
                      </div>
                    </div>
                    <Badge variant={getRiskVariant(latestPrediction.risk_level)} className="text-lg px-4 py-2">
                      {latestPrediction.risk_level}
                    </Badge>
                  </div>

                  <div className="pt-4 border-t">
                    <div className="text-sm text-muted-foreground mb-2">
                      Dernière mise à jour
                    </div>
                    <div className="text-sm font-medium">
                      {formatDate(latestPrediction.timestamp)}
                    </div>
                  </div>

                  <div className="pt-4 border-t">
                    <div className="text-sm text-muted-foreground mb-2">
                      Explication IA
                    </div>
                    <div className="text-sm bg-muted p-4 rounded-md">
                      {latestPrediction.risk_level === 'High' && (
                        <p>Risque élevé d'inondation détecté. Surveillance accrue recommandée et activation des mesures préventives.</p>
                      )}
                      {latestPrediction.risk_level === 'Medium' && (
                        <p>Risque modéré d'inondation. Maintenir la surveillance et préparer les équipes d'intervention.</p>
                      )}
                      {latestPrediction.risk_level === 'Low' && (
                        <p>Risque faible d'inondation. Situation normale, surveillance de routine.</p>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Aucune prédiction disponible
                </div>
              )}
            </CardContent>
          </Card>

          {/* Historique des prédictions */}
          <Card className="mt-6">
            <CardHeader>
              <CardTitle>Historique des prédictions</CardTitle>
              <CardDescription>10 dernières prédictions</CardDescription>
            </CardHeader>
            <CardContent>
              {predictions.length > 0 ? (
                <div className="space-y-2">
                  {predictions.map((pred, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 rounded-md bg-muted/50"
                    >
                      <div className="flex-1">
                        <div className="text-sm font-medium">
                          {formatDate(pred.timestamp)}
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <div className="text-sm font-semibold">
                            {pred.probability.toFixed(1)}%
                          </div>
                        </div>
                        <Badge variant={getRiskVariant(pred.risk_level)}>
                          {pred.risk_level}
                        </Badge>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  Aucun historique disponible
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Informations du capteur */}
        <div>
          <Card>
            <CardHeader>
              <CardTitle>Informations</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="text-sm text-muted-foreground mb-1">Identifiant</div>
                <div className="font-medium">{sensor.sensor_id}</div>
              </div>

              <div>
                <div className="text-sm text-muted-foreground mb-1">Ville</div>
                <div className="font-medium">{sensor.city_name}</div>
              </div>

              <div>
                <div className="text-sm text-muted-foreground mb-1">Position</div>
                <div className="font-mono text-sm">
                  {sensor.latitude.toFixed(6)}, {sensor.longitude.toFixed(6)}
                </div>
              </div>

              <div>
                <div className="text-sm text-muted-foreground mb-1">Statut</div>
                <Badge variant={sensor.active ? 'success' : 'danger'}>
                  {sensor.active ? 'Actif' : 'Inactif'}
                </Badge>
              </div>

              {sensor.last_seen && (
                <div>
                  <div className="text-sm text-muted-foreground mb-1">Dernière activité</div>
                  <div className="text-sm">{formatDate(sensor.last_seen)}</div>
                </div>
              )}

              <div className="pt-4 border-t">
                <div className="text-sm text-muted-foreground mb-2">Canaux surveillés</div>
                <div className="space-y-1">
                  <Badge variant="outline" className="mr-2">water_level</Badge>
                  <Badge variant="outline">humidity</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
