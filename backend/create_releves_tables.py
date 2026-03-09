import os
import sys

# Ajouter le répertoire courant (backend) au path pour les imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import engine
from models import Base

print("Création des tables manquantes...")
Base.metadata.create_all(bind=engine)
print("Terminé avec succès.")
