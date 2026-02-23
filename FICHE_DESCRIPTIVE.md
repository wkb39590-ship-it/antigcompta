# 📄 Fiche Descriptive du Projet : comptafacile

## 📝 Information Générale
**Nom du Projet :** comptafacile (Easy Accounting)  
**Domaine :** Fintech / Automatisation Comptable / Intelligence Artificielle  
**Version :** 2.1.0

---

## � Contexte du Projet
Dans un environnement économique de plus en plus numérisé, la gestion comptable reste paradoxalement l'une des tâches les plus manuelles au sein des entreprises et des cabinets d'expertise. La transition vers la facture électronique et la nécessité de traiter des volumes croissants de données obligent les professionnels du chiffre à repenser leurs processus opérationnels pour rester compétitifs.

## ⚠️ Problématique
Les cabinets comptables font face à trois défis majeurs :
1.  **La lenteur de la saisie manuelle :** Un temps considérable est perdu à recopier des données de factures papier ou PDF vers des logiciels de comptabilité.
2.  **Le risque d'erreur humaine :** La fatigue et la répétitivité entraînent inévitablement des fautes de frappe ou d'imputation.
3.  **Le manque de visibilité en temps réel :** Le décalage entre la réception d'une facture et sa saisie empêche une vision précise de la trésorerie.

## 💡 L'Idée Innovante
L'innovation de ce projet réside dans l'alliance de trois technologies de pointe pour créer un système **"Zero Entry"** :
- **Extraction Sémantique par IA (Gemini/LLM) :** Contrairement aux OCR classiques qui ne lisent que du texte, notre système "comprend" la structure de la facture, identifiant intelligemment les fournisseurs, les taux de TVA complexes et les totaux, même sur des documents mal formatés.
- **Classification Automatique PCM :** Un moteur de recommandation qui associe chaque dépense au compte correspondant du Plan Comptable Marocain sans intervention humaine.
- **design moderne et fluide :** Une interface utilisateur futuriste utilisant le *Glassmorphism*, brisant les codes esthétiques austères des logiciels de gestion traditionnels pour offrir un confort de travail inégalé.

---

## 🎯 Objectifs du Projet
- **Productivité :** Diviser par 10 le temps de traitement d'un dossier comptable.
- **Zéro Papier / Zéro Saisie :** Automatiser 95% du cycle de vie d'une facture (de l'upload à l'écriture comptable).
- **Sécurisation :** Assurer une traçabilité totale via un système d'Audit Trail et une isolation stricte des données multi-cabinets.
- **Conformité DGI :** Générer des écritures conformes aux exigences fiscales marocaines.

---

## 🚀 Fonctionnalités Principales

### 1. Pipeline de Traitement Intelligent
- **Multi-Source Upload :** Import massif de documents PDF/Images.
- **Extraction OCR Ultra-Précise :** Capture automatique de l'ICE, date, montants HT/TVA, et identification du fournisseur.
- **Validation Assistée :** Système de vérification rapide pour l'agent comptable avant validation finale.

### 2. Gestion de Cabinet & Collaboration
- **Architecture Multi-Cabinet :** Gestion de plusieurs entités comptables indépendantes sur une même instance.
- **Hiérarchie Utilisateurs :** Super-Admin, Agents Comptables, et Clients (Sociétés).
- **Association Dynamique :** Affectation flexible des agents à des portefeuilles clients spécifiques.

### 3. Reporting & Audit
- **Dashboard Dynamique :** Visualisation des flux financiers et de l'état du traitement.
- **Audit Trail Premium :** Historique détaillé de chaque modification apportée à une facture ou une écriture.

---

## 🛠️ Stack Technique
- **Frontend :** React 18, TypeScript, Vite, interface haut de gamme.
- **Backend :** FastAPI (Python), SQLAlchemy, Pydantic.
- **Évolution IA :** Intégration de modèles de vision et LLM (Large Language Models) pour l'extraction.
- **Base de Données :** PostgreSQL.
- **Infrastructure :** Docker & Docker Compose pour un déploiement agnostique de l'environnement.

---

**Développé avec passion pour l'excellence opérationnelle.**  
*Wissal KB - Ingénierie Full-Stack*