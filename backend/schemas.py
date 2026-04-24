from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

"""
schemas.py — Modèles Pydantic pour la validation des données (entrée/sortie API).
Ces schémas assurent que les données reçues et envoyées sont au bon format.
"""


# ─────────────────────────────────────────────
# SOCIETE (compatible avec  ancien code)
# ─────────────────────────────────────────────
class SocieteIn(BaseModel):
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None
    cnss: Optional[str] = None


class SocieteUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None
    cnss: Optional[str] = None


# ──────────────────────────────────────────────────────────────────────────
# SCHÉMAS SOCIÉTÉ
# ──────────────────────────────────────────────────────────────────────────
class SocieteOut(BaseModel):
    """Schéma de sortie pour une société cliente."""
    id: int
    cabinet_id: Optional[int] = None  # Peut être NULL pour compatibilité
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    patente: Optional[str] = None
    adresse: Optional[str] = None
    cnss: Optional[str] = None
    logo_path: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# FACTURE
# ─────────────────────────────────────────────
class FactureOut(BaseModel):
    id: int
    societe_id: int

    operation_type: Optional[str] = None
    operation_confidence: Optional[float] = None

    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    status: str

    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    devise: Optional[str] = None

    # Champs v2
    supplier_name: Optional[str] = None
    supplier_ice: Optional[str] = None
    supplier_if: Optional[str] = None
    supplier_rc: Optional[str] = None
    supplier_address: Optional[str] = None
    client_name: Optional[str] = None
    client_ice: Optional[str] = None
    client_if: Optional[str] = None
    due_date: Optional[date] = None
    invoice_type: Optional[str] = None
    payment_mode: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class FactureUpdate(BaseModel):
    fournisseur: Optional[str] = None
    date_facture: Optional[date] = None
    numero_facture: Optional[str] = None
    designation: Optional[str] = None

    montant_ht: Optional[float] = None
    montant_tva: Optional[float] = None
    montant_ttc: Optional[float] = None

    status: Optional[str] = None

    if_frs: Optional[str] = None
    ice_frs: Optional[str] = None
    taux_tva: Optional[float] = None
    id_paie: Optional[str] = None
    date_paie: Optional[date] = None

    operation_type: Optional[str] = None
    operation_confidence: Optional[float] = None

    devise: Optional[str] = None
    
    # Nouveaux champs v2
    due_date: Optional[date] = None
    invoice_type: Optional[str] = None
    payment_mode: Optional[str] = None
    supplier_name: Optional[str] = None
    supplier_ice: Optional[str] = None
    supplier_if: Optional[str] = None
    supplier_rc: Optional[str] = None
    supplier_address: Optional[str] = None
    client_name: Optional[str] = None
    client_ice: Optional[str] = None
    client_if: Optional[str] = None
    client_address: Optional[str] = None

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None


# ─────────────────────────────────────────────
# CABINET → AGENTS → SOCIÉTÉS (Multi-Cabinet)
# ─────────────────────────────────────────────

# ─────────────────────────────────────────────
# CABINET SCHEMAS
# ─────────────────────────────────────────────
class CabinetCreate(BaseModel):
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None


class CabinetUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None


class CabinetOut(BaseModel):
    id: int
    nom: str
    email: Optional[str] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    logo_path: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ─────────────────────────────────────────────
# AGENT (UTILISATEUR) SCHEMAS
# ─────────────────────────────────────────────
class AgentCreate(BaseModel):
    username: str
    email: str
    password: str  # Sera hasé en backend
    nom: Optional[str] = None
    prenom: Optional[str] = None
    is_admin: bool = False
    is_super_admin: bool = False


class AgentUpdate(BaseModel):
    email: Optional[str] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    password: Optional[str] = None  # Pour changement de mot de passe


class AgentOut(BaseModel):
    id: int
    cabinet_id: int
    username: str
    email: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    is_active: bool
    is_admin: bool
    is_super_admin: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgentLogin(BaseModel):
    username: str
    password: str


class AgentLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    agent: AgentOut
    cabinets: List[CabinetOut] = []


# ──────────────────────────────────────────────────────────────────────────
# SCHÉMAS SESSION / CONTEXTE
# ──────────────────────────────────────────────────────────────────────────
class SessionContext(BaseModel):
    """Contient les informations de la session active (Agent + Société sélectionnée)."""
    agent_id: int
    cabinet_id: int
    societe_id: int
    username: str
    societe_raison_sociale: str


class SelectSocieteRequest(BaseModel):
    cabinet_id: int
    societe_id: int


class CompteurFacturationOut(BaseModel):
    id: int
    societe_id: int
    annee: int
    dernier_numero: int

    model_config = ConfigDict(from_attributes=True)


class JournalComptableOut(BaseModel):
    id: int
    societe_id: int
    code: str
    label: str
    type: str

    model_config = ConfigDict(from_attributes=True)


class JournalComptableCreate(BaseModel):
    code: str
    label: str
    type: str


class SocieteCreateUpdate(BaseModel):
    raison_sociale: str
    ice: Optional[str] = None
    if_fiscal: Optional[str] = None
    rc: Optional[str] = None
    patente: Optional[str] = None
    adresse: Optional[str] = None


class SocieteWithAgents(SocieteOut):
    agents: List[AgentOut] = []


class AgentStats(BaseModel):
    total_factures_validees: int
    total_societes_gerees: int
    cabinet_nom: str


class GlobalStats(BaseModel):
    total_cabinets: int
    total_agents: int
    total_societes: int
    total_factures: int


class ActivityOut(BaseModel):
    id: str  # Pour React keys
    type: str  # CABINET, VALIDATION, ALERT
    title: str
    time: str
    dot_color: str


class ActivitiesResponse(BaseModel):
    activities: List[ActivityOut]


