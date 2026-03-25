import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService, { BulletinPaie, Employe } from '../api'
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
    AlertCircle
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
                    <h1 className="page-title">Gestion de la Paie</h1>
                    <p className="page-subtitle">Calcul des salaires, cotisations et éditions des bulletins</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn btn-outline" onClick={load}><RefreshCcw size={18} /> Actualiser</button>
                    <button className="btn btn-outline" onClick={() => navigate('/employes/nouveau')}>
                        <Users size={18} /> Nouveau Salarié
                    </button>
                    <button className="btn btn-outline" onClick={() => navigate('/paie/nouveau')}>
                        <FileText size={18} /> Générer Bulletin
                    </button>
                </div>
            </div>


            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-value">{stats.total}</div>
                    <div className="stat-label">Total Bulletins</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--success)' }}>{stats.valide}</div>
                    <div className="stat-label">Bulletins Validés</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value" style={{ color: 'var(--warning)' }}>{stats.draft}</div>
                    <div className="stat-label">En Brouillon</div>
                </div>
                <div className="stat-card">
                    <div className="stat-value">{stats.masse.toLocaleString()} MAD</div>
                    <div className="stat-label">Masse Salariale Nette</div>
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '24px' }}>
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Bulletins de paie</div>
                        <input
                            type="text"
                            className="form-input"
                            placeholder="Rechercher un salarié..."
                            style={{ width: '250px' }}
                            value={filter}
                            onChange={e => setFilter(e.target.value)}
                        />
                    </div>

                    <div className="table-wrap">
                        {loading ? (
                            <div className="loading">Chargement...</div>
                        ) : filtered.length === 0 ? (
                            <div className="empty-state">Aucun bulletin trouvé</div>
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Période</th>
                                        <th>Salarié</th>
                                        <th>Brut</th>
                                        <th>Net</th>
                                        <th>Statut</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {filtered.map(b => (
                                        <tr
                                            key={b.id}
                                            onClick={() => navigate(`/paie/${b.id}`)}
                                            style={{ cursor: 'pointer' }}
                                        >
                                            <td>{new Date(2024, b.mois - 1).toLocaleString('fr-FR', { month: 'long' })} {b.annee}</td>
                                            <td style={{ fontWeight: 600 }}>{b.employe_nom}</td>
                                            <td>{b.salaire_brut.toLocaleString()}</td>
                                            <td style={{ fontWeight: 700 }}>{b.salaire_net.toLocaleString()} MAD</td>
                                            <td>
                                                <span className={`badge badge-${b.statut === 'VALIDE' ? 'validated' : 'draft'}`}>
                                                    {b.statut}
                                                </span>
                                            </td>
                                            <td>
                                                <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
                                                    <button
                                                        className="btn btn-ghost"
                                                        style={{ padding: '6px', borderRadius: '8px' }}
                                                        onClick={(e) => { e.stopPropagation(); navigate(`/paie/${b.id}`); }}
                                                        title="Voir le bulletin"
                                                    >
                                                        <Eye size={16} />
                                                    </button>
                                                    <button
                                                        className="btn btn-ghost"
                                                        style={{ padding: '6px', borderRadius: '8px', color: 'var(--accent)' }}
                                                        title="Télécharger PDF"
                                                        onClick={async (e) => {
                                                            e.stopPropagation()
                                                            const MOIS = ['', 'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
                                                                'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
                                                            const filename = `Bulletin_Paie_${(b.employe_nom || 'Employe').replace(/\s+/g, '_')}_${MOIS[b.mois]}_${b.annee}.pdf`
                                                            try { await apiService.downloadBulletinPdf(b.id, filename) }
                                                            catch { alert('Erreur PDF') }
                                                        }}
                                                    >
                                                        <Download size={16} />
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
