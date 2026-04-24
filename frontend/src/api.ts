import axios from 'axios'
import { getSessionContext } from './utils/tokenDecoder'

// Force /api to use Vite's proxy - DO NOT use VITE_API_URL environment variable
// because Vite variables are build-time embedded, and the Docker env var might
// be resolving to 'http://backend:8000' which is an internal Docker hostname
// not accessible from the browser.
const API_BASE = '/api'

console.log('[API] Initializing with base URL:', API_BASE)

export interface AIPerformanceEntry {
  id: number;
  reference?: string;
}

export interface AIHistoryPoint {
  date: string;
  count: number;
}

export interface AIPerformanceResponse {
  accuracy: number;
  avg_time: number;
  volume: number;
  correction_rate: number;
  history: AIHistoryPoint[];
}

const api = axios.create({
    baseURL: API_BASE,
    timeout: 60000,
})

/**
 * Intercepteur de requêtes pour injecter le token d'authentification.
 * Gère deux types de tokens :
 * - access_token : Token principal de l'agent.
 * - session_token : Token spécifique à la société sélectionnée (contexte cabinet).
 */
api.interceptors.request.use((config) => {
    try {
        const client = typeof window !== 'undefined' ? localStorage.getItem('client_token') : null
        const session = typeof window !== 'undefined' ? localStorage.getItem('session_token') : null
        const access = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

        // Client token is only used for client-portal specific endpoints
        const url = config.url || ''
        const isClientRoute = url.startsWith('/client') || url === '/transmission/upload' || url.startsWith('/transmission/client')
        const tokenToUse = (isClientRoute && client) ? client : (session || access)
        const tokenType = (isClientRoute && client) ? 'CLIENT' : (session ? 'SESSION' : (access ? 'ACCESS' : 'NONE'))

        console.log(`[Axios Interceptor] Request to: ${config.url} | Token: ${tokenType}`)

        if (tokenToUse) {
            config.headers = config.headers || {}
            config.headers['Authorization'] = `Bearer ${tokenToUse}`
        }
    } catch (e) {
        console.error('[Axios Interceptor] Error:', e)
    }
    return config
})

// Add error interceptor for better debugging
api.interceptors.response.use(
    response => response,
    error => {
        console.error('[Axios Error]', {
            message: error.message,
            code: error.code,
            status: error.response?.status,
            data: error.response?.data,
            url: error.config?.url
        })
        return Promise.reject(error)
    }
)

export interface Facture {
    id: number
    status: string
    numero_facture: string | null
    date_facture: string | null
    due_date: string | null
    invoice_type: string | null
    supplier_name: string | null
    supplier_ice: string | null
    supplier_if: string | null
    supplier_rc: string | null
    supplier_address: string | null
    client_name: string | null
    client_ice: string | null
    client_if: string | null
    client_address: string | null
    montant_ht: number | null
    montant_tva: number | null
    montant_ttc: number | null
    taux_tva: number | null
    devise: string | null
    payment_mode: string | null
    payment_terms: string | null
    extraction_source: string | null
    dgi_flags: DgiFlag[]
    file_path: string | null
    created_at: string | null
}

export interface DgiFlag {
    code: string
    message: string
    severity: 'ERROR' | 'WARNING'
    field: string
}

export interface InvoiceLine {
    id: number
    line_number: number | null
    description: string | null
    quantity: number | null
    unit: string | null
    unit_price_ht: number | null
    line_amount_ht: number | null
    tva_rate: number | null
    tva_amount: number | null
    line_amount_ttc: number | null
    pcm_class: number | null
    pcm_account_code: string | null
    pcm_account_label: string | null
    classification_confidence: number | null
    classification_reason: string | null
    is_corrected: boolean
}

export interface EntryLine {
    id: number
    line_order: number | null
    account_code: string
    account_label: string | null
    debit: number
    credit: number
    tiers_name: string | null
    tiers_ice: string | null
}

export interface JournalEntry {
    id: number
    journal_code: string
    entry_date: string | null
    reference: string | null
    description: string | null
    is_validated: boolean
    total_debit: number
    total_credit: number
    entry_lines: EntryLine[]
}

