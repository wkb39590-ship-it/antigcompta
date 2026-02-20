/**
 * Configuration API centralisée
 * Tous les endpoints API sont définis ici pour faciliter la maintenance
 */

const API_BASE_URL = '/api'

export const API_CONFIG = {
  // Base URL
  BASE_URL: API_BASE_URL,

  // Authentication endpoints
  AUTH: {
    LOGIN: `${API_BASE_URL}/auth/login`,
    REGISTER: `${API_BASE_URL}/auth/register`,
    ME: `${API_BASE_URL}/auth/me`,
    LOGOUT: `${API_BASE_URL}/auth/logout`,
    SELECT_SOCIETE: `${API_BASE_URL}/auth/select-societe`,
    SOCIETES_AUTH: `${API_BASE_URL}/auth/societes`,
  },

  // Admin endpoints
  ADMIN: {
    CABINETS: {
      LIST: `${API_BASE_URL}/admin/cabinets`,
      CREATE: `${API_BASE_URL}/admin/cabinets`,
      UPDATE: (id: number) => `${API_BASE_URL}/admin/cabinets/${id}`,
      DELETE: (id: number) => `${API_BASE_URL}/admin/cabinets/${id}`,
      ADD_SOCIETE: (id: number) => `${API_BASE_URL}/admin/cabinets/${id}/societes`,
    },
    AGENTS: {
      LIST: `${API_BASE_URL}/admin/agents`,
      CREATE: `${API_BASE_URL}/admin/agents`,
      UPDATE: (id: number) => `${API_BASE_URL}/admin/agents/${id}`,
      DELETE: (id: number) => `${API_BASE_URL}/admin/agents/${id}`,
    },
  },

  // Sociétés endpoints
  SOCIETES: {
    LIST: `${API_BASE_URL}/societes`,
    CREATE: `${API_BASE_URL}/societes`,
    UPDATE: (id: number) => `${API_BASE_URL}/societes/${id}`,
    DELETE: (id: number) => `${API_BASE_URL}/societes/${id}`,
  },

  // Factures endpoints
  FACTURES: {
    LIST: `${API_BASE_URL}/factures`,
    UPLOAD: `${API_BASE_URL}/factures/upload`,
    DETAIL: (id: number) => `${API_BASE_URL}/factures/${id}`,
    DOWNLOAD: (id: number) => `${API_BASE_URL}/factures/${id}/download`,
  },

  // PCM endpoints
  PCM: {
    LIST: `${API_BASE_URL}/pcm`,
    DETAIL: (id: number) => `${API_BASE_URL}/pcm/${id}`,
  },
}

/**
 * Utilitaire pour ajouter le token aux requêtes
 * Accepte deux format: bearer token ou query param
 */
export const buildApiUrl = (endpoint: string, token?: string, useQueryParam: boolean = false): string => {
  if (!token) {
    return endpoint
  }

  if (useQueryParam) {
    const separator = endpoint.includes('?') ? '&' : '?'
    return `${endpoint}${separator}token=${token}`
  }

  return endpoint
}

/**
 * Headers pour les requêtes authentifiées
 */
export const getAuthHeaders = (token?: string) => {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  return headers
}

export default API_CONFIG
