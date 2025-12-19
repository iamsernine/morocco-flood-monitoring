/**
 * ============================================================================
 * SETUPWIZARD.TSX - Assistant de configuration initiale
 * ============================================================================
 * Description: Guide l'utilisateur à travers la configuration initiale du système.
 * 
 * Étapes:
 * 1. Configuration API (MQTT, OpenWeather, OpenAI, SMTP)
 * 2. Premier capteur obligatoire (formulaire ou JSON)
 * 
 * Forcé au premier lancement si setup non complété.
 * ============================================================================
 */

import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { CheckCircle2 } from 'lucide-react'
import api from '@/services/api'

interface SetupWizardProps {
  onComplete: () => void
}

export default function SetupWizard({ onComplete }: SetupWizardProps) {
  const navigate = useNavigate()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)

  // Étape 1: Configuration API
  const [config, setConfig] = useState({
    mqtt_broker_host: 'localhost',
    mqtt_broker_port: '1883',
    mqtt_broker_username: '',
    mqtt_broker_password: '',
    openweather_api_key: '',
    openai_api_key: '',
    smtp_host: 'smtp.gmail.com',
    smtp_port: '587',
    smtp_sender: '',
    smtp_password: '',
  })

  // Étape 2: Premier capteur
  const [sensor, setSensor] = useState({
    sensor_id: '',
    city: '',
    lat: '',
    lon: '',
    description: '',
  })

  const handleConfigChange = (key: string, value: string) => {
    setConfig({ ...config, [key]: value })
  }

  const handleSensorChange = (key: string, value: string) => {
    setSensor({ ...sensor, [key]: value })
  }

  const handleStep1Submit = async () => {
    setLoading(true)
    try {
      await api.updateConfig(config)
      setStep(2)
    } catch (error) {
      console.error('Failed to save config:', error)
      alert('Erreur lors de la sauvegarde de la configuration')
    } finally {
      setLoading(false)
    }
  }

  const handleStep2Submit = async () => {
    if (!sensor.sensor_id || !sensor.city || !sensor.lat || !sensor.lon) {
      alert('Veuillez remplir tous les champs obligatoires')
      return
    }

    setLoading(true)
    try {
      await api.addSensor({
        sensor_id: sensor.sensor_id,
        city: sensor.city,
        lat: parseFloat(sensor.lat),
        lon: parseFloat(sensor.lon),
        description: sensor.description || undefined,
      })

      await api.completeSetup()
      onComplete()
      navigate('/')
    } catch (error) {
      console.error('Failed to add sensor:', error)
      alert('Erreur lors de l\'ajout du capteur')
    } finally {
      setLoading(false)
    }
  }

  const handleSkipToSensor = () => {
    setStep(2)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full">
        {/* En-tête */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-primary mb-2">
            🌊 Morocco Flood Monitoring
          </h1>
          <p className="text-muted-foreground">
            Assistant de configuration initiale
          </p>
        </div>

        {/* Indicateur d'étapes */}
        <div className="flex items-center justify-center mb-8">
          <div className="flex items-center gap-4">
            <div className={`flex items-center gap-2 ${step >= 1 ? 'text-primary' : 'text-muted-foreground'}`}>
              {step > 1 ? (
                <CheckCircle2 className="w-6 h-6" />
              ) : (
                <div className="w-6 h-6 rounded-full border-2 border-current flex items-center justify-center">
                  1
                </div>
              )}
              <span className="font-medium">Configuration API</span>
            </div>

            <div className="w-12 h-0.5 bg-border"></div>

            <div className={`flex items-center gap-2 ${step >= 2 ? 'text-primary' : 'text-muted-foreground'}`}>
              <div className="w-6 h-6 rounded-full border-2 border-current flex items-center justify-center">
                2
              </div>
              <span className="font-medium">Premier capteur</span>
            </div>
          </div>
        </div>

        {/* Étape 1: Configuration API */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>Étape 1: Configuration API</CardTitle>
              <CardDescription>
                Configurez les clés API et paramètres MQTT. Vous pourrez les modifier plus tard.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* MQTT */}
              <div>
                <h3 className="font-semibold mb-3">Broker MQTT</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Hôte
                    </label>
                    <Input
                      value={config.mqtt_broker_host}
                      onChange={(e) => handleConfigChange('mqtt_broker_host', e.target.value)}
                      placeholder="localhost"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Port
                    </label>
                    <Input
                      value={config.mqtt_broker_port}
                      onChange={(e) => handleConfigChange('mqtt_broker_port', e.target.value)}
                      placeholder="1883"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Nom d'utilisateur (optionnel)
                    </label>
                    <Input
                      value={config.mqtt_broker_username}
                      onChange={(e) => handleConfigChange('mqtt_broker_username', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Mot de passe (optionnel)
                    </label>
                    <Input
                      type="password"
                      value={config.mqtt_broker_password}
                      onChange={(e) => handleConfigChange('mqtt_broker_password', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              {/* OpenWeather API */}
              <div>
                <h3 className="font-semibold mb-3">OpenWeather API</h3>
                <label className="text-sm text-muted-foreground mb-1 block">
                  Clé API
                </label>
                <Input
                  value={config.openweather_api_key}
                  onChange={(e) => handleConfigChange('openweather_api_key', e.target.value)}
                  placeholder="Votre clé API OpenWeatherMap"
                />
              </div>

              {/* OpenAI API */}
              <div>
                <h3 className="font-semibold mb-3">OpenAI API</h3>
                <label className="text-sm text-muted-foreground mb-1 block">
                  Clé API
                </label>
                <Input
                  value={config.openai_api_key}
                  onChange={(e) => handleConfigChange('openai_api_key', e.target.value)}
                  placeholder="Votre clé API OpenAI"
                />
              </div>

              {/* SMTP */}
              <div>
                <h3 className="font-semibold mb-3">SMTP (Email)</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Serveur SMTP
                    </label>
                    <Input
                      value={config.smtp_host}
                      onChange={(e) => handleConfigChange('smtp_host', e.target.value)}
                      placeholder="smtp.gmail.com"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Port
                    </label>
                    <Input
                      value={config.smtp_port}
                      onChange={(e) => handleConfigChange('smtp_port', e.target.value)}
                      placeholder="587"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Email expéditeur
                    </label>
                    <Input
                      type="email"
                      value={config.smtp_sender}
                      onChange={(e) => handleConfigChange('smtp_sender', e.target.value)}
                      placeholder="votre@email.com"
                    />
                  </div>
                  <div>
                    <label className="text-sm text-muted-foreground mb-1 block">
                      Mot de passe
                    </label>
                    <Input
                      type="password"
                      value={config.smtp_password}
                      onChange={(e) => handleConfigChange('smtp_password', e.target.value)}
                    />
                  </div>
                </div>
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  onClick={handleStep1Submit}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? 'Sauvegarde...' : 'Suivant'}
                </Button>
                <Button
                  variant="outline"
                  onClick={handleSkipToSensor}
                >
                  Passer
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Étape 2: Premier capteur */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>Étape 2: Premier capteur</CardTitle>
              <CardDescription>
                Ajoutez au moins un capteur pour commencer la surveillance
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm text-muted-foreground mb-1 block">
                  Identifiant du capteur *
                </label>
                <Input
                  value={sensor.sensor_id}
                  onChange={(e) => handleSensorChange('sensor_id', e.target.value)}
                  placeholder="CAS_1"
                />
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-1 block">
                  Ville *
                </label>
                <Input
                  value={sensor.city}
                  onChange={(e) => handleSensorChange('city', e.target.value)}
                  placeholder="Casablanca"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-muted-foreground mb-1 block">
                    Latitude *
                  </label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={sensor.lat}
                    onChange={(e) => handleSensorChange('lat', e.target.value)}
                    placeholder="33.5731"
                  />
                </div>
                <div>
                  <label className="text-sm text-muted-foreground mb-1 block">
                    Longitude *
                  </label>
                  <Input
                    type="number"
                    step="0.000001"
                    value={sensor.lon}
                    onChange={(e) => handleSensorChange('lon', e.target.value)}
                    placeholder="-7.5898"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm text-muted-foreground mb-1 block">
                  Description (optionnel)
                </label>
                <Input
                  value={sensor.description}
                  onChange={(e) => handleSensorChange('description', e.target.value)}
                  placeholder="Capteur centre-ville"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setStep(1)}
                >
                  Retour
                </Button>
                <Button
                  onClick={handleStep2Submit}
                  disabled={loading}
                  className="flex-1"
                >
                  {loading ? 'Création...' : 'Terminer la configuration'}
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}
