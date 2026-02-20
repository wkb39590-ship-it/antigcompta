# ✅ Checklist de Test - Système Admin Frontend

## 📋 Pre-test Configuration

- [ ] Backend running on `http://localhost:8090`
- [ ] Database `compta_db` initialized with seed data
- [ ] Admin users exist: wissal, ahmed, oumayma
- [ ] Frontend on `http://localhost:3090`
- [ ] Node modules installed: `npm install`

**Commandes**:
```bash
# Terminal 1: Backend
cd backend
$env:DATABASE_URL = 'postgresql+psycopg2://admin:admin123@localhost:5444/compta_db'
python -m uvicorn main:app --host 0.0.0.0 --port 8090 --reload

# Terminal 2: Frontend  
cd frontend
npm run dev  # Should start on http://localhost:3090
```

---

## 🔐 Test 1: Authentication Flow

### 1.1 Access /admin/login without token
- [ ] Navigate to `http://localhost:3090/admin/login`
- [ ] Page should display login form
- [ ] Form shows hint text with admin usernames
- [ ] Form has 3 fields: username input, password input, login button

### 1.2 Failed login - wrong credentials
- [ ] Enter username: `wrong_user`
- [ ] Enter password: `wrong_password`
- [ ] Click "Se connecter"
- [ ] Error message should appear: "Erreur de connexion"

### 1.3 Failed login - non-admin user
- [ ] Need: Create or use a non-admin user (eg: comptable, facturiste)
- [ ] Enter non-admin username
- [ ] Enter valid password
- [ ] Click "Se connecter"
- [ ] Error message: "Accès réservé aux administrateurs"

### 1.4 Successful login - admin user
- [ ] Enter username: `wissal`
- [ ] Enter password: `password123`
- [ ] Click "Se connecter"
- [ ] Should navigate to `/admin/dashboard`
- [ ] Page should load AdminLayout (sidebar visible)
- [ ] Admin name "wissal" displayed in sidebar header

---

## 🛡️ Test 2: Route Protection

### 2.1 Try access /admin/dashboard without login
- [ ] Clear localStorage: `localStorage.clear()`
- [ ] Navigate to `http://localhost:3090/admin/dashboard`
- [ ] Should redirect to `/admin/login` automatically
- [ ] Login form should display

### 2.2 Access /admin/* with valid token
- [ ] Login with wissal
- [ ] Navigate directly to `/admin/cabinets`
- [ ] Page should load (no redirect)
- [ ] AdminLayout should render with correct page

### 2.3 Navigate between admin pages
- [ ] From dashboard, click "Cabinets" in sidebar
- [ ] Should navigate to `/admin/cabinets`
- [ ] "Cabinets" link should be highlighted in sidebar
- [ ] Repeat for: Sociétés, Agents, Associations

---

## 📊 Test 3: Admin Dashboard

### 3.1 Dashboard loads stats
- [ ] Page displays 4 stat cards
- [ ] Cards show: Total Agents, Total Sociétés, Total Cabinets, Total Factures
- [ ] Each card has a number value

### 3.2 Stats values are correct
- [ ] Total Sociétés matches actual count from `/societes?token=`
- [ ] Total Factures matches actual count from `/factures?token=`
- [ ] Total Agents = 10 (hardcoded, need backend list endpoint)
- [ ] Total Cabinets = 1 (hardcoded, need backend count endpoint)

### 3.3 Info section displays
- [ ] Section title: "Bienvenue sur le Panneau d'Administration"
- [ ] 4 feature bullets listed
- [ ] All links clickable and navigate correctly

---

## 🏢 Test 4: Admin Cabinets (CRUD)

### 4.1 List cabinets
- [ ] Navigate to `/admin/cabinets`
- [ ] Page loads with empty table or existing cabinets
- [ ] Cabinets sidebar should be highlighted

### 4.2 Create cabinet
- [ ] Fill form:
  - [ ] Nom: "Test Cabinet"
  - [ ] Email: "test@cabinet.ma"
  - [ ] Telephone: "+212 5 35 00 00 00"
  - [ ] Adresse: "123 Rue de Test"
- [ ] Click "Créer" button
- [ ] Form should clear
- [ ] Cabinet should appear in table below

### 4.3 Edit cabinet (TBD)
- [ ] [ ] Implement edit modal/form
- [ ] [ ] Click Edit button on cabinet row
- [ ] [ ] Modal shows prefilled form
- [ ] [ ] Modify name and submit
- [ ] [ ] Cabinet updated in table

### 4.4 Delete cabinet (TBD)
- [ ] [ ] Implement delete with confirmation
- [ ] [ ] Click Delete button on cabinet row
- [ ] [ ] Confirmation modal appears: "Êtes-vous sûr?"
- [ ] [ ] Click confirmdelete
- [ ] [ ] Cabinet removed from table

---

## 🏢 Test 5: Admin Sociétés (CRUD)

### 5.1 List sociétés
- [ ] Navigate to `/admin/societes`
- [ ] Page table shows existing sociétés
- [ ] Columns: Raison Sociale, ICE, IF, RC, Adresse

