# Guide d'Utilisation des Routes Admin

## Démarrage rapide

### 1. Structure des fichiers
```
frontend/src/
├── pages/
│   ├── admin/
│   │   ├── AdminLayout.tsx          # Layout réutilisable avec sidebar
│   │   ├── AdminLogin.tsx           # Page de connexion admin
│   │   ├── AdminDashboard.tsx       # Dashboard avec stats
│   │   ├── AdminCabinets.tsx        # CRUD cabinets
│   │   ├── AdminSocietes.tsx        # CRUD sociétés
│   │   ├── AdminAgents.tsx          # CRUD agents
│   │   └── AdminAssociations.tsx    # Liens sociétés ↔ cabinets
│   └── ...autres pages
├── utils/
│   ├── adminTokenDecoder.ts         # Gestion session admin
│   ├── tokenDecoder.ts              # Gestion session utilisateur
│   └── ...
├── config/
│   └── apiConfig.ts                 # Configuration API centralisée
└── App.tsx                          # Routeur principal avec admin routes
```

### 2. Accès aux pages admin

**URL**: `http://localhost:3090/admin/login`

**Identifiants de test**:
- Username: `wissal`, `ahmed`, `oumayma`
- Password: `password123`

### 3. Flux d'authentification

```
User → /admin/login → POST /auth/login → validate is_admin=true 
  → setAdminSession(token, user) → /admin/dashboard
```

## Utilisation dans le code

### Importer les utilitaires admin
```typescript
import { 
  getAdminToken, 
  getAdminUser, 
  setAdminSession, 
  clearAdminSession,
  isAdminLoggedIn 
} from '@/utils/adminTokenDecoder'
```

### Récupérer le token admin
```typescript
const token = getAdminToken()
// token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Récupérer l'utilisateur admin connecté
```typescript
const user = getAdminUser()
// user: {
//   agent_id: 1,
//   username: "wissal",
//   email: "wissal@example.com",
//   is_admin: true,
//   cabinet_id: 4
// }
```

### Vérifier si admin est connecté
```typescript
if (isAdminLoggedIn()) {
  // Afficher contenu admin
}
```

### Effectuer une requête API authentifiée
```typescript
import axios from 'axios'
import { getAdminToken } from '@/utils/adminTokenDecoder'

const token = getAdminToken()

// Méthode 1: Bearer token dans le header (recommandé)
const response = await axios.get('/admin/cabinets', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})

// Méthode 2: Token en query param (compatibilité)
const response = await axios.get(`/societes?token=${token}`)
```

### Utiliser la configuration API
```typescript
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/config/apiConfig'
import { getAdminToken } from '@/utils/adminTokenDecoder'

const token = getAdminToken()

// Utiliser les endpoints définis
const url = API_CONFIG.ADMIN.CABINETS.LIST
const headers = getAuthHeaders(token)

const response = await axios.get(url, { headers })

// Ou avec query params
const url = buildApiUrl(API_CONFIG.SOCIETES.LIST, token, true)
```

## Créer une nouvelle page admin

### Étape 1: Créer le composant
```typescript
// frontend/src/pages/admin/AdminMonEntite.tsx

import React from 'react'
import { getAdminToken } from '@/utils/adminTokenDecoder'
import axios from 'axios'

export const AdminMonEntite: React.FC = () => {
  const token = getAdminToken()
  const API_URL = 'http://localhost:8090'

  const handleFetch = async () => {
    const response = await axios.get(
      `${API_URL}/admin/mon-entite?token=${token}`
    )
    console.log(response.data)
  }

  return (
    <div>
      <h1>Ma Nouvelle Entité</h1>
      <button onClick={handleFetch}>Charger données</button>
    </div>
  )
}
```

### Étape 2: Ajouter la route dans App.tsx
```typescript
import AdminMonEntite from './pages/admin/AdminMonEntite'

// Dans la section des routes admin:
<Route
  path="/admin/mon-entite"
  element={
    <AdminProtectedRoute>
      <AdminLayout currentPage="mon-entite">
        <AdminMonEntite />
      </AdminLayout>
    </AdminProtectedRoute>
  }
/>
```

### Étape 3: Ajouter le lien dans AdminLayout.tsx
```typescript
const navItems = [
  { label: 'Dashboard', path: '/admin/dashboard', id: 'dashboard' },
  { label: 'Cabinets', path: '/admin/cabinets', id: 'cabinets' },
  // ... autres items
  { label: 'Mon Entité', path: '/admin/mon-entite', id: 'mon-entite' }, // ← Ajouter
]
```

## Bonnes pratiques

### ✅ À faire
- Utiliser `getAdminToken()` au lieu de `localStorage.getItem('admin_token')`
- Vérifier `isAdminLoggedIn()` avant d'accéder à des ressources admin
- Utiliser la configuration centralisée (`apiConfig.ts`)
- Envelopper les pages dans `AdminProtectedRoute`
- Passer `currentPage` à `AdminLayout` pour la navigation active

### ❌ À éviter
- Stocker directement dans `localStorage` sans utilitaires
- Mélanger les tokens admin et utilisateur
- Appeler des endpoints admin depuis des pages utilisateur
- Faire confiance au frontend pour la sécurité (valider côté backend)

## Gestion des erreurs

### Erreur: "Accès réservé aux administrateurs"
- L'utilisateur n'a pas le flag `is_admin: true`
- Solution: Créer un nouvel utilisateur avec `is_admin: true` via l'API

### Erreur: Token expiré ou invalide
- Le token a expiré ou n'existe pas
- Solution: Redirection auto vers `/admin/login` via `AdminProtectedRoute`

### Erreur: 401 Unauthorized
- En-têtes d'authentification mal configurés
- Solution: Vérifier format Bearer token ou query param

## Architecture de sécurité

### Frontend (layered security)
1. `AdminProtectedRoute` vérifie `isAdminLoggedIn()`
2. Si absent → redirection `/admin/login`
3. `AdminLogin` valide `agent.is_admin`
4. Sinon → affiche erreur "Accès réservé"

### Backend (stateless validation)
1. Endpoints `/admin/*` protégés par décorateur `@require_admin`
2. Tous les endpoints vérifient la validité du token JWT
3. Pas de confiance aux headers du client

## Dépannage

### Le login ne fonctionne pas
```bash
# Vérifier backend en cours d'exécution
curl http://localhost:8090/docs

# Vérifier les credentials
# Utilisateurs admin: wissal, ahmed, oumayma
# Password: password123
```

### Page admin blanche
```typescript
// Vérifier la console pour erreurs
console.log(getAdminToken())  // Doit afficher le token
console.log(isAdminLoggedIn()) // Doit être true
```

### Token non sauvegardé
```typescript
// Vérifier AdminLogin utilise setAdminSession
setAdminSession(access_token, agent)

// Vérifier localStorage
localStorage.getItem('admin_token')
localStorage.getItem('admin_user')
```

## Ressources

- [ADMIN_ARCHITECTURE.md](./ADMIN_ARCHITECTURE.md) - Vue d'ensemble technique
- [apiConfig.ts](./src/config/apiConfig.ts) - Configuration API
- [adminTokenDecoder.ts](./src/utils/adminTokenDecoder.ts) - Utilitaires session
- [App.tsx](./src/App.tsx) - Définition des routes
