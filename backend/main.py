"""
main.py — Application FastAPI "Comptabilité Zéro Saisie"
Architecture Multi-Cabinet / Multi-Agents / Multi-Sociétés
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path

from routes.auth import router as auth_router  # NOUVEAU
from routes.admin import router as admin_router  # NOUVEAU
from routes.pipeline import router as pipeline_router
from routes.pcm import router as pcm_router
from routes.societes import router as societes_router

# Legacy routers (conservés pour compatibilité)
try:
    from routes.factures import router as factures_router
    _has_factures = True
except Exception:
    _has_factures = False

try:
    from routes.ecritures import router as ecritures_router
    _has_ecritures = True
except Exception:
    _has_ecritures = False


app = FastAPI(
    title="Comptabilité Zéro Saisie — API",
    description="Pipeline OCR + Gemini → Classification PCM → Écritures comptables marocaines\nArchitecture Multi-Cabinet avec Agents et Sociétés",
    version="2.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers d'authentification et administration ──────────────────────
app.include_router(auth_router)   # /auth/login, /auth/register, /auth/select-societe
app.include_router(admin_router)  # /admin/cabinets, /admin/agents, /admin/societes

# ── Routers principaux ──────────────────────────────────────
app.include_router(pipeline_router)   # /factures/* pipeline complet
app.include_router(pcm_router)        # /pcm/accounts, /pcm/tva-rates
app.include_router(societes_router)   # /societes/*

# ── Routers legacy ──────────────────────────────────────────
if _has_factures:
    app.include_router(factures_router)
if _has_ecritures:
    app.include_router(ecritures_router)

# ── Servir les uploads ──────────────────────────────────────
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")


@app.get("/")
def home():
    return {
        "message": "Comptabilité Zéro Saisie API v2.0",
        "docs": "/docs",
        "pipeline": [
            "POST /factures/upload",
            "POST /factures/{id}/extract",
            "POST /factures/{id}/classify",
            "POST /factures/{id}/generate-entries",
            "POST /factures/{id}/validate",
        ]
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}
