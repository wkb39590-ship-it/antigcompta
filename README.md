# 📊 Zéro Saisie Comptable

> **Vers une comptabilité « Zéro Saisie »** : Développement d’une plateforme intelligente d’extraction de données par IA pour la génération automatique d'écritures comptables. Projet de Fin d'Études (PFE) développé par Wissal KB.

![Mise en cache du PFE](frontend/public/favicon.ico) <!-- Remplace par un screenshot de ton projet si tu en as un -->

## 📑 Sommaire
- [À Propos](#-à-propos)
- [Fonctionnalités Principales](#-fonctionnalités-principales)
- [Technologies Utilisées](#-technologies-utilisées)
- [Architecture du Projet](#-architecture-du-projet)
- [🚀 Guide d'Installation (Docker)](#-guide-dinstallation-docker)
- [Accès à l'Application](#-accès-à-lapplication)
- [Structure des Dossiers](#-structure-des-dossiers)

---

## 💡 À Propos

La saisie comptable manuelle dans les cabinets marocains est une activité chronophage, sujette aux erreurs et à faible valeur ajoutée. Ce projet propose une plateforme web **multi-tenante** capable d'automatiser ce processus de A à Z. 

En s'appuyant sur l'Intelligence Artificielle (**Google Gemini 2.0**) et un moteur de règles comptables robuste (PCM - Plan Comptable Marocain), l'application extrait automatiquement les données des factures PDF/Images, s'assure de la conformité DGI, et génère instantanément les écritures prêtes à être exportées.

---

## ✨ Fonctionnalités Principales

- **Extraction IA Multimodale** : Lecture de factures (PDF/Images) complexes via Gemini (Dates, Montants HT/TVA/TTC, Fournisseur, ICE).
- **Génération Automatique (PCM)** : Suggestion intelligente des comptes comptables et création des lignes de débit/crédit.
- **Vérifications DGI Intégrées** : Validation automatique du format de l'ICE et cohérence mathématique des taux de TVA.
- **Gestion Multi-Tenant :** Espace "Super Admin" pour gérer plusieurs cabinets d'expertise comptable, et "Admin Cabinet" pour gérer les sociétés (clients).
- **Feedback Loop IA** : Apprentissage continu des choix d'imputation comptable effectués par l'agent.
- **Système d'Audit Complet** : Suivi de toutes les actions réalisées sur l'interface par un journal d'historique (Audit Trail).

---

## 🛠 Technologies Utilisées

Ce projet repose sur une architecture moderne séparant clairement le Frontend, le Backend et les données :

* **Frontend** : React.js, TypeScript, Vite, Tailwind CSS (Glassmorphism & Design System Premium)
* **Backend** : Python 3, FastAPI, SQLAlchemy, Alembic
* **Intelligence Artificielle** : Google Gemini 2.0 Flash API (Vision & NLP)
* **Base de Données** : PostgreSQL 15
* **Déploiement** : Docker & Docker Compose

---

## 📐 Architecture du Projet

L'application est structurée de manière micro-modulaire (Bien que ce soit un monolithe modulaire) :

* **Frontend (`/frontend`)** : Consomme les APIs du backend. Divisé en composants réutilisables, pages métiers, et hooks personnalisés de sécurité.
* **Backend (`/backend`)** : Expose l'API REST via FastAPI. Divisé en couches (`routes/`, `services/`, `models.py`, `schemas.py`) pour une parfaite séparation entre la logique métier IA et la logique d'API.

---

## 🚀 Guide d'Installation (Docker)

Le projet est conteneurisé. Son déploiement local prend moins de 5 minutes grâce à Docker.

### Prérequis
- Docker et Docker Compose installés sur votre machine.
- Une clé API Google Gemini valide.

### Étape 1 : Configuration
Clonez le projet, puis créez un fichier `.env` à la racine principale (ou dans le dossier backend) avec vos variables d'environnement.

```env
# backend/.env
DATABASE_URL=postgresql+psycopg://admin:admin123@db:5432/compta_db
GEMINI_API_KEY=votre_cle_api_gemini_ici
SECRET_KEY=votre_cle_secrete_jwt
```

### Étape 2 : Lancement
À la racine du projet, exécutez simplement la commande Docker Compose :

```bash
docker-compose up --build -d
```

Cette commande va :
1. Démarrer la base de données PostgreSQL (`db`).
2. Construire et lancer l'API FastAPI (`backend`) tout en exécutant les scripts de seed (`seed_pcm.py`).
3. Construire et lancer l'interface React (`frontend`).

---

## 🌐 Accès à l'Application

Une fois les conteneurs lancés, les services sont disponibles sur votre machine locale aux adresses suivantes :

| Service | URL | Rôle |
| :--- | :--- | :--- |
| **Interface Agent / Admin** | [http://localhost:3333](http://localhost:3333) | Plateforme Web UI (React) |
| **API Backend** | [http://localhost:8888](http://localhost:8888) | Point de terminaison principal |
| **Documentation API (OAS)** | [http://localhost:8888/docs](http://localhost:8888/docs) | Swagger interactif de FastAPI |
| **Base de Données** | `localhost:5454` | Accès direct PostgreSQL (DB: `compta_db`) |

---

## 📂 Structure des Dossiers

```text
📁 Zéro Saisie Comptable/
├── 📁 backend/                # API Python / FastAPI
│   ├── 📁 alembic/            # Migrations de base de données
│   ├── 📁 routes/             # Endpoints API (Séparés par métier)
│   ├── 📁 services/           # Logique métier, Intelligence Artificielle & OCR
│   ├── main.py                # Point d'entrée de l'API
│   └── models.py / schemas.py # Modèles SQLAlchemy et validation Pydantic
├── 📁 frontend/               # Application React / Vite
│   ├── 📁 src/
│   │   ├── 📁 components/     # Composants UI
│   │   ├── 📁 pages/          # Vues principales de l'application
│   │   └── 📁 services/       # Appels API vers le backend
├── 📁 database/               # Logs, seeds ou scripts utiles divers
├── docker-compose.yml         # Fichier d'orchestration Docker
└── FICHE_DESCRIPTIVE.md       # Synthèse complète du projet de fin d'études
```

---
*Fait avec ❤️ par Wissal KB dans le cadre du Projet de Fin d'Études (2026).*
