"""
Burndown Chart — PFE Zéro Saisie Comptable
Suivi de l'avancement sur 8 Sprints (16 semaines)
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────
START = date(2026, 2, 2)
WEEKS = 16
END = START + timedelta(weeks=WEEKS)
TODAY = date(2026, 5, 16)  # <--- AUJOURD'HUI (16 Mai)

TOTAL_POINTS = 100 # Story Points totaux

# ── CALCUL DES DONNÉES ────────────────────────────────────────────────────
# Ligne Idéale
ideal_x = [START, END]
ideal_y = [TOTAL_POINTS, 0]

# Ligne Réelle (Simulation jusqu'à la fin)
real_x = []
real_y = []
current_points = TOTAL_POINTS

# On simule 15 semaines pour arriver au 16 Mai (qui est dans la semaine 15)
for i in range(16): 
    d = START + timedelta(weeks=i)
    if d > TODAY: break
    
    real_x.append(d)
    # Simulation d'une descente progressive vers 0
    if i == 0:
        val = TOTAL_POINTS
    elif i < 5:
        val = current_points - 6 
    elif i < 12:
        val = current_points - 9
    else:
        val = current_points - 10 # Accélération finale
    
    current_points = max(0, val)
    # Au 16 mai, on force à 0 car le projet est fini
    if d >= TODAY: current_points = 0
    
    real_y.append(current_points)

# ── VIZ ───────────────────────────────────────────────────────────────────
try:
    plt.style.use('seaborn-v0_8-whitegrid')
except:
    plt.style.use('ggplot') # Fallback
    
fig, ax = plt.subplots(figsize=(10, 6))

# Plot Ideal
ax.plot(ideal_x, ideal_y, 'r--', label='Ligne Idéale (Scope)', alpha=0.6, linewidth=2)

# Plot Réel
ax.plot(real_x, real_y, 'b-o', label='Reste à faire (Réel)', linewidth=3)

# Sprints (Axe X secondaire ou labels)
for w in range(0, WEEKS + 1, 2):
    sprint_date = START + timedelta(weeks=w)
    ax.axvline(mdates.date2num(sprint_date), color='gray', linestyle=':', alpha=0.3)
    if w < WEEKS:
        ax.text(mdates.date2num(sprint_date) + 7, TOTAL_POINTS + 2, f"S{w//2 + 1}", ha='center', fontsize=8)

# Design
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.set_ylim(0, TOTAL_POINTS + 10)
ax.set_ylabel("Story Points Restants")
ax.set_title("Burndown Chart : Suivi de l'avancement effectif", fontsize=14, fontweight='bold', pad=20)

ax.legend()
plt.tight_layout()
plt.savefig("burndown_pfe.png", dpi=200)
print("OK: Burndown Chart final genere : burndown_pfe.png")
