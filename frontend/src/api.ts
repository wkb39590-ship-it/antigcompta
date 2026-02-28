import axios from 'axios'
import { getSessionContext } from './utils/tokenDecoder'

// Force /api to use Vite's proxy - DO NOT use VITE_API_URL environment variable
// because Vite variables are build-time embedded, and the Docker env var might
// be resolving to 'http://backend:8000' which is an internal Docker hostname
// not accessible from the browser.
const API_BASE = '/api'

console.log('[API] Initializing with base URL:', API_BASE)

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
        const session = typeof window !== 'undefined' ? localStorage.getItem('session_token') : null
        const access = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
        const tokenToUse = session || access
        const tokenType = session ? 'SESSION' : (access ? 'ACCESS' : 'NONE')

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

// ── API calls ──────────────────────────────────────────────

/**
 * Service central pour tous les appels vers l'API Backend.
 * Chaque méthode correspond à un endpoint FastAPI.
 */
export const apiService = {
    // Liste des factures
    listFactures: (status?: string) =>
        api.get('/factures/', { params: { status } }).then(r => r.data),

    // Upload
    /**
     * Téléverse une facture vers le serveur.
     * @param file Fichier image ou PDF sélectionné par l'utilisateur.
     */
    uploadFacture: (file: File) => {
        const form = new FormData()
        form.append('file', file)
        return api.post(`/factures/upload`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 120000
        }).then(r => r.data)
    },

    // Extraction (Gemini can be slow, use longer timeout)
    extractFacture: (id: number) =>
        api.post(`/factures/${id}/extract`, {}, { timeout: 300000 }).then(r => r.data),  // 5 minutes


    // Classification
    classifyFacture: (id: number) =>
        api.post(`/factures/${id}/classify`, {}, { timeout: 300000 }).then(r => r.data),

    // Génération écritures
    generateEntries: (id: number) =>
        api.post(`/factures/${id}/generate-entries`, {}, { timeout: 300000 }).then(r => r.data),

    // Détail facture
    getFacture: (id: number) =>
        api.get(`/factures/${id}`).then(r => r.data),

    // Lignes produits
    getFactureLines: (id: number) =>
        api.get(`/factures/${id}/lines`).then(r => r.data),

    // Écritures
    getFactureEntries: (id: number) =>
        api.get(`/factures/${id}/entries`).then(r => r.data),

    // Validation
    validateFacture: (id: number) =>
        api.post(`/factures/${id}/validate`).then(r => r.data),

    // Rejet
    rejectFacture: (id: number, reason: string) =>
        api.post(`/factures/${id}/reject?reason=${encodeURIComponent(reason)}`).then(r => r.data),

    // Correction ligne produit
    updateInvoiceLine: (lineId: number, data: Partial<InvoiceLine>) =>
        api.put(`/factures/invoice-lines/${lineId}`, data).then(r => r.data),

    // Correction ligne écriture
    updateEntryLine: (lineId: number, data: Partial<EntryLine>) =>
        api.put(`/factures/entry-lines/${lineId}`, data).then(r => r.data),

    // PCM
    getPcmAccounts: (pcmClass?: number) =>
        api.get('/pcm/accounts', { params: { pcm_class: pcmClass } }).then(r => r.data),

    // Sociétés
    listSocietes: () =>
        api.get('/societes/').then(r => r.data),

    createSociete: (data: { raison_sociale: string; ice?: string; if_fiscal?: string }) =>
        api.post('/societes/', data).then(r => r.data),

    // Profil & Auth
    getProfile: (token: string) =>
        api.get(`/auth/me?token=${token}`).then(r => r.data),

    getAgentStats: (token: string) =>
        api.get(`/auth/stats?token=${token}`).then(r => r.data),

    // URL fichier
    getFileUrl: (id: number) => `${API_BASE}/factures/${id}/file`,

    // Mappings (Feedback Loop)
    listMappings: () =>
        api.get('/mappings/').then(r => r.data),

    deleteMapping: (id: number) =>
        api.delete(`/mappings/${id}`).then(r => r.data),

    // Suppression facture
    deleteFacture: (id: number) =>
        api.delete(`/factures/${id}`).then(r => r.data),

    // Mise à jour facture
    updateFacture: (id: number, data: Partial<Facture>) =>
        api.put(`/factures/${id}`, data).then(r => r.data),

    // Mise à jour profil (Agent)
    updateProfile: (data: any) =>
        api.put('/auth/profile', data).then(r => r.data),

    // ── Admin Routes ──────────────────────────────────────────
    adminListAgents: () => api.get('/admin/agents').then(r => r.data),
    adminCreateAgent: (data: any, cabinetId: string) =>
        api.post(`/admin/agents?cabinet_id=${cabinetId}`, data).then(r => r.data),
    adminUpdateAgent: (id: number, data: any) =>
        api.put(`/admin/agents/${id}`, data).then(r => r.data),
    adminDeleteAgent: (id: number) =>
        api.delete(`/admin/agents/${id}`).then(r => r.data),

    adminListCabinets: () => api.get('/admin/cabinets').then(r => r.data),
    adminCreateCabinet: (data: any) => api.post('/admin/cabinets', data).then(r => r.data),
    adminUpdateCabinet: (id: number, data: any) => api.put(`/admin/cabinets/${id}`, data).then(r => r.data),
    adminDeleteCabinet: (id: number) => api.delete(`/admin/cabinets/${id}`).then(r => r.data),
    adminListSocietes: () => api.get('/admin/societes').then(r => r.data),
    adminCreateSociete: (data: any, cabinetId: string) =>
        api.post(`/admin/societes?cabinet_id=${cabinetId}`, data).then(r => r.data),
    adminUpdateSociete: (id: number, data: any) =>
        api.put(`/admin/societes/${id}`, data).then(r => r.data),
    adminDeleteSociete: (id: number) =>
        api.delete(`/admin/societes/${id}`).then(r => r.data),

    adminGetProfile: () => api.get('/admin/profile').then(r => r.data),
    adminUpdateProfile: (data: any) => api.put('/admin/profile', data).then(r => r.data),
    adminGetGlobalStats: () => api.get('/admin/stats/global').then(r => r.data),
    adminGetActivities: () => api.get('/admin/activities').then(r => r.data),
    adminAssignSocieteToAgent: (cabinetId: number, agentId: number, societeId: number) =>
        api.post(`/admin/cabinets/${cabinetId}/agents/assign-societe?agent_id=${agentId}&societe_id=${societeId}`).then(r => r.data),
    adminGetLogs: (offset: number = 0, limit: number = 50) =>
        api.get('/admin/logs', { params: { offset, limit } }).then(r => r.data),
}


export default apiService
