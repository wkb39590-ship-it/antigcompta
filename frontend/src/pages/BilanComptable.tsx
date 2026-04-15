import { useState, useEffect } from 'react'
import apiService, { BilanOut, BilanSection } from '../api'
import { 
    FileText, 
    Calendar, 
    CheckCircle, 
    AlertCircle, 
    TrendingUp, 
    ArrowDownCircle, 
    ArrowUpCircle,
    Info
} from 'lucide-react'

export default function BilanComptable() {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [bilan, setBilan] = useState<BilanOut | null>(null)
    const [annee, setAnnee] = useState(new Date().getFullYear())
    const [validatedOnly, setValidatedOnly] = useState(true)

    const fetchBilan = async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await apiService.getBilan(annee, undefined, validatedOnly)
            setBilan(data)
        } catch (err: any) {
            console.error('Error fetching bilan:', err)
            setError(err.response?.data?.detail || "Erreur lors du calcul du bilan.")
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchBilan()
    }, [annee, validatedOnly])

    const formatAmount = (amount: any) => {
        const val = parseFloat(amount)
        if (isNaN(val)) return '0,00 MAD'
        return new Intl.NumberFormat('fr-MA', { style: 'currency', currency: 'MAD' }).format(val)
    }

    const TableSection = ({ section, isActif }: { section: any, isActif: boolean }) => (
        <div className="bilan-section" style={{ marginBottom: '24px' }}>
            <h3 style={{ 
                fontSize: '11px', 
                fontWeight: '700', 
                color: 'var(--text3)', 
                textTransform: 'uppercase',
                letterSpacing: '0.8px',
                padding: '12px 0 8px',
                borderBottom: '1px solid var(--border)'
            }}>
                {section.libelle}
            </h3>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                    <tr style={{ fontSize: '10px', color: 'var(--text3)', textTransform: 'uppercase' }}>
                        <th style={{ textAlign: 'left', padding: '4px' }}>Compte / Libellé</th>
                        {isActif ? (
                            <>
                                <th style={{ textAlign: 'right', padding: '4px' }}>Brut</th>
                                <th style={{ textAlign: 'right', padding: '4px' }}>Amort.</th>
                                <th style={{ textAlign: 'right', padding: '4px' }}>Net</th>
                            </>
                        ) : (
                            <th style={{ textAlign: 'right', padding: '4px' }}>Montant</th>
                        )}
                    </tr>
                </thead>
                <tbody>
                    {section.lignes.map((line: any, idx: number) => (
                        <tr key={idx} style={{ borderBottom: '1px solid rgba(0,0,0,0.03)' }}>
                            <td style={{ padding: '6px 4px', fontSize: '12px' }}>
                                <span style={{ fontWeight: '600', color: 'var(--text2)', marginRight: '8px' }}>{line.account_code}</span>
                                <span style={{ color: 'var(--text)' }}>{line.account_label}</span>
                            </td>
                            {isActif ? (
                                <>
                                    <td style={{ padding: '6px 4px', fontSize: '12px', textAlign: 'right' }}>{formatAmount(line.brut)}</td>
                                    <td style={{ padding: '6px 4px', fontSize: '12px', textAlign: 'right' }}>{formatAmount(line.amortissement)}</td>
                                    <td style={{ padding: '6px 4px', fontSize: '12px', textAlign: 'right', fontWeight: '600' }}>{formatAmount(line.net)}</td>
                                </>
                            ) : (
                                <td style={{ padding: '6px 4px', fontSize: '12px', textAlign: 'right', fontWeight: '600' }}>{formatAmount(line.net)}</td>
                            )}
                        </tr>
                    ))}
                    <tr style={{ background: isActif ? 'rgba(5, 150, 105, 0.04)' : 'rgba(99, 102, 241, 0.04)' }}>
                        <td style={{ padding: '10px 4px', fontSize: '11px', fontWeight: '700', color: isActif ? 'var(--success)' : 'var(--accent)' }}>
                            TOTAL {section.libelle}
                        </td>
                        {isActif ? (
                            <>
                                <td style={{ padding: '10px 4px', fontSize: '12px', fontWeight: '700', textAlign: 'right' }}>{formatAmount(section.total_brut)}</td>
                                <td style={{ padding: '10px 4px', fontSize: '12px', fontWeight: '700', textAlign: 'right' }}>{formatAmount(section.total_amortissement)}</td>
                                <td style={{ padding: '10px 4px', fontSize: '13px', fontWeight: '800', textAlign: 'right' }}>{formatAmount(section.total)}</td>
                            </>
                        ) : (
                            <td style={{ padding: '10px 4px', fontSize: '13px', fontWeight: '800', textAlign: 'right' }}>{formatAmount(section.total)}</td>
                        )}
                    </tr>
                </tbody>
            </table>
        </div>
    )

    const handleExportPdf = async () => {
        try {
            const token = localStorage.getItem('session_token') || localStorage.getItem('access_token')
            window.open(`/api/bilan/pdf?annee=${annee}&validated_only=${validatedOnly}&token=${token}`, '_blank')
        } catch (err) {
            console.error('Export failed:', err)
        }
    }

    return (
        <div className="container-pro">
            <header className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
                <div>
                    <h2 className="page-title">Bilan Comptable (Modèle CGNC)</h2>
                    <p className="page-subtitle">État de synthèse annuel conforme aux normes DGI</p>
                </div>
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                    <button className="btn btn-primary" onClick={handleExportPdf}>
                        <ArrowDownCircle size={18} />
                        Exporter en PDF
                    </button>
                    <div className="form-group" style={{ marginBottom: 0 }}>
                        <label className="form-label">Année</label>
                        <select 
                            className="form-input" 
                            style={{ width: '120px' }}
                            value={annee}
                            onChange={(e) => setAnnee(parseInt(e.target.value))}
                        >
                            {[2023, 2024, 2025, 2026].map(y => <option key={y} value={y}>{y}</option>)}
                        </select>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', paddingTop: '18px' }}>
                        <input 
                            type="checkbox" 
                            id="validOnly"
                            checked={validatedOnly}
                            onChange={(e) => setValidatedOnly(e.target.checked)}
                            style={{ cursor: 'pointer' }}
                        />
                        <label htmlFor="validOnly" style={{ fontSize: '13px', cursor: 'pointer', color: 'var(--text2)' }}>
                            Écritures validées uniquement
                        </label>
                    </div>
                </div>
            </header>

            {loading ? (
                <div className="loading">
                    <div className="spinner"></div>
                    Chargement des données comptables...
                </div>
            ) : error ? (
                <div className="alert alert-error">
                    <AlertCircle size={18} />
                    {error}
                </div>
            ) : bilan ? (
                <>
                    <div className="stats-grid">
                        <div className="stat-card aurora-card">
                            <div className="stat-icon"><ArrowUpCircle color="var(--success)" /></div>
                            <div className="stat-value">{formatAmount(bilan.total_actif)}</div>
                            <div className="stat-label">Total Actif</div>
                        </div>
                        <div className="stat-card aurora-card">
                            <div className="stat-icon"><ArrowDownCircle color="var(--accent)" /></div>
                            <div className="stat-value">{formatAmount(bilan.total_passif)}</div>
                            <div className="stat-label">Total Passif</div>
                        </div>
                        <div className={`stat-card aurora-card ${bilan.resultat >= 0 ? 'success' : 'danger'}`}>
                            <div className="stat-icon"><TrendingUp /></div>
                            <div className="stat-value" style={{ color: bilan.resultat >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                {formatAmount(bilan.resultat)}
                            </div>
                            <div className="stat-label">Résultat (Bénéfice/Perte)</div>
                        </div>
                        <div className="stat-card aurora-card">
                            <div className="stat-icon">
                                {bilan.is_balanced ? <CheckCircle color="var(--success)" /> : <AlertCircle color="var(--danger)" />}
                            </div>
                            <div className="stat-value" style={{ fontSize: '18px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {bilan.is_balanced ? "Équilibré" : "Hors Équilibre"}
                            </div>
                            <div className="stat-label">Statut du Bilan</div>
                        </div>
                    </div>

                    {!bilan.is_balanced && (
                        <div className="alert alert-info" style={{ marginBottom: '24px' }}>
                            <Info size={18} />
                            Veuillez vérifier vos écritures d'ouverture ou les OD de régularisation pour équilibrer le bilan.
                        </div>
                    )}

                    <div className="two-col" style={{ alignItems: 'start' }}>
                        {/* ACTIF */}
                        <div className="card aurora-card" style={{ padding: '32px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', borderBottom: '2px solid var(--success)', paddingBottom: '12px' }}>
                                <div style={{ background: 'var(--success)', color: 'white', padding: '6px', borderRadius: '8px' }}>
                                    <FileText size={20} />
                                </div>
                                <h2 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text)' }}>ACTIF (Emplois)</h2>
                            </div>
                            
                            {bilan.actif.length > 0 ? (
                                bilan.actif.map((sec, i) => <TableSection key={i} section={sec} isActif={true} />)
                            ) : (
                                <div className="empty-state">Aucun compte d'actif mouvementé.</div>
                            )}

                            <div style={{ marginTop: '20px', padding: '16px', borderRadius: '12px', background: 'var(--slate-900)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontWeight: '700', fontSize: '14px', textTransform: 'uppercase' }}>TOTAL GÉNÉRAL ACTIF</span>
                                <span style={{ fontWeight: '900', fontSize: '18px' }}>{formatAmount(bilan.total_actif)}</span>
                            </div>
                        </div>

                        {/* PASSIF */}
                        <div className="card aurora-card" style={{ padding: '32px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px', borderBottom: '2px solid var(--accent)', paddingBottom: '12px' }}>
                                <div style={{ background: 'var(--accent)', color: 'white', padding: '6px', borderRadius: '8px' }}>
                                    <FileText size={20} />
                                </div>
                                <h2 style={{ fontSize: '20px', fontWeight: '800', color: 'var(--text)' }}>PASSIF (Ressources)</h2>
                            </div>

                            {bilan.passif.length > 0 ? (
                                bilan.passif.map((sec, i) => <TableSection key={i} section={sec} isActif={false} />)
                            ) : (
                                <div className="empty-state">Aucun compte de passif mouvementé.</div>
                            )}

                            {/* Section Résultat dans le passif */}
                            <div className="bilan-section" style={{ marginBottom: '24px' }}>
                                <h3 style={{ fontSize: '12px', fontWeight: '700', color: 'var(--text3)', textTransform: 'uppercase', letterSpacing: '0.5px', padding: '12px 0 8px', borderBottom: '1px solid var(--border)' }}>
                                    RÉSULTAT NET
                                </h3>
                                <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                    <tbody>
                                        <tr>
                                            <td style={{ padding: '8px 4px', fontSize: '13px', color: 'var(--text2)', width: '60px' }}>1191</td>
                                            <td style={{ padding: '8px 4px', fontSize: '13px', color: 'var(--text)' }}>Résultat net de l'exercice</td>
                                            <td style={{ padding: '8px 4px', fontSize: '13px', fontWeight: '600', textAlign: 'right', color: bilan.resultat >= 0 ? 'var(--success)' : 'var(--danger)' }}>
                                                {formatAmount(bilan.resultat)}
                                            </td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>

                            <div style={{ marginTop: '20px', padding: '16px', borderRadius: '12px', background: 'var(--slate-900)', color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <span style={{ fontWeight: '700', fontSize: '14px', textTransform: 'uppercase' }}>TOTAL GÉNÉRAL PASSIF</span>
                                <span style={{ fontWeight: '900', fontSize: '18px' }}>{formatAmount(bilan.total_passif)}</span>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="empty-state">
                    <AlertCircle size={48} className="empty-icon" />
                    <p className="empty-title">Aucune donnée disponible pour cette période.</p>
                </div>
            )}

            <style>{`
                .bilan-section table tr:hover {
                    background: rgba(99, 102, 241, 0.05) !important;
                }
                .stat-card.success::before {
                    background: var(--success) !important;
                }
                .stat-card.danger::before {
                    background: var(--danger) !important;
                }
            `}</style>
        </div>
    )
}
