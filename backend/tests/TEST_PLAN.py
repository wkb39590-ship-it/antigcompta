"""
PLAN DE TESTS - Architecture Multi-Cabinet (Authentification & Accès)
═══════════════════════════════════════════════════════════════════════

AVANT DE COMMENCER LES PROCHAINES ÉTAPES, VALIDEZ CES SCÉNARIOS:
"""

# ═══════════════════════════════════════════════════════════════════════
# 1. TESTS D'AUTHENTIFICATION (Login & Tokens)
# ═══════════════════════════════════════════════════════════════════════

TEST_CASES_AUTH = {
    "1.1_Login_Admin_Cabinet1": {
        "description": "Login avec agent ADMIN du Cabinet 1",
        "method": "POST /auth/login",
        "payload": {
            "username": "wissal",
            "password": "password123"
        },
        "expected_status": 200,
        "expected_fields": ["access_token", "agent", "cabinets"],
        "assertions": [
            "agent.is_admin == True",
            "agent.cabinet_id == 4",
            "cabinets[0].nom contains 'Cabinet'",
            "access_token is not none"
        ]
    },
    
    "1.2_Login_User_Cabinet1": {
        "description": "Login avec agent USER du Cabinet 1 (accès restreint)",
        "method": "POST /auth/login",
        "payload": {
            "username": "fatima",
            "password": "password123"
        },
        "expected_status": 200,
        "expected_fields": ["access_token", "agent"],
        "assertions": [
            "agent.is_admin == False",
            "agent.cabinet_id == 4",
            "agent.username == 'fatima'"
        ]
    },
    
    "1.3_Login_Invalid_Password": {
        "description": "Login avec mauvais mot de passe",
        "method": "POST /auth/login",
        "payload": {
            "username": "wissal",
            "password": "wrong_password"
        },
        "expected_status": 401,
        "expected_error": "Identifiants invalides"
    },
    
    "1.4_Login_Nonexistent_User": {
        "description": "Login avec utilisateur inexistant",
        "method": "POST /auth/login",
        "payload": {
            "username": "nonexistent",
            "password": "password123"
        },
        "expected_status": 401,
        "expected_error": "Identifiants invalides"
    }
}


# ═══════════════════════════════════════════════════════════════════════
# 2. TESTS D'ACCÈS AUX SOCIÉTÉS (RBAC)
# ═══════════════════════════════════════════════════════════════════════

