import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { Immo } from '../api'
import {
    ArrowLeft,
    CheckCircle2,
    X,
    AlertCircle,
    Building2,
    Calendar,
    Clock,
    FileText,
    Hash,
    Percent,
    Zap
} from 'lucide-react'

const fmt = (n?: number) => n != null ? n.toLocaleString('fr-MA', { minimumFractionDigits: 2 }) : '—'

export default function ImmoDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [immo, setImmo] = useState<Immo | null>(null)
    const [loading, setLoading] = useState(true)
    const [msg, setMsg] = useState('')

    const currentYear = new Date().getFullYear()

    const loadDetail = async (targetId: number) => {
        setLoading(true)
        try {
            const data = await apiService.getImmobilisation(targetId)
            setImmo(data)
        } catch (err: any) {
            console.error(err)
            setMsg('❌ Erreur lors du chargement des détails')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        if (id) loadDetail(parseInt(id))
    }, [id])

    const genDotation = async (immoId: number, annee: number) => {
        try {
            await apiService.generateDotation(immoId, annee)
            setMsg(`✅ Dotation ${annee} générée`)
            loadDetail(immoId)
        } catch (err: any) {
            setMsg('❌ ' + (err.response?.data?.detail || 'Erreur'))
        }
    }

    if (loading) return <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text2)' }}>⏳ Chargement des détails...</div>

    if (!immo) return (
        <div style={{ padding: '40px', textAlign: 'center' }}>
            <p style={{ color: 'var(--text2)' }}>Immobilisation introuvable</p>
            <button onClick={() => navigate('/immobilisations')} style={{ color: 'var(--accent)', background: 'none', border: 'none', cursor: 'pointer' }}>Retour à la liste</button>
        </div>
    )

    return (
        <div style={{ padding: '32px', maxWidth: '1000px', margin: '0 auto' }}>
            {/* Header / Nav */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                <button 
                    onClick={() => navigate('/immobilisations')} 
                    style={{ 
                        background: 'var(--card)', border: '1px solid var(--border)', 
                        padding: '8px', borderRadius: '10px', cursor: 'pointer', color: 'var(--text)' 
                    }}
                >
                    <ArrowLeft size={20} />
                </button>
                <div>
                    <h1 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text)', margin: 0 }}>
                        {immo.designation}
                    </h1>
                    <p style={{ color: 'var(--text2)', margin: '4px 0 0' }}>
                        Détails de l'immobilisation #{immo.id}
                    </p>
                </div>
            </div>

            {msg && (
                <div style={{
                    background: msg.startsWith('✅') ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
                    border: `1px solid ${msg.startsWith('✅') ? '#10b981' : '#ef4444'} `,
                    borderRadius: '10px', padding: '12px 20px', marginBottom: '24px',
                    color: msg.startsWith('✅') ? '#10b981' : '#ef4444',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        {msg.startsWith('✅') ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
                        {msg.replace(/^[✅❌]\s*/, '')}
                    </div>
                    <button onClick={() => setMsg('')} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'inherit' }}><X size={18} /></button>
                </div>
            )}

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '32px' }}>
                {/* Informations générales */}
                <div style={{ 
                    background: 'var(--card)', border: '1px solid var(--border)', 
                    borderRadius: '16px', padding: '24px' 
                }}>
                    <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Building2 size={18} color="var(--accent)" /> Informations Générales
                    </h3>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                        {[
                            { icon: <Calendar size={14} />, label: 'Date Acquisition', value: immo.date_acquisition },
                            { icon: <Hash size={14} />, label: 'Valeur HT', value: `${fmt(immo.valeur_acquisition)} MAD` },
                            { icon: <Hash size={14} />, label: 'TVA', value: `${fmt(immo.tva_acquisition)} MAD` },
                            { icon: <Clock size={14} />, label: 'Durée', value: `${immo.duree_amortissement} ans` },
                            { icon: <Percent size={14} />, label: 'Taux', value: `${((immo.taux_amortissement || 0) * 100).toFixed(2)}%` },
                            { icon: <FileText size={14} />, label: 'Méthode', value: immo.methode },
                        ].map((item, idx) => (
                            <div key={idx}>
                                <div style={{ fontSize: '11px', color: 'var(--text2)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    {item.icon} {item.label}
                                </div>
                                <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text)' }}>
                                    {item.value || '—'}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Paramètres comptables */}
                <div style={{ 
                    background: 'var(--card)', border: '1px solid var(--border)', 
                    borderRadius: '16px', padding: '24px' 
                }}>
                    <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Hash size={18} color="var(--accent)" /> Paramètres Comptables
                    </h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {[
                            { label: 'Compte Actif', code: immo.compte_actif_pcm },
                            { label: 'Compte Amortissement', code: immo.compte_amort_pcm },
                            { label: 'Compte Dotation', code: immo.compte_dotation_pcm },
                        ].map((item, idx) => (
                            <div key={idx} style={{ 
                                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                paddingBottom: '12px', borderBottom: idx < 2 ? '1px solid rgba(255,255,255,0.05)' : 'none'
                             }}>
                                <span style={{ fontSize: '13px', color: 'var(--text2)' }}>{item.label}</span>
                                <span style={{ 
                                    background: 'rgba(99,102,241,0.1)', color: '#818cf8', 
                                    padding: '4px 12px', borderRadius: '6px', fontSize: '13px', fontWeight: 700 
                                }}>
                                    {item.code}
                                </span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Plan d'amortissement */}
            <div style={{ 
                background: 'var(--card)', border: '1px solid var(--border)', 
                borderRadius: '16px', padding: '24px' 
            }}>
                <h3 style={{ margin: '0 0 20px', fontSize: '16px', color: 'var(--text)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Zap size={18} color="#f59e0b" /> Plan d'amortissement
                </h3>
                
                {immo.plan_amortissement && immo.plan_amortissement.length > 0 ? (
                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid var(--border)' }}>
                                    {['Année', 'Dotation annuelle', 'Amortissement cumulé', 'VNC', 'Action'].map(h => (
                                        <th key={h} style={{ 
                                            padding: '12px 16px', textAlign: h === 'Année' ? 'left' : 'right', 
                                            color: 'var(--text2)', fontWeight: 600, fontSize: '13px' 
                                        }}>
                                            {h}
                                        </th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {immo.plan_amortissement.map((l, i) => (
                                    <tr key={l.annee} style={{ 
                                        borderBottom: '1px solid rgba(255,255,255,0.04)',
                                        background: l.annee === currentYear ? 'rgba(99,102,241,0.05)' : 'transparent' 
                                    }}>
                                        <td style={{ padding: '12px 16px', color: 'var(--text)', fontSize: '14px' }}>
                                            {l.annee} {l.annee === currentYear && <span style={{ fontSize: '11px', color: '#818cf8', background: 'rgba(99,102,241,0.15)', padding: '2px 6px', borderRadius: '4px', marginLeft: '6px' }}>En cours</span>}
                                        </td>
                                        <td style={{ textAlign: 'right', padding: '12px 16px', color: '#f59e0b', fontWeight: 600 }}>{fmt(l.dotation_annuelle)}</td>
                                        <td style={{ textAlign: 'right', padding: '12px 16px', color: 'var(--text2)' }}>{fmt(l.amortissement_cumule)}</td>
                                        <td style={{ textAlign: 'right', padding: '12px 16px', color: '#10b981', fontWeight: 600 }}>{fmt(l.valeur_nette_comptable)}</td>
                                        <td style={{ textAlign: 'right', padding: '12px 16px' }}>
                                            {!l.ecriture_generee ? (
                                                <button onClick={() => genDotation(immo.id, l.annee)}
                                                    title="Générer l'écriture comptable de dotation"
                                                    style={{ 
                                                        background: 'var(--accent)', color: 'white', border: 'none', 
                                                        borderRadius: '6px', padding: '6px 12px', cursor: 'pointer', fontSize: '12px' 
                                                    }}>
                                                    Générer
                                                </button>
                                            ) : (
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', justifyContent: 'flex-end', color: '#10b981', fontSize: '13px' }}>
                                                    <CheckCircle2 size={16} /> Écriture générée
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text2)' }}>
                        Aucun plan d'amortissement n'a encore été généré pour cet actif.
                    </div>
                )}
            </div>
        </div>
    )
}
