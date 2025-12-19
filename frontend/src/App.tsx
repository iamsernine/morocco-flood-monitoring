/**
 * ============================================================================
 * APP.TSX - Composant principal de l'application
 * ============================================================================
 * Description: Point d'entrée de l'application React avec routing et
 * vérification du setup.
 * 
 * Routes:
 * - / : Page d'accueil (grille des villes)
 * - /city/:cityName : Page ville (grille des capteurs)
 * - /sensor/:sensorId : Page capteur (détails et prédictions)
 * - /map : Vue cartographique
 * - /setup : Assistant de configuration (forcé si non complété)
 * 
 * Debugging:
 * - Vérifier que le backend est accessible
 * - Vérifier les logs de console pour les erreurs de routing
 * - Tester la navigation entre les pages
 * ============================================================================
 */

import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import api from './services/api'

// Pages (à créer)
import HomePage from './pages/HomePage'
import CityPage from './pages/CityPage'
import SensorPage from './pages/SensorPage'
import MapPage from './pages/MapPage'
import SetupWizard from './pages/SetupWizard'
import Layout from './components/Layout'

function App() {
  const [setupComplete, setSetupComplete] = useState<boolean | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkSetupStatus()
  }, [])

  const checkSetupStatus = async () => {
    try {
      const response = await api.getSetupStatus()
      setSetupComplete(response.data.setup_completed)
    } catch (error) {
      console.error('Failed to check setup status:', error)
      setSetupComplete(false)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Chargement...</p>
        </div>
      </div>
    )
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Redirection vers setup si non complété */}
        {!setupComplete && (
          <Route path="*" element={<Navigate to="/setup" replace />} />
        )}

        {/* Setup Wizard */}
        <Route path="/setup" element={<SetupWizard onComplete={() => setSetupComplete(true)} />} />

        {/* Routes principales (protégées par setup) */}
        {setupComplete && (
          <Route element={<Layout />}>
            <Route path="/" element={<HomePage />} />
            <Route path="/city/:cityName" element={<CityPage />} />
            <Route path="/sensor/:sensorId" element={<SensorPage />} />
            <Route path="/map" element={<MapPage />} />
          </Route>
        )}
      </Routes>
    </BrowserRouter>
  )
}

export default App
