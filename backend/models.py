"""
models.py — Schéma complet "Comptabilité Zéro Saisie" (PCM/CGNC Maroc)
Architecture Multi-Cabinet / Multi-Agents / Multi-Sociétés
"""
import json
from decimal import Decimal
from sqlalchemy import (
    Column, Integer, String, Date, Float, ForeignKey,
    DateTime, func, Boolean, Text, Numeric, Table
)
from sqlalchemy.orm import relationship
from database import Base


# ─────────────────────────────────────────────
# Cabinet (Entreprise de Comptabilité)
# ─────────────────────────────────────────────
class Cabinet(Base):
    __tablename__ = "cabinets"

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(255), nullable=False, unique=True)
    email = Column(String(255), nullable=True)
    telephone = Column(String(20), nullable=True)
    adresse = Column(String(500), nullable=True)
    logo_path = Column(String(500), nullable=True)  # Chemin vers le logo
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    agents = relationship("Agent", back_populates="cabinet", cascade="all, delete-orphan")
    societes = relationship("Societe", back_populates="cabinet", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Agent de Comptabilité (Utilisateur)
# ─────────────────────────────────────────────
class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False, index=True)
    
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(500), nullable=False)  # Hashed with bcrypt
    nom = Column(String(255), nullable=True)
    prenom = Column(String(255), nullable=True)
    
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Admin du cabinet
    is_super_admin = Column(Boolean, default=False)  # Super Admin système
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    cabinet = relationship("Cabinet", back_populates="agents")
    # ManyToMany: Agent peut gérer plusieurs Sociétés
    societes = relationship(
        "Societe",
        secondary="agents_societes",
        back_populates="agents"  #relation dans les deux sens
    )


# Table d'association Many-to-Many : Agent-Societe
agents_societes = Table(
    "agents_societes",
    Base.metadata,    #Ajoute cette table au schéma global de la base
    Column("agent_id", Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True),  #si l’agent est supprimé → la relation est supprimée aussi (CASCADE)
    Column("societe_id", Integer, ForeignKey("societes.id", ondelete="CASCADE"), primary_key=True)
)


# ─────────────────────────────────────────────
# Société (entreprise cliente du cabinet)
# ─────────────────────────────────────────────
class Societe(Base):
    __tablename__ = "societes"

    id = Column(Integer, primary_key=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False, index=True)
    
    raison_sociale = Column(String(255), nullable=False)
    ice = Column(String(15), nullable=True, index=True)
    if_fiscal = Column(String(50), nullable=True)
    rc = Column(String(50), nullable=True)
    patente = Column(String(50), nullable=True)
    adresse = Column(String(500), nullable=True)
    logo_path = Column(String(500), nullable=True)  # Logo de la société
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    cabinet = relationship("Cabinet", back_populates="societes")
    agents = relationship(
        "Agent",
        secondary="agents_societes",
        back_populates="societes"
    )
    factures = relationship("Facture", back_populates="societe", foreign_keys="[Facture.societe_id]", cascade="all, delete-orphan")
    compteurs = relationship("CompteurFacturation", back_populates="societe", cascade="all, delete-orphan")
    immobilisations = relationship("Immobilisation", back_populates="societe", cascade="all, delete-orphan")
    employes = relationship("Employe", back_populates="societe", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# Compteur de Facturation (par Société et Année)
# ─────────────────────────────────────────────
class CompteurFacturation(Base):
    __tablename__ = "compteurs_facturation"

    id = Column(Integer, primary_key=True, index=True)
    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)
    annee = Column(Integer, nullable=False)  # Année du compteur (ex: 2025)
    dernier_numero = Column(Integer, default=0)  # Dernier numéro utilisé
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    societe = relationship("Societe", back_populates="compteurs")

    __table_args__ = (
        # Unicité : une seule ligne par (societe, année)
        None,
    )


