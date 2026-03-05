import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { API_CONFIG } from '../config/apiConfig'
import { Building2, Search, ArrowLeft, RefreshCw, CheckCircle2, Loader2, Zap, Briefcase, User, AlertTriangle } from 'lucide-react'
import '../styles/auth.css'
import '../styles/creative-login.css'

interface Cabinet {
    id: number
    nom: string
}

interface Societe {
    id: number
    raison_sociale: string
    ice: string
}

export default function CabinetSelector() {
    const navigate = useNavigate()
    const [cabinets, setCabinets] = useState<Cabinet[]>([])
    const [selectedCabinet, setSelectedCabinet] = useState<number | null>(null)
    const [societes, setSocietes] = useState<Societe[]>([])
    const [selectedSociete, setSelectedSociete] = useState<number | null>(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    // Mouse tracking for parallax effect
    const [mousePos, setMousePos] = useState({ x: 0, y: 0 })

    const token = localStorage.getItem('access_token')
    const username = localStorage.getItem('username')

    useEffect(() => {
        const handleMouseMove = (e: MouseEvent) => {
            const x = (e.clientX / window.innerWidth - 0.5) * 40;
            const y = (e.clientY / window.innerHeight - 0.5) * 40;
            setMousePos({ x, y });
        };
        window.addEventListener('mousemove', handleMouseMove);
        return () => window.removeEventListener('mousemove', handleMouseMove);
    }, []);

    useEffect(() => {
        const cabinetsData = localStorage.getItem('cabinets')
        if (cabinetsData) {
            setCabinets(JSON.parse(cabinetsData))
        }
    }, [])

    useEffect(() => {
        if (selectedCabinet) {
            loadSocietes(selectedCabinet)
        }
    }, [selectedCabinet])

    const loadSocietes = async (cabinetId: number) => {
        setLoading(true)
        setError('')
        try {
            const response = await fetch(
                `${API_CONFIG.AUTH.SOCIETES_AUTH}?token=${token}&cabinet_id=${cabinetId}`
            )

            const text = await response.text()
            let data = null
            try {
                data = text ? JSON.parse(text) : null
            } catch (e) {
                console.error('[CabinetSelector] Failed to parse JSON:', text)
            }

            if (!response.ok) {
                const msg = data && data.detail
                    ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail))
                    : `Erreur ${response.status}: ${text.substring(0, 100)}`
                throw new Error(msg)
            }

            setSocietes(data || [])
        } catch (err) {
            console.error('[CabinetSelector] loadSocietes error:', err)
            setError(err instanceof Error ? err.message : 'Erreur inconnue')
        } finally {
            setLoading(false)
        }
    }


    const handleSelectSociete = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedCabinet || !selectedSociete) return

        setLoading(true)
        setError('')
        try {
            if (!token) throw new Error('Token manquant, reconnectez-vous')

            const response = await fetch(`${API_CONFIG.AUTH.SELECT_SOCIETE}?token=${encodeURIComponent(token)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cabinet_id: selectedCabinet,
                    societe_id: selectedSociete
                })
            })

            if (!response.ok) {
                let data = null
                try { data = await response.json() } catch { }
                const msg = data && data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Erreur lors de la sélection'
                throw new Error(msg)
            }

            const data = await response.json()
            localStorage.setItem('session_token', data.session_token)

            const cabinet_id = data.context?.cabinet_id || selectedCabinet
            const societe_id = data.context?.societe_id || selectedSociete

            localStorage.setItem('current_cabinet_id', String(cabinet_id))
            localStorage.setItem('current_societe_id', String(societe_id))

            navigate('/dashboard')
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : (err ? JSON.stringify(err) : 'Erreur inconnue')
            setError(errorMsg)
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

            <div className="auth-content-wrapper">
                <div className="auth-glass-panel">

                    {/* Left: Showcase */}
                    <div className="auth-showcase-glass">
                        <div className="showcase-text">
                            <div className="brand-title">
                                <div className="brand-icon-glass">
                                    <Zap size={28} />
                                </div>
                                <h1>comptafacile</h1>
                            </div>
                            <h2>Espace de<br />Travail.</h2>
                            <p>Veuillez sélectionner le cabinet et la société pour laquelle vous souhaitez travailler aujourd'hui.</p>

                            <div style={{ marginTop: '32px', display: 'flex', alignItems: 'center', gap: '12px', color: 'var(--auth-text-main)' }}>
                                <div style={{ padding: '8px', background: 'white', borderRadius: '10px', boxShadow: '0 4px 12px rgba(0,0,0,0.05)' }}>
                                    <User size={20} color="var(--auth-accent-1)" />
                                </div>
                                <div>
                                    <div style={{ fontSize: '12px', color: 'var(--auth-text-dim)', fontWeight: 600 }}>Connecté en tant que</div>
                                    <div style={{ fontWeight: 700 }}>{username}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Right: Form */}
                    <div className="auth-form-glass">
                        <div className="form-header">
                            <h2>Saisie Contexte</h2>
                            <p>Choisissez votre périmètre d'action</p>
                        </div>

                        <form onSubmit={handleSelectSociete}>
                            <div className="glass-input-group">
                                <label>Cabinet Comptable</label>
                                <div className="glass-input-wrapper">
                                    <select
                                        value={selectedCabinet || ''}
                                        onChange={(e) => {
                                            setSelectedCabinet(Number(e.target.value))
                                            setSelectedSociete(null)
                                            setSocietes([])
                                        }}
                                        disabled={loading}
                                        required
                                        style={{
                                            width: '100%',
                                            padding: '16px 20px 16px 48px',
                                            background: 'var(--auth-input-bg)',
                                            border: '1px solid rgba(0,0,0,0.05)',
                                            borderRadius: '16px',
                                            appearance: 'none'
                                        }}
                                    >
                                        <option value="">-- Choisir un cabinet --</option>
                                        {cabinets.map((cab) => (
                                            <option key={cab.id} value={cab.id}>
                                                {cab.nom}
                                            </option>
                                        ))}
                                    </select>
                                    <Building2 size={18} className="input-icon" />
                                </div>
                            </div>

                            {selectedCabinet && (
                                <div className="glass-input-group">
                                    <label>Société / Client</label>
                                    <div className="glass-input-wrapper">
                                        <select
                                            value={selectedSociete || ''}
                                            onChange={(e) => setSelectedSociete(Number(e.target.value))}
                                            disabled={loading || societes.length === 0}
                                            required
                                            style={{
                                                width: '100%',
                                                padding: '16px 20px 16px 48px',
                                                background: 'var(--auth-input-bg)',
                                                border: '1px solid rgba(0,0,0,0.05)',
                                                borderRadius: '16px',
                                                appearance: 'none'
                                            }}
                                        >
                                            <option value="">
                                                {loading ? 'Chargement...' : '-- Choisir une société --'}
                                            </option>
                                            {societes.map((soc) => (
                                                <option key={soc.id} value={soc.id}>
                                                    {soc.raison_sociale} {soc.ice ? `(${soc.ice})` : ''}
                                                </option>
                                            ))}
                                        </select>
                                        <Briefcase size={18} className="input-icon" />
                                    </div>
                                </div>
                            )}

                            {error && (
                                <div className="auth-error-glass">
                                    <AlertTriangle size={18} />
                                    <span>{error}</span>
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={!selectedSociete || loading}
                                className="glass-submit-btn"
                            >
                                {loading ? (
                                    <div className="creative-spinner"></div>
                                ) : (
                                    <>
                                        <span>Entrer dans le système</span>
                                        <CheckCircle2 size={18} />
                                    </>
                                )}
                            </button>
                        </form>

                        <div style={{ marginTop: '24px', textAlign: 'center' }}>
                            <button
                                onClick={() => {
                                    localStorage.clear()
                                    navigate('/login')
                                }}
                                className="link-button"
                                style={{ display: 'flex', alignItems: 'center', gap: '8px', justifyContent: 'center', margin: '0 auto' }}
                            >
                                <ArrowLeft size={16} /> Retour connexion
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
