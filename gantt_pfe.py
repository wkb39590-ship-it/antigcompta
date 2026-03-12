"""
Diagramme de Gantt — PFE Zéro Saisie Comptable
Design : Heatmap de progression (Rouge -> Jaune -> Vert)
Mise à jour : 12/03/2026
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from datetime import date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────
TODAY = date(2026, 3, 12)  # <--- AUJOURD'HUI
START = date(2026, 2, 2)
END   = date(2026, 6, 20)

# ── DONNÉES DES TÂCHES ────────────────────────────────────────────────────
# (Nom, Début, Fin, % Avancement)
TASKS = [
    ("Compréhension du domaine comptable",    date(2026,2,2),  date(2026,2,10), 100),
    ("Analyse des besoins des utilisateurs",  date(2026,2,10), date(2026,2,20), 100),
    ("Planification du projet",               date(2026,2,20), date(2026,2,25), 100),
    ("Conception de l’architecture du système",date(2026,2,25), date(2026,3,3),  100),
    ("Conception de la base de données",      date(2026,3,3),  date(2026,3,8),  100), # <--- TERMINÉ
    ("Conception des interfaces (Admin/User)",date(2026,3,8),  date(2026,3,12), 80),  
    ("Développement du backend",              date(2026,3,10), date(2026,4,5),  15),  # <--- AUJOURD'HUI (En cours)
    ("Développement du frontend",             date(2026,4,1),  date(2026,4,25), 0),
    ("Intégration des modules du système",    date(2026,4,20), date(2026,5,2),  0),
    ("Développement fonctionnalités compta",  date(2026,4,28), date(2026,5,15), 0),
    ("Génération rapports & tableaux de bord",date(2026,5,12), date(2026,5,22), 0),
    ("Tests et validation du système",        date(2026,5,20), date(2026,6,5),  0),
    ("Déploiement de l’application",          date(2026,6,10), date(2026,6,15), 0),
]

# ── PREPARATION ───────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(top=0.9, right=0.85) # Faire de la place pour la colorbar et le label Today

# Colormap : Rouge -> Jaune -> Vert
# Note: matplotlib 3.7+ utilise cm.get_cmap, sinon utilisez plt.get_cmap
try:
    cmap = cm.get_cmap('RdYlGn')
except AttributeError:
    cmap = plt.get_cmap('RdYlGn')
    
norm = mcolors.Normalize(vmin=0, vmax=100)

for i, (name, start, end, pct) in enumerate(TASKS):
    x_s = mdates.date2num(start)
    x_e = mdates.date2num(end + timedelta(days=1))
    width = x_e - x_s
    
    # Couleur basée sur le pourcentage
    color = cmap(norm(pct))
    
    # Dessiner la barre de la tâche
    ax.barh(i, width, left=x_s, height=0.6, color=color, edgecolor='none', alpha=0.9)

# Axe Y (Tâches)
ax.set_yticks(range(len(TASKS)))
ax.set_yticklabels([t[0] for t in TASKS], fontsize=9)
ax.invert_yaxis()
ax.set_ylabel("Tâche", fontsize=10, labelpad=10)

# Axe X (Dates)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.xticks(rotation=45, fontsize=9)

# Ligne Aujourd'hui
today_v = mdates.date2num(TODAY)
ax.axvline(today_v, color='red', linestyle='--', linewidth=1.5, alpha=0.7)
ax.text(today_v, -1, 'Aujourd\'hui', color='red', ha='center', fontweight='bold')

# Grille
ax.grid(axis='x', linestyle=':', alpha=0.4)

# Colorbar (Légende d'avancement)
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7]) # [left, bottom, width, height]
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('Avancement (%)', fontsize=10)

# Finitions
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.suptitle("Planning PFE : Zéro Saisie Comptable", fontsize=16, fontweight='bold', x=0.4)


# Sauvegarde
plt.savefig("gantt_pfe_v3.png", dpi=200, bbox_inches="tight")
print(f"✅ Nouveau diagramme généré : gantt_pfe_v3.png (Date: {TODAY.strftime('%d/%m/%Y')})")
plt.show()
