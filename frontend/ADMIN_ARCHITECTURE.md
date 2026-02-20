# Architecture Admin Frontend

## Vue d'ensemble

Le système d'administration est basé sur une séparation claire entre :
- **Routes utilisateur normal** : `/`, `/dashboard`, `/upload`, `/pcm`, `/factures/:id`
- **Routes admin** : `/admin/*`

## Structure du routage

### App.tsx
Le routeur principal détecte le type de page et rend le layout approprié :

```
Route Detection
├── Admin Pages (/admin/*) → AdminLayout + AdminProtectedRoute
│   ├── /admin/login → AdminLogin (non protégé)
│   ├── /admin/dashboard → AdminDashboard (protégé)
│   ├── /admin/cabinets → AdminCabinets (protégé)
│   ├── /admin/societes → AdminSocietes (protégé)
│   ├── /admin/agents → AdminAgents (protégé)
│   └── /admin/associations → AdminAssociations (protégé)
├── Auth Pages (/login, /select-cabinet) → Login, CabinetSelector (non protégé)
└── User Pages (autres) → Sidebar + ProtectedRoute
```

## Système d'authentification admin

### Utilitaires (adminTokenDecoder.ts)

**Fonctions disponibles :**
```typescript
getAdminSession() → AdminSession | null
getAdminToken() → string | null
getAdminUser() → AdminUser | null
setAdminSession(token, user) → void
clearAdminSession() → void
isAdminLoggedIn() → boolean
```

### Flux de connexion admin
1. Utilisateur accède à `/admin/dashboard`
2. Admin protection détecte absence de token → redirect `/admin/login`
3. Utilisateur se connecte via `POST /auth/login`
4. Backend valide identifiants et retourne `access_token` + `agent` avec `is_admin: true`
5. AdminLogin stocke via `setAdminSession(token, agent)`
6. Token et user sauvegardés dans localStorage
7. Utilisateur redirigé vers `/admin/dashboard`

### Protection des routes admin

**AdminProtectedRoute** :
```typescript
function AdminProtectedRoute({ children }) {
  if (!isAdminLoggedIn()) {
    return <Navigate to="/admin/login" replace />
  }
  return <>{children}</>
}
```

Chaque page admin imbriquée dans AdminProtectedRoute + AdminLayout :
```tsx
<Route
  path="/admin/cabinets"
  element={
    <AdminProtectedRoute>
      <AdminLayout currentPage="cabinets">
        <AdminCabinets />
      </AdminLayout>
    </AdminProtectedRoute>
  }
/>
```

## Pages Admin

### AdminLogin.tsx
- Formulaire de connexion sécurisé
- Valide `agent.is_admin` avant d'autoriser
- Utilise `setAdminSession()` pour stocker les credentials

### AdminLayout.tsx
- Sidebar navigation réutilisable
- Menu avec lien actif en surbrillance (prop `currentPage`)
- Affiche nom de l'utilisateur admin
- Bouton déconnexion qui appelle `clearAdminSession()`

### AdminDashboard.tsx
- Stats globales (agents, sociétés, cabinets, factures)
- Appels API avec bearer token

### AdminCabinets.tsx
- CRUD cabinets de comptabilité
- Endpoints : `GET/POST /admin/cabinets`

### AdminSocietes.tsx
- CRUD sociétés clientes
- Endpoints : `GET/POST /societes` (avec `token` query param)

### AdminAgents.tsx
- CRUD agents/utilisateurs
- Endpoints : `POST /auth/register` (avec `token` + `cabinet_id` query params)

### AdminAssociations.tsx
- Associer sociétés à cabinets
- Endpoints : `GET /admin/cabinets`, `GET /societes`, `POST /admin/cabinets/{id}/societes`

## Flux d'API appels admin

Toutes les pages admin utilisent le token depuis `getAdminToken()` :

```typescript
const token = getAdminToken()

// Approche 1 : Query params (compatibilité)
const response = await axios.get(`/societes?token=${token}`)

// Approche 2 : Bearer token header (recommandé)
const response = await axios.get('/admin/cabinets', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
```

## Sécurité

### Côté Frontend
- ✅ Vérification `isAdminLoggedIn()` pour accès routes `/admin`
- ✅ Redirection auto `/admin/login` si token absent
- ✅ Effacement localStorage + tokens `clearAdminSession()` à la déconnexion
- ✅ Validation `agent.is_admin` au login

### Côté Backend
- ✅ Endpoints `/admin/*` protégés par `require_admin` helper
- ✅ Routes `/societes` create (admin-only) vérifiées
- ✅ Token valide requis dans headers ou query params

## Prochaines étapes

1. **Delete/Edit modals** : Implémenter modales de confirmation avant suppression
2. **Error handling** : Ajouter gestion erreurs API + toast notifications
3. **Loading states** : Skeleton loaders pendant chargement données
4. **Pagination** : Limiter tables si trop de données
5. **Search/Filter** : Ajouter recherche dans les tableaux
6. **Validations** : Valider formulaires avant soumission
7. **Backend sync** : Confirmer tous les endpoints existent et retournent bon format
