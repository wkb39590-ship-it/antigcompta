#!/usr/bin/env python3
"""
test_auth_complete.py - Tests d'intégration complets pour l'authentification multi-cabinet
Exécutez: python test_auth_complete.py
"""
import requests
import json
from typing import Dict, List, Optional
import sys

class FullAuthTester:
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.tokens = {}
        self.session_tokens = {}
        self.passed = 0
        self.failed = 0
        
    def log_test(self, test_id: str, status: str, message: str = ""):
        """Log un résultat de test"""
        icon = "✅" if status == "PASS" else "❌"
        if message:
            print(f"{icon} [{test_id}] {status}: {message}")
        else:
            print(f"{icon} [{test_id}] {status}")
        
        if status == "PASS":
            self.passed += 1
        else:
            self.failed += 1
    
    def assert_equal(self, actual, expected, test_id: str, field_name: str):
        """Assert que actual == expected"""
        if actual == expected:
            self.log_test(test_id, "PASS", f"{field_name}: {actual}")
        else:
            self.log_test(test_id, "FAIL", f"{field_name}: got {actual}, expected {expected}")
    
    def assert_status(self, response, expected_status: int, test_id: str):
        """Assert le status code HTTP"""
        if response.status_code == expected_status:
            self.log_test(test_id, "PASS", f"Status {expected_status}")
            return True
        else:
            self.log_test(test_id, "FAIL", f"Status: got {response.status_code}, expected {expected_status}")
            if response.status_code >= 400:
                try:
                    print(f"   Error: {response.json()}")
                except:
                    print(f"   Response: {response.text[:100]}")
            return False
    
    def print_section(self, title: str):
        """Affiche une section"""
        print(f"\n{'='*70}")
        print(f"  {title}")
        print(f"{'='*70}")
    
    # ───────────────────────────────────────────────────────────────────
    # TESTS 1: AUTHENTICATION
    # ───────────────────────────────────────────────────────────────────
    
    def test_login_success(self):
        """1.1 - Login réussi (wissal)"""
        self.print_section("1. AUTHENTIFICATION")
        
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "wissal", "password": "password123"}
        )
        
        test_id = "1.1"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.tokens["wissal"] = data["access_token"]
            self.assert_equal(data["agent"]["username"], "wissal", test_id, "username")
            self.assert_equal(data["agent"]["is_admin"], True, test_id, "is_admin")
            self.assert_equal(len(data["cabinets"]) > 0, True, test_id, "cabinets count")
    
    def test_login_user(self):
        """1.2 - Login user restreint (fatima)"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "fatima", "password": "password123"}
        )
        
        test_id = "1.2"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.tokens["fatima"] = data["access_token"]
            self.assert_equal(data["agent"]["username"], "fatima", test_id, "username")
            self.assert_equal(data["agent"]["is_admin"], False, test_id, "is_admin")
    
    def test_login_admin_cabinet2(self):
        """1.3 - Login admin Cabinet 2 (ahmed)"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "ahmed", "password": "password123"}
        )
        
        test_id = "1.3"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.tokens["ahmed"] = data["access_token"]
            self.assert_equal(data["agent"]["username"], "ahmed", test_id, "username")
    
    def test_login_invalid_password(self):
        """1.4 - Login avec mauvais mot de passe"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "wissal", "password": "wrong"}
        )
        
        test_id = "1.4"
        self.assert_status(response, 401, test_id)
    
    def test_login_nonexistent(self):
        """1.5 - Login utilisateur inexistant"""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        
        test_id = "1.5"
        self.assert_status(response, 401, test_id)
    
    # ───────────────────────────────────────────────────────────────────
    # TESTS 2: ACCÈS AUX SOCIÉTÉS (RBAC)
    # ───────────────────────────────────────────────────────────────────
    
    def test_admin_view_all_societes(self):
        """2.1 - Admin voit TOUTES les sociétés du cabinet"""
        self.print_section("2. ACCÈS AUX SOCIÉTÉS (RBAC)")
        
        response = requests.get(
            f"{self.base_url}/auth/societes?token={self.tokens['wissal']}"
        )
        
        test_id = "2.1"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.assert_equal(len(data), 2, test_id, "Societes count")
            societe_names = [s["raison_sociale"] for s in data]
            self.assert_equal("Ets. EL OUJDI & FILS" in societe_names, True, test_id, "Societe 1 présente")
            self.assert_equal("COMPTOIRE ARRAHMA SARL" in societe_names, True, test_id, "Societe 2 présente")
    
    def test_user_view_assigned_societes(self):
        """2.2 - User voit SEULEMENT ses sociétés assignées"""
        response = requests.get(
            f"{self.base_url}/auth/societes?token={self.tokens['fatima']}"
        )
        
        test_id = "2.2"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.assert_equal(len(data), 1, test_id, "Societes count")
            self.assert_equal(data[0]["raison_sociale"], "Ets. EL OUJDI & FILS", test_id, "Societe assignée")
    
    def test_admin_cabinet2_view_societes(self):
        """2.3 - Admin Cabinet 2 voit SEULEMENT ses sociétés"""
        response = requests.get(
            f"{self.base_url}/auth/societes?token={self.tokens['ahmed']}"
        )
        
        test_id = "2.3"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.assert_equal(len(data), 1, test_id, "Societes count")
            self.assert_equal(data[0]["raison_sociale"], "Entreprise Import-Export", test_id, "Societe Cabinet 2")
    
    # ───────────────────────────────────────────────────────────────────
    # TESTS 3: SÉLECTION SOCIÈTE (Context Switching)
    # ───────────────────────────────────────────────────────────────────
    
    def test_select_societe_admin(self):
        """3.1 - Admin sélectionne une société"""
        self.print_section("3. SÉLECTION SOCIÈTE (Context)")
        
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['wissal']}",
            json={"cabinet_id": 4, "societe_id": 2}
        )
        
        test_id = "3.1"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.session_tokens["wissal_societe2"] = data["session_token"]
            context = data["context"]
            self.assert_equal(context["societe_id"], 2, test_id, "societe_id")
            self.assert_equal(context["cabinet_id"], 4, test_id, "cabinet_id")
            self.assert_equal(context["agent_id"], 4, test_id, "agent_id")
            self.assert_equal(data["societe"]["raison_sociale"], "Ets. EL OUJDI & FILS", test_id, "societe_name")
    
    def test_select_societe_user(self):
        """3.2 - User sélectionne sa société assignée"""
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['fatima']}",
            json={"cabinet_id": 4, "societe_id": 2}
        )
        
        test_id = "3.2"
        if self.assert_status(response, 200, test_id):
            data = response.json()
            self.session_tokens["fatima_societe2"] = data["session_token"]
            self.assert_equal(data["context"]["societe_id"], 2, test_id, "societe_id")
    
    def test_select_forbidden_societe(self):
        """3.3 - User essaie de sélectionner une sociète NON assignée"""
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['fatima']}",
            json={"cabinet_id": 4, "societe_id": 3}  # Fatima n'a pas accès
        )
        
        test_id = "3.3"
        self.assert_status(response, 403, test_id)
    
    def test_select_invalid_societe(self):
        """3.4 - Sélectionner une sociète inexistante"""
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['wissal']}",
            json={"cabinet_id": 4, "societe_id": 999}
        )
        
        test_id = "3.4"
        self.assert_status(response, 404, test_id)
    
    # ───────────────────────────────────────────────────────────────────
    # TESTS 4: SÉCURITÉ & TOKENS
    # ───────────────────────────────────────────────────────────────────
    
    def test_invalid_token(self):
        """4.1 - Token invalide"""
        self.print_section("4. SÉCURITÉ & TOKENS")
        
        response = requests.get(
            f"{self.base_url}/auth/societes?token=INVALID_TOKEN_XYZ"
        )
        
        test_id = "4.1"
        self.assert_status(response, 401, test_id)
    
    def test_missing_token(self):
        """4.2 - Token manquant"""
        response = requests.get(
            f"{self.base_url}/auth/societes"
        )
        
        test_id = "4.2"
        self.assert_status(response, 422, test_id)
    
    # ───────────────────────────────────────────────────────────────────
    # TESTS 5: ISOLATION DES DONNÉES
    # ───────────────────────────────────────────────────────────────────
    
    def test_cabinet_isolation(self):
        """5.1 - Agent Cabinet 1 ne peut pas voir Cabinet 2"""
        self.print_section("5. ISOLATION DES DONNÉES")
        
        # Le Cabinet 2 est le ID 5, mais wissal est du Cabinet 4
        # Essayer d'accéder à une sociétédu Cabinet 5 devrait échouer
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['wissal']}",
            json={"cabinet_id": 5, "societe_id": 4}  # Cabinet 2's societe
        )
        
        test_id = "5.1"
        # L'agent wissal ne peut pas sélectionner une société du cabinet 5
        # car il ne peut pas accéder aux sociétés du cabinet 5
        # Cela devrait échouer (404 ou 403)
        if response.status_code in [403, 404]:
            self.log_test(test_id, "PASS", f"Correctly denied: {response.status_code}")
            self.passed += 1
        else:
            self.log_test(test_id, "FAIL", f"Got {response.status_code}, expected 403/404")
    
    def test_cross_cabinet_prevention(self):
        """5.2 - Agents de cabinets différents isolés"""
        self.print_section("")  # Même section
        
        # ahmed (Cabinet 2) ne devrait pas pouvoir accéder à wissal's sociétés
        response = requests.post(
            f"{self.base_url}/auth/select-societe?token={self.tokens['ahmed']}",
            json={"cabinet_id": 4, "societe_id": 2}  # Cabinet 1's societe
        )
        
        test_id = "5.2"
        if response.status_code in [403, 404]:
            self.log_test(test_id, "PASS", f"Correctly denied: {response.status_code}")
            self.passed += 1
        else:
            self.log_test(test_id, "FAIL", f"Got {response.status_code}, expected 403/404")
    
    # ───────────────────────────────────────────────────────────────────
    # Main test runner
    # ───────────────────────────────────────────────────────────────────
    
    def run_all_tests(self):
        """Exécute tous les tests"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║      TESTS D'INTÉGRATION - AUTHENTIFICATION MULTI-CABINET        ║
