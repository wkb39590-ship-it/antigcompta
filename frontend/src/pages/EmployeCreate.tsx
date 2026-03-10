import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'
import { ArrowLeft, Save, User as UserIcon } from 'lucide-react'

export default function EmployeCreate() {
    const navigate = useNavigate()
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    // Default values for a new employee
    const [employe, setEmploye] = useState({
        prenom: '',
        nom: '',
        cin: '',
        poste: '',
        date_embauche: new Date().toISOString().split('T')[0],
        salaire_base: 0,
        nb_enfants: 0,
        anciennete_pct: 0,
        numero_cnss: ''
    })

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            await apiService.createEmploye({
                prenom: employe.prenom,
                nom: employe.nom,
                cin: employe.cin,
                poste: employe.poste,
                date_embauche: employe.date_embauche,
                salaire_base: employe.salaire_base,
                nb_enfants: employe.nb_enfants,
                anciennete_pct: employe.anciennete_pct,
                numero_cnss: employe.numero_cnss,
                statut: 'ACTIF' // Implicit status on creation
            })
            // Redirect back to Paie dashboard after success
            navigate('/paie')
        } catch (err: any) {
            console.error('Create error:', err)
            setError(err.response?.data?.detail || 'Erreur lors de la création de l\'employé.')
        } finally {
            setLoading(false)
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
                            <UserIcon size={24} color="var(--accent)" />
                            Nouveau Salarié
                        </h1>
                        <p className="page-subtitle">Ajouter un nouveau collaborateur au système de paie</p>
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
                    <div className="card-title">Informations Personnelles et Contractuelles</div>
                </div>

                <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Prénom *</label>
                            <input
                                type="text"
                                className="form-input"
                                required
                                value={employe.prenom}
                                onChange={e => setEmploye({ ...employe, prenom: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Nom *</label>
                            <input
                                type="text"
                                className="form-input"
                                required
                                value={employe.nom}
                                onChange={e => setEmploye({ ...employe, nom: e.target.value })}
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Numéro de CIN</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.cin}
                                onChange={e => setEmploye({ ...employe, cin: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Poste Occupé</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.poste}
                                onChange={e => setEmploye({ ...employe, poste: e.target.value })}
                            />
                        </div>
                    </div>

                    <hr style={{ border: 'none', borderTop: '1px solid var(--border)', margin: '10px 0' }} />

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Date d'embauche *</label>
                            <input
                                type="date"
                                className="form-input"
                                required
                                value={employe.date_embauche}
                                onChange={e => setEmploye({ ...employe, date_embauche: e.target.value })}
                            />
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                            <div className="form-group">
                                <label className="form-label">Numéro de CNSS</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="8 chiffres (ex: 12345678)"
                                    value={employe.numero_cnss}
                                    onChange={e => setEmploye({ ...employe, numero_cnss: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Salaire de Base (MAD) *</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    className="form-input"
                                    required
                                    value={employe.salaire_base || ''}
                                    onChange={e => setEmploye({ ...employe, salaire_base: parseFloat(e.target.value) || 0 })}
                                />
                            </div>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Nombre d'enfants (Abattement IGR)</label>
                            <input
                                type="number"
                                min="0"
                                max="6"
                                className="form-input"
                                value={employe.nb_enfants}
                                onChange={e => setEmploye({ ...employe, nb_enfants: parseInt(e.target.value) || 0 })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Taux d'ancienneté manuel (%)</label>
                            <input
                                type="number"
                                step="0.1"
                                min="0"
                                max="25"
                                className="form-input"
                                placeholder="Laisser 0 pour calcul auto"
                                value={employe.anciennete_pct}
                                onChange={e => setEmploye({ ...employe, anciennete_pct: parseFloat(e.target.value) || 0 })}
                            />
                            <div style={{ fontSize: '11px', color: 'var(--text3)', marginTop: '4px' }}>
                                Par défaut, calculé automatiquement selon la date d'embauche.
                            </div>
                        </div>
                    </div>

                </div>
                <div style={{ padding: '20px 24px', borderTop: '1px solid var(--border)', background: 'var(--bg2)', display: 'flex', justifyContent: 'flex-end', gap: '12px', borderBottomLeftRadius: '12px', borderBottomRightRadius: '12px' }}>
                    <button type="button" className="btn btn-ghost" onClick={() => navigate('/paie')} disabled={loading}>
                        Annuler
                    </button>
                    <button type="submit" className="btn btn-primary" disabled={loading}>
                        <Save size={18} />
                        {loading ? 'Enregistrement...' : 'Enregistrer le salarié'}
                    </button>
                </div>
            </form>
        </div>
    )
}
