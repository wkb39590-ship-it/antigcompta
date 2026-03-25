import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService, { DocumentTransmis } from '../api'
import { Inbox, CheckCircle2, XCircle, AlertCircle, FileText, ChevronRight, Clock, Search, Filter } from 'lucide-react'

const fmtDate = (d: string) => new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })

export default function TransmissionDashboard() {
    const [stats, setStats] = useState<any[]>([])
    const [allSocietes, setAllSocietes] = useState<any[]>([])
    const [totalAttente, setTotalAttente] = useState(0)
    const [docs, setDocs] = useState<DocumentTransmis[]>([])
    const [loading, setLoading] = useState(true)
    const navigate = useNavigate()

    // Filters
    const [filterSociete, setFilterSociete] = useState<number | ''>('')
    const [filterStatut, setFilterStatut] = useState('A_TRAITER')
    
    // Action loading
    const [actionId, setActionId] = useState<number | null>(null)

    useEffect(() => {
        loadData()
    }, [filterSociete, filterStatut])

    const loadData = async () => {
        setLoading(true)
        try {
            const [dashboardData, societesData] = await Promise.all([
                apiService.getTransmissionDashboard(),
                apiService.listSocietes()
            ])
            setStats(dashboardData.stats_par_societe)
            setAllSocietes(societesData)
            setTotalAttente(dashboardData.total_a_traiter)

            const listData = await apiService.listTransmissionDocs(filterSociete === '' ? undefined : Number(filterSociete), filterStatut)
            setDocs(listData)
        } catch (err) {
            console.error('Erreur chargement dashboard', err)
        } finally {
            setLoading(false)
        }
    }

    const handleAccept = async (id: number) => {
        if (!window.confirm("Valider ce document pour l'envoyer au pipeline OCR ?")) return
        setActionId(id)
        try {
            await apiService.accepterTransmissionDoc(id)
            loadData() // Refresh
        } catch (err: any) {
            alert("Erreur: " + err.message)
        } finally {
            setActionId(null)
        }
    }

    const handleReject = async (id: number) => {
        if (!window.confirm("Rejeter définitivement ce document ?")) return
        setActionId(id)
        try {
            await apiService.rejeterTransmissionDoc(id)
            loadData() // Refresh
        } catch (err: any) {
            alert("Erreur: " + err.message)
        } finally {
            setActionId(null)
        }
    }

    return (
        <div style={{ padding: '32px', maxWidth: '1400px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ margin: 0, fontSize: '28px', color: 'var(--text)', fontWeight: 800, letterSpacing: '-0.5px', display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Inbox size={32} color="var(--accent)" />
                        Boîte de Réception Clients
                    </h1>
                    <p style={{ margin: '8px 0 0', color: 'var(--text3)', fontSize: '15px' }}>
                        Gérez les documents envoyés par vos clients depuis leur portail.
                    </p>
                </div>
                <div style={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', padding: '12px 24px', borderRadius: '16px', color: 'white', display: 'flex', alignItems: 'center', gap: '12px', boxShadow: '0 10px 15px -3px rgba(239, 68, 68, 0.3)' }}>
                    <AlertCircle size={24} />
                    <div>
                        <div style={{ fontSize: '12px', fontWeight: 600, opacity: 0.9, textTransform: 'uppercase', letterSpacing: '0.5px' }}>À Traiter</div>
                        <div style={{ fontSize: '24px', fontWeight: 800, lineHeight: 1 }}>{totalAttente}</div>
                    </div>
                </div>
            </div>

            {/* Stats Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', marginBottom: '40px' }}>
                {(() => {
                    let displayedStats = stats
                    if (filterSociete !== '') {
                        displayedStats = stats.filter(s => s.societe_id === filterSociete)
                        // If selected society has 0 activity, synthesize a 0 card
                        if (displayedStats.length === 0) {
                            const soc = allSocietes.find(s => s.id === filterSociete)
                            if (soc) {
                                displayedStats = [{
                                    societe_id: soc.id,
                                    raison_sociale: soc.raison_sociale,
                                    A_TRAITER: 0,
                                    VALIDE: 0,
                                    REJETE: 0
                                }]
                            }
                        }
                    }

                    if (displayedStats.length === 0 && !loading) {
                        return <div style={{ color: 'var(--text3)' }}>Aucune activité client détectée.</div>
                    }

                    return displayedStats.map(s => (
                        <div key={s.societe_id} onClick={() => setFilterSociete(s.societe_id)} style={{ background: 'white', border: filterSociete === s.societe_id ? '2px solid var(--accent)' : '1px solid var(--border)', borderRadius: '16px', padding: '20px', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)' }}>
                            <h3 style={{ margin: '0 0 16px', fontSize: '16px', fontWeight: 700, color: 'var(--text)' }}>{s.raison_sociale}</h3>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <div style={{ flex: 1, background: '#fef3c7', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#b45309' }}>{s.A_TRAITER}</div>
                                    <div style={{ fontSize: '11px', color: '#b45309', fontWeight: 600, textTransform: 'uppercase' }}>Nouveaux</div>
                                </div>
                                <div style={{ flex: 1, background: '#dcfce7', padding: '10px', borderRadius: '8px', textAlign: 'center' }}>
                                    <div style={{ fontSize: '20px', fontWeight: 800, color: '#15803d' }}>{s.VALIDE}</div>
                                    <div style={{ fontSize: '11px', color: '#15803d', fontWeight: 600, textTransform: 'uppercase' }}>Validés</div>
                                </div>
                            </div>
                        </div>
                    ))
                })()}
            </div>

            {/* Toolbar */}
            <div style={{ display: 'flex', gap: '16px', marginBottom: '24px', alignItems: 'center', background: 'white', padding: '16px', borderRadius: '12px', border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                    <Filter size={18} color="var(--text3)" />
                    <select value={filterSociete} onChange={e => setFilterSociete(e.target.value === '' ? '' : Number(e.target.value))} style={{ padding: '8px 12px', border: '1px solid var(--border)', borderRadius: '8px', outline: 'none', background: 'var(--bg)', width: '250px' }}>
                        <option value="">Toutes les sociétés</option>
                        {allSocietes.map(s => (
                            <option key={s.id} value={s.id}>
                                {s.raison_sociale} {stats.find(st => st.societe_id === s.id)?.A_TRAITER > 0 ? `(${stats.find(st => st.societe_id === s.id).A_TRAITER})` : ''}
                            </option>
                        ))}
                    </select>
                </div>
                <div style={{ display: 'flex', background: 'var(--bg)', padding: '4px', borderRadius: '8px', gap: '4px' }}>
                    <button onClick={() => setFilterStatut('A_TRAITER')} style={{ padding: '6px 16px', background: filterStatut === 'A_TRAITER' ? 'white' : 'transparent', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '13px', color: filterStatut === 'A_TRAITER' ? 'var(--text)' : 'var(--text3)', boxShadow: filterStatut === 'A_TRAITER' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none', cursor: 'pointer' }}>À Traiter</button>
                    <button onClick={() => setFilterStatut('VALIDE')} style={{ padding: '6px 16px', background: filterStatut === 'VALIDE' ? 'white' : 'transparent', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '13px', color: filterStatut === 'VALIDE' ? 'var(--text)' : 'var(--text3)', boxShadow: filterStatut === 'VALIDE' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none', cursor: 'pointer' }}>Validés</button>
                    <button onClick={() => setFilterStatut('REJETE')} style={{ padding: '6px 16px', background: filterStatut === 'REJETE' ? 'white' : 'transparent', border: 'none', borderRadius: '6px', fontWeight: 600, fontSize: '13px', color: filterStatut === 'REJETE' ? 'var(--text)' : 'var(--text3)', boxShadow: filterStatut === 'REJETE' ? '0 2px 4px rgba(0,0,0,0.05)' : 'none', cursor: 'pointer' }}>Rejetés</button>
                </div>
            </div>

            {/* List */}
            {loading ? (
                <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text3)' }}>Chargement en cours...</div>
            ) : docs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '60px', background: 'white', borderRadius: '16px', border: '1px dashed var(--border)' }}>
                    <Inbox size={48} color="var(--border)" style={{ margin: '0 auto 16px' }} />
                    <h3 style={{ margin: '0 0 8px', color: 'var(--text)' }}>Aucun document</h3>
                    <p style={{ margin: 0, color: 'var(--text3)' }}>Il n'y a aucun document correspondant à ces filtres.</p>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {docs.map(doc => {
                        const socName = stats.find(s => s.societe_id === doc.societe_id)?.raison_sociale || 'Société Inconnue'
                        return (
                            <div key={doc.id} style={{ background: 'white', border: '1px solid var(--border)', borderRadius: '12px', padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', transition: 'all 0.2s', boxShadow: '0 2px 4px rgba(0,0,0,0.02)' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
                                    <div style={{ width: '48px', height: '48px', background: 'var(--bg)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <FileText size={24} color="var(--accent)" />
                                    </div>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                            <span style={{ fontSize: '15px', fontWeight: 700, color: 'var(--text)' }}>{doc.file_name}</span>
                                            <span style={{ background: '#f1f5f9', color: '#475569', padding: '2px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>{doc.type_document}</span>
                                        </div>
                                        <div style={{ fontSize: '13px', color: 'var(--text3)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                            <strong>{socName}</strong> • Uploadé le {fmtDate(doc.date_upload)}
                                        </div>
                                        {doc.notes_client && (
                                            <div style={{ fontSize: '12px', color: '#64748b', marginTop: '6px', background: '#f8fafc', padding: '6px 10px', borderRadius: '6px', display: 'inline-block' }}>
                                                📝 Note: {doc.notes_client}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    {doc.statut === 'A_TRAITER' ? (
                                        <>
                                            <button 
                                                onClick={() => handleAccept(doc.id)} 
                                                disabled={actionId === doc.id}
                                                style={{ padding: '8px 16px', background: '#10b981', color: 'white', border: 'none', borderRadius: '8px', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
                                            >
                                                <CheckCircle2 size={16} /> Accepter
                                            </button>
                                            <button 
                                                onClick={() => handleReject(doc.id)} 
                                                disabled={actionId === doc.id}
                                                style={{ padding: '8px 16px', background: 'transparent', color: '#ef4444', border: '1px solid #fca5a5', borderRadius: '8px', fontWeight: 600, cursor: 'pointer' }}
                                            >
                                                Rejeter
                                            </button>
                                        </>
                                    ) : (
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            <div style={{ fontSize: '13px', fontWeight: 600, color: doc.statut === 'VALIDE' ? '#10b981' : '#ef4444', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                                {doc.statut === 'VALIDE' ? <CheckCircle2 size={16} /> : <XCircle size={16} />}
                                                {doc.statut === 'VALIDE' ? 'Document Transféré' : 'Document Rejeté'}
                                            </div>
                                            {doc.statut === 'VALIDE' && (doc as any).facture_id && (
                                                <button 
                                                    onClick={() => navigate(`/factures/${(doc as any).facture_id}`)}
                                                    style={{ padding: '6px 12px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', border: '1px solid #10b981', borderRadius: '6px', fontSize: '12px', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                                                >
                                                    Gérer <ChevronRight size={14} />
                                                </button>
                                            )}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )
                    })}
                </div>
            )}
        </div>
    )
}
