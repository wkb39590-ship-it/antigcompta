# 📄 FICHE DESCRIPTIVE DU SUJET PFE

---

## 🎓 Informations Académiques

| Champ | Détail |
|-------|--------|
| **Intitulé du PFE** | Vers une comptabilité “Zéro Saisie” : plateforme intelligente d’extraction de données par IA pour l'automatisation comptable. |
| **Domaine** | Génie Logiciel / Intelligence Artificielle / Fintech |
| **Filière** | Ingénierie des Systèmes d'Information |
| **Durée** | 4 mois (Février — Mai 2026) |
| **Étudiant(e)** | Wissal KB |
| **Encadrants** | [À compléter : Pédagogique / Professionnel / Établissement] |

---

### 1. Intitulé du Projet
**Vers une comptabilité “Zéro Saisie” : Développement d’une plateforme intelligente d’extraction de données par IA pour la génération automatique des écritures comptables.**

### 2. Contexte et Enjeux
La transformation digitale des entreprises a permis l’automatisation de nombreux processus métiers. Toutefois, la saisie comptable manuelle demeure encore aujourd’hui une activité chronophage dans les cabinets comptables marocains. 
Cette étape représente un frein opérationnel majeur (risques de erreurs de saisie, délais de traitement longs). Dans un contexte où la précision et la conformité fiscale (ICE, TVA) sont essentielles, il devient stratégique de moderniser ce processus pour permettre aux comptables de se concentrer sur l'analyse plutôt que sur la saisie.

### 3. Problématique
Le traitement manuel des factures engendre plusieurs limites :
*   **Risque d'erreurs humaines** : Erreurs de saisie (montants, dates, ICE) pouvant fausser les déclarations fiscales (DGI).
*   **Faible valeur ajoutée** : Mobilisation excessive des collaborateurs sur des tâches répétitives.
*   **Délais de traitement** : Latence entre réception et intégration, empêchant un suivi en temps réel de la trésorerie.
*   **Cloisonnement Multi-entités** : Difficulté de gérer isolément les données de plusieurs sociétés clientes au sein d'un même cabinet.

### 4. Objectif Général
Mettre en place une plateforme intelligente multi-tenante capable de supprimer ou réduire drastiquement la saisie manuelle, en automatisant l’extraction d'informations par IA et en générant les écritures comptables associées.

### 5. Objectifs Spécifiques
*   **Automatiser l’extraction** : ICE, date, fournisseur, montants HT/TVA/TTC depuis PDF/images multi-pages.
*   **IA Apprenante (Feedback Loop)** : Mémoriser les corrections des agents pour améliorer la précision de la classification PCM.
*   **Conformité DGI** : Vérifier automatiquement la validité des données fiscales (ICE, cohérence TVA).
*   **Isolation Multi-tenant** : Garantir la sécurité et la séparation stricte des données entre cabinets et agents.

### 6. Solution Proposée
La solution repose sur un pipeline intelligent :
*   **OCR & Vision Multimodale** : Utilisation de **Google Gemini 2.0 Flash** pour comprendre la structure visuelle complexe des factures (mieux que l'OCR classique).
*   **Système Apprenant** : Moteur de "Supplier Mapping" qui stocke les préférences d'imputation comptable de chaque cabinet.
*   **Architecture Multi-niveaux** : Gestion hiérarchique (Super-Admin / Admin Cabinet / Agent) pour une exploitation professionnelle en cabinet.

### 7. Fonctionnalités Principales
*   **a) Gestion des documents** : Import PDF multi-pages (conversion auto), gestion des brouillons.
*   **b) Extraction IA** : Détection auto des champs fiscaux, détection de doublons (Sécurité).
*   **c) Génération comptable** : Suggestion de compte PCM, génération automatique d'écritures débit/crédit.
*   **d) Administration** : Gestion des cabinets, agents et affectations sécurisées aux sociétés.
*   **e) Dashboard & Statistiques** : Suivi de productivité et historique complet (Audit Trail).

### 8. Technologies Utilisées
*   **Frontend** : React.js + TypeScript + Tailwind CSS (Design Premium Glassmorphism).
*   **Backend** : Python + FastAPI (Performances et rapidité).
*   **IA & Vision** : Google Gemini API (Modèle multimodal) + Tesseract (Fallback).
*   **Base de Données** : PostgreSQL (Fiabilité multi-tenant).
*   **DevOps** : Docker & Docker Compose (Déploiement reproductible).

### 9. Livrables Attendus
*   **Plateforme Web fonctionnelle** (Interface Agent & Admin).
*   **Pipeline d'extraction IA** intégré et testé sur factures réelles.
*   **Documentation technique** et diagrammes UML de conception.
*   **Rapport de PFE complet** détaillant la réalisation et les tests.

### 10. Résultats et Bénéfices Attendus
*   **Gain de productivité** : Réduction du temps de saisie de plus de 80%.
*   **Fiabilité** : Diminution drastique des erreurs sur les montants et les ICE.
*   **Conformité** : Alignement automatique sur les exigences de la DGI marocaine.
*   **Modernisation** : Valorisation du métier de comptable vers le rôle de conseiller.

---
*Fiche mise à jour le 25 Février 2026 — Wissal KB*
