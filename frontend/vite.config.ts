/**
 * ============================================================================
 * VITE.CONFIG.TS - Configuration Vite
 * ============================================================================
 * Description: Configuration du bundler Vite pour le frontend React.
 * 
 * Fonctionnalités:
 * - Support React avec Fast Refresh
 * - Alias de chemins pour imports simplifiés
 * - Proxy vers l'API backend
 * - Optimisation de build
 * 
 * Debugging:
 * - Vérifier que le serveur dev démarre sur le port 3000
 * - Vérifier que le proxy API fonctionne vers localhost:5000
 * ============================================================================
 */

import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
})
