# -*- coding: utf-8 -*-
"""
gantt_pfe.py — Diagramme de Gantt PFE "Comptabilité Zéro Saisie"
Stage de 4 mois : 02/02/2026 → 01/06/2026
Aujourd'hui : Semaine 4 (24/02/2026)
Scope : Fonctionnalités côté Agent uniquement (pas d'interface Admin)
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from datetime import datetime

# ──────────────────────────────────────────
# PARAMÈTRES PROJET
# ──────────────────────────────────────────
project_start = datetime(2026, 2, 2)   # Début de stage officiel
project_end   = datetime(2026, 6, 1)   # Fin de stage officiel
today         = datetime(2026, 2, 24)  # Semaine 4

# ──────────────────────────────────────────
# DÉFINITION DES PHASES ET COULEURS
# ──────────────────────────────────────────
PHASE_COLORS = {
    "Analyse & Conception":  "#6C63FF",   # Violet
    "Infrastructure":        "#3B82F6",   # Bleu
    "Backend Auth":          "#0EA5E9",   # Bleu ciel
    "Pipeline IA & OCR":     "#10B981",   # Vert
    "Classification & IA":   "#34D399",   # Vert clair
    "Frontend Agent":        "#F59E0B",   # Orange
    "Validation Comptable":  "#EF4444",   # Rouge
    "Tests & Stabilisation": "#8B5CF6",   # Violet foncé
    "Mémoire & Soutenance":  "#6B7280",   # Gris
}

# ──────────────────────────────────────────
# TÂCHES — Avancement basé sur S4 réelle
# (✅ = terminé, 🔄 = en cours, ⏳ = à venir)
# ──────────────────────────────────────────
tasks = [
    # ══════════════════════════════
    # PHASE 1 — Analyse & Conception (S1–S3, 100%)
    # ══════════════════════════════
    {"phase": "Analyse & Conception",
     "task": "Compréhension métier & processus comptable cabinet",
     "start": "2026-02-02", "end": "2026-02-10", "progress": 100},

    {"phase": "Analyse & Conception",
     "task": "Étude PCM/CGNC + règles fiscales DGI (ICE, TVA, TTC)",
     "start": "2026-02-04", "end": "2026-02-14", "progress": 100},

    {"phase": "Analyse & Conception",
     "task": "Conception architecture globale (React + FastAPI + PostgreSQL)",
     "start": "2026-02-09", "end": "2026-02-18", "progress": 100},

    {"phase": "Analyse & Conception",
     "task": "Modélisation BDD multi-tenant (Cabinet, Agent, Société, Facture…)",
     "start": "2026-02-11", "end": "2026-02-20", "progress": 100},

    {"phase": "Analyse & Conception",
     "task": "Diagrammes UML : Use Case, Séquence, Classes",
     "start": "2026-02-12", "end": "2026-02-26", "progress": 65},

    # ══════════════════════════════
    # PHASE 2 — Infrastructure (S2–S3, 100%)
    # ══════════════════════════════
    {"phase": "Infrastructure",
     "task": "Setup Docker + Docker Compose + PostgreSQL 15",
     "start": "2026-02-10", "end": "2026-02-17", "progress": 100},

    {"phase": "Infrastructure",
     "task": "Init projet FastAPI + SQLAlchemy + Alembic (migrations)",
     "start": "2026-02-12", "end": "2026-02-19", "progress": 100},

    {"phase": "Infrastructure",
     "task": "Init frontend React 18 + TypeScript + Vite",
     "start": "2026-02-14", "end": "2026-02-21", "progress": 100},

    # ══════════════════════════════
    # PHASE 3 — Backend Auth (S2–S3, 100%)
    # ══════════════════════════════
    {"phase": "Backend Auth",
     "task": "Auth JWT : login / logout / refresh token",
     "start": "2026-02-10", "end": "2026-02-18", "progress": 100},

    {"phase": "Backend Auth",
     "task": "Gestion rôles : isolation Agent ↔ Société ↔ Cabinet",
     "start": "2026-02-14", "end": "2026-02-22", "progress": 100},

    {"phase": "Backend Auth",
     "task": "CRUD : Agents, Sociétés, Cabinets + endpoints REST",
     "start": "2026-02-16", "end": "2026-02-24", "progress": 100},

    # ══════════════════════════════
    # PHASE 4 — Pipeline IA & OCR (S2–S4, 100%)
    # ══════════════════════════════
    {"phase": "Pipeline IA & OCR",
     "task": "Upload PDF/Image + validation format",
     "start": "2026-02-13", "end": "2026-02-19", "progress": 100},

    {"phase": "Pipeline IA & OCR",
     "task": "Conversion multi-pages PDF → images (pdf2image, 10 pages max)",
     "start": "2026-02-17", "end": "2026-02-24", "progress": 100},

    {"phase": "Pipeline IA & OCR",
     "task": "Extraction Gemini Vision : ICE, Date, HT, TVA, TTC, Fournisseur",
     "start": "2026-02-14", "end": "2026-02-24", "progress": 100},

    {"phase": "Pipeline IA & OCR",
     "task": "Fallback OCR Tesseract (documents dégradés / scan faible qualité)",
     "start": "2026-02-18", "end": "2026-02-24", "progress": 100},

    # ══════════════════════════════
    # PHASE 5 — Classification & IA Apprenante (S3–S4, 100%)
    # ══════════════════════════════
    {"phase": "Classification & IA",
     "task": "Classification PCM automatique (mapping règles métier)",
     "start": "2026-02-17", "end": "2026-02-24", "progress": 100},

    {"phase": "Classification & IA",
     "task": "Feedback Loop : SupplierMapping (apprentissage corrections agents)",
     "start": "2026-02-19", "end": "2026-02-25", "progress": 100},

    {"phase": "Classification & IA",
     "task": "Détection doublons (ICE + Date + TTC) — Sécurité anti re-saisie",
     "start": "2026-02-20", "end": "2026-02-25", "progress": 100},

    # ══════════════════════════════
    # PHASE 6 — Frontend Agent (S3–S5)
    # ══════════════════════════════
    {"phase": "Frontend Agent",
     "task": "Design Glassmorphism Premium + système de couleurs Aurora",
     "start": "2026-02-14", "end": "2026-02-22", "progress": 100},

    {"phase": "Frontend Agent",
     "task": "Interface : Login + sélection Cabinet/Société",
     "start": "2026-02-15", "end": "2026-02-22", "progress": 100},

    {"phase": "Frontend Agent",
     "task": "Dashboard Agent : upload facture + affichage résultats extraction",
     "start": "2026-02-18", "end": "2026-02-28", "progress": 90},

    {"phase": "Frontend Agent",
     "task": "Historique des factures : filtres, pagination, statuts",
     "start": "2026-02-21", "end": "2026-03-05", "progress": 80},

    {"phase": "Frontend Agent",
     "task": "Page Profil Agent : stats personnelles + infos Cabinet",
     "start": "2026-02-20", "end": "2026-02-28", "progress": 100},

    {"phase": "Frontend Agent",
     "task": "Interface Répertoire Fournisseurs (Feedback Loop UI)",
     "start": "2026-02-22", "end": "2026-03-05", "progress": 100},

    # ══════════════════════════════
    # PHASE 7 — Validation Comptable (S5–S8)
    # ══════════════════════════════
    {"phase": "Validation Comptable",
     "task": "Workflow facture : DRAFT → EXTRACTED → VALIDATED",
     "start": "2026-02-28", "end": "2026-03-20", "progress": 0},

    {"phase": "Validation Comptable",
     "task": "Contrôles DGI : ICE valide, TVA cohérente, N° facture unique",
     "start": "2026-03-10", "end": "2026-03-28", "progress": 0},

    {"phase": "Validation Comptable",
     "task": "Génération écriture comptable normalisée (débit / crédit PCM)",
     "start": "2026-03-20", "end": "2026-04-10", "progress": 0},

    {"phase": "Validation Comptable",
     "task": "Export récapitulatif PDF par période (rapports mensuels)",
     "start": "2026-04-05", "end": "2026-04-25", "progress": 0},

    # ══════════════════════════════
    # PHASE 8 — Tests & Stabilisation (S8–S14)
    # ══════════════════════════════
    {"phase": "Tests & Stabilisation",
     "task": "Tests unitaires backend (pytest) — routes & services",
     "start": "2026-04-20", "end": "2026-05-05", "progress": 0},

    {"phase": "Tests & Stabilisation",
     "task": "Tests E2E frontend + scénarios utilisateur complets",
     "start": "2026-04-28", "end": "2026-05-15", "progress": 0},

    {"phase": "Tests & Stabilisation",
     "task": "Optimisation performance (requêtes BDD, prompts Gemini, cache)",
     "start": "2026-05-01", "end": "2026-05-20", "progress": 0},

    {"phase": "Tests & Stabilisation",
     "task": "Correction bugs finaux + revue sécurité (JWT, injection SQL)",
     "start": "2026-05-10", "end": "2026-05-25", "progress": 0},

    # ══════════════════════════════
    # PHASE 9 — Mémoire & Soutenance (S4→S16)
    # ══════════════════════════════
    {"phase": "Mémoire & Soutenance",
     "task": "Rédaction mémoire PFE (état de l'art, conception, réalisation)",
     "start": "2026-02-24", "end": "2026-05-25", "progress": 10},

    {"phase": "Mémoire & Soutenance",
     "task": "Finalisation documentation technique + fiches",
     "start": "2026-05-10", "end": "2026-05-28", "progress": 0},

    {"phase": "Mémoire & Soutenance",
     "task": "Préparation présentation soutenance (slides + démonstration)",
     "start": "2026-05-20", "end": "2026-06-01", "progress": 0},
]

# ──────────────────────────────────────────
# PRÉPARATION DES DONNÉES
# ──────────────────────────────────────────
for t in tasks:
    t["start_dt"] = datetime.fromisoformat(t["start"])
    t["end_dt"]   = datetime.fromisoformat(t["end"])

# NE PAS trier pour garder l'ordre des phases
n = len(tasks)

# ──────────────────────────────────────────
# FIGURE
# ──────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 12))
fig.patch.set_facecolor("#0F172A")
ax.set_facecolor("#1E293B")

# Colormap avancement : Rouge → Jaune → Vert
cmap = plt.cm.RdYlGn
norm = Normalize(vmin=0, vmax=100)

for i, t in enumerate(tasks):
    start = mdates.date2num(t["start_dt"])
    end   = mdates.date2num(t["end_dt"])
    width = end - start

    phase_color = PHASE_COLORS.get(t["phase"], "#888888")
    progress    = t["progress"]

    # Barre fond (grisé = non fait)
    ax.barh(i, width, left=start, height=0.55,
            color="#334155", edgecolor="#1E293B", linewidth=0.5)

    # Barre pleine (progression)
    if progress > 0:
        ax.barh(i, width * (progress / 100), left=start, height=0.55,
                color=phase_color, edgecolor="#1E293B", linewidth=0.5,
                alpha=0.9)

    # Pourcentage affiché dans la barre
    if progress == 100:
        label = "✓ 100%"
    elif progress > 0:
        label = f"{progress}%"
    else:
        label = ""
    if label:
        center = start + (width * (progress / 100)) / 2
        ax.text(center, i, label, va="center", ha="center",
                fontsize=6.5, color="white", fontweight="bold")

# ──────────────────────────────────────────
# AXES
# ──────────────────────────────────────────
ax.set_yticks(range(n))
ax.set_yticklabels([t["task"] for t in tasks], fontsize=8.5, color="#E2E8F0")
ax.invert_yaxis()

ax.xaxis_date()
ax.set_xlim(mdates.date2num(project_start), mdates.date2num(project_end))
ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))  # tous les 14 jours
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax.tick_params(axis="x", colors="#94A3B8", labelsize=8)
plt.setp(ax.get_xticklabels(), rotation=35, ha="right")

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.spines["left"].set_color("#334155")
ax.spines["bottom"].set_color("#334155")

# ──────────────────────────────────────────
# LIGNE "AUJOURD'HUI" — Semaine 4
# ──────────────────────────────────────────
today_num = mdates.date2num(today)
ax.axvline(today_num, color="#F97316", linewidth=2, linestyle="--", zorder=5)
ax.text(today_num + 0.3, -0.8, "← Auj. S4", color="#F97316",
        fontsize=8.5, fontweight="bold", va="center")

# ──────────────────────────────────────────
# GRILLE
# ──────────────────────────────────────────
ax.grid(axis="x", linestyle=":", alpha=0.25, color="#94A3B8")
ax.grid(axis="y", linestyle=":", alpha=0.10, color="#94A3B8")

# ──────────────────────────────────────────
# LÉGENDE DES PHASES
# ──────────────────────────────────────────
legend_patches = [
    mpatches.Patch(color=color, label=phase)
    for phase, color in PHASE_COLORS.items()
]
ax.legend(handles=legend_patches, loc="lower right",
          fontsize=7.5, framealpha=0.2,
          facecolor="#1E293B", edgecolor="#334155",
          labelcolor="#E2E8F0", ncol=2)

# ──────────────────────────────────────────
# TITRES
# ──────────────────────────────────────────
ax.set_title(
    "Diagramme de Gantt — PFE · Comptabilité Zéro Saisie\n"
    "Stage 4 mois : 02 Fév → 01 Juin 2026  |  Scope : Interface Agent (hors Admin)",
    fontsize=13, color="white", fontweight="bold", pad=15
)
ax.set_xlabel("Calendrier (par semaine)", fontsize=9, color="#94A3B8", labelpad=8)

# ──────────────────────────────────────────
# COLORBAR AVANCEMENT
# ──────────────────────────────────────────
sm = ScalarMappable(norm=norm, cmap=cmap)
sm.set_array([])
cbar = plt.colorbar(sm, ax=ax, pad=0.01, fraction=0.012)
cbar.set_label("Avancement (%)", color="#94A3B8", fontsize=8)
cbar.ax.yaxis.set_tick_params(color="#94A3B8")
plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#94A3B8", fontsize=7.5)

# ──────────────────────────────────────────
# ANNOTATION SEMAINES
# ──────────────────────────────────────────
week_starts = [
    datetime(2026, 2,  2),   # S1
    datetime(2026, 2,  9),   # S2
    datetime(2026, 2, 16),   # S3
    datetime(2026, 2, 23),   # S4  ← maintenant
    datetime(2026, 3,  2),   # S5
]
for i, ws in enumerate(week_starts, 1):
    ax.axvline(mdates.date2num(ws), color="#334155", linewidth=0.8, linestyle="-", alpha=0.5)
    ax.text(mdates.date2num(ws) + 0.2, n - 0.3,
            f"S{i}", fontsize=6.5, color="#64748B", va="bottom")

plt.tight_layout()
plt.savefig("gantt_pfe_semaine4.png", dpi=150, bbox_inches="tight",
            facecolor=fig.get_facecolor())
print("✅ Gantt sauvegardé : gantt_pfe_semaine4.png")
plt.show()