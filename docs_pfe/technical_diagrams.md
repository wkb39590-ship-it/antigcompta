# Documentation Technique - Diagrammes PlantUML

Ce document regroupe les diagrammes de conception mis à jour pour l'application **Comptafacile**.

## 1. Diagramme de Cas d'Utilisation

Le système permet aux comptables (Agents) de gérer le flux complet de traitement des pièces comptables, de l'import à la génération des écritures.

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle

actor "Agent Comptable" as Agent
note left of Agent
  **Utilisateur de Production**
  Il traite au quotidien les factures
  des sociétés qui lui sont assignées.
end note

actor "Administrateur Cabinet" as Admin
note left of Admin
  **Gérant du Cabinet**
  Il gère son équipe (création agents),
  ses clients (sociétés) et supervise
  le travail.
end note

actor "Super Administrateur" as Super
note left of Super
  **Propriétaire de la Plateforme**
  Il gère la plateforme de manière globale,
  crée les nouveaux cabinets et accède à
  toutes les statistiques.
end note

actor "Service IA" as AI <<System>>

package "Système de Comptabilité Intelligente (IA)" {
  
  package "Fonctionnalités Métier (Production)" {
    usecase "Téléverser des factures (PDF/Images)" as UC_Upload
    usecase "Extraire les données via l'IA Générative" as UC_AI
    usecase "Vérifier et corriger les imputations (PCM)" as UC_Verify
    usecase "Valider les écritures comptables" as UC_Validate
    usecase "Sélectionner son contexte de travail\n(Cabinet & Société)" as UC_Context
    
    ' Nouvelles fonctionnalités ajoutées
    usecase "Gérer les Immobilisations\n(Amortissements)" as UC_Immo
    usecase "Gérer les Avoirs (Notes de crédit)" as UC_Avoirs
    usecase "Gérer la Paie (Employés & Bulletins)" as UC_Paie
  }
  
  package "Gestion du Cabinet (Administration)" {
    usecase "Affecter les Agents aux Sociétés" as UC_Assign
    usecase "Consulter les métriques du cabinet" as UC_Stats
    usecase "Accéder directement aux factures\nd'une société cliente" as UC_DirectAccess
    usecase "Créer et gérer les profils Agents" as UC_Agents
    usecase "Créer et gérer les Sociétés clientes" as UC_Societes
    usecase "Tracer les actions (Historique d'audit)" as UC_Logs
  }
  
  package "Gestion Globale (Super Administration)" {
    usecase "Créer un nouveau Cabinet" as UC_NewCabinet
    usecase "Créer le compte Administrateur d'un cabinet" as UC_NewAdmin
    usecase "Superviser les métriques globales\nde la plateforme" as UC_GlobalStats
  }
}

' Relations Agent
Agent -- UC_Upload
Agent -- UC_Validate
Agent -- UC_Context
Agent -- UC_Immo
Agent -- UC_Avoirs
Agent -- UC_Paie

UC_AI ..> UC_Upload : <<include>>
UC_Validate ..> UC_Verify : <<include>>
UC_AI -- AI

' Relations Admin
Admin -- UC_Assign
Admin -- UC_Stats
Admin -- UC_DirectAccess
Admin -- UC_Agents
Admin -- UC_Societes
Admin -- UC_Logs

UC_DirectAccess ..> UC_Context : <<extend>>

' Relations Super Admin
Super -- UC_NewCabinet
Super -- UC_NewAdmin
Super -- UC_GlobalStats