### 5.2 Create sociét
- [ ] Fill form:
  - [ ] Raison Sociale: "Test SARL"
  - [ ] ICE: "123456789012345" (15 digits)
  - [ ] IF: "123456"
  - [ ] RC: "789012"
  - [ ] Adresse: "Test Address Maroc"
- [ ] Click "Créer" button
- [ ] Société appears in table
- [ ] Verify on backend: `GET /societes?token=` returns new entry

### 5.3 Edit société (TBD)
- [ ] [ ] Similar to cabinet edit
- [ ] [ ] Update raison sociale field
- [ ] [ ] Save changes

### 5.4 Delete société (TBD)
- [ ] [ ] Similar to cabinet delete
- [ ] [ ] Confirmation required

---

## 👥 Test 6: Admin Agents (CRUD)

### 6.1 List agents
- [ ] Navigate to `/admin/agents`
- [ ] Table shows 2 hardcoded agents: wissal, fatima
- [ ] Columns: Prénom, Nom, Username, Email, Rôle, Statut

### 6.2 Create agent
- [ ] Fill form:
  - [ ] Prénom: "Test"
  - [ ] Nom: "Agent"
  - [ ] Username: "test_agent"
  - [ ] Email: "test@cabinet4.ma"
  - [ ] Password: "TestPass123"
  - [ ] is_admin: unchecked (pour utilisateur normal)
- [ ] Click "Créer" button
- [ ] Agent appears in table
- [ ] Role badge should show "Utilisateur" (not Admin)

### 6.3 Create admin agent
- [ ] Similar to 6.2 but check is_admin checkbox
- [ ] Role badge should show "Admin" (blue highlight)
- [ ] Agent should be able to login to /admin/login

### 6.4 Edit agent (TBD)
- [ ] [ ] Click Edit on agent row
- [ ] [ ] Modal shows current data
- [ ] [ ] Toggle is_admin role
- [ ] [ ] Save and verify role changes

### 6.5 Delete agent (TBD)
- [ ] [ ] Click Delete on agent row
- [ ] [ ] Cannot delete current logged-in user
- [ ] [ ] Can delete other agents
- [ ] [ ] After delete, agent cannot login anymore

---

## 🔗 Test 7: Admin Associations

### 7.1 View associations page
- [ ] Navigate to `/admin/associations`
- [ ] Page shows 2 sections: Selection form (left), Associated list (right)

### 7.2 Associate société to cabinet
- [ ] Select cabinet from dropdown: "Cabinet 4" (or first available)
- [ ] Right side shows current sociétés linked (if any)
- [ ] Left side shows available sociétés to link
- [ ] Click "Ajouter" button on a société
- [ ] Société moves to right (Associated list)

### 7.3 Dissociate société from cabinet (TBD)
- [ ] [ ] Associated list shows button to dissociate
- [ ] [ ] Click dissociate button
- [ ] [ ] Société moves back to available list

### 7.4 Multiple associations
- [ ] [ ] Link multiple sociétés to same cabinet
- [ ] [ ] List on right shows all linked sociétés
- [ ] [ ] Cabinet selection also works with other cabinets

---

## 🎯 Test 8: Navigation & Sidebar

### 8.1 Sidebar displays correctly
- [ ] Logo visible: "🔐 Admin Panel"
- [ ] Admin name displayed: "👤 wissal"
- [ ] 5 menu items visible with icons: Dashboard, Cabinets, Sociétés, Agents, Associations
- [ ] Logout button at bottom: "🚪 Déconnexion"

### 8.2 Active link highlighting
- [ ] Current page link has blue highlight + border
- [ ] Hover on other links shows opacity change
- [ ] Hover effect: subtle background change

### 8.3 Logout functionality
- [ ] Click "🚪 Déconnexion" button
- [ ] localStorage cleared (admin_token, admin_user removed)
- [ ] Navigate to `/admin/login`
- [ ] Trying to access `/admin/dashboard` redirects to login

### 8.4 Mobile responsive
- [ ] [ ] Resize window to mobile width (375px)
- [ ] [ ] Sidebar should collapse or stack vertically
- [ ] [ ] Content should be readable
- [ ] [ ] Navigation should remain functional

---

## 🔄 Test 9: API Integration

### 9.1 Admin token sent correctly
- [ ] Open browser DevTools → Network tab
- [ ] Navigate to `/admin/cabinets`
- [ ] Inspect GET request to API
- [ ] Verify:
  - [ ] Token in URL query param `?token=xyz...` OR
  - [ ] Token in Authorization header `Bearer xyz...`

### 9.2 Error handling
- [ ] With network tab open, intentionally disable backend
- [ ] Try to load a page (eg: /admin/cabinets)
- [ ] Error message should display: "Erreur lors du chargement"
- [ ] Page should not crash

### 9.3 Missing endpoints
- [ ] If backend endpoint missing (404):
  - [ ] Check console for error
  - [ ] Error message appears on page
  - [ ] Page remains functional

