"""
seed_multi_cabinet.py - Initialise les données de test pour l'architecture multi-cabinet
"""
import sys
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Cabinet, Agent, Societe, CompteurFacturation
from routes.auth import hash_password
from datetime import datetime

def seed_data():
    """Crée les données de test pour multi-cabinet"""
    db = SessionLocal()
    
    try:
        # 1. Créer les cabinets
        print("📦 Création des cabinets...")
        
        cabinet1 = db.query(Cabinet).filter(Cabinet.nom == "Cabinet Expertise Comptable").first()
        if not cabinet1:
            cabinet1 = Cabinet(
                nom="Cabinet Expertise Comptable",
                email="contact@expertise-cpt.ma",
                telephone="+212 5 24 12 34 56",
                adresse="123 Avenue Hassan II, Casablanca"
            )
            db.add(cabinet1)
        
        cabinet2 = db.query(Cabinet).filter(Cabinet.nom == "Finances & Audit Maroc").first()
        if not cabinet2:
            cabinet2 = Cabinet(
                nom="Finances & Audit Maroc",
                email="info@finances-audit.ma",
                telephone="+212 5 37 77 88 99",
                adresse="45 Rue de Fès, Rabat"
            )
            db.add(cabinet2)
            
        db.flush()  # Pour obtenir les IDs

        
        # 2. Créer les les agents
        print("👤 Création des agents...")
        
        # Agents du cabinet 1
        agent1 = db.query(Agent).filter(Agent.username == "wissal").first()
        if not agent1:
            agent1 = Agent(
                cabinet_id=cabinet1.id,
                username="wissal",
                email="wissal@expertise-cpt.ma",
                password_hash=hash_password("password123"),
                nom="Bennani",
                prenom="Wissal",
                is_admin=False,
                is_super_admin=True
            )
            db.add(agent1)
        else:
            # Forcer la mise à jour pour les tests
            agent1.is_admin = False
            agent1.is_super_admin = True
            print("   → Mise à jour des rôles pour wissal (Super Admin uniquement)")

        
        agent2 = db.query(Agent).filter(Agent.username == "fatima").first()
        if not agent2:
            agent2 = Agent(
                cabinet_id=cabinet1.id,
                username="fatima",
                email="fatima@expertise-cpt.ma",
                password_hash=hash_password("password123"),
                nom="El Oujdi",
                prenom="Fatima",
                is_admin=False,
                is_super_admin=False
            )
            db.add(agent2)
        
        # Agent du cabinet 2
        agent3 = db.query(Agent).filter(Agent.username == "ahmed").first()
        if not agent3:
            agent3 = Agent(
                cabinet_id=cabinet2.id,
                username="ahmed",
                email="ahmed@finances-audit.ma",
                password_hash=hash_password("password123"),
                nom="Ahmed",
                prenom="Kabil",
                is_admin=True,
                is_super_admin=False
            )
            db.add(agent3)
        else:
            agent3.is_admin = True
            agent3.is_super_admin = False
            print("   → Mise à jour des rôles pour ahmed (Admin Cabinet)")

            
        db.flush()

        
        # 3. Créer les sociétés clients
        print("🏢 Création des sociétés...")
        
        # Sociétés du cabinet 1
        societe1 = db.query(Societe).filter(Societe.raison_sociale == "Ets. EL OUJDI & FILS").first()
        if not societe1:
            societe1 = Societe(
                cabinet_id=cabinet1.id,
                raison_sociale="Ets. EL OUJDI & FILS",
                ice="001234567890001",
                if_fiscal="12345678",
                rc="RC-12345",
                patente="PAT-001",
                adresse="Quartier des Affaires, Casablanca"
            )
            db.add(societe1)
        
        societe2 = db.query(Societe).filter(Societe.raison_sociale == "COMPTOIRE ARRAHMA SARL").first()
        if not societe2:
            societe2 = Societe(
                cabinet_id=cabinet1.id,
                raison_sociale="COMPTOIRE ARRAHMA SARL",
                ice="002234567890002",
                if_fiscal="87654321",
                rc="RC-54321",
                patente="PAT-002",
                adresse="Zone Industrielle, Fès"
            )
            db.add(societe2)
        
        # Sociète du cabinet 2
        societe3 = db.query(Societe).filter(Societe.raison_sociale == "Entreprise Import-Export").first()
        if not societe3:
            societe3 = Societe(
                cabinet_id=cabinet2.id,
                raison_sociale="Entreprise Import-Export",
                ice="003234567890003",
                if_fiscal="11111111",
                rc="RC-99999",
                patente="PAT-003",
                adresse="Port de Casablanca"
            )
            db.add(societe3)
            
        db.flush()

        
        # 4. Assigner les sociétés aux agents
        print("🔗 Assignation des sociétés aux agents...")
        
        # Wissal (admin) peut gérer toutes les sociétés de son cabinet
        if societe1 not in agent1.societes:
            agent1.societes.append(societe1)
        if societe2 not in agent1.societes:
            agent1.societes.append(societe2)
        
        # Fatima gère seulement la première société
        if societe1 not in agent2.societes:
            agent2.societes.append(societe1)
        
        # Ahmed (admin) gère la société de son cabinet
        if societe3 not in agent3.societes:
            agent3.societes.append(societe3)
        
        db.flush()

        
        # 5. Créer les compteurs de facturation
        print("📊 Création des compteurs de facturation...")
        
        annee_courante = datetime.now().year
        
        for societe in [societe1, societe2, societe3]:
            compteur_existant = db.query(CompteurFacturation).filter(
                CompteurFacturation.societe_id == societe.id,
                CompteurFacturation.annee == annee_courante
            ).first()
            
            if not compteur_existant:
                compteur = CompteurFacturation(
                    societe_id=societe.id,
                    annee=annee_courante,
                    dernier_numero=0
                )
                db.add(compteur)

        
        db.commit()
        
        print(f"""
✅ Données de test créées avec succès !

📦 Cabinets:
   1. {cabinet1.nom}
   2. {cabinet2.nom}

👤 Agents:
   Cabinet 1:
   - ahmed / password123 (ADMIN CABINET)
   - wissal / password123 (SUPER ADMIN)

🏢 Sociétés:
   Cabinet 1:
   - {societe1.raison_sociale}
   - {societe2.raison_sociale}
   
   Cabinet 2:
   - {societe3.raison_sociale}

🔗 Assignations:
   - Wissal (admin): Gère toutes les sociétés du cabinet
   - Fatima: Accès à {societe1.raison_sociale}
   - Ahmed (admin): Gère {societe3.raison_sociale}

🚀 Prêt pour les tests !
        """)
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors du seed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