export interface LignePaie {
    id: number
    libelle: string
    type_ligne: 'GAIN' | 'RETENUE'
    montant: number
    taux: number | null
    base_calcul: number | null
    ordre: number
}

export interface BulletinPaie {
    id: number
    employe_id: number
    employe_nom?: string
    employe_cin?: string
    employe_cnss?: string
    employe_date_embauche?: string
    societe_nom?: string
    societe_adresse?: string
    societe_ice?: string
    societe_rc?: string
    societe_cnss?: string

    mois: number
    annee: number
    salaire_base: number
    prime_anciennete: number
    autres_gains: number
    salaire_brut: number
    cnss_salarie: number
    amo_salarie: number
    ir_retenu: number
    total_retenues: number
    cnss_patronal: number
    amo_patronal: number
    total_patronal: number
    salaire_net: number
    cout_total_employeur: number | null
    statut: 'BROUILLON' | 'VALIDE'
    created_at: string
    lignes: LignePaie[]
}

export interface Employe {
    id: number
    nom: string
    prenom: string | null
    cin: string | null
    poste: string | null
    date_embauche: string
    salaire_base: number
    nb_enfants: number
    anciennete_pct: number
    numero_cnss?: string
}

export interface LigneAmort {
    annee: number
    dotation_annuelle: number
    amortissement_cumule: number
    valeur_nette_comptable: number
    ecriture_generee: boolean
}

export interface Immo {
    id: number
    designation: string
    categorie: string
    date_acquisition: string
    valeur_acquisition: number
    tva_acquisition: number
    duree_amortissement: number
    taux_amortissement: number
    methode: string
    compte_actif_pcm: string
    compte_amort_pcm: string
    compte_dotation_pcm: string
    statut: string
    plan_amortissement?: LigneAmort[]
}

export interface LigneReleve {
    id: number
    date_operation: string
    description: string | null
    debit: number
    credit: number
    is_rapproche: boolean
    entry_line_id: number | null
}

export interface ReleveBancaire {
    id: number
    date_import: string
    date_debut: string | null
    date_fin: string | null
    solde_initial: number | null
    solde_final: number | null
    banque_nom: string | null
    file_name: string | null
    lignes_count?: number
    lignes?: LigneReleve[]
}


export interface UtilisateurClient {
    id: number
    societe_id: number
    username: string
    email: string
    nom: string | null
    prenom: string | null
    is_active: boolean
    created_at: string
}

export interface DocumentTransmis {
    id: number
    societe_id: number
    client_id: number | null
    file_path: string
    file_name: string
    type_document: string
    statut: string
    notes_client: string | null
    date_upload: string
    date_traitement: string | null
    client?: UtilisateurClient
}

export interface BalanceLine {
    account_code: string
    account_label: string | null
    total_debit: number
    total_credit: number
    balance: number
    type: 'DEBIT' | 'CREDIT'
}

export interface BilanSection {
    libelle: string
    lignes: BalanceLine[]
    total: number
}

export interface BilanOut {
    societe_id: number
    annee: number
    actif: BilanSection[]
    passif: BilanSection[]
    total_actif: number
    total_passif: number
    resultat: number
    is_balanced: boolean
}

// ── API calls ──────────────────────────────────────────────

/**
 * Service central pour tous les appels vers l'API Backend.
 * Chaque méthode correspond à un endpoint FastAPI.
 */
