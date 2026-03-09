"""
main.py — Application FastAPI "comptafacile"
Architecture Multi-Cabinet / Multi-Agents / Multi-Sociétés
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

# ── Importation des routeurs (Logique métier par domaine) ────────────────
from routes.auth import router as auth_router
from routes.admin import router as admin_router
from routes.pipeline import router as pipeline_router
from routes.pcm import router as pcm_router
from routes.societes import router as societes_router
from routes.mappings import router as mappings_router
from routes.avoirs import router as avoirs_router
from routes.immobilisations import router as immobilisations_router
from routes.journaux import router as journaux_router
from routes.paie import router as paie_router
from routes.employes import router as employes_router
from routes.releves import router as releves_router

# Legacy routers (conservés pour compatibilité)
try:
    from routes.factures import router as factures_router
    _has_factures = True
except Exception:
    _has_factures = False


app = FastAPI(
    title="comptafacile — API",
    description="Pipeline OCR + Gemini → Classification PCM → Écritures comptables marocaines\nArchitecture Multi-Cabinet avec Agents et Sociétés",
    version="2.1.0",
    redirect_slashes=False,  # Désactivé pour éviter les redirects 307 avec hostname Docker interne
)

# ── Gestion du CORS (Cross-Origin Resource Sharing) ────────────────────
# Permet au frontend (React) de communiquer avec l'API même s'ils sont sur des ports différents
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En développement, on autorise toutes les sources
    allow_credentials=True,
    allow_methods=["*"], # Autorise toutes les méthodes (GET, POST, PUT, DELETE)
    allow_headers=["*"], # Autorise tous les en-têtes (Authorization, etc.)
)

# ── Routers d'authentification et administration ──────────────────────
app.include_router(auth_router)   # /auth/login, /auth/register, /auth/select-societe
app.include_router(admin_router)  # /admin/cabinets, /admin/agents, /admin/societes

# ── Routers principaux ──────────────────────────────────────────────
app.include_router(pipeline_router)         # /factures/* pipeline complet
app.include_router(pcm_router)              # /pcm/accounts, /pcm/tva-rates
app.include_router(societes_router)         # /societes/*
app.include_router(mappings_router)         # /mappings/*
app.include_router(avoirs_router)           # /avoirs/*
app.include_router(immobilisations_router)  # /immobilisations/*
app.include_router(journaux_router)         # /journaux/*
app.include_router(paie_router)             # /paie/*
app.include_router(employes_router)         # /employes/*
app.include_router(releves_router)          # /releves/*


# ── Routers legacy ──────────────────────────────────────────
if _has_factures:
    app.include_router(factures_router)

# ── Servir les uploads ──────────────────────────────────────
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def home():
    return {
        "message": "comptafacile API v2.0",
        "docs": "/docs",
        "pipeline": [
            "1. POST /factures/upload           -> Téléchargement du fichier",
            "2. POST /factures/{id}/extract     -> OCR + Intelligence Artificielle (Gemini)",
            "3. POST /factures/{id}/classify    -> Classification automatique (PCM)",
            "4. POST /factures/{id}/generate-entries -> Génération des écritures comptables",
            "5. POST /factures/{id}/validate    -> Validation finale et enregistrement",
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