@enduml
```

---

## 2. Diagramme de Classe

Le schéma de données suit une architecture multi-tenant (Multi-Cabinet / Multi-Société).

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam monochrome true
skinparam shadowing false

title Diagramme de Classes Complet (Multi-Tenant & ERP)

package "Structure Organisationnelle" {
    class Cabinet {
        + id : int
        + nom : string
        + email : string
        + telephone : string
        + adresse : string
        + logo_path : string
        + created_at : datetime
    }

    class Agent {
        + id : int
        + cabinet_id : int
        + username : string
        + email : string
        + password_hash : string
        + nom : string
        + prenom : string
        + is_active : boolean
        + is_admin : boolean
        + is_super_admin : boolean
        + created_at : datetime
        --
        + check_password(pwd) : bool
    }

    class Societe {
        + id : int
        + cabinet_id : int
        + raison_sociale : string
        + ice : string
        + if_fiscal : string
        + rc : string
        + patente : string
        + adresse : string
        + logo_path : string
        + created_at : datetime
        + updated_at : datetime
    }

    class agents_societes << (T,#FFAAAA) association >> {
        + agent_id : int <<FK>>
        + societe_id : int <<FK>>
    }
}

package "Traitement Factures & Avoirs" {
    class Facture {
        + id : int
        + societe_id : int
        + numero_facture : string
        + date_facture : date
        + due_date : date
        + invoice_type : string
        + supplier_name : string
        + supplier_ice : string
        + supplier_if : string
        + client_name : string
        + client_ice : string
        + montant_ht : numeric
        + montant_tva : numeric
        + montant_ttc : numeric
        + taux_tva : numeric
        + devise : string
        + payment_mode : string
        + status : string
        + extraction_source : string
        + ocr_confidence : numeric
        + dgi_flags : JSON
        + file_path : string
        + validated_by : string
        + validated_at : datetime
        + reject_reason : string
        + created_at : datetime
        + updated_at : datetime
        --
        + get_dgi_flags() : list
        + set_dgi_flags(flags) : void
    }

    class LigneFacture {
        + id : int
        + facture_id : int
        + description : text
        + quantity : numeric
        + unit_price_ht : numeric
        + line_amount_ht : numeric
        + tva_rate : numeric
        + pcm_account_code : string
        + pcm_account_label : string
        + corrected_account_code : string
        + classification_reason : string
    }
}

package "Comptabilité (PCM & Journal)" {
    class EcritureJournal {
        + id : int
        + facture_id : int
        + journal_code : string
        + entry_date : date
        + reference : string
        + description : text
        + total_debit : numeric
        + total_credit : numeric
        + is_validated : boolean
        + created_at : datetime
    }

    class LigneEcriture {
        + id : int
        + journal_entry_id : int
        + line_order : int
        + account_code : string
        + account_label : string
        + debit : numeric
        + credit : numeric
        + tiers_name : string
        + tiers_ice : string
    }

    class ComptePCM {
        + code : string
        + label : string
        + pcm_class : int
        + account_type : string
        + is_tva_account : boolean
    }
}

package "Immobilisations" {
    class Immobilisation {
        + id : int
        + societe_id : int
        + facture_id : int
        + designation : string
        + categorie : string
        + date_acquisition : date
        + valeur_acquisition : numeric
        + duree_amortissement : int
        + methode : string
        + statut : string
        --
        + generer_plan_amortissement() : void
    }

    class LigneAmortissement {
        + id : int
        + immobilisation_id : int
        + annee : int
        + dotation_annuelle : numeric
        + amortissement_cumule : numeric
        + valeur_nette_comptable : numeric
        + ecriture_generee : boolean
    }
}

package "Paie & RH" {
    class Employe {
        + id : int
        + societe_id : int
        + nom : string
        + prenom : string
        + cin : string
        + poste : string
        + date_embauche : date
        + salaire_base : numeric
        + nb_enfants : int
        + numero_cnss : string
        + statut : string
    }

    class BulletinPaie {
        + id : int
        + employe_id : int
        + mois : int
        + annee : int
        + salaire_base : numeric
        + prime_anciennete : numeric
        + autres_gains : numeric
        + salaire_brut : numeric
        + cnss_salarie : numeric
        + amo_salarie : numeric
        + ir_retenu : numeric
        + total_retenues : numeric
        + salaire_net : numeric
        + statut : string
        --
        + calculer_paie() : void
    }

    class LignePaie {
        + id : int
        + bulletin_id : int
        + libelle : string
        + type_ligne : string
        + montant : numeric
        + taux : numeric
    }
}

package "Audit & Utilitaires" {
    class ActionLog {
        + id : int
        + cabinet_id : int
        + agent_id : int
        + action_type : string
        + entity_type : string
        + entity_id : int
        + details : text
        + created_at : datetime
    }

    class CompteurFacturation {
        + id : int
        + societe_id : int
        + annee : int
        + dernier_numero : int
    }

    class MappingFournisseur {
        + id : int
        + cabinet_id : int
        + supplier_ice : string
        + pcm_account_code : string
        + usage_count : int
    }
}

' relations
Cabinet "1" *-- "0..*" Agent
Cabinet "1" *-- "0..*" Societe
Cabinet "1" *-- "0..*" ActionLog

Agent "1" -- "0..*" ActionLog
Agent "0..*" -- "0..*" agents_societes
Societe "1" -- "0..*" agents_societes

Societe "1" *-- "0..*" Facture
Societe "1" *-- "0..*" Immobilisation
Societe "1" *-- "0..*" Employe
Societe "1" *-- "0..*" CompteurFacturation
Cabinet "1" *-- "0..*" MappingFournisseur

Facture "1" *-- "0..*" LigneFacture
Facture "1" -- "0..1" EcritureJournal
Facture "1" -- "0..*" Immobilisation : origine

EcritureJournal "1" *-- "0..*" LigneEcriture
Immobilisation "1" *-- "0..*" LigneAmortissement

Employe "1" *-- "0..*" BulletinPaie
BulletinPaie "1" *-- "0..*" LignePaie
BulletinPaie "1" -- "0..1" EcritureJournal : génère

' Relations PCM
LigneEcriture "0..*" --> "1" ComptePCM
LigneFacture "0..*" --> "1" ComptePCM
MappingFournisseur "0..*" --> "1" ComptePCM

@enduml
```

