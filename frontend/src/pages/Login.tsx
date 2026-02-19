import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/auth.css'

interface LoginResponse {
    access_token: string
    is_admin: boolean
    cabinets: Array<{ id: number; nom: string }>
}

export default function Login() {
    const navigate = useNavigate()
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault()
        setError('')
        setLoading(true)

        try {
            const response = await fetch('http://localhost:8090/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.detail || 'Erreur de connexion')
            }

            const data: LoginResponse = await response.json()

            // Stocker le token et les infos dans localStorage
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('is_admin', String(data.is_admin))
            localStorage.setItem('username', username)
            localStorage.setItem('cabinets', JSON.stringify(data.cabinets))

            // Rediriger vers le sélecteur de cabinet
            navigate('/select-cabinet')
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erreur inconnue')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>⚡ Comptabilité Zéro Saisie</h1>
                    <p>Connexion décentralisée par cabinet</p>
                </div>

                <form onSubmit={handleLogin} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="username">Nom d'utilisateur</label>
                        <input
                            id="username"
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="wissal"
                            disabled={loading}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label htmlFor="password">Mot de passe</label>
                        <input
                            id="password"
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            disabled={loading}
                            required
                        />
                    </div>

                    {error && <div className="form-error">{error}</div>}

                    <button
                        type="submit"
                        disabled={loading}
                        className="auth-button"
                    >
                        {loading ? '🔄 Connexion...' : '🔐 Connexion'}
                    </button>
                </form>

                <div className="auth-footer">
                    <p>🧪 Comptes de test:</p>
                    <ul>
                        <li><strong>wissal</strong> / password123 (admin cabinet 4)</li>
                        <li><strong>fatima</strong> / password123 (user cabinet 4)</li>
                        <li><strong>ahmed</strong> / password123 (admin cabinet 5)</li>
                    </ul>
                </div>
            </div>
        </div>
    )
}
