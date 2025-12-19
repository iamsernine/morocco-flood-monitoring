/**
 * ============================================================================
 * MAPPAGE.TSX - Page cartographique avec Leaflet
 * ============================================================================
 * Description: Carte interactive du Maroc avec marqueurs de capteurs.
 * Couleur des marqueurs selon le niveau de risque (vert = sûr, rouge = risque).
 * Clic sur marqueur → modal avec actions (informer/pompe).
 * ============================================================================
 */

import { useEffect, useState, useMemo } from 'react'
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet'
import { Icon } from 'leaflet'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Bell, Power } from 'lucide-react'
import api from '@/services/api'
import 'leaflet/dist/leaflet.css'

interface Sensor {
  sensor_id: string
  city_name: string
  latitude: number
  longitude: number
  description: string | null
  active: boolean
  last_seen: string | null
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

// Icônes de marqueurs personnalisées (créées une seule fois)
const createIcon = (color: string) => new Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
})

// Créer les icônes une seule fois (pas à chaque render)
const ICONS = {
  green: createIcon('green'),
  orange: createIcon('orange'),
  red: createIcon('red'),
  grey: createIcon('grey')
}

export default function MapPage() {
  const [sensors, setSensors] = useState<Sensor[]>([])
  const [riskSummary, setRiskSummary] = useState<RiskSummary>({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
    const interval = setInterval(loadData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadData = async () => {
    try {
      const [sensorsResponse, riskResponse] = await Promise.all([
        api.getSensors(),
        api.getPredictionsSummary(),
      ])

      if (sensorsResponse.success) {
        setSensors(sensorsResponse.data)
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

  const getSensorRiskLevel = (sensor: Sensor): string => {
    const cityRisk = riskSummary[sensor.city_name]
    if (!cityRisk) return 'Low'

    if (cityRisk.high_risk > 0) return 'High'
    if (cityRisk.medium_risk > 0) return 'Medium'
    return 'Low'
  }

  const getSensorIcon = (sensor: Sensor) => {
    if (!sensor.active) return ICONS.grey

    const riskLevel = getSensorRiskLevel(sensor)
    switch (riskLevel) {
      case 'High':
        return ICONS.red
      case 'Medium':
        return ICONS.orange
      default:
        return ICONS.green
    }
  }

  // Mémoriser les marqueurs pour éviter le re-render inutile
  const markers = useMemo(() => {
    return sensors.map((sensor) => {
      const riskLevel = getSensorRiskLevel(sensor)
      return {
        sensor,
        riskLevel,
        icon: getSensorIcon(sensor)
      }
    })
  }, [sensors, riskSummary])

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

  const handlePumpControl = async (sensor: Sensor, command: 'ON' | 'OFF') => {
    try {
      await api.controlPump(sensor.city_name, sensor.sensor_id, command)
      alert(`Pompe ${command === 'ON' ? 'activée' : 'désactivée'} avec succès`)
    } catch (error) {
      console.error('Failed to control pump:', error)
      alert('Erreur lors du contrôle de la pompe')
    }
  }

  // Centre du Maroc (approximatif)
  const moroccoCenter: [number, number] = [31.7917, -7.0926]

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement de la carte...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-[calc(100vh-180px)]">
      <div className="container mx-auto px-4 py-4 h-full">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Carte des capteurs</h2>
            <p className="text-sm text-muted-foreground">
              {sensors.length} capteur{sensors.length !== 1 ? 's' : ''} déployé{sensors.length !== 1 ? 's' : ''}
            </p>
          </div>

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span>Risque faible</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
              <span>Risque modéré</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span>Risque élevé</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-gray-500 rounded-full"></div>
              <span>Inactif</span>
            </div>
          </div>
        </div>

        <div className="h-[calc(100%-80px)] rounded-lg overflow-hidden border shadow-lg">
          <MapContainer
            center={moroccoCenter}
            zoom={6}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {markers.map(({ sensor, riskLevel, icon }) => (
                <Marker
                  key={sensor.sensor_id}
                  position={[sensor.latitude, sensor.longitude]}
                  icon={icon}
                >
                  <Popup>
                    <div className="min-w-[250px]">
                      <h3 className="font-bold text-lg mb-2">{sensor.sensor_id}</h3>
                      <p className="text-sm text-gray-600 mb-3">{sensor.city_name}</p>

                      {sensor.description && (
                        <p className="text-sm mb-3">{sensor.description}</p>
                      )}

                      <div className="mb-3">
                        <Badge variant={getRiskVariant(riskLevel)}>
                          Risque: {riskLevel}
                        </Badge>
                      </div>

                      <div className="flex flex-col gap-2">
                        <Link to={`/sensor/${sensor.sensor_id}`}>
                          <Button size="sm" className="w-full">
                            Voir les détails
                          </Button>
                        </Link>

                        <Button
                          size="sm"
                          variant="outline"
                          className="w-full"
                          onClick={() => alert('Fonction de notification à implémenter')}
                        >
                          <Bell className="w-4 h-4 mr-2" />
                          Informer
                        </Button>

                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                            onClick={() => handlePumpControl(sensor, 'ON')}
                          >
                            <Power className="w-4 h-4 mr-1" />
                            ON
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            className="flex-1"
                            onClick={() => handlePumpControl(sensor, 'OFF')}
                          >
                            <Power className="w-4 h-4 mr-1" />
                            OFF
                          </Button>
                        </div>
                      </div>
                    </div>
                  </Popup>
                </Marker>
            ))}
          </MapContainer>
        </div>
      </div>
    </div>
  )
}