# ──────────────────────────────────────────────────────────────────────────
# FACTURE - Entité centrale du traitement
# ──────────────────────────────────────────────────────────────────────────
class Facture(Base):
    """
    Représente un document fiscal (Facture d'achat ou vente).
    Contient les données extraites par l'IA et le statut du traitement.
    """
    __tablename__ = "factures"

    id = Column(Integer, primary_key=True, index=True)
    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)

    # Identifiants facture
    numero_facture = Column(String(100), nullable=True)
    date_facture = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    invoice_type = Column(String(30), nullable=True)  # ACHAT/VENTE/AVOIR/NOTE_FRAIS/IMMOBILISATION

    # Fournisseur
    supplier_name = Column(String(255), nullable=True)
    supplier_ice = Column(String(15), nullable=True)
    supplier_if = Column(String(50), nullable=True)
    supplier_rc = Column(String(50), nullable=True)
    supplier_address = Column(Text, nullable=True)

    # Client
    client_name = Column(String(255), nullable=True)
    client_ice = Column(String(15), nullable=True)
    client_if = Column(String(50), nullable=True)
    client_address = Column(Text, nullable=True)

    # Montants
    montant_ht = Column(Numeric(15, 2), nullable=True)
    montant_tva = Column(Numeric(15, 2), nullable=True)
    montant_ttc = Column(Numeric(15, 2), nullable=True)
    taux_tva = Column(Numeric(5, 2), nullable=True)
    devise = Column(String(10), nullable=True, server_default="MAD")

    # Paiement
    payment_mode = Column(String(50), nullable=True)   # Virement/Chèque/Espèces
    payment_terms = Column(String(100), nullable=True)

    # OCR / Extraction
    ocr_confidence = Column(Float, nullable=True)
    extraction_source = Column(String(20), nullable=True)  # OCR/GEMINI/HYBRID
    dgi_flags = Column(Text, nullable=True)  # JSON stocké en texte

    # Statut du cycle de vie
    status = Column(String(30), nullable=False, server_default="IMPORTED")
    # IMPORTED → EXTRACTED → CLASSIFIED → DRAFT → VALIDATED → EXPORTED / ERROR

    # Validation
    validated_by = Column(String(255), nullable=True)  # Nom d'utilisateur ou ID
    validated_at = Column(DateTime, nullable=True)
    reject_reason = Column(Text, nullable=True)

    # Fichier source
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=True, index=True)

    # Champs legacy (compatibilité)
    fournisseur = Column(String, nullable=True)
    operation_type = Column(String(50), nullable=True)
    operation_confidence = Column(Float, nullable=True)
    if_frs = Column(String(50), nullable=True)
    ice_frs = Column(String(50), nullable=True)
    designation = Column(String(255), nullable=True)
    id_paie = Column(String(50), nullable=True)
    date_paie = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    societe = relationship("Societe", back_populates="factures", foreign_keys=[societe_id])
    lines = relationship("InvoiceLine", back_populates="facture", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="facture", cascade="all, delete-orphan")



    # Cette méthode sert à récupérer les dgi_flags depuis la base de données.
# En base, ils sont stockés sous forme de texte JSON.
# On veut les transformer en liste Python pour pouvoir les utiliser facilement.
    def get_dgi_flags(self):
        if self.dgi_flags:
            try:    # On convertit le texte JSON en objet Python (ex: liste)
                return json.loads(self.dgi_flags)
            except Exception:
                return []
        return []




   # Cette méthode sert à enregistrer des dgi_flags.
# On reçoit une liste Python (ex: ["Erreur TVA", "ICE manquant"])
# et on la transforme en texte JSON pour la stocker en base.
    def set_dgi_flags(self, flags: list):


        # On convertit la liste Python en texte JSON
    # ensure_ascii=False permet de garder les accents correctement
        self.dgi_flags = json.dumps(flags, ensure_ascii=False)


