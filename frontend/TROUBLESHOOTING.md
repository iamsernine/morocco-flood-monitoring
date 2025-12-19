# 🔧 Guide de dépannage - Frontend

## Erreur: Failed to resolve import "@/lib/utils"

Cette erreur se produit lorsque l'alias `@/` n'est pas correctement configuré ou que le cache de Vite est corrompu.

### ✅ Solution rapide (recommandée)

```bash
cd ~/Desktop/morocco-flood-monitoring/frontend

# 1. Récupérer les dernières modifications
git pull origin main

# 2. Supprimer node_modules et le cache
rm -rf node_modules .vite

# 3. Réinstaller les dépendances
pnpm install

# 4. Redémarrer le serveur
pnpm dev
```

### 🔍 Vérifications

#### 1. Vérifier que le fichier utils.ts existe

```bash
ls -la src/lib/utils.ts
```

Devrait afficher :
```
-rw-r--r-- 1 user user 2157 Dec 19 08:08 src/lib/utils.ts
```

#### 2. Vérifier vite.config.ts

Le fichier doit contenir :

```typescript
import { fileURLToPath } from 'url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export default defineConfig({
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  // ...
})
```

#### 3. Vérifier tsconfig.json

Le fichier doit contenir :

```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```

### 🧹 Nettoyage complet

Si le problème persiste :

```bash
# Arrêter le serveur (Ctrl+C)

# Supprimer tous les caches
rm -rf node_modules
rm -rf .vite
rm -rf dist
rm -rf pnpm-lock.yaml

# Réinstaller
pnpm install

# Redémarrer
pnpm dev
```

### 🐛 Mode debug

Pour voir plus d'informations :

```bash
# Démarrer en mode debug
DEBUG=vite:* pnpm dev
```

### 📝 Vérifier les versions

```bash
# Vérifier la version de Vite
pnpm list vite

# Devrait afficher: vite@6.0.5
```

### 🔄 Alternative : Utiliser des imports relatifs

Si l'alias ne fonctionne toujours pas, vous pouvez temporairement utiliser des imports relatifs :

```typescript
// Au lieu de:
import { formatDate } from "@/lib/utils"

// Utiliser:
import { formatDate } from "../lib/utils"
```

### 💡 Problèmes connus

#### Vite 6 + pnpm

Vite 6 a changé la façon dont les alias sont résolus. Assurez-vous d'utiliser `fileURLToPath` dans `vite.config.ts`.

#### Cache corrompu

Le cache de Vite (`.vite/`) peut parfois se corrompre. Le supprimer résout généralement le problème.

#### node_modules

Si vous avez installé les dépendances avec npm puis pnpm (ou vice versa), supprimez `node_modules` et réinstallez.

### 🆘 Toujours bloqué ?

1. Vérifier que vous êtes sur la dernière version du code :
   ```bash
   git pull origin main
   git status
   ```

2. Vérifier qu'il n'y a pas de modifications locales qui interfèrent :
   ```bash
   git diff vite.config.ts
   git diff tsconfig.json
   ```

3. Créer une issue sur GitHub avec :
   - La sortie de `pnpm list vite`
   - La sortie de `cat vite.config.ts`
   - Le message d'erreur complet

---

## Autres erreurs courantes

### Port 3000 déjà utilisé

```bash
# Changer le port dans vite.config.ts
server: {
  port: 3001,
}
```

### Erreur de connexion à l'API

Vérifier que le backend est démarré :

```bash
cd ../backend
python app/main.py
```

### Erreur TypeScript

```bash
# Vérifier les erreurs TypeScript
pnpm run build
```
