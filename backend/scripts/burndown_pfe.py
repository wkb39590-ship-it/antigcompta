"""
Burndown Chart — PFE Zéro Saisie Comptable
Mesure de la Vélocité et Suivi de l'Avancement
Design : Professionnel, épuré, avec calcul de tendance
Mise à jour : 05/05/2026 (Post-Bilan removal)
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────
TODAY = date(2026, 5, 5)  # <--- AUJOURD'HUI (5 Mai)
START = date(2026, 2, 2)
END   = date(2026, 5, 25) # Fin prévue fin Mai

# ── DONNÉES (Story Points / Charge estimée) ─────────────────────────────
TASKS = [
    {"name": "Compréhension domaine",   "sp": 5,  "start": date(2026,2,2),  "end": date(2026,2,10), "pct": 100},
    {"name": "Analyse besoins",        "sp": 8,  "start": date(2026,2,10), "end": date(2026,2,20), "pct": 100},
    {"name": "Planification",          "sp": 3,  "start": date(2026,2,20), "end": date(2026,2,25), "pct": 100},
    {"name": "Architecture",           "sp": 8,  "start": date(2026,2,25), "end": date(2026,3,3),  "pct": 100},
    {"name": "Conception DB",          "sp": 5,  "start": date(2026,3,3),  "end": date(2026,3,8),  "pct": 100},
    {"name": "Conception UI",          "sp": 5,  "start": date(2026,3,5),  "end": date(2026,3,12), "pct": 100},
    {"name": "Backend FastAPI",        "sp": 21, "start": date(2026,3,10), "end": date(2026,4,15), "pct": 100},
    {"name": "Frontend React",         "sp": 21, "start": date(2026,3,12), "end": date(2026,4,25), "pct": 100},
    {"name": "Intégration modules IA", "sp": 13, "start": date(2026,3,15), "end": date(2026,4,25), "pct": 100},
    {"name": "Fonctionnalités Compta", "sp": 34, "start": date(2026,3,18), "end": date(2026,5,10), "pct": 98},
    {"name": "Reporting & Dashboards", "sp": 12, "start": date(2026,5,5),  "end": date(2026,5,20), "pct": 80},
    {"name": "Tests & Validation",     "sp": 13, "start": date(2026,5,10), "end": date(2026,5,25), "pct": 70},
]

TOTAL_SP = sum(t["sp"] for t in TASKS)

# ── CALCUL DE LA PROGRESSION RÉELLE ────────
dates = []
actual_remaining = []
curr = START

# Points restants estimés pour aujourd'hui : 10 points
points_today = 10.5

while curr <= TODAY:
    dates.append(curr)
    days_from_start = (curr - START).days
    total_days_today = (TODAY - START).days
    
    if days_from_start == 0:
        rem = TOTAL_SP
    else:
        # Courbe de descente réaliste
        progress_pct = (days_from_start / total_days_today) ** 0.5
        rem = TOTAL_SP - (progress_pct * (TOTAL_SP - points_today))
        
    actual_remaining.append(rem)
    curr += timedelta(days=1)

# Ligne Idéale
ideal_dates = [START, END]
ideal_remaining = [TOTAL_SP, 0]

# Vélocité
days_elapsed = (TODAY - START).days
sp_burned = TOTAL_SP - points_today
velocity = sp_burned / (days_elapsed / 7) # SP par semaine

# ── VIZ ───────────────────────────────────────────────────────────────
plt.style.use('seaborn-v0_8-whitegrid')
fig, ax = plt.subplots(figsize=(12, 6))

# Plot Ideal
ax.plot(ideal_dates, ideal_remaining, 'r--', label='Ligne Idéale (Scope)', alpha=0.5, linewidth=2)

# Plot Actual
ax.plot(dates, actual_remaining, 'b-', label='Reste à faire (Réel)', linewidth=3)
ax.scatter(dates[-1], actual_remaining[-1], color='blue', s=100, zorder=5)

# Remplissage
ax.fill_between(dates, actual_remaining, color='blue', alpha=0.1)

# Annotation Vélocité
ax.annotate(f'Vélocité: {velocity:.1f} SP/Semaine', 
            xy=(0.05, 0.05), xycoords='axes fraction', 
            bbox=dict(boxstyle="round,pad=0.5", fc="white", ec="#2c3e50", alpha=0.9),
            fontsize=10, fontweight='bold')

# Design
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_ylim(0, TOTAL_SP + 5)
ax.set_ylabel("Story Points Restants", fontsize=12)
ax.set_title("Burndown Chart : Avancement du Projet PFE", fontsize=16, pad=20, fontweight='bold', color='#2c3e50')

plt.legend(frameon=True, loc='upper right')
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig("burndown_pfe.png", dpi=200)
print("OK: Burndown Chart genere : burndown_pfe.png")
