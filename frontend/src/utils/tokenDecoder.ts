/**
 * Token decoder utility for session_token
 * Supports both standard JWT (3-part) and legacy simple base64 tokens
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
        // Standard JWT is header.payload.signature
        const parts = token.split('.')
        let encodedPayload = ''
        
        if (parts.length === 3) {
            // It's a real JWT
            encodedPayload = parts[1]
        } else {
            // Fallback for legacy simple base64 tokens
            encodedPayload = token
        }

        // Add proper padding to base64 (Handle URL-safe base64)
        let base64 = encodedPayload.replace(/-/g, '+').replace(/_/g, '/')
        while (base64.length % 4) {
            base64 += '='
        }

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
