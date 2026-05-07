import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService, { BulletinPaie, Employe } from '../../api'
import {
    Users,
    Search,
    FileText,
    Calendar,
    ChevronRight,
    Download,
    CheckCircle2,
    Clock,
    Printer,
    ChevronLeft,
    Eye,
    X,
    Trash2,
    RefreshCcw,
    AlertCircle,
    Edit
} from 'lucide-react'

/**
 * PAIE V1 - LEGACY VERSION
 * Simple list and side-panel detail view.
 */
export default function Paie() {
    const navigate = useNavigate()
    const [bulletins, setBulletins] = useState<BulletinPaie[]>([])
    const [employes, setEmployes] = useState<Employe[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState('')

    const load = async () => {
        setLoading(true)
        try {
            const [b, e] = await Promise.all([
                apiService.listBulletins(),
                apiService.listEmployes('ACTIF')
            ])
            setBulletins(b)
            setEmployes(e)
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => { load() }, [])


    const handleValidate = async (id: number) => {
        if (!window.confirm('Valider définitivement ce bulletin ?')) return
    }

    const stats = {
        total: bulletins.length,
        valide: bulletins.filter(b => b.statut === 'VALIDE').length,
        draft: bulletins.filter(b => b.statut === 'BROUILLON').length,
        masse: bulletins.reduce((sum, b) => sum + (b.salaire_net || 0), 0)
    }

    const filtered = bulletins.filter(b =>
        (b.employe_nom || '').toLowerCase().includes(filter.toLowerCase())
    )

    return (
        <div>
            <div className="page-header">
                <div>
                    <h1 className="page-title">Gestion du Personnel</h1>
                    <p className="page-subtitle">Administration des salariés et de leurs contrats</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn btn-outline" onClick={load}><RefreshCcw size={18} /> Actualiser</button>
                    <button className="btn btn-primary" onClick={() => navigate('/employes/nouveau')}>
                        <Users size={18} /> Nouveau Salarié
                    </button>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
                {/* Liste des Salariés */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Registre du Personnel</div>
                        <p style={{ fontSize: '13px', color: 'var(--text3)' }}>{employes.length} salarié(s) actif(s)</p>
                    </div>
                    <div className="table-wrap">
                        {loading ? (
                            <div className="loading">Chargement...</div>
                        ) : employes.length === 0 ? (
                            <div className="empty-state">Aucun salarié enregistré</div>
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Nom & Prénom</th>
                                        <th>Poste</th>
                                        <th>CIN</th>
                                        <th>Date d'embauche</th>
                                        <th>Salaire de base</th>
                                        <th style={{ textAlign: 'center' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {employes.map(emp => (
                                        <tr key={emp.id}>
                                            <td style={{ fontWeight: 600 }}>{emp.nom} {emp.prenom}</td>
                                            <td>{emp.poste || '—'}</td>
                                            <td>{emp.cin || '—'}</td>
                                            <td>{emp.date_embauche}</td>
                                            <td style={{ fontWeight: 700, color: 'var(--accent)' }}>{emp.salaire_base?.toLocaleString()} MAD</td>
                                            <td style={{ textAlign: 'center' }}>
                                                <div style={{ display: 'flex', gap: '8px', justifyContent: 'center' }}>
                                                    <button 
                                                        className="btn btn-ghost"
                                                        style={{ padding: '8px', color: 'var(--accent)' }}
                                                        onClick={() => navigate(`/employes/${emp.id}/edit`)}
                                                        title="Modifier"
                                                    >
                                                        <Edit size={16} />
                                                    </button>
                                                    <button 
                                                        className="btn btn-ghost"
                                                        style={{ padding: '8px', color: '#ef4444' }}
                                                        onClick={async () => {
                                                            if (window.confirm(`Supprimer le salarié ${emp.nom} ${emp.prenom} ?`)) {
                                                                try {
                                                                    await apiService.updateEmploye(emp.id, { statut: 'INACTIF' })
                                                                    load()
                                                                } catch { alert('Erreur lors de la suppression') }
                                                                }
                                                        }}
                                                        title="Désactiver"
                                                    >
                                                        <Trash2 size={16} />
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}