---

## 3. Diagrammes de Séquence

### Séquence A : Authentification & Initialisation Multi-Tenant
Ce flux décrit l'accès sécurisé et la configuration du contexte de travail dynamique.

```plantuml
@startuml
actor User
participant "Frontend (React)" as FE
participant "Auth/Context API" as API
database "DB (PostgreSQL)" as DB

User -> FE: Saisit identifiants
FE -> API: POST /auth/login
API -> DB: Vérifie Agent & Cabinet
DB --> API: Agent Data (is_admin, cabinets)
API --> FE: JWT Token + Liste Cabinets

User -> FE: Sélectionne un Cabinet
FE -> API: GET /societes (filter by cabinet_id)
API --> FE: Liste des Sociétés clientes

User -> FE: Sélectionne la Société cible
FE -> API: POST /auth/select-context
note right: Initialise le contexte (CabinetID, SocieteID)
API --> FE: Token Contextualisé (Session)
FE -> FE: Charge le PCM & Paramètres de la Société
@enduml
```

### Séquence B : Pipeline Intelligent de Traitement (Facture / Avoir)
Le flux automatisé de capture et d'analyse par l'intelligence artificielle.

```plantuml
@startuml
actor User
participant "Frontend" as FE
participant "Pipeline API" as API
participant "Service OCR & IA" as IA
participant "Classification PCM" as PCM
database "DB" as DB

User -> FE: Téléverse PDF/Image (Achat, Vente, Avoir)
FE -> API: POST /pipeline/process
API -> DB: Crée Facture (Status: IMPORTED)
API -> IA: Analyse Document (Vision + LLM)
IA --> API: JSON (Num_Fact, Date, Fournisseur, Montants, Type)
API -> PCM: Mapper selon MappingFournisseur
PCM --> API: Comptes PCM suggérés (6111, 2355, etc.)

opt Si Avoir détecté
    API -> API: Lier à une facture d'origine
end

API -> DB: Sauvegarde Facture + Lignes (Status: EXTRACTED)
API --> FE: Affiche les données pour vérification
@enduml
```

### Séquence C : Validation Métier & Génération Automatisée (ERP)
Ce flux montre comment une validation déclenche les moteurs comptables spécialisés.

```plantuml
@startuml
actor User
participant "Frontend" as FE
participant "Validation API" as API
participant "Moteur Comptable" as MC
participant "Modules (Immo/Paie)" as MOD
database "DB" as DB

User -> FE: Clique sur "Valider"
FE -> API: POST /factures/{id}/validate

group Processus Comptable
    API -> MC: Générer Ecriture Journal (Débit/Crédit)
    MC -> DB: Création JournalEntry + Lignes
end

alt Si Document type IMMOBILISATION
    API -> MOD: Créer Fiche Immobilisation
    MOD -> MOD: Calculer Plan Amortissement (DDA/VNC)
    MOD -> DB: Sauvegarde Immo + Lignes Amortissement
else Si Bulletin de PAIE
    API -> MOD: Calculer Salaire (Brut -> Retenues -> Net)
    MOD -> DB: Sauvegarde Bulletin + Lignes Paie
end

API -> DB: Update Statut Final (VALIDATED)
API --> FE: Succès (Interface mise à jour)
@enduml
```

---

### Séquence D : Flux Global de l'Agent Comptable (Processus de Bout en Bout)
Ce diagramme synthétise le parcours complet d'un agent de la connexion jusqu'à l'aboutissement comptable des pièces.

