/**
 * ============================================================================
 * LAYOUT.TSX - Layout principal avec navigation
 * ============================================================================
 * Description: Layout de l'application avec header, navigation et footer.
 * ============================================================================
 */

import { Outlet, Link, useLocation } from 'react-router-dom'
import { Home, Map, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

export default function Layout() {
  const location = useLocation()

  const isActive = (path: string) => {
    return location.pathname === path
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-primary">
                🌊 Morocco Flood Monitoring
              </h1>
              <p className="text-sm text-muted-foreground">
                Système intelligent de surveillance des inondations - Coupe du Monde 2030
              </p>
            </div>

            <nav className="flex gap-4">
              <Link
                to="/"
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-md transition-colors",
                  isActive('/')
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent"
                )}
              >
                <Home className="w-4 h-4" />
                Accueil
              </Link>

              <Link
                to="/map"
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-md transition-colors",
                  isActive('/map')
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent"
                )}
              >
                <Map className="w-4 h-4" />
                Carte
              </Link>

              <Link
                to="/setup"
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-md transition-colors",
                  isActive('/setup')
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-accent"
                )}
              >
                <Settings className="w-4 h-4" />
                Configuration
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 bg-background">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="border-t bg-card py-4">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>© 2024 Morocco Flood Monitoring System - Coupe du Monde 2030</p>
          <p className="mt-1">Système de démonstration locale - Pas d'authentification</p>
        </div>
      </footer>
    </div>
  )
}