║        Comptabilité Zéro Saisie - Architecture Multi-Tenant      ║
╚══════════════════════════════════════════════════════════════════╝
        """)
        
        # Section 1: Authentication
        self.test_login_success()
        self.test_login_user()
        self.test_login_admin_cabinet2()
        self.test_login_invalid_password()
        self.test_login_nonexistent()
        
        # Section 2: RBAC
        self.test_admin_view_all_societes()
        self.test_user_view_assigned_societes()
        self.test_admin_cabinet2_view_societes()
        
        # Section 3: Select
        self.test_select_societe_admin()
        self.test_select_societe_user()
        self.test_select_forbidden_societe()
        self.test_select_invalid_societe()
        
        # Section 4: Security
        self.test_invalid_token()
        self.test_missing_token()
        
        # Section 5: Isolation
        self.test_cabinet_isolation()
        self.test_cross_cabinet_prevention()
        
        # Summary
        print(f"\n{'='*70}")
        print(f"📊 RÉSUMÉ DES TESTS")
        print(f"{'='*70}")
        print(f"✅ Réussis: {self.passed}")
        print(f"❌ Échoués: {self.failed}")
        print(f"📈 Total: {self.passed + self.failed}")
        
        if self.failed == 0:
            print(f"\n🎉 TOUS LES TESTS PASSÉS!")
            return True
        else:
            print(f"\n⚠️  {self.failed} test(s) échoué(s)")
            return False


def main():
    tester = FullAuthTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
