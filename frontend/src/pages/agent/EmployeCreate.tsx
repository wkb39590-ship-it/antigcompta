import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import apiService from '../../api'
import { ArrowLeft, Save, User as UserIcon } from 'lucide-react'

export default function EmployeCreate() {
    const navigate = useNavigate()
    const { id } = useParams()
    const isEdit = !!id
    const [loading, setLoading] = useState(false)
    const [fetching, setFetching] = useState(isEdit)
    const [error, setError] = useState('')

    // Default values
    const [employe, setEmploye] = useState({
        prenom: '',
        nom: '',
        matricule: '',
        cin: '',
        date_naissance: '',
        situation_familiale: 'Célibataire',
        adresse: '',
        poste: '',
        departement: '',
        date_embauche: new Date().toISOString().split('T')[0],
        salaire_base: 0,
        nb_enfants: 0,
        anciennete_pct: 0,
        numero_cnss: '',
        numero_mutuelle: '',
        numero_retraite: ''
    })

    useEffect(() => {
        if (isEdit) {
            loadEmploye()
        }
    }, [id])

    const loadEmploye = async () => {
        try {
            const data = await apiService.getEmploye(Number(id))
            setEmploye({
                ...data,
                date_naissance: data.date_naissance || '',
                date_embauche: data.date_embauche || new Date().toISOString().split('T')[0],
                situation_familiale: data.situation_familiale || 'Célibataire',
                adresse: data.adresse || '',
                departement: data.departement || '',
                matricule: data.matricule || '',
                numero_mutuelle: data.numero_mutuelle || '',
                numero_retraite: data.numero_retraite || ''
            })
        } catch (err) {
            setError("Impossible de charger les données de l'employé.")
        } finally {
            setFetching(false)
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            if (isEdit) {
                await apiService.updateEmploye(Number(id), employe)
            } else {
                await apiService.createEmploye({ ...employe, statut: 'ACTIF' })
            }
            navigate('/paie')
        } catch (err: any) {
            console.error('Save error:', err)
            setError(err.response?.data?.detail || 'Erreur lors de l\'enregistrement.')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="page-content" style={{ maxWidth: '900px', margin: '0 auto' }}>
            <div className="page-header" style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn btn-ghost" onClick={() => navigate('/paie')} style={{ padding: '8px' }}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <UserIcon size={24} color="var(--accent)" />
                            {isEdit ? 'Modifier le Salarié' : 'Nouveau Salarié'}
                        </h1>
                        <p className="page-subtitle">Gestion des informations détaillées du collaborateur</p>
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
                    <div className="card-title">Identité et Situation Familiale</div>
                </div>

                <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Matricule</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="ex: 0319"
                                value={employe.matricule}
                                onChange={e => setEmploye({ ...employe, matricule: e.target.value })}
                            />
                        </div>
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

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">CIN</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.cin}
                                onChange={e => setEmploye({ ...employe, cin: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Date de Naissance</label>
                            <input
                                type="date"
                                className="form-input"
                                value={employe.date_naissance}
                                onChange={e => setEmploye({ ...employe, date_naissance: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Situation Familiale</label>
                            <select 
                                className="form-input"
                                value={employe.situation_familiale}
                                onChange={e => setEmploye({ ...employe, situation_familiale: e.target.value })}
                            >
                                <option value="Célibataire">Célibataire</option>
                                <option value="Marié(e)">Marié(e)</option>
                                <option value="Divorcé(e)">Divorcé(e)</option>
                                <option value="Veuf(ve)">Veuf(ve)</option>
                            </select>
                        </div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Adresse Personnelle</label>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Adresse complète..."
                            value={employe.adresse}
                            onChange={e => setEmploye({ ...employe, adresse: e.target.value })}
                        />
                    </div>

                    <div className="card-header" style={{ padding: '20px 0 10px 0', borderBottom: 'none' }}>
                        <div className="card-title" style={{ fontSize: '15px' }}>Affectation et Salaire</div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Poste Occupé</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.poste}
                                onChange={e => setEmploye({ ...employe, poste: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Département</label>
                            <input
                                type="text"
                                className="form-input"
                                placeholder="ex: RH, Technique..."
                                value={employe.departement}
                                onChange={e => setEmploye({ ...employe, departement: e.target.value })}
                            />
                        </div>
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
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">Salaire de Base (MAD) *</label>
                            <input
                                type="number"
                                step="0.01"
                                className="form-input"
                                required
                                value={employe.salaire_base || ''}
                                onChange={e => setEmploye({ ...employe, salaire_base: parseFloat(e.target.value) || 0 })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Nombre d'enfants</label>
                            <input
                                type="number"
                                min="0"
                                className="form-input"
                                value={employe.nb_enfants}
                                onChange={e => setEmploye({ ...employe, nb_enfants: parseInt(e.target.value) || 0 })}
                            />
                        </div>
                    </div>

                    <div className="card-header" style={{ padding: '20px 0 10px 0', borderBottom: 'none' }}>
                        <div className="card-title" style={{ fontSize: '15px' }}>Organismes Sociaux</div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px' }}>
                        <div className="form-group">
                            <label className="form-label">N° CNSS</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.numero_cnss}
                                onChange={e => setEmploye({ ...employe, numero_cnss: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">N° Mutuelle</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.numero_mutuelle}
                                onChange={e => setEmploye({ ...employe, numero_mutuelle: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">N° Retraite</label>
                            <input
                                type="text"
                                className="form-input"
                                value={employe.numero_retraite}
                                onChange={e => setEmploye({ ...employe, numero_retraite: e.target.value })}
                            />
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
