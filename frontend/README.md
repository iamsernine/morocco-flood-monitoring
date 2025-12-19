# Frontend - Morocco Flood Monitoring System

Interface React pour le système de surveillance des inondations au Maroc.

## 🛠️ Technologies

- **React 18** avec TypeScript
- **Vite** pour le bundling rapide
- **Tailwind CSS** pour le styling
- **shadcn/ui** pour les composants UI
- **React Router** pour la navigation
- **Leaflet** pour la cartographie
- **Axios** pour les requêtes API

## 📦 Installation

```bash
cd frontend
pnpm install
```

## 🚀 Démarrage

```bash
# Mode développement
pnpm dev

# Build production
pnpm build

# Preview production
pnpm preview
```

L'application sera accessible sur `http://localhost:3000`

## 📁 Structure

```
src/
├── components/       # Composants réutilisables
│   ├── ui/          # Composants UI (shadcn/ui)
│   └── Layout.tsx   # Layout principal
├── pages/           # Pages de l'application
│   ├── HomePage.tsx
│   ├── CityPage.tsx
│   ├── SensorPage.tsx
│   ├── MapPage.tsx
│   └── SetupWizard.tsx
├── services/        # Services API
│   └── api.ts
├── lib/            # Utilitaires
│   └── utils.ts
├── App.tsx         # Composant racine
└── main.tsx        # Point d'entrée
```

## 🎨 Design

Design minimal et professionnel basé sur shadcn/ui :
- Palette de couleurs adaptée (bleu pour l'eau, rouge pour les alertes)
- Composants accessibles et responsives
- Pas d'animations flashy

## 🔗 API Backend

Le frontend communique avec le backend Flask sur `http://localhost:5000`.

Configuration du proxy dans `vite.config.ts` :
```typescript
proxy: {
  '/api': {
    target: 'http://localhost:5000',
    changeOrigin: true,
  },
}
```

## 📄 Pages

### Home Page
Grille des villes avec statistiques et niveau de risque.

### City Page
Grille des capteurs d'une ville avec statuts.

### Sensor Page
Détails d'un capteur avec prédictions IA et actions (pompe, notifications).

### Map Page
Carte interactive du Maroc avec marqueurs de capteurs colorés selon le risque.

### Setup Wizard
Assistant de configuration initiale (forcé au premier lancement).

## 🔧 Configuration

Les variables d'environnement peuvent être définies dans `.env` :

```env
VITE_API_URL=http://localhost:5000
```

## 📝 Notes

- Pas d'authentification (démo locale uniquement)
- Rafraîchissement automatique des données toutes les 30 secondes
- Support complet de TypeScript