```plantuml
@startuml
autonumber
actor "Agent Comptable" as Agent
participant "Interface (SPA)" as FE
participant "API Gateway" as API
participant "Intelligence Artificielle" as IA
participant "Moteur ERP (Compta/Ventes)" as ERP
database "Base de Données" as DB

== Phase 1 : Accès & Contexte ==
Agent -> FE: Se connecte
FE -> API: Auth Request
API -> DB: Vérifier identité
DB --> API: OK (Agent Data)
API --> FE: JWT + Cabinets
Agent -> FE: Sélectionne Cabinet & Société
FE -> API: POST /select-context
API --> FE: Session initialisée

== Phase 2 : Traitement Documentaire ==
Agent -> FE: Upload Facture / Avoir / Note
FE -> API: Submit Document
API -> DB: Stocker (Statut: IMPORTED)

group Pipeline IA & Extraction
    API -> IA: Analyse Multi-modale
    IA -> IA: OCR + Classification PCM
    IA --> API: Données structurées (JSON)
end

API -> DB: Sauvegarder (Statut: EXTRACTED)
API --> FE: Afficher pour révision

== Phase 3 : Validation & Finalisation ==
Agent -> FE: Vérifier & Corriger
FE -> API: Valider (Statut: VALIDATED)

group Moteur ERP Automatisé
    API -> ERP: Générer Écritures Journal
    ERP -> DB: JournalEntry + Lignes
    
    alt Si Immobilisation
        API -> ERP: Créer Fiche Immobilisation
        ERP -> DB: Plan d'Amortissement
    else Si Bulletin Paie
        API -> ERP: Calculer Bulletin (Brut/Net)
        ERP -> DB: BulletinPaie + LignesPaie
    end
end

API --> FE: Confirmation de validation terminée
FE -> Agent: Afficher succès & Dashboard à jour
@enduml---

## 4. Architecture Globale de la Plateforme

Ce diagramme illustre le déploiement technique (Docker) et l'interaction entre les composants frontend, backend et les services tiers.

```plantuml
@startuml
!define RECTANGLE class
skinparam componentStyle uml2
skinparam nodesep 40
skinparam ranksep 50
skinparam defaultFontName Arial

' --- Couleurs et Styles ---
skinparam actor {
    BackgroundColor #E3F2FD
    BorderColor #1565C0
}
skinparam component {
    BackgroundColor #FFFFFF
    BorderColor #424242
    ArrowColor #616161
}
skinparam database {
    BackgroundColor #E8F5E9
    BorderColor #2E7D32
}
skinparam cloud {
    BackgroundColor #FFF3E0
    BorderColor #E65100
}

title Architecture Globale - Plateforme de Comptabilité Intelligente

' ==========================================
' ACTEURS (UTILISATEURS)
' ==========================================
actor "Agent Comptable" as Agent
actor "Administrateur Cabinet" as Admin
actor "Super Administrateur" as SAdmin

' ==========================================
' INFRASTRUCTURE DOCKER (Conteneurs)
' ==========================================
node "Serveur Hôte / Cloud (Docker Engine)" as DockerHost {

    node "Conteneur Frontend (pfe_frontend_v2)" as FrontendContainer {
        component "Application Web Client" as SPA <<React JS / TypeScript>> {
            component "UI Components (Tailwind CSS)" as UI
            component "State Management" as State
            component "API Services (Axios)" as Axios
            
            UI --> State
            State --> Axios
        }
    }

    node "Conteneur Backend (pfe_backend_v2)" as BackendContainer {
        component "API REST Principale" as Backend <<FastAPI / Python>> {
            component "Routeurs (Endpoints)" as Routes
            component "Contrôleurs (CRUD)" as CRUD
            component "Services Métiers" as Services {
                component "Service Extraction IA (Gemini)" as GeminiService
                component "Générateur d'Écritures Journal" as EntryGen
                component "Module Immobilisations" as ImmoMod
                component "Module Paie & RH" as PaieMod
                component "Gestion des Droits (Auth)" as AuthService
            }
            component "ORM (SQLAlchemy)" as ORM
            
            Routes --> AuthService
            Routes --> CRUD
            CRUD --> Services
            CRUD --> ORM
        }
    }

    node "Conteneur Database (pfe_postgres_v2)" as DBContainer {
        database "PostgreSQL DB (compta_db)" as Postgres {
            folder "Schémas de données" {
                [Agents, Cabinets, Sociétés]
                [Factures, Lignes, Avoirs]
                [Comptabilité (PCM, Écritures)]
                [RH (Employés, Bulletins)]
                [Immos (Plan Amortissement)]
                [Audit (ActionLog)]
            }
        }
    }
}

' ==========================================
' SERVICES EXTERNES (API)
' ==========================================
cloud "Google Cloud Platform" as GCP {
    component "Service IA Générative" as GeminiAPI <<Google Gemini (Pro/Flash)>>
    note right of GeminiAPI : Extraction OCR & Classification PCM
}

' ==========================================
' RELATIONS ET FLUX DE DONNÉES
' ==========================================

' Interactions Utilisateurs -> Frontend
Agent --> UI : Dashboard & Upload (HTTPS)
Admin --> UI : Gestion Cabinet (HTTPS)
SAdmin --> UI : Admin Système (HTTPS)

' Interactions Frontend -> Backend
Axios --> Routes : Appels API REST (JSON :8000)

' Interactions Backend -> Database
ORM --> Postgres : Requêtes SQL (TCP :5432)

' Interactions Backend -> Services Externes
GeminiService --> GeminiAPI : Prompts Vision (HTTPS)
GeminiAPI --> GeminiService : Struct (JSON)
@enduml
```
```
