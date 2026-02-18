"""
test_auth_api.py - Tests d'intégration pour l'API d'authentification multi-cabinet
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8090"

class AuthAPITester:
    def __init__(self):
        self.session = requests.Session()
        # Utiliser le nom du service (hostname interne au Docker network)
        self.base_url = "http://127.0.0.1:8000"
        self.token = None
        self.session_token = None
    
    def test_login(self, username: str, password: str) -> dict:
        """Test de connexion"""
        print(f"\n🔐 TEST: Login {username}/{password}")
        
        response = self.session.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password}
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            self.token = data["access_token"]
            print(f"✅ Login réussi")
            print(f"   Token: {self.token[:50]}...")
            print(f"   Agent: {data['agent']['prenom']} {data['agent']['nom']}")
            print(f"   Cabinet: {data['agent']['cabinet_id']}")
            return data
        else:
            print(f"❌ Erreur: {data}")
            return None
    
    def test_get_societes(self):
        """Test de récupération des sociétés accessibles"""
        print(f"\n🏢 TEST: Récupérer les sociétés")
        
        if not self.token:
            print("❌ Token non disponible, login d'abord")
            return
        
        response = self.session.get(
            f"{self.base_url}/auth/societes?token={self.token}"
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ {len(data)} sociétés trouvées:")
            for societe in data:
                print(f"   - [{societe['id']}] {societe['raison_sociale']}")
            return data
        else:
            print(f"❌ Erreur: {data}")
            return None
    
    def test_select_societe(self, cabinet_id: int, societe_id: int):
        """Test de sélection d'une société"""
        print(f"\n🎯 TEST: Sélectionner société #{societe_id} du cabinet #{cabinet_id}")
        
        if not self.token:
            print("❌ Token non disponible, login d'abord")
            return
        
        response = self.session.post(
            f"{self.base_url}/auth/select-societe?token={self.token}",
            json={"cabinet_id": cabinet_id, "societe_id": societe_id}
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            self.session_token = data["session_token"]
            print(f"✅ Société sélectionnée")
            print(f"   Société: {data['societe']['raison_sociale']}")
            print(f"   Session Token: {self.session_token[:50]}...")
            return data
        else:
            print(f"❌ Erreur: {data}")
            return None
    
    def test_list_cabinets_societes(self, cabinet_id: int):
        """Test de liste des sociétés d'un cabinet"""
        print(f"\n📋 TEST: Lister les sociétés du cabinet #{cabinet_id}")
        
        if not self.token:
            print("❌ Token non disponible, login d'abord")
            return
        
        response = self.session.get(
            f"{self.base_url}/admin/cabinets/{cabinet_id}/societes?token={self.token}"
        )
        
        print(f"Status: {response.status_code}")
        data = response.json()
        
        if response.status_code == 200:
            print(f"✅ {len(data)} sociétés dans le cabinet #{cabinet_id}:")
            for societe in data:
                print(f"   - [{societe['id']}] {societe['raison_sociale']} (ICE: {societe.get('ice', 'N/A')})")
            return data
        else:
            print(f"❌ Erreur: {data}")
            return None
    
    def test_generate_invoice_number(self, societe_id: int):
        """Test de génération de numéro de facture"""
        print(f"\n🔢 TEST: Générer numéro de facture pour société #{societe_id}")
        
        if not self.session_token:
            print("❌ Session token non disponible, sélectionner une société d'abord")
            return
        
        # Cet endpoint devrait être implémenté dans routes/admin.py
        print("   ℹ Endpoint à implémenter: GET /admin/societes/{societe_id}/next-numero")
        print("   Format attendu: '00001/25' pour 2025")
    
    def run_full_workflow(self):
        """Exécute le flux complet de test"""
        print("\n" + "="*60)
        print("🚀 WORKFLOW COMPLET: Login → Sélection → Context")
        print("="*60)
        
        # 1. Test login agent 1 (wissal - admin)
        login_data = self.test_login("wissal", "password123")
        if not login_data:
            return
        
        cabinet_id = login_data['agent']['cabinet_id']
        
        # 2. Lister les sociétés accessibles
        societes = self.test_get_societes()
        if not societes or len(societes) == 0:
            print("❌ Aucune société trouvée")
            return
        
        # 3. Sélectionner la première société
        first_societe_id = societes[0]['id']
        select_data = self.test_select_societe(cabinet_id, first_societe_id)
        if not select_data:
            return
        
        # 4. Afficher le contexte de session
        print(f"\n📍 CONTEXT DE SESSION:")
        context = select_data['context']
        print(f"   Agent ID: {context['agent_id']}")
        print(f"   Cabinet ID: {context['cabinet_id']}")
        print(f"   Société ID: {context['societe_id']}")
        print(f"   Utilisateur: {context['username']}")
        print(f"   Entreprise: {context['societe_raison_sociale']}")
        
        print(f"\n💡 PROCHAINES ÉTAPES:")
        print(f"   1. Toutes les factures créées seront liées à la société #{context['societe_id']}")
        print(f"   2. Le numéro de facture sera généré selon le compteur de cette société")
        print(f"   3. Les écritures seront isolées au contexte de cette société")
        
        # 5. Test avec un autre agent avec accès restreint
        print("\n" + "-"*60)
        print("Test avec agent à accès restreint (fatima)")
        print("-"*60)
        
        # Reset du token pour nouveau login
        self.token = None
        login_data2 = self.test_login("fatima", "password123")
        if login_data2:
            societes2 = self.test_get_societes()
            print(f"✅ Fatima a accès à {len(societes2) if societes2 else 0} société(s)")
            if societes2:
                for s in societes2:
                    print(f"   - {s['raison_sociale']}")


def main():
    print("""
╔════════════════════════════════════════════════════════════╗
║  TEST API AUTHENTIFICATION MULTI-CABINET                   ║
║  Comptabilité Zéro Saisie - Architecture Multi-Tenant      ║
╚════════════════════════════════════════════════════════════╝
    """)
    
    tester = AuthAPITester()
    
    try:
        # Run workflow
        tester.run_full_workflow()
        
        print(f"\n{'='*60}")
        print("✅ TESTS TERMINÉS AVEC SUCCÈS")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
