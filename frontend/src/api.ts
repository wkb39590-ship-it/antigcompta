import axios from 'axios'
import { getSessionContext } from './utils/tokenDecoder'

const API_BASE = '/api'

console.log('[API] Initializing with base URL:', API_BASE)

const api = axios.create({
    baseURL: API_BASE,
    timeout: 60000,  // Increased from 15s to 60s for generic calls
})

// Attach session_token (if present) as Authorization Bearer for all requests
api.interceptors.request.use((config) => {
    try {
        const session = typeof window !== 'undefined' ? localStorage.getItem('session_token') : null
        console.log('[Axios Interceptor] Request to:', config.url, 'Session token:', session ? `${session.substring(0, 20)}...` : 'NONE')

        if (session) {
            config.headers = config.headers || {}
            config.headers['Authorization'] = `Bearer ${session}`
            console.log('[Axios Interceptor] ✅ Added Authorization header')
        } else {
            console.warn('[Axios Interceptor] ⚠️ No session_token found (this might be expected for login/auth endpoints)')
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

export const apiService = {
    // Liste des factures
    listFactures: (status?: string) =>
        api.get('/factures/', { params: { status } }).then(r => r.data),

    // Upload
    uploadFacture: (file: File) => {
        const form = new FormData()
        form.append('file', file)
        // session_token is sent automatically via Authorization header interceptor
        return api.post(`/factures/upload-facture/`, form, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 120000  // 2 minutes for upload + OCR
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
}


export default apiService
