# 📊 Zéro Saisie Comptable

<div align="center">

**Vers une comptabilité « Zéro Saisie »** 
*Plateforme SAAS intelligente d’extraction de données multi-modales par Intelligence Artificielle (OCR/NLP) pour l'automatisation de la génération d'écritures comptables.*

Projet de Fin d'Études (PFE) développé par **Wissal KB** (2026).

</div>

---

## 📑 Sommaire
1. [À Propos du Projet](#-a-propos-du-projet)
2. [Enjeux & Problématique](#-enjeux--problématique)
3. [Architecture Système & Diagramme](#-architecture-système-et-flux-de-données)
4. [Fonctionnalités Détaillées](#-fonctionnalités-détaillées)
5. [Stack Technique](#-stack-technique)
6. [Guide de Déploiement Local (Docker)](#-guide-de-déploiement-local-docker)
7. [Structure Complète du Code](#-structure-du-code-source)

---

## 💡 À Propos du Projet

Dans les cabinets d'expertise comptable, la saisie manuelle des factures est un goulot d'étranglement majeur, source d'erreurs (saisie erronée d'ICE, mauvaise imputation TVA) et sans valeur ajoutée intellectuelle. 

**Zéro Saisie** est une application web métier multi-tenante développée pour pallier ce problème. En exploitant la puissance du LLM **Google Gemini 2.0 Flash** pour la reconnaissance visuelle (OCR) et sémantique, la plateforme lit, interprète, vérifie la conformité fiscale (DGI) et génère instantanément l'écriture comptable (Plan Comptable Marocain - PCM).

---

## 🎯 Enjeux & Problématique

*   **Réduction des Erreurs :** Éviter les erreurs humaines sur les taux de TVA et la saisie de l'Identifiant Commun d'Entreprise (ICE).
*   **Conformité Fiscale :** Aligner automatiquement les processus avec les réglementations de la Direction Générale des Impôts (DGI) au Maroc.
*   **Gain de Temps :** Réduire le temps de saisie de **80%**, permettant à l'expert-comptable de se repositionner sur un rôle de conseiller stratégique.
*   **Sécurité Multi-Cabinet :** Garantir une isolation parfaite et sécurisée des données avec des rôles stricts (Super-Admin / Admin / Agent).

---

## 📐 Architecture Système et Flux de Données

Voici comment les données transitent à travers le système (rendu généré par Mermaid) :

```mermaid
graph TD
    %% Entités Externes
    User([👨‍💼 Utilisateur / Agent])
    DGI([🏛️ Règles DGI (ICE/TVA)])
    Gemini([🧠 IA - Google Gemini 2.0])

    %% Frontend
    subgraph Frontend [🌐 Frontend (React + Vite)]
        AuthUI[Interface Connexion]
        UploadUI[Upload & Validation PDF]
        DashboardUI[Dashboard & Statistiques]
    end

    %% Backend API
    subgraph Backend [⚡ Backend (FastAPI)]
        Router[Routes API REST]
        Auth[Service d'Authentification / JWT]
        OCR[Service OCR & Vision IA]
        Compta[Moteur de Règles Comptables PCM]
        CRUD[Accès aux données SQLAlchemy]
    end

    %% Base de données
    subgraph Database [🗄️ Base de Données (PostgreSQL)]
        Schema[Tables Multi-Tenant]
        Brouillons[Brouillons de factures]
        Ecritures[Écritures Comptables Validées]
    end

    %% Flux d'actions
    User -->|Télécharge Facture PDF| UploadUI
    UploadUI -->|Requête POST| Router
    Router --> Auth
    Router --> OCR
    OCR -->|Analyse Visuelle Multimodale| Gemini
    Gemini -->|Données Structurées JSON| OCR
    Router --> Compta
    Compta -.->|Vérification Conformité| DGI
    Compta --> CRUD
    CRUD --> Schema
    Schema --> Brouillons
    Brouillons -->|Validation Agent| Ecritures
    Ecritures -->|Export| User

    %% Styles Modernes
    classDef frontend fill:#1E88E5,stroke:#0D47A1,stroke-width:2px,color:#fff;
    classDef backend fill:#43A047,stroke:#1B5E20,stroke-width:2px,color:#fff;
    classDef db fill:#FB8C00,stroke:#E65100,stroke-width:2px,color:#fff;
    classDef ai fill:#8E24AA,stroke:#4A148C,stroke-width:2px,color:#fff;
    
    class Frontend frontend;
    class Backend backend;
    class Database db;
    class Gemini,DGI ai;
```

---

## ✨ Fonctionnalités Détaillées

### 1. Extraction par Intelligence Artificielle Milti-Modale
* Traduction des images et PDF complexes en données JSON grâce à Gemini.
* Détection automatique : Fournisseur, Date, ICE, Montants (HT, TTC, TVA).
* Identification et blocage des **doublons** pour éviter la double facturation.

### 2. Le Moteur Comptable PCM (Plan Comptable Marocain)
* Suggestion automatique du compte d'achat / vente adapté selon la nature de la facture.
* Génération des lignes de Débit et de Crédit prêtes pour la comptabilité à partie double.
* Rapprochement bancaire intelligent suggérant automatiquement les factures associées à un relevé.

### 3. Gestion Administrative (ACL Avancé)
* **Super-Admin** : Gestion des abonnements, des cabinets et des demandes d'accès. Vues globales.
* **Administrateur Cabinet** : Outils pour configurer les sociétés clientes et attribuer les dossiers aux différents agents.
* **Agent Saisisseur** : Tableaux de bord de traitement et de validation, centrés uniquement sur les entités qui lui sont assignées.

---

## 🛠 Stack Technique

Le socle technique a été sélectionné pour sa scalabilité et robustesse en entreprise logicielle (Enterprise-Grade) :

### Frontend
- **Framework :** React 18, TypeScript, Vite
- **Styling :** Tailwind CSS, Design System orienté Glassmorphism
- **État & Fetching :** Hooks natifs et contexte sécurisé.

### Backend
- **Framework :** Python 3, FastAPI (Standard asynchrone, hautes performances)
- **Validation :** Pydantic (Stricte validation typée des requêtes HTTP)
- **Base de données :** PostgreSQL 15, interfacé avec **SQLAlchemy** (ORM)
- **Migrations :** Alembic

### DevOps
- **Conteneurisation :** Docker, Docker Compose
- **Services IA :** Google Gemini Cloud APIs

---

## 🚀 Guide de Déploiement Local (Docker)

Le lancement du projet complet prend moins de 3 minutes sur n'importe quel ordinateur grâce à l'orchestration Docker.

### 1. Cloner et configurer
Dans un fichier `.env` principal (ou explicitement dans `backend/.env`), insérez vos clés :

```properties
DATABASE_URL=postgresql+psycopg://admin:admin123@db:5432/compta_db
GEMINI_API_KEY=AIzaSy...votre-clé-google...
SECRET_KEY=votre_cle_hyper_secrete_123
```

### 2. Démarrer avec Docker Compose
Si Docker est allumé de votre côté, tapez simplement cette commande dans le dossier source :

```bash
docker-compose up --build -d
```
Les bases de données (PCM et sociétés tests) seront automatiquement *seedées* au démarrage.

### 3. URLs d'accès local
| Ressource | Lien |
| :--- | :--- |
| **Plafeforme UI (React)** | [http://localhost:3333](http://localhost:3333) |
| **Backend API** | [http://localhost:8888](http://localhost:8888) |
| **Documentation API Interactive**| [http://localhost:8888/docs](http://localhost:8888/docs) |

---

## 📂 Structure du Code Source

```text
Zéro Saisie Comptable/
├── backend/                  # Application Serveur (FastAPI)
│   ├── alembic/              # Fichiers de migration de schéma BDD
│   ├── routes/               # Contrôleurs API répartis par domaine
│   ├── services/             # Logique Métier (OCR, Gemini, PCM, Audit)
│   ├── main.py               # Point d'entrée de l'application
│   ├── models.py             # ORM SQLAlchemy - Schéma DB PostgreSQL
│   └── schemas.py            # Sérialisation et Validation Pydantic
│
├── frontend/                 # Application Client (React / Vite)
│   ├── src/
│   │   ├── components/       # Éléments d'UI Réutilisables, Modales
│   │   ├── pages/            # Vues complètes (Dashboard, Upload)
│   │   └── services/         # Wrappers API Axios/Fetch pour le backend
│
└── docker-compose.yml        # Définition des conteneurs DB / Front / Back
```

---
<div align="center">
<i>Soutenance PFE 2026 — Rendu finalisé.</i>
</div>