export const apiService = {
    getBilan: (annee: number, mois?: number, validatedOnly: boolean = true) =>
        api.get('/bilan/comptable', { params: { annee, mois, validated_only: validatedOnly } }).then(r => r.data),

    // ... existants
    listFactures: (status?: string) =>
        api.get('/factures/', { params: { status } }).then(r => r.data),

    uploadFacture: (file: File) => {
        const form = new FormData()
        form.append('file', file)
        return api.post(`/factures/upload`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 300000
        }).then(r => r.data)
    },

    extractFacture: (id: number) =>
        api.post(`/factures/${id}/extract`, {}, { timeout: 300000 }).then(r => r.data),
    classifyFacture: (id: number) =>
        api.post(`/factures/${id}/classify`, {}, { timeout: 300000 }).then(r => r.data),
    generateEntries: (id: number) =>
        api.post(`/factures/${id}/generate-entries`, {}, { timeout: 300000 }).then(r => r.data),
    getFacture: (id: number) => api.get(`/factures/${id}`).then(r => r.data),
    getFactureLines: (id: number) => api.get(`/factures/${id}/lines`).then(r => r.data),
    getFactureEntries: (id: number) => api.get(`/factures/${id}/entries`).then(r => r.data),
    validateFacture: (id: number) => api.post(`/factures/${id}/validate`).then(r => r.data),
    rejectFacture: (id: number, reason: string) =>
        api.post(`/factures/${id}/reject?reason=${encodeURIComponent(reason)}`).then(r => r.data),
    updateInvoiceLine: (lineId: number, data: Partial<InvoiceLine>) =>
        api.put(`/factures/invoice-lines/${lineId}`, data).then(r => r.data),
    updateEntryLine: (lineId: number, data: Partial<EntryLine>) =>
        api.put(`/factures/entry-lines/${lineId}`, data).then(r => r.data),

    getPcmAccounts: (pcmClass?: number) =>
        api.get('/pcm/accounts', { params: { pcm_class: pcmClass } }).then(r => r.data),

    listSocietes: () => api.get('/societes/').then(r => r.data),
    createSociete: (data: { raison_sociale: string; ice?: string; if_fiscal?: string }) =>
        api.post('/societes/', data).then(r => r.data),

    getProfile: (token: string) => api.get(`/auth/me?token=${token}`).then(r => r.data),
    getAgentStats: (token: string) => api.get(`/auth/stats?token=${token}`).then(r => r.data),
    getFileUrl: (id: number) => `${API_BASE}/factures/${id}/file`,
    getFileBlob: (id: number) => api.get(`/factures/${id}/file`, { responseType: 'blob' }).then(r => r.data),

    listMappings: () => api.get('/mappings/').then(r => r.data),
    createMapping: (data: { supplier_ice: string; pcm_account_code: string }) =>
        api.post('/mappings/', data).then(r => r.data),
    deleteMapping: (id: number) => api.delete(`/mappings/${id}`).then(r => r.data),

    deleteFacture: (id: number) => api.delete(`/factures/${id}`).then(r => r.data),
    updateFacture: (id: number, data: Partial<Facture>) => api.put(`/factures/${id}`, data).then(r => r.data),
    updateProfile: (data: any) => api.put('/auth/profile', data).then(r => r.data),

    // ── Admin Routes ──────────────────────────────────────────
    adminListAgents: () => api.get('/admin/agents').then(r => r.data),
    adminCreateAgent: (data: any, cabinetId: string) => api.post(`/admin/agents?cabinet_id=${cabinetId}`, data).then(r => r.data),
    adminUpdateAgent: (id: number, data: any) => api.put(`/admin/agents/${id}`, data).then(r => r.data),
    adminDeleteAgent: (id: number) => api.delete(`/admin/agents/${id}`).then(r => r.data),
    adminListCabinets: () => api.get('/admin/cabinets').then(r => r.data),
    adminCreateCabinet: (data: any) => api.post('/admin/cabinets', data).then(r => r.data),
    adminUpdateCabinet: (id: number, data: any) => api.put(`/admin/cabinets/${id}`, data).then(r => r.data),
    adminDeleteCabinet: (id: number) => api.delete(`/admin/cabinets/${id}`).then(r => r.data),
    adminListSocietes: () => api.get('/admin/societes').then(r => r.data),
    adminCreateSociete: (data: any, cabinetId: string) => api.post(`/admin/societes?cabinet_id=${cabinetId}`, data).then(r => r.data),
    adminUpdateSociete: (id: number, data: any) => api.put(`/admin/societes/${id}`, data).then(r => r.data),
    adminDeleteSociete: (id: number) => api.delete(`/admin/societes/${id}`).then(r => r.data),
    adminGetProfile: () => api.get('/admin/profile').then(r => r.data),
    adminUpdateProfile: (data: any) => api.put('/admin/profile', data).then(r => r.data),
    adminGetGlobalStats: () => api.get('/admin/stats/global').then(r => r.data),
    adminGetActivities: () => api.get('/admin/activities').then(r => r.data),
    adminAssignSocieteToAgent: (cabinetId: number, agentId: number, societeId: number) =>
        api.post(`/admin/cabinets/${cabinetId}/agents/assign-societe?agent_id=${agentId}&societe_id=${societeId}`).then(r => r.data),
    adminGetLogs: (offset: number = 0, limit: number = 50) =>
        api.get('/admin/logs', { params: { offset, limit } }).then(r => r.data),

    // ── Client Access Management ─────────────────────────────
    adminListClientUsers: (societeId: number) =>
        api.get(`/admin/societes/${societeId}/clients`).then(r => r.data),
    adminCreateClientUser: (societeId: number, data: { username: string; email: string; password: string; nom?: string; prenom?: string }) =>
        api.post(`/admin/societes/${societeId}/clients`, data).then(r => r.data),
    adminDeleteClientUser: (clientId: number) =>
        api.delete(`/admin/clients/${clientId}`).then(r => r.data),

    // ── Paie Routes ──────────────────────────────────────────
    listBulletins: () => api.get('/paie/').then(r => r.data),
    getBulletin: (id: number) => api.get(`/paie/${id}`).then(r => r.data),
    calculateBulletin: (data: { employe_id: number; mois: number; annee: number; primes?: number; heures_sup?: number }) =>
        api.post('/paie/calcul', data).then(r => r.data),
    saveBulletin: (data: { employe_id: number; mois: number; annee: number; primes?: number; heures_sup?: number }) =>
        api.post('/paie/', data).then(r => r.data),
    validateBulletin: (id: number) => api.post(`/paie/${id}/validate`).then(r => r.data),
    getBulletinEntries: (id: number) => api.get(`/paie/${id}/entries`).then(r => r.data),
    downloadBulletinPdf: async (id: number, filename: string) => {
        const response = await api.get(`/paie/${id}/pdf`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
    },
    downloadBulletinFromEntry: async (entryId: number, filename: string) => {
        const response = await api.get(`/journaux/${entryId}/bulletin-pdf`, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
        const a = document.createElement('a')
        a.href = url
        a.download = filename
        document.body.appendChild(a)
        a.click()
        a.remove()
        window.URL.revokeObjectURL(url)
    },

    // ── Employés Routes ────────────────────────────────────────
    listEmployes: (statut?: string) => api.get('/employes/', { params: { statut } }).then(r => r.data),
    getEmploye: (id: number) => api.get(`/employes/${id}`).then(r => r.data),
    createEmploye: (data: any) => api.post('/employes/', data).then(r => r.data),
    updateEmploye: (id: number, data: any) => api.put(`/employes/${id}`, data).then(r => r.data),

    // ── Immobilisations Routes ──────────────────────────────
    listImmobilisations: (categorie?: string, statut?: string) =>
        api.get('/immobilisations/', { params: { categorie, statut } }).then(r => r.data),
    getImmobilisation: (id: number) => api.get(`/immobilisations/${id}`).then(r => r.data),
    createImmobilisation: (data: any) => api.post('/immobilisations/', data).then(r => r.data),
    generateDotation: (immoId: number, annee: number) =>
        api.post(`/immobilisations/${immoId}/dotation/${annee}`).then(r => r.data),

    // ── Relevés Bancaires ───────────────────────────────────
    listReleves: () => api.get('/releves/').then(r => r.data),
    getReleve: (id: number) => api.get(`/releves/${id}`).then(r => r.data),
    uploadReleve: (file: File) => {
        const form = new FormData()
        form.append('file', file)
        return api.post(`/releves/upload`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 300000
        }).then(r => r.data)
    },

    getSuggestions: (ligneId: number) =>
        api.get(`/releves/suggestions/${ligneId}`).then(r => r.data),

    rapprocher: (ligneReleveId: number, entryLineId: number) =>
        api.post(`/releves/rapprocher`, { ligne_releve_id: ligneReleveId, entry_line_id: entryLineId }).then(r => r.data),

    genererEcriture: (ligneReleveId: number, compteContrepartie: string) =>
        api.post(`/releves/generer-ecriture`, { ligne_releve_id: ligneReleveId, compte_contrepartie: compteContrepartie }).then(r => r.data),

    getAccountSuggestion: (ligneId: number) =>
        api.get(`/releves/suggest-account/${ligneId}`).then(r => r.data),

    getAllSuggestions: (releveId: number) =>
        api.get(`/releves/suggestions-all/${releveId}`).then(r => r.data),

    deleteReleve: (id: number) =>
        api.delete(`/releves/${id}`).then(r => r.data),

    // ── Transmission (Dépôt & Tableau de bord) ───────────────
    clientLogin: (data: any) => api.post('/client/login', data).then(r => r.data),
    clientRegister: (societeId: number, data: any) => api.post(`/client/register?societe_id=${societeId}`, data).then(r => r.data),
    clientUploadDocument: (file: File, typeDocument: string, notes?: string) => {
        const form = new FormData()
        form.append('file', file)
        form.append('type_document', typeDocument)
        if (notes) form.append('notes', notes)
        return api.post('/transmission/upload', form, {
            headers: { 'Content-Type': 'multipart/form-data' }
        }).then(r => r.data)
    },
    clientGetHistorique: () => api.get('/transmission/client/historique').then(r => r.data),

    getTransmissionDashboard: () => api.get('/transmission/dashboard').then(r => r.data),
    listTransmissionDocs: (societeId?: number, statut: string = 'A_TRAITER') => {
        let url = `/transmission/documents?statut=${statut}`
        if (societeId) url += `&societe_id=${societeId}`
        return api.get(url).then(r => r.data)
    },
    accepterTransmissionDoc: (id: number) => api.post(`/transmission/${id}/accepter`).then(r => r.data),
    rejeterTransmissionDoc: (id: number) => api.post(`/transmission/${id}/rejeter`).then(r => r.data),
    clientDeleteTransmissionDoc: (id: number) => api.delete(`/transmission/${id}/client`).then(r => r.data),

    // ── Journaux Routes ────────────────────────────────────────
    getJournalsConfig: () => api.get('/journaux/config').then(r => r.data),
    createJournalConfig: (data: { code: string; label: string; type: string }) =>
        api.post('/journaux/config', data).then(r => r.data),

    adminGetAIPerformance: (): Promise<AIPerformanceResponse> =>
        api.get('/admin/ai-performance').then(r => r.data),

    createDemandeAcces: (data: { nom_complet: string; entreprise: string; email: string; telephone?: string; message?: string; cabinet_id?: number | null }) =>
        api.post('/demandes-acces/', data).then(r => r.data),

    clientGetProfile: () => api.get('/client/me').then(r => r.data),
    clientUpdateProfile: (data: { nom?: string; prenom?: string; email?: string }) =>
        api.put('/client/me', data).then(r => r.data),
    clientChangePassword: (data: { old_password: string; new_password: string }) =>
        api.post('/client/me/password', data).then(r => r.data),

    getPublicCabinets: () => api.get('/demandes-acces/cabinets').then(r => r.data),

    listDemandesAcces: () => api.get('/demandes-acces/').then(r => r.data),
    updateStatutDemande: (id: number, statut: string, username?: string, password?: string) =>
        api.patch(`/demandes-acces/${id}/statut`, { statut, username, password }).then(r => r.data),
    updateDemandeAcces: (id: number, data: { nom_complet?: string; entreprise?: string; email?: string; telephone?: string; message?: string }) =>
        api.put(`/demandes-acces/${id}`, data).then(r => r.data),
    deleteDemandeAcces: (id: number) =>
        api.delete(`/demandes-acces/${id}`).then(r => r.data),
}

export default apiService
