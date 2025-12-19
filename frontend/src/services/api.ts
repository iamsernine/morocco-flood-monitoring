/**
 * ============================================================================
 * API.TS - Service de communication avec le backend
 * ============================================================================
 * Description: Client API pour toutes les requêtes vers le backend Flask.
 * 
 * Endpoints:
 * - Configuration: get/set config, setup status
 * - Cities: CRUD villes
 * - Sensors: CRUD capteurs
 * - Predictions: Historique et résumé
 * - MQTT: Contrôle du client MQTT
 * - Reports: Génération de rapports
 * 
 * Debugging:
 * - Vérifier que le backend est démarré sur localhost:5000
 * - Vérifier les logs de console pour les erreurs
 * - Utiliser les DevTools Network pour voir les requêtes
 * ============================================================================
 */

import axios, { AxiosInstance } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

class ApiService {
  private client: AxiosInstance

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Intercepteur pour logger les erreurs
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        console.error('API Error:', error.response?.data || error.message)
        return Promise.reject(error)
      }
    )
  }

  // ========================================================================
  // CONFIGURATION
  // ========================================================================

  async getConfig() {
    const response = await this.client.get('/api/config')
    return response.data
  }

  async updateConfig(config: Record<string, string>) {
    const response = await this.client.post('/api/config', config)
    return response.data
  }

  async getSetupStatus() {
    const response = await this.client.get('/api/config/setup-status')
    return response.data
  }

  async completeSetup() {
    const response = await this.client.post('/api/config/complete-setup')
    return response.data
  }

  // ========================================================================
  // CITIES
  // ========================================================================

  async getCities() {
    const response = await this.client.get('/api/cities')
    return response.data
  }

  async addCity(city: {
    name: string
    latitude: number
    longitude: number
    description?: string
  }) {
    const response = await this.client.post('/api/cities', city)
    return response.data
  }

  // ========================================================================
  // SENSORS
  // ========================================================================

  async getSensors(city?: string) {
    const params = city ? { city } : {}
    const response = await this.client.get('/api/sensors', { params })
    return response.data
  }

  async addSensor(sensor: {
    sensor_id: string
    city: string
    lat: number
    lon: number
    description?: string
  }) {
    const response = await this.client.post('/api/sensors', sensor)
    return response.data
  }

  async deleteSensor(sensorId: string) {
    const response = await this.client.delete(`/api/sensors/${sensorId}`)
    return response.data
  }

  // ========================================================================
  // PREDICTIONS
  // ========================================================================

  async getPredictions(sensorId: string, limit: number = 100) {
    const response = await this.client.get(`/api/predictions/${sensorId}`, {
      params: { limit },
    })
    return response.data
  }

  async getPredictionsSummary() {
    const response = await this.client.get('/api/predictions/summary')
    return response.data
  }

  // ========================================================================
  // PUMP CONTROL
  // ========================================================================

  async controlPump(city: string, sensorId: string, command: 'ON' | 'OFF') {
    const response = await this.client.post('/api/pump/control', {
      city,
      sensor_id: sensorId,
      command,
    })
    return response.data
  }

  // ========================================================================
  // REPORTS
  // ========================================================================

  async generateReport(params: {
    cities: string[]
    sensors: string[]
    metrics: string[]
    time_range: string
    language?: string
  }) {
    const response = await this.client.post('/api/reports/generate', params)
    return response.data
  }

  // ========================================================================
  // MQTT
  // ========================================================================

  async startMqtt() {
    const response = await this.client.post('/api/mqtt/start')
    return response.data
  }

  async stopMqtt() {
    const response = await this.client.post('/api/mqtt/stop')
    return response.data
  }

  async getMqttStatus() {
    const response = await this.client.get('/api/mqtt/status')
    return response.data
  }

  // ========================================================================
  // HEALTH
  // ========================================================================

  async healthCheck() {
    const response = await this.client.get('/api/health')
    return response.data
  }
}

// Export singleton instance
export const api = new ApiService()
export default api