# ──────────────────────────────────────────────────────────────────────────
# LIGNES DE FACTURE - Tableau détaillé des produits/services
# ──────────────────────────────────────────────────────────────────────────
class InvoiceLine(Base):
    """
    Détail de chaque ligne de la facture (Désignation, Quantité, Prix, TVA).
    C'est ici qu'on stocke la classification comptable (compte PCM).
    """
    __tablename__ = "lignes_factures"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False, index=True)
    line_number = Column(Integer, nullable=True)

    # Désignation et quantités
    description = Column(Text, nullable=True)
    quantity = Column(Numeric(10, 3), nullable=True)
    unit = Column(String(50), nullable=True)
    unit_price_ht = Column(Numeric(15, 4), nullable=True)

    # Montants ligne
    line_amount_ht = Column(Numeric(15, 2), nullable=True)
    tva_rate = Column(Numeric(5, 2), nullable=True)
    tva_amount = Column(Numeric(15, 2), nullable=True)
    line_amount_ttc = Column(Numeric(15, 2), nullable=True)

    # Classification PCM (remplie par le service de classification)
    pcm_class = Column(Integer, nullable=True)           # 1 à 8
    pcm_account_code = Column(String(10), nullable=True) # ex: 6111, 2355
    pcm_account_label = Column(String(255), nullable=True)
    classification_confidence = Column(Float, nullable=True)
    classification_reason = Column(Text, nullable=True)

    # Correction manuelle par le comptable
    is_corrected = Column(Boolean, nullable=False, server_default="false")
    corrected_account_code = Column(String(10), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    facture = relationship("Facture", back_populates="lines")


# ──────────────────────────────────────────────────────────────────────────
# RÉFÉRENTIEL PCM - Plan Comptable Marocain
# ──────────────────────────────────────────────────────────────────────────
class PcmAccount(Base):
    """
    Base de données des comptes comptables officiels au Maroc.
    Utilisée pour suggérer des comptes lors de la classification.
    """
    __tablename__ = "comptes_pcm"

    code = Column(String(10), primary_key=True)
    label = Column(String(255), nullable=False)
    pcm_class = Column(Integer, nullable=False)   # 1 à 8
    group_code = Column(String(10), nullable=True)
    account_type = Column(String(20), nullable=True)  # CHARGE/PRODUIT/ACTIF/PASSIF/TIERS
    is_tva_account = Column(Boolean, nullable=False, server_default="false")
    tva_type = Column(String(30), nullable=True)  # RECUPERABLE/COLLECTEE/IMMOBILISATION


# ─────────────────────────────────────────────
# SupplierMapping — Apprentissage par l'usage
# ─────────────────────────────────────────────
class SupplierMapping(Base):
    __tablename__ = "mappings_fournisseurs"

    id = Column(Integer, primary_key=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id"), nullable=False, index=True)
    supplier_ice = Column(String(15), nullable=False, index=True)
    pcm_account_code = Column(String(10), nullable=False)
    
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Unicité par cabinet et ICE
    __table_args__ = (
        None,
    )


# ─────────────────────────────────────────────
# JournalEntry — En-tête écriture comptable
# ─────────────────────────────────────────────
class JournalEntry(Base):
    __tablename__ = "ecritures_journal"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=True, index=True)

    journal_code = Column(String(10), nullable=False)  # ACH/VTE/OD/BQ/CAIS
    entry_date = Column(Date, nullable=True)
    reference = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    is_validated = Column(Boolean, nullable=False, server_default="false")
    validated_by = Column(String(255), nullable=True)  # Nom d'utilisateur ou ID
    validated_at = Column(DateTime, nullable=True)

    total_debit = Column(Numeric(15, 2), nullable=True, server_default="0")
    total_credit = Column(Numeric(15, 2), nullable=True, server_default="0")

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    facture = relationship("Facture", back_populates="journal_entries")
    entry_lines = relationship("EntryLine", back_populates="journal_entry", cascade="all, delete-orphan", foreign_keys="[EntryLine.ecriture_journal_id]")


# ─────────────────────────────────────────────
# EntryLine — Lignes débit/crédit
# ─────────────────────────────────────────────
class EntryLine(Base):
    __tablename__ = "lignes_ecritures"

    id = Column(Integer, primary_key=True, index=True)
    ecriture_journal_id = Column(Integer, ForeignKey("ecritures_journal.id", ondelete="CASCADE"), nullable=False, index=True)

    line_order = Column(Integer, nullable=True)
    account_code = Column(String(10), nullable=False)
    account_label = Column(String(255), nullable=True)
    debit = Column(Numeric(15, 2), nullable=False, server_default="0")
    credit = Column(Numeric(15, 2), nullable=False, server_default="0")
    tiers_name = Column(String(255), nullable=True)
    tiers_ice = Column(String(15), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    journal_entry = relationship("JournalEntry", back_populates="entry_lines", foreign_keys=[ecriture_journal_id])


# ─────────────────────────────────────────────
# ActionLog — Historique des actions d'administration
# ─────────────────────────────────────────────
class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinets.id", ondelete="CASCADE"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    
    action_type = Column(String(50), nullable=False) # CREATE, UPDATE, DELETE, VALIDATE
    entity_type = Column(String(50), nullable=False) # AGENT, SOCIETE, CABINET, FACTURE
    entity_id = Column(Integer, nullable=True)
    
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    cabinet = relationship("Cabinet")
    agent = relationship("Agent")

# Fin du fichier modèles.


# ──────────────────────────────────────────────────────────────────────────
# IMMOBILISATION — Actifs immobilisés (corporels, incorporels, financiers)
# ──────────────────────────────────────────────────────────────────────────
class Immobilisation(Base):
    """
    Représente un bien immobilisé acquis par la société.
    Supporte le calcul du plan d'amortissement (linéaire ou dégressif).
    """
    __tablename__ = "immobilisations"

    id = Column(Integer, primary_key=True, index=True)
    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id"), nullable=True, index=True)  # Lien optionnel à la facture source

    # Description
    designation = Column(String(500), nullable=False)
    categorie = Column(String(30), nullable=True, server_default="CORPORELLE")
    # CORPORELLE (matériel, véhicule) / INCORPORELLE (logiciel, brevet) / FINANCIERE (titres)

    # Acquisition
    date_acquisition = Column(Date, nullable=False)
    valeur_acquisition = Column(Numeric(15, 2), nullable=False)  # HT
    tva_acquisition = Column(Numeric(15, 2), nullable=True)      # TVA récupérable

    # Amortissement
    duree_amortissement = Column(Integer, nullable=False)         # En années
    taux_amortissement = Column(Numeric(6, 4), nullable=True)     # Calculé automatiquement
    methode = Column(String(20), nullable=False, server_default="LINEAIRE")  # LINEAIRE / DEGRESSIF

    # Comptes PCM associés
    compte_actif_pcm = Column(String(10), nullable=True)          # ex: 2355 (Matériel informatique)
    compte_amort_pcm = Column(String(10), nullable=True)          # ex: 2835 (Amort. matériel info)
    compte_dotation_pcm = Column(String(10), nullable=True)       # ex: 6193 (Dotations)

    # Statut
    statut = Column(String(20), nullable=False, server_default="ACTIF")
    # ACTIF / CEDE / MIS_EN_REBUT / TOTALEMENT_AMORTI

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    societe = relationship("Societe", back_populates="immobilisations")
    facture = relationship("Facture")
    lignes_amortissement = relationship("LigneAmortissement", back_populates="immobilisation", cascade="all, delete-orphan")


# ──────────────────────────────────────────────────────────────────────────
# LIGNE D'AMORTISSEMENT — Plan d'amortissement annuel
# ──────────────────────────────────────────────────────────────────────────
class LigneAmortissement(Base):
    """
    Représente une ligne du plan d'amortissement pour une immobilisation.
    Une ligne par année de la durée d'amortissement.
    """
    __tablename__ = "lignes_amortissement"

    id = Column(Integer, primary_key=True, index=True)
    immobilisation_id = Column(Integer, ForeignKey("immobilisations.id", ondelete="CASCADE"), nullable=False, index=True)

    annee = Column(Integer, nullable=False)                              # Année comptable
    dotation_annuelle = Column(Numeric(15, 2), nullable=False)           # Dotation de l'année
    amortissement_cumule = Column(Numeric(15, 2), nullable=False)        # Cumul des dotations
    valeur_nette_comptable = Column(Numeric(15, 2), nullable=False)      # VNC = Valeur - Cumul

    # Écriture comptable générée pour cet exercice
    ecriture_generee = Column(Boolean, default=False)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    immobilisation = relationship("Immobilisation", back_populates="lignes_amortissement")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE PAIE — Gestion de la rémunération du personnel
# ══════════════════════════════════════════════════════════════════════════════

class Employe(Base):
    """
    Représente un employé d'une société cliente.
    Contient les données servant au calcul du bulletin de paie.
    """
    __tablename__ = "employes"

    id             = Column(Integer, primary_key=True, index=True)
    societe_id     = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)

    # Identité
    nom            = Column(String(100), nullable=False)
    prenom         = Column(String(100), nullable=True)
    cin            = Column(String(20), nullable=True, unique=False)
    date_naissance = Column(Date, nullable=True)

    # Emploi
    poste          = Column(String(200), nullable=True)
    date_embauche  = Column(Date, nullable=False)
    type_contrat   = Column(String(20), nullable=True, server_default="CDI")  # CDI / CDD / INTERIM

    # Salaire
    salaire_base   = Column(Numeric(12, 2), nullable=False)    # Salaire de base brut (MAD)
    nb_enfants     = Column(Integer, nullable=False, default=0) # Pour déduction IR
    anciennete_pct = Column(Numeric(5, 2), nullable=True, default=0)  # Prime d'ancienneté %

    # CNSS
    numero_cnss    = Column(String(30), nullable=True)
    affiliee_cnss  = Column(Boolean, default=True)

    # Statut
    statut         = Column(String(20), nullable=False, server_default="ACTIF")  # ACTIF / SUSPENDU / REVOQUE

    created_at     = Column(DateTime, nullable=False, server_default=func.now())
    updated_at     = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    societe   = relationship("Societe", back_populates="employes")
    bulletins = relationship("BulletinPaie", back_populates="employe", cascade="all, delete-orphan")


class BulletinPaie(Base):
    """
    Bulletin de paie mensuel d'un employé.
    Stocke le résultat du calcul (brut, cotisations, net).
    """
    __tablename__ = "bulletins_paie"

    id             = Column(Integer, primary_key=True, index=True)
    employe_id     = Column(Integer, ForeignKey("employes.id", ondelete="CASCADE"), nullable=False, index=True)

    mois           = Column(Integer, nullable=False)   # 1-12
    annee          = Column(Integer, nullable=False)

    # Salaire brut
    salaire_base   = Column(Numeric(12, 2), nullable=False)
    prime_anciennete = Column(Numeric(12, 2), nullable=True, default=0)
    autres_gains   = Column(Numeric(12, 2), nullable=True, default=0)  # Primes, heures sup...
    salaire_brut   = Column(Numeric(12, 2), nullable=False)  # = base + ancienneté + primes

    # Cotisations salariales
    cnss_salarie   = Column(Numeric(10, 2), nullable=False, default=0)  # 4.48% plafonné
    amo_salarie    = Column(Numeric(10, 2), nullable=False, default=0)  # 2.26%
    ir_retenu      = Column(Numeric(10, 2), nullable=False, default=0)  # Barème progressif
    total_retenues = Column(Numeric(10, 2), nullable=False, default=0)

    # Cotisations patronales (charge de l'entreprise)
    cnss_patronal  = Column(Numeric(10, 2), nullable=False, default=0)  # 10.64% plafonné
    amo_patronal   = Column(Numeric(10, 2), nullable=False, default=0)  # 3.94%
    total_patronal = Column(Numeric(10, 2), nullable=False, default=0)

    # Net
    salaire_net    = Column(Numeric(12, 2), nullable=False)  # Brut - cotisations salariales
    cout_total_employeur = Column(Numeric(12, 2), nullable=True)  # Brut + cotisations patronales

    # Écriture comptable liée
    journal_entry_id = Column(Integer, ForeignKey("ecritures_journal.id"), nullable=True)

    statut         = Column(String(20), nullable=False, server_default="BROUILLON")  # BROUILLON / VALIDE
    valide_par     = Column(String(100), nullable=True)
    valide_at      = Column(DateTime, nullable=True)

    created_at     = Column(DateTime, nullable=False, server_default=func.now())

    # Relations
    employe        = relationship("Employe", back_populates="bulletins")
    lignes         = relationship("LignePaie", back_populates="bulletin", cascade="all, delete-orphan")
    journal_entry  = relationship("JournalEntry")


class LignePaie(Base):
    """
    Ligne de détail d'un bulletin de paie.
    Chaque ligne représente un GAIN (positif) ou une RETENUE (négatif).
    """
    __tablename__ = "lignes_paie"

    id             = Column(Integer, primary_key=True, index=True)
    bulletin_id    = Column(Integer, ForeignKey("bulletins_paie.id", ondelete="CASCADE"), nullable=False, index=True)

    libelle        = Column(String(300), nullable=False)   # ex: "Salaire de base", "CNSS salarié"
    type_ligne     = Column(String(10), nullable=False)    # GAIN / RETENUE
    montant        = Column(Numeric(12, 2), nullable=False)
    taux           = Column(Numeric(6, 4), nullable=True)  # ex: 0.0448 pour CNSS
    base_calcul    = Column(Numeric(12, 2), nullable=True) # Sur quelle assiette est calculé ce montant

    ordre          = Column(Integer, nullable=True, default=0)  # Ordre d'affichage

    # Relations
    bulletin       = relationship("BulletinPaie", back_populates="lignes")
