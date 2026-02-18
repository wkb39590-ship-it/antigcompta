"""
apply_migration.py - Applique la migration multi-cabinet manuellement
"""
from sqlalchemy import text
from database import engine

def apply_migration():
    """Crée les tables manquantes"""
    
    commands = [
        # Créer la table Cabinet
        """CREATE TABLE IF NOT EXISTS cabinets (
            id SERIAL PRIMARY KEY,
            nom VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255),
            telephone VARCHAR(20),
            adresse VARCHAR(500),
            logo_path VARCHAR(500),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        # Créer la table Agent
        """CREATE TABLE IF NOT EXISTS agents (
            id SERIAL PRIMARY KEY,
            cabinet_id INTEGER NOT NULL REFERENCES cabinets(id),
            username VARCHAR(100) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash VARCHAR(500) NOT NULL,
            nom VARCHAR(255),
            prenom VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            is_admin BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""",
        
        "CREATE INDEX IF NOT EXISTS ix_agents_cabinet_id ON agents(cabinet_id)",
        
        # Ajouter colonnes à Societes
        "ALTER TABLE societes ADD COLUMN IF NOT EXISTS cabinet_id INTEGER",
        "ALTER TABLE societes ADD COLUMN IF NOT EXISTS logo_path VARCHAR(500)",
        "ALTER TABLE societes ADD COLUMN IF NOT EXISTS patente VARCHAR(50)",
        "ALTER TABLE societes ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
        
        # Créer table d'association Agent-Societe
        """CREATE TABLE IF NOT EXISTS agent_societes (
            agent_id INTEGER NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
            societe_id INTEGER NOT NULL REFERENCES societes(id) ON DELETE CASCADE,
            PRIMARY KEY (agent_id, societe_id)
        )""",
        
        "CREATE INDEX IF NOT EXISTS ix_agent_societes_agent_id ON agent_societes(agent_id)",
        "CREATE INDEX IF NOT EXISTS ix_agent_societes_societe_id ON agent_societes(societe_id)",
        
        # Créer table CompteurFacturation
        """CREATE TABLE IF NOT EXISTS compteurs_facturation (
            id SERIAL PRIMARY KEY,
            societe_id INTEGER NOT NULL REFERENCES societes(id),
            annee INTEGER NOT NULL,
            dernier_numero INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(societe_id, annee)
        )""",
        
        "CREATE INDEX IF NOT EXISTS ix_compteurs_facturation_societe_id ON compteurs_facturation(societe_id)",
        
        # Insérer un Cabinet par défaut
        "INSERT INTO cabinets (nom, email, telephone, adresse) VALUES ('Cabinet par Défaut', 'admin@cabinet.ma', '+212 5 24 12 34 56', 'Casablanca') ON CONFLICT (nom) DO NOTHING",
    ]
    
    with engine.begin() as connection:
        print("✅ Exécution de la migration...")
        
        for i, command in enumerate(commands, 1):
            try:
                connection.execute(text(command))
                print(f"   ✓ [{i}/{len(commands)}] {command[:50]}...")
            except Exception as e:
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print(f"   ⚠ [{i}/{len(commands)}] Déjà existant: {command[:40]}...")
                else:
                    print(f"   ❌ [{i}/{len(commands)}] Erreur: {str(e)[:60]}")
        
        print("✅ Migration appliquée avec succès !")

if __name__ == "__main__":
    apply_migration()
