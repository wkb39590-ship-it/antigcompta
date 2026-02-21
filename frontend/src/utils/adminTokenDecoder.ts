/**
 * Utilitaires pour gérer la session admin (authentification et tokens)
 */

export interface AdminUser {
  agent_id: number
  username: string
  email: string
  nom?: string
  prenom?: string
  is_admin: boolean
  cabinet_id: number
}

export interface AdminSession {
  token: string
  user: AdminUser
}

/**
 * Récupère le contexte de la session admin depuis localStorage
 */
export function getAdminSession(): AdminSession | null {
  try {
    const token = localStorage.getItem('admin_token')
    const userJson = localStorage.getItem('admin_user')

    if (!token || !userJson) {
      return null
    }

    const user = JSON.parse(userJson)
    return {
      token,
      user
    }
  } catch (error) {
    console.error('Erreur lors de la lecture de la session admin:', error)
    return null
  }
}

/**
 * Retourne le token admin s'il existe et est valide
 */
export function getAdminToken(): string | null {
  const token = localStorage.getItem('admin_token')
  return token || null
}

/**
 * Retourne l'utilisateur admin s'il existe et est valide
 */
export function getAdminUser(): AdminUser | null {
  try {
    const userJson = localStorage.getItem('admin_user')
    if (!userJson) {
      return null
    }
    return JSON.parse(userJson)
  } catch (error) {
    console.error('Erreur lors de la lecture de l\'utilisateur admin:', error)
    return null
  }
}

/**
 * Définit la session admin (stockage localStorage)
 */
export function setAdminSession(token: string, user: AdminUser): void {
  localStorage.setItem('admin_token', token)
  localStorage.setItem('admin_user', JSON.stringify(user))
}

/**
 * Efface la session admin
 */
export function clearAdminSession(): void {
  localStorage.removeItem('admin_token')
  localStorage.removeItem('admin_user')
}

/**
 * Vérifie si l'utilisateur est actuellement connecté en tant qu'admin
 */
export function isAdminLoggedIn(): boolean {
  const token = getAdminToken()
  const user = getAdminUser()
  return !!(token && user && user.is_admin)
}
