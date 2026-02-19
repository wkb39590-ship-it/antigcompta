import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import '../styles/auth.css'

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

    const token = localStorage.getItem('access_token')
    const username = localStorage.getItem('username')
    const usernameDisplay = username ? (typeof username === 'string' ? username : JSON.stringify(username)) : ''

    useEffect(() => {
        // Charger les cabinets au chargement
        const cabinetsData = localStorage.getItem('cabinets')
        if (cabinetsData) {
            setCabinets(JSON.parse(cabinetsData))
        }
    }, [])

    useEffect(() => {
        // Charger les sociétés quand un cabinet est sélectionné
        if (selectedCabinet) {
            loadSocietes(selectedCabinet)
        }
    }, [selectedCabinet])

    const loadSocietes = async (cabinetId: number) => {
        setLoading(true)
        setError('')
        try {
            const response = await fetch(
                `http://localhost:8090/auth/societes?token=${token}&cabinet_id=${cabinetId}`
            )
            if (!response.ok) {
                let data = null
                try { data = await response.json() } catch {}
                const msg = data && data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Erreur lors du chargement des sociétés'
                throw new Error(msg)
            }
            const data = await response.json()
            setSocietes(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : (err ? JSON.stringify(err) : 'Erreur inconnue'))
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
            
            console.log('[CabinetSelector] Calling select-societe with:', { selectedCabinet, selectedSociete })
            
            const response = await fetch(`http://localhost:8090/auth/select-societe?token=${encodeURIComponent(token)}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    cabinet_id: selectedCabinet,
                    societe_id: selectedSociete
                })
            })

            console.log('[CabinetSelector] Response status:', response.status)

            if (!response.ok) {
                let data = null
                try { data = await response.json() } catch {}
                const msg = data && data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : 'Erreur lors de la sélection'
                console.error('[CabinetSelector] Error response:', msg)
                throw new Error(msg)
            }

            const data = await response.json()
            console.log('[CabinetSelector] Response data:', data)
            console.log('[CabinetSelector] session_token:', data.session_token ? `${data.session_token.substring(0, 20)}...` : 'MISSING')

            // Stocker le session_token et le contexte
            localStorage.setItem('session_token', data.session_token)
            
            // Extract cabinet_id and societe_id from context
            const cabinet_id = data.context?.cabinet_id || selectedCabinet
            const societe_id = data.context?.societe_id || selectedSociete
            
            localStorage.setItem('current_cabinet_id', String(cabinet_id))
            localStorage.setItem('current_societe_id', String(societe_id))
            
            console.log('[CabinetSelector] ✅ Stored session_token in localStorage')
            console.log('[CabinetSelector] ✅ Stored context:', { cabinet_id, societe_id })

            // Rediriger vers le dashboard
            navigate('/dashboard')
        } catch (err) {
            const errorMsg = err instanceof Error ? err.message : (err ? JSON.stringify(err) : 'Erreur inconnue')
            console.error('[CabinetSelector] Error:', errorMsg)
            setError(errorMsg)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-container">
            <div className="auth-card">
                <div className="auth-header">
                    <h1>🏢 Sélection Cabinet & Société</h1>
                    <p>Connecté en tant que: <strong>{username}</strong></p>
                </div>

                <form onSubmit={handleSelectSociete} className="auth-form">
                    <div className="form-group">
                        <label htmlFor="cabinet">Sélectionner un cabinet</label>
                        <select
                            id="cabinet"
                            value={selectedCabinet || ''}
                            onChange={(e) => {
                                setSelectedCabinet(Number(e.target.value))
                                setSelectedSociete(null)
                                setSocietes([])
                            }}
                            disabled={loading}
                            required
                        >
                            <option value="">-- Choisir un cabinet --</option>
                            {cabinets.map((cab) => (
                                <option key={cab?.id ?? JSON.stringify(cab)} value={cab?.id ?? JSON.stringify(cab)}>
                                    {typeof cab?.nom === 'string' ? cab.nom : JSON.stringify(cab)}
                                </option>
                            ))}
                        </select>
                    </div>

                    {selectedCabinet && (
                        <div className="form-group">
                            <label htmlFor="societe">Sélectionner une société</label>
                            <select
                                id="societe"
                                value={selectedSociete || ''}
                                onChange={(e) => setSelectedSociete(Number(e.target.value))}
                                disabled={loading || societes.length === 0}
                                required
                            >
                                <option value="">
                                    {loading ? '⏳ Chargement...' : '-- Choisir une société --'}
                                </option>
                                {societes.map((soc) => (
                                    <option key={soc?.id ?? JSON.stringify(soc)} value={soc?.id ?? JSON.stringify(soc)}>
                                        {typeof soc?.raison_sociale === 'string' ? soc.raison_sociale : JSON.stringify(soc)} {soc?.ice ? `(${soc.ice})` : ''}
                                    </option>
                                ))}
                            </select>
                        </div>
                    )}

                    {error && <div className="form-error">{error}</div>}

                    <button
                        type="submit"
                        disabled={!selectedSociete || loading}
                        className="auth-button"
                    >
                        {loading ? '🔄 Entrée...' : '✅ Entrer dans le système'}
                    </button>
                </form>

                <div className="auth-footer">
                    <button
                        onClick={() => {
                            localStorage.clear()
                            navigate('/login')
                        }}
                        className="link-button"
                    >
                        ← Retour connexion
                    </button>
                </div>
            </div>
        </div>
    )
}
