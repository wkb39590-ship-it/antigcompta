import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { BulletinPaie, JournalEntry } from '../api'
import {
    ChevronLeft,
    Printer,
    CheckCircle2,
    FileText,
    Clock,
    User as UserIcon,
    Calendar,
    ArrowLeft
} from 'lucide-react'

export default function BulletinPaieDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [bulletin, setBulletin] = useState<BulletinPaie | null>(null)
    const [entries, setEntries] = useState<JournalEntry | null>(null)
    const [loading, setLoading] = useState(true)
    const [loadingEntries, setLoadingEntries] = useState(false)
    const [error, setError] = useState('')

    useEffect(() => {
        if (id) {
            loadData(parseInt(id))
        }
    }, [id])

    const loadData = async (bulletinId: number) => {
        setLoading(true)
        try {
            const data = await apiService.getBulletin(bulletinId)
            setBulletin(data)
            if (data.statut === 'VALIDE') {
                fetchEntries(bulletinId)
            }
        } catch (err: any) {
            setError('Impossible de charger le bulletin.')
        } finally {
            setLoading(false)
        }
    }

    const fetchEntries = async (bulletinId: number) => {
        setLoadingEntries(true)
        try {
            const data = await apiService.getBulletinEntries(bulletinId)
            setEntries(data.journal_entry)
        } catch (err) {
            console.error('Error fetching entries:', err)
        } finally {
            setLoadingEntries(false)
        }
    }

    const handleValidate = async () => {
        if (!bulletin || !window.confirm('Valider définitivement ce bulletin ?')) return
        try {
            await apiService.validateBulletin(bulletin.id)
            loadData(bulletin.id)
        } catch (err) {
            alert('Erreur de validation')
        }
    }

    if (loading) return <div className="page-content">Chargement...</div>
    if (error || !bulletin) return <div className="page-content">{error || 'Bulletin introuvable'}</div>

    return (
        <div className="page-content" style={{ maxWidth: '1000px', margin: '0 auto' }}>
            <div className="page-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <button className="btn btn-ghost" onClick={() => navigate('/paie')} style={{ padding: '8px' }}>
                        <ArrowLeft size={20} />
                    </button>
                    <div>
                        <h1 className="page-title">Bulletin de Paie #{bulletin.id}</h1>
                        <p className="page-subtitle">
                            {bulletin.employe_nom} · {new Date(2024, bulletin.mois - 1).toLocaleString('fr-FR', { month: 'long' })} {bulletin.annee}
                        </p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="btn btn-ghost"><Printer size={18} /> Imprimer</button>
                    {bulletin.statut !== 'VALIDE' && (
                        <button className="btn btn-primary" onClick={handleValidate}>
                            <CheckCircle2 size={18} /> Valider le bulletin
                        </button>
                    )}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 350px', gap: '24px' }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Infos Salarié */}
                    <div className="card">
                        <div className="card-header">
                            <div className="card-title">Informations du Salarié</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', padding: '20px' }}>
                            <div style={{
                                width: '64px', height: '64px', borderRadius: '50%', background: 'var(--accent)',
                                color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontWeight: 'bold', fontSize: '24px'
                            }}>
                                {bulletin.employe_nom?.[0].toUpperCase()}
                            </div>
                            <div style={{ flexGrow: 1 }}>
                                <div style={{ fontSize: '18px', fontWeight: 'bold' }}>{bulletin.employe_nom}</div>
                                <div style={{ color: 'var(--text3)', display: 'flex', gap: '12px', fontSize: '13px', marginTop: '4px' }}>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><UserIcon size={14} /> Matricule: #{bulletin.employe_id}</span>
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={14} /> Période: {bulletin.mois}/{bulletin.annee}</span>
                                </div>
                            </div>
                            <div className={`badge badge-${bulletin.statut === 'VALIDE' ? 'validated' : 'draft'}`} style={{ fontSize: '12px', padding: '6px 12px' }}>
                                {bulletin.statut}
                            </div>
                        </div>
                    </div>

                    {/* Écritures Comptables */}
                    {bulletin.statut === 'VALIDE' && (
                        <div className="card">
                            <div className="card-header">
                                <div className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <FileText size={18} /> Écritures Comptables OD
                                </div>
                            </div>
                            {loadingEntries ? (
                                <div style={{ padding: '20px', color: 'var(--text3)' }}>Chargement...</div>
                            ) : entries ? (
                                <div className="table-wrap">
                                    <table>
                                        <thead>
                                            <tr>
                                                <th>Compte</th>
                                                <th>Libellé</th>
                                                <th style={{ textAlign: 'right' }}>Débit</th>
                                                <th style={{ textAlign: 'right' }}>Crédit</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {entries.entry_lines.map(el => (
                                                <tr key={el.id}>
                                                    <td style={{ fontWeight: 600 }}>{el.account_code}</td>
                                                    <td>{el.account_label || '-'}</td>
                                                    <td style={{ textAlign: 'right', fontWeight: el.debit > 0 ? 600 : 400 }}>
                                                        {el.debit > 0 ? el.debit.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '-'}
                                                    </td>
                                                    <td style={{ textAlign: 'right', fontWeight: el.credit > 0 ? 600 : 400 }}>
                                                        {el.credit > 0 ? el.credit.toLocaleString(undefined, { minimumFractionDigits: 2 }) : '-'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                        <tfoot>
                                            <tr style={{ fontWeight: 'bold', background: 'var(--bg3)' }}>
                                                <td colSpan={2}>TOTAUX</td>
                                                <td style={{ textAlign: 'right' }}>{entries.total_debit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                                                <td style={{ textAlign: 'right' }}>{entries.total_credit.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                                            </tr>
                                        </tfoot>
                                    </table>
                                </div>
                            ) : (
                                <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text3)' }}>
                                    Aucune écriture trouvée pour ce bulletin.
                                </div>
                            )}
                        </div>
                    )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Résumé Financier */}
                    <div className="card">
                        <div className="card-header">
                            <div className="card-title">Résumé Financier</div>
                        </div>
                        <div style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: 'var(--text3)', fontSize: '14px' }}>Salaire de Base</span>
                                <span style={{ fontWeight: 600 }}>{bulletin.salaire_base.toLocaleString()} MAD</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: 'var(--text3)', fontSize: '14px' }}>Salaire Brut</span>
                                <span style={{ fontWeight: 600 }}>{bulletin.salaire_brut.toLocaleString()} MAD</span>
                            </div>
                            <div style={{ height: '1px', background: 'var(--border)' }} />
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ color: 'var(--text3)', fontSize: '14px' }}>Retenues Salariales</span>
                                <span style={{ fontWeight: 600, color: 'var(--danger)' }}>- {bulletin.total_retenues.toLocaleString()} MAD</span>
                            </div>
                            <div style={{ background: 'rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '12px', border: '1px solid rgba(16, 185, 129, 0.2)', marginTop: '8px' }}>
                                <div style={{ fontSize: '12px', color: 'var(--success)', textTransform: 'uppercase', fontWeight: 'bold' }}>Net à Payer</div>
                                <div style={{ fontSize: '24px', fontWeight: '900', color: 'var(--success)' }}>{bulletin.salaire_net.toLocaleString()} MAD</div>
                            </div>
                        </div>
                    </div>

                    {/* Charges Patronales */}
                    <div className="card">
                        <div className="card-header">
                            <div className="card-title">Charges Patronales</div>
                        </div>
                        <div style={{ padding: '20px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                                <span style={{ color: 'var(--text3)', fontSize: '14px' }}>Part Patronale</span>
                                <span style={{ fontWeight: 600 }}>{bulletin.total_patronal.toLocaleString()} MAD</span>
                            </div>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>Coût Total</span>
                                <span style={{ fontWeight: 'bold', color: 'var(--accent)' }}>{(bulletin.salaire_brut + bulletin.total_patronal).toLocaleString()} MAD</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
