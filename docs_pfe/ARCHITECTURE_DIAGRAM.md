# 🏗️ Diagramme d'Architecture - Système Admin Frontend

## Flow d'accès aux routes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        UTILISATEUR ACCÈDE À URL                      │
└─┬───────────────────────────────────────────────────────────────────┘
  │
  ▼
┌──────────────────────────────────────────────────────────────────────┐
│              App.tsx DÉTECTE TYPE DE ROUTE                           │
│              location.pathname.startsWith('/admin')                  │
└─┬─────────────────────────────────────────┬──────────────────────┬──┘
  │ URL = /admin/*                          │ URL = /login ou    │ URL = autres
  │                                         │ /select-cabinet     │
  ▼                                         ▼                     ▼
┌──────────────────────┐        ┌───────────────────┐   ┌─────────────────┐
│   ADMIN ROUTES       │        │  AUTH ROUTES      │   │ USER ROUTES     │
│   DETECTED           │        │  DETECTED         │   │ DETECTED        │
└──────┬───────────────┘        └─────────┬─────────┘   └────────┬────────┘
       │                                  │                      │
       ├─ /admin/login                   └─ Rend        ├─ Rend Sidebar
       │  (NonProtected)                   Login et     │ + Main Routes
       │  Rend AdminLogin()                CabinetSelector
       │
       └─ /admin/* (autres)
          AdminProtectedRoute
               ├─ isAdminLoggedIn() ?
               │  ├─ OUI ✅  → Rend AdminLayout(children)
               │  │            + Page spécifique
               │  └─ NON ❌  → Navigate to /admin/login
               │
               └─ Pages:
                  ├─ AdminDashboard
                  ├─ AdminCabinets
                  ├─ AdminSocietes
                  ├─ AdminAgents
                  └─ AdminAssociations
```

## Hiérarchie des composants

```
App.tsx (routeur principal)
├── isAdminPage ? 
│   ├─ OUI → AdminLayout
│   │        ├─ Sidebar
│   │        │  ├─ Logo
│   │        │  ├─ Nav Menu (5 items avec highlight)
│   │        │  └─ Logout Button
│   │        └─ AdminContent (children)
│   │           ├─ AdminDashboard
│   │           ├─ AdminCabinets
│   │           ├─ AdminSocietes
│   │           ├─ AdminAgents
│   │           └─ AdminAssociations
│   └─ AdminProtectedRoute (gate)
│      └─ Si !isAdminLoggedIn() → Navigate /admin/login
│
├── isAuthPage ?
│   ├─ OUI → Login / CabinetSelector
│   └─ NON → Sidebar + ProtectedRoute
│            ├─ Dashboard
│            ├─ Upload
│            ├─ FactureDetail
│            └─ PcmPage
```

## Flux d'authentification admin

```
┌─────────────────────────────────────┐
│  User @ http://localhost:3090/admin │
└──────────────────┬──────────────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ AdminProtectedRoute ? │
        │ isAdminLoggedIn()==true
        └──────┬──┬────────────┘
          NO   │  │ YES
              │  └────────────────────┐
              │                       ▼
         ┌────┴────────┐    ┌──────────────────────┐
         │ /admin/login │    │ AdminLayout + Page   │
         │             │    │ (Cabinets, etc)      │
         └──────┬───────┘    └──────────────────────┘
                │
         Form Input Username/Password
                │
                ▼
    ┌───────────────────────────────┐
    │ POST /auth/login              │
    │ ├─ username                   │
    │ └─ password                   │
    └──────────┬────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ Backend /auth/login         │
    │ ├─ Validate credentials     │
    │ ├─ Check agent.is_admin=true│
    │ └─ Return access_token      │
    └──────────┬────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ AdminLogin.tsx              │
    │ ├─ Récupère token + agent   │
    │ ├─ Valide is_admin          │
    │ ├─ setAdminSession()        │
    │ │  ├─ localStorage['admin_token']
    │ │  └─ localStorage['admin_user']
    │ └─ navigate(/admin/dashboard)
    └──────────┬────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ AdminProtectedRoute         │
    │ ├─ isAdminLoggedIn()==true ✅
    │ └─ Rend AdminLayout         │
    └──────────┬────────────────────┘
               │
               ▼
    ┌─────────────────────────────┐
    │ AdminLayout                 │
    │ ├─ Sidebar Left (280px)      │
    │ └─ Main Content Right        │
    └─────────────────────────────┘
```

## Gestion du localStorage (Session Admin)

```
┌──────────────────────────── localStorage ─────────────────────────────┐
│                                                                        │
│ Key: admin_token                                                      │
│ Value: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."                    │
│                                                                        │
│ Key: admin_user                                                       │
│ Value: {                                                              │
│   "agent_id": 1,                                                      │
│   "username": "wissal",                                               │
│   "email": "wissal@cabinet4.ma",                                      │
│   "is_admin": true,                                                   │
│   "cabinet_id": 4                                                     │
│ }                                                                      │
│                                                                        │
│ Key: session_token (utilisateur normal - DIFFÉRENT)                   │
│ Key: session_user (utilisateur normal - DIFFÉRENT)                    │
└─────────────────────────────────────────────────────────────────────┘

                              ↓ setAdminSession()
                 ┌────────────┴────────────┐
         ├──────────────┘                  └──────────────┤
         │                                                 │
    Lors login                                      Lors logout
    admin valide                            clearAdminSession()
                                            ├─ Efface admin_token
                                            ├─ Efface admin_user
                                            └─ Navigate /admin/login
```

## Structure des fichiers

```
frontend/
├── src/
│   ├── App.tsx ⭐ (Routeur principal + AdminProtectedRoute)
│   │
│   ├── pages/
│   │   ├── admin/ ⭐ (Pages admin - 7 fichiers)
│   │   │   ├── AdminLayout.tsx (Sidebar + nav réutilisable)
│   │   │   ├── AdminLogin.tsx (Form login + is_admin validation)
│   │   │   ├── AdminDashboard.tsx (Stats cards)
│   │   │   ├── AdminCabinets.tsx (CRUD cabinets)
│   │   │   ├── AdminSocietes.tsx (CRUD sociétés)
│   │   │   ├── AdminAgents.tsx (CRUD agents)
│   │   │   └── AdminAssociations.tsx (Lier sociétés ↔ cabinets)
│   │   │
│   │   ├── Dashboard.tsx (Utilisateur normal)
│   │   ├── Upload.tsx (Utilisateur normal)
│   │   ├── FactureDetail.tsx (Utilisateur normal)
│   │   ├── PcmPage.tsx (Utilisateur normal)
│   │   ├── Login.tsx (Utilisateur normal)
│   │   └── CabinetSelector.tsx (Utilisateur normal)
│   │
│   ├── utils/ ⭐
│   │   ├── adminTokenDecoder.ts (Gestion session admin)
│   │   │   ├─ getAdminToken()
│   │   │   ├─ getAdminUser()
│   │   │   ├─ setAdminSession()
│   │   │   ├─ clearAdminSession()
│   │   │   └─ isAdminLoggedIn()
│   │   │
│   │   ├── tokenDecoder.ts (Gestion session utilisateur)
│   │   └── ...
│   │
│   └── config/ ⭐
│       └── apiConfig.ts (Config endpoints centralisée)
│           ├─ API_CONFIG.AUTH
│           ├─ API_CONFIG.ADMIN
│           ├─ API_CONFIG.SOCIETES
│           ├─ API_CONFIG.FACTURES
│           ├─ API_CONFIG.PCM
│           ├─ buildApiUrl()
│           └─ getAuthHeaders()
│
├── ADMIN_ARCHITECTURE.md ⭐ (Vue technique)
├── ADMIN_USAGE_GUIDE.md ⭐ (Guide pour développeurs)
├── COMPLETION_SUMMARY.md ⭐ (Résumé/status)
└── ...
```

## Appels API depuis les pages admin

```
              ┌─────────────────────────────────────┐
              │ Page Admin (ex: AdminCabinets.tsx)  │
              └──────────────┬──────────────────────┘
                      useEffect()
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
            GET Token            POST/GET/DELETE
         getAdminToken()      API_CONFIG + axios
                │                      │
                ├─ Token from       ├─ Headers:
                │   localStorage      │  Authorization: Bearer token
                │                     │
                └──────────────┬──────┘
                               │
                    ┌──────────▼──────────┐
                    │ Backend API Endpoint│
                    │ /admin/cabinets     │
                    │ /societes           │
                    │ /auth/register      │
                    └─────────┬────────────┘
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
              Response 200/OK      Error (400/401/500)
              setStats()           setError() + logging
```

## Sécurité en couches

```
Couche 1: Frontend Route Guard
├─ AdminProtectedRoute
├─ Checks: isAdminLoggedIn()
│  ├─ Token in localStorage
│  ├─ User in localStorage
│  └─ user.is_admin == true
└─ Si fail → /admin/login

Couche 2: Login Gate
├─ AdminLogin.tsx
├─ Checks: agent.is_admin from backend
└─ Si false → Error "Accès réservé"

Couche 3: Backend Auth
├─ @require_admin decorator on endpoints
├─ JWT validation
├─ Token expiration check
└─ is_admin field check in DB

Couche 4: Backend Authorization
├─ Per-endpoint permission checks
├─ Cabinet/Societe ownership validation
└─ Audit logging
```

---

**Notes**:
- JWT Token format standard (HS256)
- localStorage NOT SAFE pour production (use httpOnly cookies)
- Tokens must have expiration (implement refresh token flow)
- All endpoints require HTTPS in production