TEST_CASES_SOCIETES = {
    "2.1_Admin_List_All_Societes": {
        "description": "Admin voit TOUTES les sociétés du cabinet",
        "method": "GET /auth/societes?token={WISSAL_TOKEN}",
        "expected_status": 200,
        "expected_count": 2,  # Cabinet 1 a 2 sociétés
        "expected_societes": [
            "Ets. EL OUJDI & FILS",
            "COMPTOIRE ARRAHMA SARL"
        ]
    },
    
    "2.2_User_List_Assigned_Societes": {
        "description": "User voit SEULEMENT les sociétés assignées",
        "method": "GET /auth/societes?token={FATIMA_TOKEN}",
        "expected_status": 200,
        "expected_count": 1,  # Fatima n'a accès qu'à 1
        "expected_societes": [
            "Ets. EL OUJDI & FILS"
        ]
    },
    
    "2.3_Admin_Other_Cabinet": {
        "description": "Admin du Cabinet 2 voit SEULEMENT ses sociétés",
        "method": "GET /auth/societes?token={AHMED_TOKEN}",
        "expected_status": 200,
        "expected_count": 1,  # Cabinet 2 a 1 société
        "expected_societes": [
            "Entreprise Import-Export"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════
# 3. TESTS DE SÉLECTION DE SOCIÉTÉ (Context Switching)
# ═══════════════════════════════════════════════════════════════════════

TEST_CASES_SELECT = {
    "3.1_Admin_Select_Own_Societe": {
        "description": "Admin sélectionne SON propre société",
        "method": "POST /auth/select-societe?token={WISSAL_TOKEN}",
        "payload": {
            "cabinet_id": 4,
            "societe_id": 2
        },
        "expected_status": 200,
        "expected_fields": ["session_token", "societe", "context"],
        "assertions": [
            "context.societe_id == 2",
            "context.cabinet_id == 4",
            "context.agent_id == 4",
            "societe.raison_sociale == 'Ets. EL OUJDI & FILS'",
            "session_token is not none"
        ]
    },
    
    "3.2_User_Select_Assigned_Societe": {
        "description": "User sélectionne UNE société assignée",
        "method": "POST /auth/select-societe?token={FATIMA_TOKEN}",
        "payload": {
            "cabinet_id": 4,
            "societe_id": 2
        },
        "expected_status": 200,
        "assertions": [
            "context.societe_id == 2",
            "societe.raison_sociale == 'Ets. EL OUJDI & FILS'"
        ]
    },
    
    "3.3_User_Select_Forbidden_Societe": {
        "description": "User essaie de sélectionner une société NON assignée",
        "method": "POST /auth/select-societe?token={FATIMA_TOKEN}",
        "payload": {
            "cabinet_id": 4,
            "societe_id": 3  # Fatima n'a pas accès à la societe 3
        },
        "expected_status": 403,
        "expected_error": "Accès refusé à cette société"
    },
    
    "3.4_Select_Invalid_Societe": {
        "description": "Sélectionner une société inexistante",
        "method": "POST /auth/select-societe?token={WISSAL_TOKEN}",
        "payload": {
            "cabinet_id": 4,
            "societe_id": 999
        },
        "expected_status": 404,
        "expected_error": "Société introuvable"
    }
}


# ═══════════════════════════════════════════════════════════════════════
# 4. TESTS DE TOKEN & SÉCURITÉ
# ═══════════════════════════════════════════════════════════════════════

TEST_CASES_SECURITY = {
    "4.1_Invalid_Token": {
        "description": "Utiliser un token invalide",
        "method": "GET /auth/societes?token=INVALID_TOKEN",
        "expected_status": 401,
        "expected_error": "Token invalide"
    },
    
    "4.2_Expired_Token": {
        "description": "Utiliser un token expiré",
        "method": "GET /auth/societes?token={EXPIRED_TOKEN}",
        "expected_status": 401,
        "expected_error": "Token expiré"
    },
    
    "4.3_Missing_Token": {
        "description": "Pas de token fourni",
        "method": "GET /auth/societes",
        "expected_status": 422,
        "expected_error": "query param 'token' required"
    }
}


# ═══════════════════════════════════════════════════════════════════════
# 5. TESTS D'ISOLATION DES DONNÉES
# ═══════════════════════════════════════════════════════════════════════

TEST_CASES_ISOLATION = {
    "5.1_Cabinet1_Cannot_Access_Cabinet2": {
        "description": "Agent du Cabinet 1 ne peut pas accéder Cabinet 2",
        "scenario": [
            "1. Login: wissal (cabin et 1)",
            "2. GET /admin/cabinets/5/societes?token=wissal_token",  # Cabinet 2
            "3. Devrait recevoir 403 Forbidden"
        ]
    },
    
    "5.2_Agent_Cannot_See_Other_Cabinets": {
        "description": "Un agent ne voit que SON cabinet",
        "scenario": [
            "1. Login: wissal",
            "2. GET /auth/societes",
            "3. Devrait voir SEULEMENT sociétés du cabinet 4",
            "4. Ne devrait PAS voir sociétés du cabinet 5 (Ahmed)"
        ]
    }
}


# ═══════════════════════════════════════════════════════════════════════
# DONNÉES DE RÉFÉRENCE
# ═══════════════════════════════════════════════════════════════════════

REFERENCE_DATA = {
    "Cabinets": {
        "Cabinet 1": {"id": 4, "name": "Cabinet Expertise Comptable"},
        "Cabinet 2": {"id": 5, "name": "Finances & Audit Maroc"}
    },
    
    "Agents": {
        "wissal": {"username": "wissal", "cabinet": 4, "role": "ADMIN", "societes": [2, 3]},
        "fatima": {"username": "fatima", "cabinet": 4, "role": "USER", "societes": [2]},
        "ahmed": {"username": "ahmed", "cabinet": 5, "role": "ADMIN", "societes": [4]}
    },
    
    "Societes": {
        "Ets. EL OUJDI & FILS": {"id": 2, "cabinet": 4, "ice": "001234567890001"},
        "COMPTOIRE ARRAHMA SARL": {"id": 3, "cabinet": 4, "ice": "002234567890002"},
        "Entreprise Import-Export": {"id": 4, "cabinet": 5, "ice": "003234567890003"}
    }
}
