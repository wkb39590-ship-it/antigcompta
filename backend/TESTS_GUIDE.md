# 🧪 GUIDE COMPLET - Tests de l'Authentification Multi-Cabinet

## 📋 Table des Matières
1. [Tests Automatisés Python](#tests-automatisés-python)
2. [Tests Manuels avec cURL](#tests-manuels-avec-curl)
3. [Tests dans Postman](#tests-dans-postman)
4. [Checklist de Validation](#checklist-de-validation)

---

## 🐍 Tests Automatisés Python

### Exécution Complète

```bash
# Depuis le conteneur backend
docker exec pfe_backend_v2 python test_auth_complete.py

# Ou depuis le host (exposer l'API)
python backend/test_auth_complete.py
```

### Ce que ce script teste:

✅ **Section 1: Authentification** (5 tests)
- Login admin réussi
- Login user restreint  
- Login autre cabinet
- Login mot de passe invalide
- Login utilisateur inexistant

✅ **Section 2: Contrôle d'Accès (RBAC)** (3 tests)
- Admin voit toutes les sociétés
- User voit seulement ses sociétés
- Cabinet 2 isolation

✅ **Section 3: Sélection de Société** (4 tests)
- Selection admin
- Selection user
- Tentée forbidden
- Selection inexistante

✅ **Section 4: Sécurité** (2 tests)
- Token invalide
- Token manquant

✅ **Section 5: Isolation Inter-Cabinet** (2 tests)
- Cross-cabinet prevention
- Cabinet 1 ↔ Cabinet 2 isolation

### Résultat Attendu

```
✅ Réussis: 16
❌ Échoués: 0
📈 Total: 16

🎉 TOUS LES TESTS PASSÉS!
```

---

## 🔧 Tests Manuels avec cURL

### 1️⃣ TEST: Login & Récupérer Token

```bash
# Login: wissal (Admin Cabinet 1)
curl -X POST http://localhost:8090/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"wissal","password":"password123"}' | jq '.'

# Réponse attendue:
{
  "access_token": "eyJhZ2VudF9pZCI6IDQsICJjYWJpbmV0X2lkIjo...",
  "token_type": "bearer",
  "agent": {
    "id": 4,
    "username": "wissal",
    "is_admin": true,
    "cabinet_id": 4
  },
  "cabinets": [...]
}
```

### 2️⃣ TEST: Lister Sociétés Accessibles

```bash
# Admin (wissal) doit voir 2 sociétés
TOKEN="eyJhZ2VudF9pZCI6IDQsIC..."

curl -X GET "http://localhost:8090/auth/societes?token=$TOKEN" | jq '.'

# Réponse attendue: 2 sociétés
[
  {
    "id": 2,
    "raison_sociale": "Ets. EL OUJDI & FILS",
    "ice": "001234567890001"
  },
  {
    "id": 3,
    "raison_sociale": "COMPTOIRE ARRAHMA SARL",
    "ice": "002234567890002"
  }
]
```

### 3️⃣ TEST: User Accès Restreint

```bash
# Login: fatima (User Cabinet 1 - accès limité)
curl -X POST http://localhost:8090/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"fatima","password":"password123"}' | jq '.access_token' > /tmp/fatima_token.txt

FATIMA_TOKEN=$(cat /tmp/fatima_token.txt | tr -d '"')

# Fatima doit voir SEULEMENT 1 société
curl -X GET "http://localhost:8090/auth/societes?token=$FATIMA_TOKEN" | jq 'length'

# Réponse attendue: 1
```

### 4️⃣ TEST: Select Sociète (Create Session Context)

```bash
curl -X POST "http://localhost:8090/auth/select-societe?token=$TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cabinet_id": 4,
    "societe_id": 2
  }' | jq '.context'

# Réponse attendue:
{
  "agent_id": 4,
  "cabinet_id": 4,
  "societe_id": 2,
  "username": "wissal",
  "societe_raison_sociale": "Ets. EL OUJDI & FILS"
}
```

### 5️⃣ TEST: Security - Cross-Cabinet Prevention

```bash
# Ahmed (Cabinet 2) essaie d'accéder à Cabinet 1
AHMED_TOKEN="eyJ..."
curl -X POST "http://localhost:8090/auth/select-societe?token=$AHMED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cabinet_id": 5,  # Cabinet 2 correctement
    "societe_id": 4   # Societe 4 (une du Cabinet 2)
  }' | jq '.context'

# Maintenant, essayer une societe du Cabinet 1 (devrait échouer):
curl -X POST "http://localhost:8090/auth/select-societe?token=$AHMED_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cabinet_id": 4,  # Cabinet 1 <- NOT ALLOWED
    "societe_id": 2
  }' 

# Réponse attendue: 403 ou 404 Forbidden
```

---

## 📮 Tests dans Postman

### 1. Créer une Collection

1. Ouvrir Postman → New Collection → "Auth Multi-Cabinet"

### 2. Ajouter les Requêtes

#### Requête 1: Login Wissal
```
POST http://localhost:8090/auth/login

Body (JSON):
{
  "username": "wissal",
  "password": "password123"
}

Tests:
pm.test("Status 200", () => pm.response.code === 200);
pm.test("Token exists", () => pm.response.json().access_token);
pm.globals.set("wissal_token", pm.response.json().access_token);
```

#### Requête 2: List Societes
```
GET http://localhost:8090/auth/societes?token={{wissal_token}}

Tests:
pm.test("Status 200", () => pm.response.code === 200);
pm.test("2 societes", () => pm.response.json().length === 2);
```

#### Requête 3: Select Societe
```
POST http://localhost:8090/auth/select-societe?token={{wissal_token}}

Body (JSON):
{
  "cabinet_id": 4,
  "societe_id": 2
}

Tests:
pm.test("Has session context", () => pm.response.json().context);
pm.test("Societe 2 selected", () => pm.response.json().context.societe_id === 2);
```

---

## ✅ Checklist de Validation

### Phase 1: Authentification
- [ ] ✅ Login wissal avec credentials OK
- [ ] ✅ Token JWT retourné valide
- [ ] ✅ Password hash sécurisé (PBKDF2)
- [ ] ✅ Login invalide → 401 Unauthorized
- [ ] ✅ Login user → is_admin = false

### Phase 2: RBAC (Role-Based Access Control)
- [ ] ✅ Admin voit 2 sociétés du cabinet
- [ ] ✅ User (fatima) voit 1 seule société
- [ ] ✅ Ahmed (Cabinet 2) voit sa société uniquement
- [ ] ✅ Pas d'accès cross-cabinet

### Phase 3: Sélection Société
- [ ] ✅ Selection crée context de session
- [ ] ✅ Session token généré
- [ ] ✅ Context contient: agent_id, cabinet_id, societe_id
- [ ] ✅ Societe NON assignée → 403 Forbidden
- [ ] ✅ Societe inexistante → 404 Not Found

### Phase 4: Sécurité
- [ ] ✅ Token invalide → 401
- [ ] ✅ Token manquant → 422
- [ ] ✅ Cross-cabinet access denied
- [ ] ✅ Tokens ne leakent pas en logs

### Phase 5: Isolation de Données
- [ ] ✅ Cabinet 1 ↔ Cabinet 2 complètement isolés
- [ ] ✅ wissal ne voit pas sociétés d'Ahmed
- [ ] ✅ Transfert token wissal ≠ accès à Cabinet 2
- [ ] ✅ Bases de données isolées par cabinet_id

---

## 🚨 Erreurs à Chercher

### Erreur 1: Token Rejeté
```
Symptôme: 401 Token invalide sur requête /auth/societes
Cause: Token format incorrect ou session non valide
Solution: Vérifier JWT encoding/decoding dans auth.py
```

### Erreur 2: RBAC Bypass
```
Symptôme: User (fatima) voit 2 sociétés au lieu de 1
Cause: Filtre agent_societes non appliqué
Solution: Vérifier query dans /auth/societes (ligne ~ 240 admin.py)
```

### Erreur 3: Cross-Cabinet Access
```
Symptôme: ahmed peut sélectionner societe 2 (Cabinet 1)
Cause: Validation cabinet_id non stricte
Solution: Vérifier validation 3-4 dans /auth/select-societe
```

### Erreur 4: Token Expiration
```
Symptôme: 401 Token expiré après quelques minutes
Cause: Expiration JWT trop courte
Solution: Augmenter timedelta(hours=8) dans create_jwt_token
```

---

## 📊 Résumé des Données de Test

| Agent | Cabinet | Role | Sociétés Accès |
|-------|---------|------|---------|
| wissal | 4 | ADMIN | 2, 3 |
| fatima | 4 | USER | 2 |
| ahmed | 5 | ADMIN | 4 |

| Cabinet | Sociétés |
|---------|----------|
| 4 | Ets. EL OUJDI & FILS (2), COMPTOIRE ARRAHMA SARL (3) |
| 5 | Entreprise Import-Export (4) |

---

## 🎯 Prochaines Étapes (Après Validation ✅)

1. **Frontend Selector** : PageLogin + Sélecteur Societe
2. **Compteurs** : Routes pour GET/POST compteurs
3. **TVA Calcul** : Logique automatique de calcul
4. **Route Integration** : Ajouter session_token à /factures/*
5. **Tests E2E** : Full workflow Upload → Extract → Validate

---

**💡 Priorité**: Valider que TOUS les ✅ passent avant de continuer !
