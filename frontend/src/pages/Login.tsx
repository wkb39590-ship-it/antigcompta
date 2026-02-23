import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import { setAdminSession } from '../utils/adminTokenDecoder'
import '../styles/auth.css'

interface RoleAgent {
    id: number;
    username: string;
    email: string;
    nom?: string;
    prenom?: string;
    is_admin: boolean;
    cabinet_id: number;
}

interface LoginResponse {
    access_token: string
    token_type: string
    agent: RoleAgent
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
            const response = await fetch(API_CONFIG.AUTH.LOGIN, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            })

            if (!response.ok) {
                const data = await response.json()
                throw new Error(data.detail || 'Erreur de connexion')
            }

            const data: LoginResponse = await response.json()

            // 1. Stockage commun des informations de base
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('username', data.agent.username)
            localStorage.setItem('is_admin', String(data.agent.is_admin))
            localStorage.setItem('cabinets', JSON.stringify(data.cabinets))

            // 2. Logique de redirection selon le rôle
            if (data.agent.is_admin) {
                console.log('[Login] Connexion Administrateur détectée');
                // Session Admin (nécessaire pour AdminProtectedRoute)
                setAdminSession(data.access_token, data.agent);
                navigate('/admin/dashboard');
            } else {
                console.log('[Login] Connexion Agent standard');
                navigate('/select-cabinet');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erreur inconnue')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="unified-login-page">
            <div className="aurora-login-card">
                <div className="login-glow"></div>

                <div className="login-header">
                    <div className="logo-icon">⚡</div>
                    <h1>comptafacile</h1>
                    <p className="subtitle">L'IA qui simplifie votre comptabilité</p>
                </div>

                <form onSubmit={handleLogin} className="login-form">
                    <div className="input-group">
                        <label>Nom d'utilisateur</label>
                        <input
                            type="text"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            placeholder="Entrez votre identifiant"
                            disabled={loading}
                            required
                        />
                    </div>

                    <div className="input-group">
                        <label>Mot de passe</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            disabled={loading}
                            required
                        />
                    </div>

                    {error && (
                        <div className="login-error">
                            <span className="error-icon">⚠️</span>
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={loading}
                        className="login-btn"
                    >
                        {loading ? (
                            <div className="loader-container">
                                <div className="btn-spinner"></div>
                                <span>Authentification...</span>
                            </div>
                        ) : (
                            <span>Se connecter 🔐</span>
                        )}
                    </button>
                </form>

                <div className="login-footer">
                    <div className="test-accounts">
                        <p>💡 Comptes d'accès</p>
                        <div className="account-chips">
                            <span className="chip admin">Admin: wissal</span>
                            <span className="chip user">Agent: fatima</span>
                        </div>
                    </div>
                </div>
            </div>

            <style>{`
                :root {
                    --login-bg: #0f172a;
                    --login-panel: rgba(30, 41, 59, 0.7);
                    --login-accent: #6366f1;
                    --login-border: rgba(255, 255, 255, 0.1);
                }

                .unified-login-page {
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: radial-gradient(circle at top right, #1e1b4b, #0f172a);
                    font-family: 'Inter', system-ui, sans-serif;
                    padding: 20px;
                }

                .aurora-login-card {
                    position: relative;
                    width: 100%;
                    max-width: 440px;
                    background: var(--login-panel);
                    backdrop-filter: blur(20px);
                    border: 1px solid var(--login-border);
                    border-radius: 28px;
                    padding: 40px;
                    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                    overflow: hidden;
                    animation: fadeIn 0.6s ease-out;
                }

                .login-glow {
                    position: absolute;
                    top: -100px;
                    right: -100px;
                    width: 300px;
                    height: 300px;
                    background: radial-gradient(circle, rgba(99, 102, 241, 0.15), transparent 70%);
                    pointer-events: none;
                }

                @keyframes fadeIn {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }

                .login-header {
                    text-align: center;
                    margin-bottom: 35px;
                }

                .logo-icon {
                    font-size: 42px;
                    margin-bottom: 10px;
                    filter: drop-shadow(0 0 10px var(--login-accent));
                }

                .login-header h1 {
                    font-size: 28px;
                    font-weight: 800;
                    color: white;
                    margin: 0;
                    letter-spacing: -0.5px;
                }

                .subtitle {
                    color: #94a3b8;
                    font-size: 14px;
                    margin-top: 5px;
                    font-weight: 500;
                }

                .input-group {
                    margin-bottom: 24px;
                }

                .input-group label {
                    display: block;
                    font-size: 13px;
                    font-weight: 600;
                    color: #94a3b8;
                    margin-bottom: 8px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }

                .input-group input {
                    width: 100%;
                    background: rgba(15, 23, 42, 0.5);
                    border: 1px solid var(--login-border);
                    border-radius: 14px;
                    padding: 14px 16px;
                    color: white;
                    font-size: 15px;
                    transition: all 0.3s;
                    box-sizing: border-box;
                }

                .input-group input:focus {
                    outline: none;
                    border-color: var(--login-accent);
                    background: rgba(15, 23, 42, 0.8);
                    box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.1);
                }

                .login-error {
                    background: rgba(239, 68, 68, 0.1);
                    border-left: 4px solid #ef4444;
                    padding: 12px;
                    border-radius: 8px;
                    color: #fca5a5;
                    font-size: 13px;
                    margin-bottom: 24px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                .login-btn {
                    width: 100%;
                    background: linear-gradient(135deg, #6366f1, #4f46e5);
                    color: white;
                    border: none;
                    padding: 16px;
                    border-radius: 14px;
                    font-size: 16px;
                    font-weight: 700;
                    cursor: pointer;
                    transition: all 0.3s;
                    box-shadow: 0 10px 20px -5px rgba(79, 70, 229, 0.4);
                }

                .login-btn:hover:not(:disabled) {
                    transform: translateY(-2px);
                    box-shadow: 0 15px 25px -5px rgba(79, 70, 229, 0.5);
                }

                .login-btn:disabled {
                    opacity: 0.7;
                    cursor: not-allowed;
                }

                .loader-container {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 12px;
                }

                .btn-spinner {
                    width: 18px;
                    height: 18px;
                    border: 2px solid rgba(255, 255, 255, 0.3);
                    border-top-color: white;
                    border-radius: 50%;
                    animation: spin 0.8s linear infinite;
                }

                @keyframes spin { to { transform: rotate(360deg); } }

                .login-footer {
                    margin-top: 35px;
                    padding-top: 25px;
                    border-top: 1px solid var(--login-border);
                }

                .test-accounts p {
                    font-size: 12px;
                    color: #64748b;
                    margin-bottom: 12px;
                    text-align: center;
                }

                .account-chips {
                    display: flex;
                    justify-content: center;
                    gap: 10px;
                    flex-wrap: wrap;
                }

                .chip {
                    font-size: 11px;
                    padding: 5px 12px;
                    border-radius: 20px;
                    font-weight: 600;
                    background: rgba(255, 255, 255, 0.05);
                    color: #94a3b8;
                    border: 1px solid var(--login-border);
                }

                .chip.admin { color: #818cf8; border-color: rgba(129, 140, 248, 0.3); }
            `}</style>
        </div>
    )
}
