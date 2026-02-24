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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    # Relations
    cabinet = relationship("Cabinet", back_populates="agents")
    # ManyToMany: Agent peut gérer plusieurs Sociétés
    societes = relationship(
        "Societe",
        secondary="agent_societes",
        back_populates="agents"
    )


# Table d'association Many-to-Many : Agent-Societe
agent_societes = Table(
    "agent_societes",
    Base.metadata,
    Column("agent_id", Integer, ForeignKey("agents.id", ondelete="CASCADE"), primary_key=True),
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
        secondary="agent_societes",
        back_populates="societes"
    )
    factures = relationship("Facture", back_populates="societe", foreign_keys="[Facture.societe_id]", cascade="all, delete-orphan")
    compteurs = relationship("CompteurFacturation", back_populates="societe", cascade="all, delete-orphan")


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


# ─────────────────────────────────────────────
# Facture — En-tête (Tableau 1)
# Éléments obligatoires DGI
# ─────────────────────────────────────────────
class Facture(Base):
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

    # Champs legacy (compatibilité)
    fournisseur = Column(String, nullable=True)
    operation_type = Column(String(50), nullable=True)
    operation_confidence = Column(Float, nullable=True)
    if_frs = Column(String(50), nullable=True)
    ice_frs = Column(String(50), nullable=True)
    designation = Column(String(255), nullable=True)
    id_paie = Column(String(50), nullable=True)
    date_paie = Column(Date, nullable=True)
    ded_file_path = Column(String(255), nullable=True)
    ded_pdf_path = Column(String(255), nullable=True)
    ded_xlsx_path = Column(String(255), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    societe = relationship("Societe", back_populates="factures", foreign_keys=[societe_id])
    lines = relationship("InvoiceLine", back_populates="facture", cascade="all, delete-orphan")
    journal_entries = relationship("JournalEntry", back_populates="facture", cascade="all, delete-orphan")

    def get_dgi_flags(self):
        if self.dgi_flags:
            try:
                return json.loads(self.dgi_flags)
            except Exception:
                return []
        return []

    def set_dgi_flags(self, flags: list):
        self.dgi_flags = json.dumps(flags, ensure_ascii=False)


# ─────────────────────────────────────────────
# InvoiceLine — Lignes produits (Tableau 2)
# ─────────────────────────────────────────────
class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

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


# ─────────────────────────────────────────────
# PcmAccount — Référentiel Plan Comptable Marocain
# ─────────────────────────────────────────────
class PcmAccount(Base):
    __tablename__ = "pcm_accounts"

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
    __tablename__ = "supplier_mappings"

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
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False, index=True)

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
    entry_lines = relationship("EntryLine", back_populates="journal_entry", cascade="all, delete-orphan")


# ─────────────────────────────────────────────
# EntryLine — Lignes débit/crédit
# ─────────────────────────────────────────────
class EntryLine(Base):
    __tablename__ = "entry_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id", ondelete="CASCADE"), nullable=False, index=True)
    invoice_line_id = Column(Integer, ForeignKey("invoice_lines.id", ondelete="SET NULL"), nullable=True)

    line_order = Column(Integer, nullable=True)
    account_code = Column(String(10), nullable=False)
    account_label = Column(String(255), nullable=True)
    debit = Column(Numeric(15, 2), nullable=False, server_default="0")
    credit = Column(Numeric(15, 2), nullable=False, server_default="0")
    tiers_name = Column(String(255), nullable=True)
    tiers_ice = Column(String(15), nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=func.now())

    journal_entry = relationship("JournalEntry", back_populates="entry_lines")


# ─────────────────────────────────────────────
# Legacy: EcritureComptable + EcritureLigne
# (conservés pour compatibilité)
# ─────────────────────────────────────────────
class EcritureComptable(Base):
    __tablename__ = "ecritures_comptables"

    id = Column(Integer, primary_key=True, index=True)
    societe_id = Column(Integer, ForeignKey("societes.id"), nullable=False, index=True)
    facture_id = Column(Integer, ForeignKey("factures.id", ondelete="CASCADE"), nullable=False, index=True)

    operation = Column(String(50), nullable=False)
    numero_piece = Column(String(50), nullable=False, index=True)
    date_operation = Column(Date, nullable=False, index=True)
    tiers_nom = Column(String(255), nullable=True)
    journal = Column(String(10), nullable=False, server_default="OD", index=True)
    statut = Column(String(50), nullable=False, server_default="brouillon")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    validated_at = Column(DateTime, nullable=True)
    libelle = Column(String(255), nullable=True)
    total_debit = Column(Float, nullable=False, server_default="0")
    total_credit = Column(Float, nullable=False, server_default="0")

    societe = relationship("Societe")
    facture = relationship("Facture")
    lignes = relationship(
        "EcritureLigne",
        back_populates="ecriture",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class EcritureLigne(Base):
    __tablename__ = "ecritures_lignes"

    id = Column(Integer, primary_key=True, index=True)
    ecriture_id = Column(Integer, ForeignKey("ecritures_comptables.id", ondelete="CASCADE"), nullable=False, index=True)
    compte = Column(String(20), nullable=False)
    libelle = Column(String(255), nullable=True)
    debit = Column(Float, nullable=False, server_default="0")
    credit = Column(Float, nullable=False, server_default="0")

    ecriture = relationship("EcritureComptable", back_populates="lignes")
