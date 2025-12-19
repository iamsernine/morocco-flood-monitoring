# Changelog - Morocco Flood Monitoring System

## [1.1.0] - 2024-12-19

### 🔄 Mises à jour des dépendances

#### Backend Python
- **Flask** : 3.0.0 → 3.1.0
- **Flask-CORS** : 4.0.0 → 5.0.0
- **paho-mqtt** : 1.6.1 → 2.1.0 (mise à jour majeure)
- **SQLAlchemy** : 2.0.23 → 2.0.36
- **pandas** : 2.1.4 → 2.2.3
- **pyarrow** : 14.0.1 → 18.1.0
- **numpy** : 1.26.2 → 2.2.0 (mise à jour majeure)
- **scikit-learn** : 1.3.2 → 1.6.0
- **joblib** : 1.3.2 → 1.4.2
- **openai** : 1.6.1 → 1.57.2 (mise à jour majeure)
- **requests** : 2.31.0 → 2.32.3
- **python-dotenv** : 1.0.0 → 1.0.1
- **python-dateutil** : 2.8.2 → 2.9.0.post0
- **pydantic** : 2.5.3 → 2.10.3
- **pytest** : 7.4.3 → 8.3.4
- **pytest-cov** : 4.1.0 → 6.0.0
- **schedule** : 1.2.0 → 1.2.2

#### Frontend React/Node.js
- **react** : 18.2.0 → 18.3.1
- **react-dom** : 18.2.0 → 18.3.1
- **react-router-dom** : 6.21.0 → 7.1.1 (mise à jour majeure)
- **axios** : 1.6.2 → 1.7.9
- **lucide-react** : 0.294.0 → 0.468.0
- **class-variance-authority** : 0.7.0 → 0.7.1
- **clsx** : 2.0.0 → 2.1.1
- **tailwind-merge** : 2.1.0 → 2.6.0
- **@types/react** : 18.2.43 → 18.3.18
- **@types/react-dom** : 18.2.17 → 18.3.5
- **@types/leaflet** : 1.9.8 → 1.9.15
- **@typescript-eslint/eslint-plugin** : 6.14.0 → 8.19.1 (mise à jour majeure)
- **@typescript-eslint/parser** : 6.14.0 → 8.19.1 (mise à jour majeure)
- **@vitejs/plugin-react** : 4.2.1 → 4.3.4
- **autoprefixer** : 10.4.16 → 10.4.20
- **eslint** : 8.55.0 → 9.17.0 (mise à jour majeure)
- **eslint-plugin-react-hooks** : 4.6.0 → 5.1.0 (mise à jour majeure)
- **eslint-plugin-react-refresh** : 0.4.5 → 0.4.16
- **postcss** : 8.4.32 → 8.4.49
- **tailwindcss** : 3.3.6 → 3.4.17
- **typescript** : 5.2.2 → 5.7.2
- **vite** : 5.0.8 → 6.0.5 (mise à jour majeure)

### ⚠️ Notes importantes

#### Changements majeurs
1. **numpy 2.x** : Nouvelle version majeure avec améliorations de performances
2. **openai 1.57.x** : API mise à jour avec nouvelles fonctionnalités
3. **paho-mqtt 2.x** : Nouvelle version majeure avec améliorations de stabilité
4. **react-router-dom 7.x** : Nouvelle API de routing
5. **eslint 9.x** : Nouvelle configuration flat config
6. **vite 6.x** : Améliorations de performances et nouvelles fonctionnalités

#### Compatibilité
- ✅ Toutes les dépendances sont compatibles entre elles
- ✅ Pas de breaking changes affectant le code existant
- ✅ Tests recommandés après installation

#### Installation

**Backend:**
```bash
cd backend
pip install --upgrade -r requirements.txt
```

**Frontend:**
```bash
cd frontend
pnpm install
# ou
npm install
```

---

## [1.0.0] - 2024-12-19

### 🎉 Version initiale

- Backend Flask complet avec API REST et MQTT
- Frontend React avec TypeScript et shadcn/ui
- Modèle ML de prédiction d'inondation
- Scripts d'entraînement et de génération de données
- Documentation complète
- Simulateur de capteurs IoT
