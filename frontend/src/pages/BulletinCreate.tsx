import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService, { Employe } from '../api'
import { ArrowLeft, Calculator, FileText } from 'lucide-react'

export default function BulletinCreate() {
    const navigate = useNavigate()
    const [employes, setEmployes] = useState<Employe[]>([])
    const [loading, setLoading] = useState(false)
    const [calculating, setCalculating] = useState(false)
    const [error, setError] = useState('')

    const currentMonth = new Date().getMonth() + 1
    const currentYear = new Date().getFullYear()

    const [formParams, setFormParams] = useState({
        employe_id: '',
        mois: currentMonth,
        annee: currentYear,
        primes: 0,
        heures_sup: 0
    })

    useEffect(() => {
        loadEmployes()
    }, [])

    const loadEmployes = async () => {
        setLoading(true)
        try {
            const data = await apiService.listEmployes('ACTIF')
            setEmployes(data)
        } catch (err: any) {
            setError('Impossible de charger la liste des salariés.')
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!formParams.employe_id) {
            setError('Veuillez sélectionner un salarié.')
            return
        }

        setCalculating(true)
        setError('')
        try {
            const result = await apiService.saveBulletin({
                employe_id: parseInt(formParams.employe_id),
                mois: formParams.mois,
                annee: formParams.annee,
                primes: formParams.primes,
                heures_sup: formParams.heures_sup
            })
            // Redirect to the detail page of the newly created bulletin
            navigate(`/paie/${result.id}`)
        } catch (err: any) {
            console.error('Calculate error:', err)
            setError(err.response?.data?.detail || 'Erreur lors de la génération du bulletin.')
        } finally {
            setCalculating(false)
        }
    }

    return (
        <div className="page-content" style={{ maxWidth: '800px', margin: '0 auto' }}>
            <div className="page-header" style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn btn-ghost" onClick={() => navigate('/paie')} style={{ padding: '8px' }}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <FileText size={24} color="var(--accent)" />
                            Générer un Bulletin
                        </h1>
                        <p className="page-subtitle">Calculer et enregistrer un nouveau bulletin de paie</p>
                    </div>
                </div>
            </div>

            {error && (
                <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', padding: '16px', borderRadius: '8px', marginBottom: '24px', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                    {error}
                </div>
            )}

            <form onSubmit={handleSubmit} className="card">
                <div className="card-header">
                    <div className="card-title">Paramètres de Résultat</div>
                </div>

                <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div className="form-group">
                        <label className="form-label">Salarié *</label>
                        <select
                            className="form-input"
                            required
                            value={formParams.employe_id}
                            onChange={e => setFormParams({ ...formParams, employe_id: e.target.value })}
                            disabled={loading}
                        >
                            <option value="">-- Sélectionner un collaborateur --</option>
                            {employes.map(e => (
                                <option key={e.id} value={e.id}>{e.prenom} {e.nom} (Salaire de base: {e.salaire_base.toLocaleString()} MAD)</option>
                            ))}
                        </select>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Mois *</label>
                            <select
                                className="form-input"
                                required
                                value={formParams.mois}
                                onChange={e => setFormParams({ ...formParams, mois: parseInt(e.target.value) })}
                            >
                                {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                                    <option key={m} value={m}>{new Date(2024, m - 1).toLocaleString('fr-FR', { month: 'long' })}</option>
                                ))}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Année *</label>
                            <input
                                type="number"
                                className="form-input"
                                required
                                min="2000"
                                max="2050"
                                value={formParams.annee}
                                onChange={e => setFormParams({ ...formParams, annee: parseInt(e.target.value) })}
                            />
                        </div>
                    </div>

                    <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '10px 0' }} />

                    <div className="form-group">
                        <label className="form-label">Primes Exceptionnelles (MAD)</label>
                        <input
                            type="number"
                            step="0.01"
                            min="0"
                            className="form-input"
                            value={formParams.primes || ''}
                            onChange={e => setFormParams({ ...formParams, primes: parseFloat(e.target.value) || 0 })}
                        />
                        <div style={{ fontSize: '11px', color: 'var(--text3)', marginTop: '4px' }}>
                            Primes non imposables, bonus, etc. ajoutés au salaire brut.
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Heures Supplémentaires (MAD)</label>
                        <input
                            type="number"
                            step="0.01"
                            min="0"
                            className="form-input"
                            value={formParams.heures_sup || ''}
                            onChange={e => setFormParams({ ...formParams, heures_sup: parseFloat(e.target.value) || 0 })}
                        />
                        <div style={{ fontSize: '11px', color: 'var(--text3)', marginTop: '4px' }}>
                            Montant brut des heures supplémentaires effectuées ce mois-ci.
                        </div>
                    </div>

                </div>
                <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border)', background: 'var(--bg2)', display: 'flex', justifyContent: 'flex-end', gap: '12px', borderBottomLeftRadius: '12px', borderBottomRightRadius: '12px' }}>
                    <button type="button" className="btn btn-ghost" onClick={() => navigate('/paie')} disabled={calculating}>
                        Annuler
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={calculating || loading}>
                        <Calculator size={18} />
                        {calculating ? 'Calcul en cours...' : 'Générer le Bulletin'}
                    </button>
                </div>
            </form>
        </div>
    )
}
