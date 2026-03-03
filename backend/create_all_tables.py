
import os
import sys

# Ajouter le répertoire actuel au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base
import models  # Import complet pour enregistrer tous les modèles

print("🔧 Tentative de création des tables manquantes...")
try:
    Base.metadata.create_all(bind=engine)
    print("✅ Opération terminée. Vérifiez les tables dans pgAdmin.")
    
    # Lister les tables connues par SQLAlchemy
    print("\nTables enregistrées dans SQLAlchemy :")
    for table_name in Base.metadata.tables.keys():
        print(f" - {table_name}")
        
except Exception as e:
    print(f"❌ Erreur lors de la création des tables : {e}")
    import traceback
    traceback.print_exc()