class ActionLogOut(BaseModel):
    id: int
    cabinet_id: Optional[int] = None
    agent_id: Optional[int] = None
    agent_username: Optional[str] = None # Pour faciliter l'affichage
    action_type: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ActionLogResponse(BaseModel):
    logs: List[ActionLogOut]
    total: int



# ──────────────────────────────────────────────────────────────────────────
# SCHÉMAS PAIE
# ──────────────────────────────────────────────────────────────────────────
class LignePaieOut(BaseModel):
    id: int = 0
    libelle: str
    type_ligne: str
    montant: float
    taux: Optional[float] = None
    base_calcul: Optional[float] = None
    ordre: int = 0

    model_config = ConfigDict(from_attributes=True)


class BulletinPaieCreate(BaseModel):
    employe_id: int
    mois: int
    annee: int
    primes: Optional[float] = 0
    heures_sup: Optional[float] = 0


class BulletinPaieOut(BaseModel):
    id: int
    employe_id: int
    employe_nom: Optional[str] = None
    employe_cin: Optional[str] = None
    employe_cnss: Optional[str] = None
    employe_date_embauche: Optional[date] = None
    societe_nom: Optional[str] = None
    societe_adresse: Optional[str] = None
    societe_ice: Optional[str] = None
    societe_rc: Optional[str] = None
    societe_cnss: Optional[str] = None
    mois: int
    annee: int
    salaire_base: float
    prime_anciennete: float
    autres_gains: float
    salaire_brut: float
    cnss_salarie: float
    amo_salarie: float
    ir_retenu: float
    total_retenues: float
    cnss_patronal: float
    amo_patronal: float
    total_patronal: float
    salaire_net: float
    cout_total_employeur: Optional[float] = None
    statut: str
    created_at: datetime
    lignes: List[LignePaieOut] = []

    model_config = ConfigDict(from_attributes=True)


# ──────────────────────────────────────────────────────────────────────────
# SCHÉMAS TRANSMISSION (Client / Boîte de réception)
# ──────────────────────────────────────────────────────────────────────────
class UtilisateurClientCreate(BaseModel):
    username: str
    email: str
    password: str
    nom: Optional[str] = None
    prenom: Optional[str] = None


class UtilisateurClientOut(BaseModel):
    id: int
    societe_id: int
    username: str
    email: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentTransmisOut(BaseModel):
    id: int
    societe_id: int
    client_id: Optional[int] = None
    file_path: str
    file_name: str
    type_document: str
    statut: str
    notes_client: Optional[str] = None
    date_upload: datetime
    date_traitement: Optional[datetime] = None
    
    facture_id: Optional[int] = None
    
    client: Optional[UtilisateurClientOut] = None

    model_config = ConfigDict(from_attributes=True)


# ──────────────────────────────────────────────────────────────────────────
# MANUEL JOURNAL ENTRY SCHEMAS
# ──────────────────────────────────────────────────────────────────────────

class ManualEntryLine(BaseModel):
    account_code: str
    account_label: str = ""
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    tiers_name: Optional[str] = None

class ManualEntryCreate(BaseModel):
    journal_code: str
    entry_date: date
    reference: str = ""
    description: str = ""
    lines: List[ManualEntryLine]


# ──────────────────────────────────────────────────────────────────────────
# AI PERFORMANCE SCHEMAS
# ──────────────────────────────────────────────────────────────────────────

class AIHistoryPoint(BaseModel):
    date: str
    count: int

class AIPerformanceResponse(BaseModel):
    accuracy: float
    avg_time: float
    volume: int
    correction_rate: float
    history: List[AIHistoryPoint]


# ──────────────────────────────────────────────────────────────────────────
# MAPPING FOURNISSEUR SCHEMAS
# ──────────────────────────────────────────────────────────────────────────
class SupplierMappingCreate(BaseModel):
    supplier_ice: str
    pcm_account_code: str


# ──────────────────────────────────────────────────────────────────────────
# DEMANDE D'ACCÈS SCHEMAS
# ──────────────────────────────────────────────────────────────────────────

class DemandeAccesCreate(BaseModel):
    nom_complet: str
    entreprise: str
    email: str
    telephone: Optional[str] = None
    message: Optional[str] = None
    cabinet_id: Optional[int] = None
    nom_cabinet: Optional[str] = None

class DemandeAccesValidation(BaseModel):
    statut: str
    username: Optional[str] = None
    password: Optional[str] = None

class DemandeAccesUpdate(BaseModel):
    nom_complet: Optional[str] = None
    entreprise: Optional[str] = None
    email: Optional[str] = None
    telephone: Optional[str] = None
    message: Optional[str] = None

class DemandeAccesOut(BaseModel):
    id: int
    nom_complet: str
    entreprise: str
    email: str
    telephone: Optional[str] = None
    message: Optional[str] = None
    statut: str
    cabinet_id: Optional[int] = None
    created_at: datetime
    
    generated_username: Optional[str] = None
    generated_password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ──────────────────────────────────────────────────────────────────────────
# SCHÉMAS BILAN ET RÉPORTING
# ──────────────────────────────────────────────────────────────────────────

class BalanceLine(BaseModel):
    account_code: str
    account_label: Optional[str] = None
    brut: Decimal
    amortissement: Decimal
    net: Decimal
    type: str  # DEBIT ou CREDIT

class BilanSection(BaseModel):
    libelle: str
    lignes: List[BalanceLine]
    total_brut: Optional[Decimal] = None
    total_amortissement: Optional[Decimal] = None
    total: Decimal

class BilanOut(BaseModel):
    societe_id: int
    annee: int
    actif: List[BilanSection]
    passif: List[BilanSection]
    total_actif: Decimal
    total_passif: Decimal
    resultat: Decimal
    is_balanced: bool
