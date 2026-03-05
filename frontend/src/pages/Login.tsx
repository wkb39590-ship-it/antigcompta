import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import { setAdminSession } from '../utils/adminTokenDecoder'
import { Zap, AlertTriangle, ArrowRight, User, Lock } from 'lucide-react'
import '../styles/auth.css'
import '../styles/creative-login.css'

interface RoleAgent {
    id: number;
    username: string;
    email: string;
    nom?: string;
    prenom?: string;
    is_admin: boolean;
    is_super_admin: boolean;
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
    // Mouse tracking for parallax effect
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 40; // Max 40px movement
            const y = (e.clientY / window.innerHeight - 0.5) * 40;
            setMousePos({ x, y });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

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

            localStorage.removeItem('session_token')
            localStorage.setItem('access_token', data.access_token)
            localStorage.setItem('username', data.agent.username)
            localStorage.setItem('is_admin', String(data.agent.is_admin))
            localStorage.setItem('is_super_admin', String(data.agent.is_super_admin))
            localStorage.setItem('cabinets', JSON.stringify(data.cabinets))

            if (data.agent.is_admin || data.agent.is_super_admin) {
                setAdminSession(data.access_token, data.agent);
                navigate('/admin/dashboard');
            } else {
                navigate('/select-cabinet');
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Erreur inconnue')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="creative-auth-container">
            {/* Background Animated Blurs */}
            <div className="animated-bg">
                <div className="bg-shape shape-1"></div>
                <div className="bg-shape shape-2"></div>
                <div className="bg-shape shape-3"></div>
            </div>

            {/* Parallax Floating Elements */}
            <div
                className="floating-elements"
                style={{ transform: `translate(${mousePos.x}px, ${mousePos.y}px)` }}
            >
                <div className="float-item float-item-1"></div>
                <div className="float-item float-item-2"></div>
                <div className="float-item float-item-3"></div>
                <div className="float-item float-item-4"></div>
            </div>

            {/* Main Center Content */}
            <div className="auth-content-wrapper">
                <div className="auth-glass-panel">

                    {/* Left: Animated Showcase */}
                    <div className="auth-showcase-glass">
                        <div className="showcase-text">
                            <div className="brand-title">
                                <div className="brand-icon-glass">
                                    <Zap size={28} />
                                </div>
                                <h1>comptafacile</h1>
                            </div>
                            <h2>L'avenir de votre<br />comptabilité.</h2>
                            <p>Une expérience fluide, intelligente et dynamique pour gérer toutes vos écritures comptables sans effort.</p>
                        </div>
                    </div>

                    {/* Right: Glass Form */}
                    <div className="auth-form-glass">
                        <div className="form-header">
                            <h2>Connexion</h2>
                            <p>Accédez à votre espace de travail intelligent</p>
                        </div>

                        <form onSubmit={handleLogin}>
                            <div className="glass-input-group">
                                <label>Identifiant</label>
                                <div className="glass-input-wrapper">
                                    <input
                                        type="text"
                                        value={username}
                                        onChange={(e) => setUsername(e.target.value)}
                                        placeholder="Votre identifiant"
                                        disabled={loading}
                                        required
                                    />
                                    <User size={18} className="input-icon" />
                                </div>
                            </div>

                            <div className="glass-input-group">
                                <label>Mot de passe</label>
                                <div className="glass-input-wrapper">
                                    <input
                                        type="password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        placeholder="••••••••"
                                        disabled={loading}
                                        required
                                    />
                                    <Lock size={18} className="input-icon" />
                                </div>
                            </div>

                            {error && (
                                <div className="auth-error-glass">
                                    <AlertTriangle size={18} />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={loading}
                                className="glass-submit-btn"
                            >
                                {loading ? (
                                    <div className="creative-spinner"></div>
                                ) : (
                                    <>
                                        <span>Entrer dans l'application</span>
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    )
}
