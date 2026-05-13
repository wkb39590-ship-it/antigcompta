"""
Diagramme de Gantt — PFE Zéro Saisie Comptable
Style détaillé avec Heatmap d'avancement
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from datetime import date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────
TODAY = date(2026, 5, 15)  # <--- AUJOURD'HUI (15 Mai)
START = date(2026, 2, 2)
END   = date(2026, 6, 1)

# ── DONNÉES DES TÂCHES ────────────────────────────────────────────────────
# (Nom, Début, Fin, % Avancement)
TASKS = [
    ("Compréhension du domaine comptable",    date(2026,2,2),  date(2026,2,10), 100),
    ("Analyse des besoins des utilisateurs",  date(2026,2,10), date(2026,2,20), 100),
    ("Planification du projet",               date(2026,2,20), date(2026,2,25), 100),
    ("Conception de l’architecture du système",date(2026,2,25), date(2026,3,3),  100),
    ("Conception de la base de données",      date(2026,3,3),  date(2026,3,8),  100),
    ("Conception des interfaces (Admin/User)",date(2026,3,5),  date(2026,3,12), 100),
    ("Développement du backend (FastAPI)",   date(2026,3,10), date(2026,4,15), 100),
    ("Développement du frontend (React)",    date(2026,3,12), date(2026,4,25), 100),
    ("Intégration des modules (IA/Inbox)",    date(2026,3,15), date(2026,4,25), 100),
    ("Développement fonctionnalités compta",  date(2026,3,18), date(2026,5,15), 100),
    ("Génération rapports & tableaux de bord",date(2026,4,20), date(2026,5,10), 100),
    ("Tests et validation du système",        date(2026,4,25), date(2026,5,15), 100),
]

# ── PREPARATION ───────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
plt.subplots_adjust(top=0.9, right=0.85)

# Colormap : Rouge -> Jaune -> Vert
try:
    cmap = cm.get_cmap('RdYlGn')
except AttributeError:
    cmap = plt.get_cmap('RdYlGn')
    
norm = mcolors.Normalize(vmin=0, vmax=100)

for i, (name, start, end, pct) in enumerate(TASKS):
    x_s = mdates.date2num(start)
    x_e = mdates.date2num(end + timedelta(days=1))
    full_width = x_e - x_s
    
    # 1. Dessiner la barre de fond (Gris clair)
    ax.barh(i, full_width, left=x_s, height=0.6, color='#EEEEEE', edgecolor='#CCCCCC', alpha=0.5)
    
    # 2. Dessiner la barre de progression (Couleur basée sur le %)
    prog_width = full_width * (pct / 100.0)
    color = cmap(norm(pct))
    ax.barh(i, prog_width, left=x_s, height=0.6, color=color, edgecolor='none', alpha=0.9)

# Axe Y
ax.set_yticks(range(len(TASKS)))
ax.set_yticklabels([t[0] for t in TASKS], fontsize=9)
ax.invert_yaxis()
ax.set_ylabel("Tâche", fontsize=10, labelpad=10)

# Axe X
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.xticks(rotation=45, fontsize=9)

# Grille
ax.grid(axis='x', linestyle=':', alpha=0.4)

# Colorbar (Légende d'avancement)
sm = cm.ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar_ax = fig.add_axes([0.88, 0.15, 0.02, 0.7])
cbar = fig.colorbar(sm, cax=cbar_ax)
cbar.set_label('Avancement (%)', fontsize=10)

# Finitions
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.suptitle("Planning PFE : Zéro Saisie Comptable", fontsize=16, fontweight='bold', x=0.4)

# Sauvegarde
plt.savefig("gantt_pfe_v3.png", dpi=200, bbox_inches="tight")
print("OK: Gantt detaille genere : gantt_pfe_v3.png")
