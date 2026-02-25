from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


# ─────────────────────────────────────────────
# SOCIETE (compatible avec  ancien code)
# ─────────────────────────────────────────────
class SocieteIn(BaseModel):
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


class SocieteUpdate(BaseModel):
    raison_sociale: Optional[str] = None
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    adresse: Optional[str] = None


class SocieteOut(BaseModel):
    id: int
    cabinet_id: Optional[int] = None  # Peut être NULL pour compatibilité
    raison_sociale: str
    if_fiscal: Optional[str] = None
    ice: Optional[str] = None
    rc: Optional[str] = None
    patente: Optional[str] = None
    adresse: Optional[str] = None
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

    ded_file_path: Optional[str] = None
    ded_pdf_path: Optional[str] = None
    ded_xlsx_path: Optional[str] = None

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
# ECRITURES (HEADER + LIGNES)
# ─────────────────────────────────────────────
class EcritureLigneOut(BaseModel):
    id: int
    ecriture_id: int
    compte: str
    libelle: Optional[str] = None
    debit: float
    credit: float

    model_config = ConfigDict(from_attributes=True)


class EcritureOut(BaseModel):
    id: int
    societe_id: int
    facture_id: int
    operation: str
    journal: str
    numero_piece: str
    date_operation: date
    tiers_nom: Optional[str] = None
    statut: str
    created_at: datetime
    validated_at: Optional[datetime] = None
    libelle: Optional[str] = None
    total_debit: float
    total_credit: float
    lignes: List[EcritureLigneOut] = []

    model_config = ConfigDict(from_attributes=True)


class GenererEcrituresResponse(BaseModel):
    facture_id: int
    journal: str
    total_debit: float
    total_credit: float
    ecriture: EcritureOut


# ═════════════════════════════════════════════
# CABINET → AGENTS → SOCIÉTÉS (Multi-Cabinet)
# ═════════════════════════════════════════════

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


# ─────────────────────────────────────────────
# SESSION / CONTEXT SCHEMAS
# ─────────────────────────────────────────────
class SessionContext(BaseModel):
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


