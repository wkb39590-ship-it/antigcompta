

"""
Diagramme de Gantt — PFE Zéro Saisie Comptable
Période : 02/02/2026 → 31/05/2026
Aujourd'hui : 27/02/2026
(Sans Excel / Sans pandas)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from datetime import date, timedelta

# ── CONFIG ────────────────────────────────────────────────────────────────
TODAY = date(2026, 2, 27)   # ✅ AUJOURD'HUI
START = date(2026, 2, 2)
END   = date(2026, 5, 31)

# ── DONNÉES (phases + tâches, % avancement) ───────────────────────────────
PHASES = [
    {
        "name": "Phase 1 — Compréhension Métier & Cadrage",
        "color": "#2E75B6",
        "tasks": [
            ("1.1", "Réunion lancement & recueil des besoins",          date(2026,2,2),  date(2026,2,4),  100),
            ("1.2", "Étude domaine comptable marocain (PCM, DGI, TVA)", date(2026,2,2),  date(2026,2,9),  100),
            ("1.3", "Analyse des processus existants (As-Is)",          date(2026,2,9),  date(2026,2,13), 100),
            ("1.4", "Définition périmètre fonctionnel",                date(2026,2,13), date(2026,2,18), 100),
            ("1.5", "Rédaction cahier des charges",                    date(2026,2,16), date(2026,2,20), 100),
        ],
    },
    {
        "name": "Phase 2 — Analyse & Conception",
        "color": "#70AD47",
        "tasks": [
            ("2.1", "Cas d'utilisation (Use Cases)",                   date(2026,2,20), date(2026,2,23), 100),
            ("2.2", "UML — Diagramme de classes",                      date(2026,2,20), date(2026,2,24), 100),
            ("2.3", "UML — Diagrammes de séquence",                    date(2026,2,23), date(2026,2,25), 100),
            ("2.4", "Architecture multi-tenant (DB & API)",            date(2026,2,23), date(2026,2,25), 100),
            ("2.5", "Maquettes UI/UX — Wireframes & Figma",            date(2026,2,24), date(2026,2,25), 100),
            ("2.6", "Validation conception avec tuteur",               date(2026,2,25), date(2026,2,25), 100),
        ],
    },
    {
        "name": "Phase 3 — Développement Backend & IA",
        "color": "#ED7D31",
        "tasks": [
            ("3.1", "Setup Docker, FastAPI, PostgreSQL",               date(2026,2,26), date(2026,2,27), 100),
            ("3.2", "Modèles DB multi-tenant & JWT Auth",              date(2026,3,4),  date(2026,3,13), 0),
            ("3.3", "Pipeline PDF → images (conversion auto)",         date(2026,3,11), date(2026,3,18), 0),
            ("3.4", "Intégration Gemini — Extraction IA",              date(2026,3,16), date(2026,3,27), 0),
            ("3.5", "Fallback Tesseract OCR",                          date(2026,3,25), date(2026,4,1),  0),
            ("3.6", "Classification PCM (Supplier Mapping)",           date(2026,3,30), date(2026,4,9),  0),
            ("3.7", "Feedback Loop & apprentissage continu",           date(2026,4,7),  date(2026,4,15), 0),
            ("3.8", "Validation fiscale : ICE, TVA, anti-doublons",    date(2026,4,14), date(2026,4,22), 0),
        ],
    },
    {
        "name": "Phase 4 — Développement Frontend",
        "color": "#FFC000",
        "tasks": [
            ("4.1", "Setup React + Tailwind + Design System",          date(2026,3,18), date(2026,3,20), 0),
            ("4.2", "Interface Agent : import, validation",            date(2026,3,20), date(2026,4,3),  0),
            ("4.3", "Interface Admin Cabinet",                         date(2026,4,1),  date(2026,4,10), 0),
            ("4.4", "Interface Super-Admin",                           date(2026,4,9),  date(2026,4,16), 0),
            ("4.5", "Module export données (CSV / Excel)",             date(2026,4,15), date(2026,4,22), 0),
        ],
    },
    {
        "name": "Phase 5 — Tests & Validation",
        "color": "#C00000",
        "tasks": [
            ("5.1", "Tests unitaires Backend (API, modèles)",          date(2026,4,22), date(2026,4,29), 0),
            ("5.2", "Tests intégration Pipeline IA (factures réelles)",date(2026,4,27), date(2026,5,6),  0),
            ("5.3", "Tests UI/UX & recette fonctionnelle",             date(2026,5,4),  date(2026,5,11), 0),
            ("5.4", "Tests sécurité isolation multi-tenant",           date(2026,5,6),  date(2026,5,13), 0),
            ("5.5", "Corrections bugs & optimisation",                 date(2026,5,11), date(2026,5,19), 0),
        ],
    },
    {
        "name": "Phase 6 — Déploiement & Documentation",
        "color": "#7030A0",
        "tasks": [
            ("6.1", "Déploiement Docker Compose (prod)",               date(2026,5,18), date(2026,5,22), 0),
            ("6.2", "Documentation technique (API, UML)",              date(2026,4,28), date(2026,5,20), 0),
            ("6.3", "Rédaction rapport PFE complet",                   date(2026,5,11), date(2026,5,26), 0),
            ("6.4", "Préparation présentation soutenance",             date(2026,5,25), date(2026,5,29), 0),
            ("6.5", "Livraison finale & Soutenance",                   date(2026,5,29), date(2026,5,31), 0),
        ],
    },
]

# ── APLATIR LES LIGNES (phase + tâches) ────────────────────────────────────
rows = []  # (label, start, end, pct or None, color, is_phase)
for ph in PHASES:
    ph_s = min(t[2] for t in ph["tasks"])
    ph_e = max(t[3] for t in ph["tasks"])
    rows.append((ph["name"], ph_s, ph_e, None, ph["color"], True))
    for num, name, ts, te, pct in ph["tasks"]:
        rows.append((f"  {num}  {name}", ts, te, pct, ph["color"], False))

n_rows = len(rows)

# ── FIGURE (fond blanc) ────────────────────────────────────────────────────
fig_h = max(10, n_rows * 0.33 + 2.5)
fig, ax = plt.subplots(figsize=(20, fig_h))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

# Axe temps
ax.set_xlim(mdates.date2num(START), mdates.date2num(END + timedelta(days=1)))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=1))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
plt.setp(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)

# Axe y
ax.set_ylim(-0.5, n_rows - 0.5)
ax.set_yticks(range(n_rows))
ax.set_yticklabels([r[0] for r in rows], fontsize=8)
ax.invert_yaxis()

# Grille
ax.xaxis.grid(True, linestyle="--", linewidth=0.5, alpha=0.35)
ax.yaxis.grid(False)
ax.set_axisbelow(True)

# Barres
for i, (label, ts, te, pct, color, is_phase) in enumerate(rows):
    x_s = mdates.date2num(ts)
    x_e = mdates.date2num(te + timedelta(days=1))
    width = x_e - x_s
    h = 0.55 if is_phase else 0.48

    if is_phase:
        ax.barh(i, width, left=x_s, height=h, color=color, alpha=0.18, linewidth=0)
        ax.barh(i, width, left=x_s, height=h, color="none", edgecolor=color, linewidth=1.5)
    else:
        ax.barh(i, width, left=x_s, height=h, color=color, alpha=0.15, linewidth=0)
        done_w = width * (pct / 100.0)
        ax.barh(i, done_w, left=x_s, height=h, color=color, alpha=0.70, linewidth=0)
        ax.text(x_e + 0.2, i, f"{pct}%", va="center", fontsize=8)

# Ligne aujourd’hui
today_x = mdates.date2num(TODAY)
ax.axvline(today_x, color="red", linewidth=2)
ax.text(today_x + 0.3, -0.35, f"Aujourd'hui {TODAY.strftime('%d/%m/%Y')}",
        color="red", fontsize=9, fontweight="bold", va="top")

# Titre
ax.set_title(
    "Diagramme de Gantt — PFE Zéro Saisie Comptable (02 Fév → 31 Mai 2026)",
    fontsize=14, fontweight="bold", loc="left"
)

# Légende
legend_elements = [
    mpatches.Patch(facecolor="gray", alpha=0.15, label="Planifié"),
    mpatches.Patch(facecolor="gray", alpha=0.70, label="Avancement"),
]
ax.legend(handles=legend_elements, loc="lower right", frameon=True)

plt.tight_layout()

# Sauvegarde (dans le même dossier que le script)
out_file = "gantt_pfe.png"
plt.savefig(out_file, dpi=200, bbox_inches="tight")
print(f"✅ Diagramme sauvegardé : {out_file}")

plt.show()