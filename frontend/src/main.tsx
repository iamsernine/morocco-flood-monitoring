/**
 * ============================================================================
 * MAIN.TSX - Point d'entrée de l'application React
 * ============================================================================
 * Description: Initialise et monte l'application React dans le DOM.
 * ============================================================================
 */

import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
