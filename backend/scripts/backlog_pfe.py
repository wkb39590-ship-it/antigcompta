"""
Génération visuelle du Product Backlog — PFE Zéro Saisie
Basé sur les fonctionnalités réelles du projet (Gemini, SHA-256, PCM)
"""
import matplotlib.pyplot as plt

# Données réelles du projet ComptaFacile (Zéro Saisie)
backlog = [
    {"ID": "US01", "User Story": "Authentification sécurisée & Rôles (JWT)", "Priorité": "Critique", "Statut": "Terminé"},
    {"ID": "US02", "User Story": "Gestion multi-tenant (Isolation Cabinets)", "Priorité": "Haute", "Statut": "Terminé"},
    {"ID": "US03", "User Story": "Extraction IA sémantique (API Gemini)", "Priorité": "Critique", "Statut": "Terminé"},
    {"ID": "US04", "User Story": "Détection doublons binaires (SHA-256)", "Priorité": "Haute", "Statut": "Terminé"},
    {"ID": "US05", "User Story": "Classification auto Plan Comptable Marocain", "Priorité": "Haute", "Statut": "Terminé"},
    {"ID": "US06", "User Story": "Portail client pour transmission documents", "Priorité": "Moyenne", "Statut": "Terminé"},
    {"ID": "US07", "User Story": "Gestion des Journaux et du Grand Livre", "Priorité": "Haute", "Statut": "Terminé"},
    {"ID": "US08", "User Story": "Logs d'audit et historique des actions", "Priorité": "Moyenne", "Statut": "Terminé"},
]

def generate_backlog_viz():
    # Style
    plt.rcParams['font.sans-serif'] = ['Arial']
    
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.axis('off')

    # Préparation des données pour le tableau
    table_data = [[item["ID"], item["User Story"], item["Priorité"], item["Statut"]] for item in backlog]
    columns = ("ID", "User Story (Fonctionnalité)", "Priorité", "Statut")

    # Création du tableau
    table = ax.table(cellText=table_data, colLabels=columns, loc='center', cellLoc='left')

    # Style du tableau
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.2, 2.8)

    # Coloration des entêtes et des statuts
    for (row, col), cell in table.get_celld().items():
        # Header
        if row == 0:
            cell.set_text_props(weight='bold', color='white')
            cell.set_facecolor('#2c3e50')
        
        # Coloration alternée des lignes
        elif row % 2 == 0:
            cell.set_facecolor('#f2f2f2')
            
        # Colonne Statut
        if col == 3 and row > 0:
            text = cell.get_text().get_text()
            if text == "Terminé": 
                cell.set_text_props(color='#27ae60', weight='bold') # Vert
            if text == "En cours": 
                cell.set_text_props(color='#e67e22', weight='bold') # Orange

        # Colonne Priorité
        if col == 2 and row > 0:
            text = cell.get_text().get_text()
            if text == "Critique": cell.set_text_props(color='#c0392b', weight='bold')

    plt.title("Product Backlog : Plateforme Zéro Saisie Comptable", fontsize=18, fontweight='bold', pad=30, color='#2c3e50')
    
    # Ajout d'une petite note de bas de page
    plt.figtext(0.5, 0.05, "Extrait du Backlog Technique - Projet de Fin d'Études", ha="center", fontsize=10, style='italic', color='gray')

    plt.tight_layout()
    plt.savefig("backlog_pfe.png", dpi=200, bbox_inches="tight")
    print("OK: Visuel du Product Backlog genere : backlog_pfe.png")

if __name__ == "__main__":
    generate_backlog_viz()
