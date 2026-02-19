/**
 * Token decoder utility for session_token
 * Backend uses simple base64 encoding (not JWT 3-part format)
 */

export interface SessionPayload {
    agent_id: number
    cabinet_id: number
    societe_id: number
    username: string
    societe_raison_sociale: string
    exp?: string
}

/**
 * Decode a base64-encoded session token
 * @param token The base64 encoded token from localStorage
 * @returns The decoded payload or null if invalid
 */
export function decodeSessionToken(token: string | null): SessionPayload | null {
    if (!token) {
        console.warn('[TokenDecoder] No token provided')
        return null
    }

    try {
        // Add proper padding to base64
        let base64 = token
        base64 = base64 + '=='.substring(0, (4 - base64.length % 4) % 4)

        // Decode from base64
        const payload = JSON.parse(atob(base64)) as SessionPayload

        // Validate required fields
        if (!payload.societe_id) {
            console.error('[TokenDecoder] societe_id missing from payload')
            return null
        }

        console.log('[TokenDecoder] ✅ Token decoded successfully')
        return payload
    } catch (err) {
        console.error('[TokenDecoder] Failed to decode token:', err)
        return null
    }
}

/**
 * Get current société from session token
 */
export function getCurrentSociete() {
    const token = localStorage.getItem('session_token')
    const payload = decodeSessionToken(token)
    
    if (!payload) {
        return null
    }

    return {
        id: payload.societe_id,
        raison_sociale: payload.societe_raison_sociale
    }
}

/**
 * Get full session context from token
 */
export function getSessionContext() {
    const token = localStorage.getItem('session_token')
    return decodeSessionToken(token)
}