---

## 🔒 Test 10: Security Validation

### 10.1 Token isolation
- [ ] Login as admin: token stored as `admin_token`
- [ ] Can NOT see regular user session token in localStorage
- [ ] Regular user session: stored as `session_token` (different key)

### 10.2 is_admin flag enforcement
- [ ] Backend returns `is_admin: false` for non-admin user
- [ ] Frontend blocks access: "Accès réservé aux administrateurs"
- [ ] Non-admin trying to access `/admin/*` redirects to login

### 10.3 Token validation on page load
- [ ] Login, then clear admin_token from localStorage manually
- [ ] Refresh page
- [ ] Should redirect to `/admin/login`
- [ ] isAdminLoggedIn() returns false

### 10.4 CORS/Origin validation
- [ ] Backend should reject requests from wrong origin
- [ ] Admin API calls should succeed from `localhost:3090`

---

## 📈 Test 11: Data Persistence

### 11.1 Create and verify data persists
- [ ] Create cabinet in AdminCabinets
- [ ] Refresh page
- [ ] Cabinet should still appear in table
- [ ] Navigate away and back
- [ ] Cabinet still visible

### 11.2 Database consistency
- [ ] Login to backend admin/database directly
- [ ] Verify created cabinets/sociétés exist in DB
- [ ] IDs and fields match frontend display

### 11.3 Multiple sessions
- [ ] Open 2 browser windows
- [ ] Login as wissal in window 1
- [ ] Login as ahmed in window 2
- [ ] Each should show own admin session
- [ ] Logout in window 1 only
- [ ] Window 2 still works (separate logincontext)

---

## 🎨 Test 12: UI/UX

### 12.1 Form validation messages
- [ ] [ ] Required fields show error if empty
- [ ] [ ] Email field validates format
- [ ] [ ] Phone validates format
- [ ] [ ] ICE validates 15-digit format

### 12.2 Loading states
- [ ] [ ] When fetching data, show loader/spinner
- [ ] [ ] Buttons disabled while request in progress
- [ ] [ ] Clear feedback on successful submission

### 12.3 Error display
- [ ] [ ] Network errors show user-friendly message
- [ ] [ ] API errors show detail from backend
- [ ] [ ] Form validation errors highlight problkesmatic fields

### 12.4 Styling consistency
- [ ] All pages use same color scheme
- [ ] Sidebar color matches throughout
- [ ] Button hover/active states consistent
- [ ] Form input styling uniform

---

## 🚀 Test 13: Performance

### 13.1 Page load time
- [ ] `/admin/dashboard` loads in < 2s
- [ ] Tables with 50+ items don't lag
- [ ] Form submission feedback is instant

### 13.2 Network requests
- [ ] Open DevTools Network tab
- [ ] Check number of requests per page
- [ ] No duplicate requests
- [ ] All requests necessary

### 13.3 Memory leaks
- [ ] [ ] Navigate between pages multiple times
- [ ] [ ] Check memory usage (DevTools → Memory)
- [ ] No exponential memory growth

---

## 📝 Test 14: End-to-End Workflow

### Complete admin workflow
- [ ] Login as wissal → `/admin/login`
- [ ] Navigate to Dashboard → `/admin/dashboard`
- [ ] View stats cards
- [ ] Go to Cabinets → create new cabinet "Cabinet Test"
- [ ] Go to Sociétés → create new société "SARL Test" with ICE
- [ ] Go to Agents → create new agent "Ahmed Test" with is_admin=true
- [ ] Go to Associations → link new société to cabinet
- [ ] Try to login as new admin agent
- [ ] Can new admin access /admin/dashboard ?
- [ ] Logout and verify token cleared

---

## 📋 Final Checklist

| Category | Test | Status | Notes |
|----------|------|--------|-------|
| **Auth** | Login success | [ ] | |
| | Login failure | [ ] | |
| | Route protection | [ ] | |
| **CRUD** | Create cabinet | [ ] | |
| | List cabinets | [ ] | |
| | Edit cabinet | [ ] | TBD |
| | Delete cabinet | [ ] | TBD |
| | Create société | [ ] | |
| | Create agent | [ ] | |
| | Create association | [ ] | |
| **UI** | Sidebar nav | [ ] | |
| | Active links | [ ] | |
| | Responsive | [ ] | |
| **API** | Token sent | [ ] | |
| | Error handling | [ ] | |
| **Security** | is_admin check | [ ] | |
| | Token isolation | [ ] | |
| **Data** | Persistence | [ ] | |

---

## 🐛 Bug Report Template

If you find a bug during testing:

```markdown
### Bug: [Title]

**Severity**: 🔴 Critical / 🟡 Medium / 🟢 Low

**Steps to Reproduce**:
1. 
2. 
3. 

**Expected Result**:


**Actual Result**:


**Screenshot**:


**Browser/OS**: 


**Timestamp**: 

```

---

**Test Date**: _________
**Tester Name**: _________
**Backend Version**: _________
**Frontend Version**: _________
