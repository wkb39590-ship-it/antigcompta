import React, { Component, ErrorInfo, ReactNode, useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import apiService, { ReleveBancaire, LigneReleve } from '../api'
import {
    FileText,
    ArrowRight,
    Link as LinkIcon,
    CheckCircle2,
    X,
    Link2,
    Search,
    ChevronDown,
    AlertCircle,
    ArrowLeft
} from 'lucide-react'

// --- COMPOSANT SÉLECTEUR DE COMPTE PCM ---
interface AccountSelectorProps {
    isOpen: boolean;
    onClose: () => void;
    onSelect: (code: string) => void;
    suggestion?: { pcm_account_code: string; pcm_account_label: string; confidence: number; reason: string } | null;
}

function AccountSelector({ isOpen, onClose, onSelect, suggestion }: AccountSelectorProps) {
    const [searchTerm, setSearchTerm] = useState('')
    const [accounts, setAccounts] = useState<any[]>([])
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (isOpen) {
            loadAccounts()
            if (suggestion) {
                setSearchTerm('') // Reset search to show suggestion
            }
        }
    }, [isOpen, suggestion])

    const loadAccounts = async () => {
        setLoading(true)
        try {
            // On charge une liste de base (ex: classes 4, 1, 6, 7 souvent utiles en rapprochement)
            const data = await apiService.getPcmAccounts()
            setAccounts(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const filtered = accounts.filter(a =>
        a.code.includes(searchTerm) ||
        a.label.toLowerCase().includes(searchTerm.toLowerCase())
    ).slice(0, 100) // Limite pour la perf

    if (!isOpen) return null

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: '20px'
        }}>
            <div className="card" style={{ width: '100%', maxWidth: '500px', maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
                <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '16px' }}>
                    <div style={{ fontWeight: 'bold' }}>Sélectionner un compte (PCM)</div>
                    <button onClick={onClose} style={{ border: 'none', background: 'none', cursor: 'pointer' }}><X size={20} /></button>
                </div>
                <div style={{ padding: '16px', borderBottom: '1px solid var(--border)' }}>
                    <div className="search-bar" style={{ width: '100%', padding: '8px' }}>
                        <Search size={16} />
                        <input
                            autoFocus
                            type="text"
                            placeholder="Rechercher code ou libellé..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{ width: '100%', outline: 'none' }}
                        />
                    </div>
                </div>
                <div style={{ overflowY: 'auto', flex: 1, padding: '8px' }}>
                    {loading ? (
                        <div style={{ padding: '20px', textAlign: 'center' }}>Chargement...</div>
                    ) : (
                        <>
                            {/* Affichage de la suggestion IA en priorité */}
                            {suggestion && !searchTerm && (
                                <div style={{ marginBottom: '16px', padding: '12px', background: 'rgba(99, 102, 241, 0.1)', borderRadius: '8px', border: '1px dashed var(--accent)' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--accent)', fontWeight: 'bold', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                        <CheckCircle2 size={12} /> SUGGESTION IA (Confiance: {Math.round(suggestion.confidence * 100)}%)
                                    </div>
                                    <div
                                        onClick={() => onSelect(suggestion.pcm_account_code)}
                                        style={{
                                            padding: '10px 16px', borderRadius: '6px', cursor: 'pointer',
                                            display: 'flex', justifyContent: 'space-between', background: '#fff'
                                        }}
                                    >
                                        <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{suggestion.pcm_account_code}</div>
                                        <div style={{ fontSize: '13px', color: 'var(--text2)', textAlign: 'right', flex: 1, marginLeft: '12px' }}>{suggestion.pcm_account_label}</div>
                                    </div>
                                    <div style={{ fontSize: '10px', color: 'var(--text3)', marginTop: '6px', fontStyle: 'italic' }}>
                                        Raison : {suggestion.reason}
                                    </div>
                                </div>
                            )}

                            {filtered.length === 0 ? (
                                <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text3)' }}>Aucun compte trouvé</div>
                            ) : (
                                filtered.map(a => (
                                    <div
                                        key={a.code}
                                        onClick={() => onSelect(a.code)}
                                        style={{
                                            padding: '10px 16px', borderRadius: '6px', cursor: 'pointer',
                                            display: 'flex', justifyContent: 'space-between',
                                            transition: 'background 0.2s',
                                            background: suggestion?.pcm_account_code === a.code ? 'rgba(99, 102, 241, 0.05)' : 'transparent'
                                        }}
                                        onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg2)'}
                                        onMouseOut={(e) => {
                                            if (suggestion?.pcm_account_code === a.code) {
                                                e.currentTarget.style.background = 'rgba(99, 102, 241, 0.05)'
                                            } else {
                                                e.currentTarget.style.background = 'transparent'
                                            }
                                        }}
                                    >
                                        <div style={{ fontWeight: 600, color: 'var(--accent)' }}>{a.code}</div>
                                        <div style={{ fontSize: '13px', color: 'var(--text2)', textAlign: 'right', flex: 1, marginLeft: '12px' }}>{a.label}</div>
                                    </div>
                                ))
                            )}
                        </>
                    )}
                </div>
            </div>
        </div>
    )
}

function RapprochementInner() {
    const { id } = useParams()
    const navigate = useNavigate()
    const [releves, setReleves] = useState<any[]>([])
    const [selectedReleve, setSelectedReleve] = useState<ReleveBancaire | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState('')

    // UI State for reconciliation
    const [selectedLigne, setSelectedLigne] = useState<LigneReleve | null>(null)
    const [suggestions, setSuggestions] = useState<any[]>([])
    const [bulkSuggestions, setBulkSuggestions] = useState<Record<number, any>>({})
    const [loadingSuggestions, setLoadingSuggestions] = useState(false)
    const [processing, setProcessing] = useState(false)
    const [showAccountSelector, setShowAccountSelector] = useState(false)
    const [aiSuggestion, setAiSuggestion] = useState<any>(null)

    useEffect(() => {
        if (selectedLigne) {
            loadSuggestions(selectedLigne.id)
        } else {
            setSuggestions([])
        }
    }, [selectedLigne])

    const loadBulkSuggestions = async (releveId: number) => {
        try {
            const suggestions = await apiService.getAllSuggestions(releveId)
            setBulkSuggestions(suggestions)
        } catch (err) {
            console.error("Erreur bulk suggestions:", err)
        }
    }

    const loadSuggestions = async (ligneId: number) => {
        setLoadingSuggestions(true)
        try {
            const data = await apiService.getSuggestions(ligneId)
            setSuggestions(data)
        } catch (err) {
            console.error("Erreur suggestions:", err)
        } finally {
            setLoadingSuggestions(false)
        }
    }

    const handleLink = async (entryLineId: number) => {
        if (!selectedLigne) return
        setProcessing(true)
        try {
            await apiService.rapprocher(selectedLigne.id, entryLineId)
            // Recharger le relevé pour mettre à jour l'affichage (is_rapproche)
            if (id) loadReleve(parseInt(id))
            setSelectedLigne(null)
        } catch (err) {
            alert("Erreur lors du rapprochement")
        } finally {
            setProcessing(false)
        }
    }

    const handleGenerate = async () => {
        if (!selectedLigne) return

        setProcessing(true)
        try {
            const suggestion = await apiService.getAccountSuggestion(selectedLigne.id)
            setAiSuggestion(suggestion)
            setShowAccountSelector(true)
        } catch (err) {
            console.error(err)
            setShowAccountSelector(true) // Open anyway even if AI fails
        } finally {
            setProcessing(false)
        }
    }

    const onAccountSelected = async (compte: string) => {
        if (!selectedLigne) return
        setShowAccountSelector(false)
        setProcessing(true)
        try {
            await apiService.genererEcriture(selectedLigne.id, compte)
            if (id) loadReleve(parseInt(id))
            setSelectedLigne(null)
        } catch (err) {
            alert("Erreur lors de la génération de l'écriture")
        } finally {
            setProcessing(false)
        }
    }

    useEffect(() => {
        if (id) loadReleve(parseInt(id))
    }, [id])

    const loadReleve = async (releveId: number) => {
        setLoading(true)
        setError('')
        try {
            const data = await apiService.getReleve(releveId)
            setSelectedReleve(data)
            setSelectedLigne(null)

            // Charger les suggestions en masse
            loadBulkSuggestions(releveId)
        } catch (err: any) {
            setError("Erreur lors du chargement du relevé. Il n'existe peut-être pas ou vous n'avez pas les droits.")
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return <div style={{ padding: '40px', textAlign: 'center' }}><div className="spinner" /> Chargement du rapprochement...</div>
    }

    if (error || !selectedReleve) {
        return (
            <div style={{ padding: '40px' }}>
                <div className="alert alert-error" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={18} /> {error || "Relevé introuvable"}
                </div>
                <button className="btn btn-secondary" style={{ marginTop: '20px' }} onClick={() => navigate('/releves')}>
                    <ArrowLeft size={16} /> Retour aux relevés
                </button>
            </div>
        )
    }

    const lignesNonRapprochees = selectedReleve.lignes?.filter(l => !l.is_rapproche) || []
    const lignesRapprochees = selectedReleve.lignes?.filter(l => l.is_rapproche) || []

    const formatAmount = (val: any) => {
        const num = Number(val)
        return isNaN(num) ? '0.00' : num.toFixed(2)
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 40px)', gap: '24px' }}>

            {/* EN-TÊTE FIXE */}
            <div className="card" style={{ padding: '20px', flexShrink: 0, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                    <button className="btn-icon" onClick={() => navigate('/releves')} style={{ marginBottom: '12px', background: 'var(--bg2)', padding: '6px 12px', borderRadius: '4px', fontSize: '12px' }}>
                        <ArrowLeft size={14} /> Relevés
                    </button>
                    <h1 style={{ fontSize: '20px', fontWeight: 'bold', margin: '0 0 4px 0', display: 'flex', alignItems: 'center', gap: '10px' }}>
                        Rapprochement Bancaire
                        <span className="badge badge-success" style={{ fontSize: '11px', padding: '4px 8px' }}>
                            {selectedReleve.banque_nom || 'Banque'}
                        </span>
                    </h1>
                    <div style={{ color: 'var(--text3)', fontSize: '13px' }}>
                        Période du <strong style={{ color: 'var(--text)' }}>{selectedReleve.date_debut}</strong> au <strong style={{ color: 'var(--text)' }}>{selectedReleve.date_fin}</strong>
                    </div>
                </div>

                <div style={{ display: 'flex', gap: '32px', textAlign: 'right' }}>
                    <div>
                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', fontWeight: 600 }}>Taux de rapprochement</div>
                        <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--accent)' }}>
                            {selectedReleve.lignes?.length ? Math.round((lignesRapprochees.length / selectedReleve.lignes.length) * 100) : 0}%
                        </div>
                    </div>
                    <div>
                        <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', fontWeight: 600 }}>Solde Final</div>
                        <div style={{ fontSize: '24px', fontWeight: '800', fontFamily: 'monospace' }}>
                            {selectedReleve.solde_final !== null ? formatAmount(selectedReleve.solde_final) : '-'} <span style={{ fontSize: '14px', color: 'var(--text3)' }}>MAD</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* VUE SCINDÉE RESPONSIVE */}
            <div style={{ display: 'flex', gap: '24px', flexGrow: 1, minHeight: 0 }}>

                {/* COLONNE GAUCHE: Lignes du relevé bancaire */}
                <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, border: '1px solid var(--border)' }}>
                    <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', flexShrink: 0 }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div className="card-title" style={{ fontSize: '15px' }}>
                                Lignes du Relevé
                                <span className="badge" style={{ marginLeft: '10px', background: 'var(--bg2)', color: 'var(--text2)' }}>
                                    {lignesNonRapprochees.length} en attente
                                </span>
                            </div>
                            <div className="search-bar" style={{ width: '200px' }}>
                                <Search size={14} />
                                <input type="text" placeholder="Rechercher montant/libellé..." style={{ fontSize: '12px', padding: '6px' }} />
                            </div>
                        </div>
                    </div>

                    <div style={{ flexGrow: 1, overflowY: 'auto' }}>
                        <table className="data-table" style={{ width: '100%', fontSize: '12px' }}>
                            <thead style={{ position: 'sticky', top: 0, background: '#fff', zIndex: 1, boxShadow: '0 1px 2px rgba(0,0,0,0.05)' }}>
                                <tr>
                                    <th>Date</th>
                                    <th>Libellé Bancaire</th>
                                    <th style={{ textAlign: 'right' }}>Débit</th>
                                    <th style={{ textAlign: 'right' }}>Crédit</th>
                                    <th style={{ width: '40px' }}></th>
                                </tr>
                            </thead>
                            <tbody>
                                {selectedReleve.lignes?.map(ligne => {
                                    const isSelected = selectedLigne?.id === ligne.id
                                    return (
                                        <tr
                                            key={ligne.id}
                                            style={{
                                                opacity: ligne.is_rapproche ? 0.5 : 1,
                                                background: isSelected ? 'var(--bg2)' : (ligne.is_rapproche ? 'var(--bg2)' : 'transparent'),
                                                cursor: ligne.is_rapproche ? 'default' : 'pointer',
                                                borderLeft: isSelected ? '3px solid var(--accent)' : '3px solid transparent'
                                            }}
                                            onClick={() => {
                                                if (!ligne.is_rapproche) {
                                                    setSelectedLigne(ligne)
                                                }
                                            }}
                                        >
                                            <td style={{ color: 'var(--text3)' }}>{ligne.date_operation}</td>
                                            <td style={{ fontWeight: 500 }}>{ligne.description}</td>
                                            <td style={{ textAlign: 'right', color: 'var(--error)' }}>
                                                {Number(ligne.debit) > 0 ? formatAmount(ligne.debit) : ''}
                                            </td>
                                            <td style={{ textAlign: 'right', color: 'var(--success)' }}>
                                                {Number(ligne.credit) > 0 ? formatAmount(ligne.credit) : ''}
                                            </td>
                                            <td style={{ padding: '12px', borderBottom: '1px solid var(--bg2)' }}>
                                                {ligne.is_rapproche ? (
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--success)', fontSize: '12px', fontWeight: 600 }}>
                                                        <CheckCircle2 size={14} /> Rapproché
                                                    </div>
                                                ) : bulkSuggestions[ligne.id] ? (
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            const suggestion = bulkSuggestions[ligne.id];
                                                            if (suggestion.type === 'exact') {
                                                                apiService.rapprocher(ligne.id, suggestion.entry_line_id)
                                                                    .then(() => loadReleve(selectedReleve.id));
                                                            } else if (suggestion.type === 'ai') {
                                                                apiService.genererEcriture(ligne.id, suggestion.account_code)
                                                                    .then(() => loadReleve(selectedReleve.id));
                                                            }
                                                        }}
                                                        style={{
                                                            padding: '4px 10px',
                                                            background: bulkSuggestions[ligne.id].type === 'ai' ? 'var(--accent)' : 'var(--success)',
                                                            color: '#fff',
                                                            border: 'none', borderRadius: '4px', fontSize: '11px', cursor: 'pointer',
                                                            display: 'flex', alignItems: 'center', gap: '4px',
                                                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                                        }}
                                                    >
                                                        <Link2 size={12} />
                                                        {bulkSuggestions[ligne.id].type === 'ai' ? `Lier (${bulkSuggestions[ligne.id].account_code})` : 'Lier'}
                                                    </button>
                                                ) : (
                                                    <span style={{ fontSize: '12px', color: 'var(--text3)' }}>À traiter</span>
                                                )}
                                            </td>
                                        </tr>
                                    )
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* COLONNE DROITE: Écritures Comptables ou Suggestions */}
                <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0, background: 'var(--bg2)', border: '1px solid var(--border)' }}>
                    <div className="card-header" style={{ padding: '16px 20px', borderBottom: '1px solid var(--border)', flexShrink: 0, background: '#fff' }}>
                        <div className="card-title" style={{ fontSize: '15px' }}>
                            Comptabilité (Livre de Banque)
                        </div>
                        <div className="card-subtitle">
                            {selectedLigne ? 'Suggestions d\'écritures pour la transaction sélectionnée' : 'Sélectionnez une ligne du relevé pour voir les suggestions intelligentes'}
                        </div>
                    </div>

                    <div style={{ flexGrow: 1, display: 'flex', flexDirection: 'column', background: selectedLigne ? '#fff' : 'transparent' }}>
                        {!selectedLigne ? (
                            <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '40px', textAlign: 'center', color: 'var(--text3)' }}>
                                <div>
                                    <LinkIcon size={48} opacity={0.2} style={{ margin: '0 auto 16px auto' }} />
                                    <p style={{ maxWidth: '300px', margin: '0 auto', fontSize: '13px', lineHeight: 1.5 }}>
                                        Cliquez sur l'icône de liaison d'une transaction bancaire pour rechercher et associer une écriture comptable correspondante.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                                {/* Info Box Transaction */}
                                <div style={{ padding: '16px', background: 'rgba(99, 102, 241, 0.05)', borderBottom: '1px solid var(--border)' }}>
                                    <div style={{ fontSize: '11px', color: 'var(--text3)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '8px' }}>
                                        Transaction à rapprocher
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <div style={{ fontWeight: 'bold', fontSize: '14px' }}>{selectedLigne.description}</div>
                                            <div style={{ fontSize: '12px', color: 'var(--text2)' }}>Date : {selectedLigne.date_operation}</div>
                                        </div>
                                        <div style={{ textAlign: 'right', fontSize: '18px', fontWeight: 'bold', color: Number(selectedLigne.debit) > 0 ? 'var(--error)' : 'var(--success)' }}>
                                            {Number(selectedLigne.debit) > 0 ? `-${formatAmount(selectedLigne.debit)}` : `+${formatAmount(selectedLigne.credit)}`} <span style={{ fontSize: '12px', color: 'var(--text3)' }}>MAD</span>
                                        </div>
                                    </div>
                                </div>

                                {/* Real Suggestions List */}
                                <div style={{ flexGrow: 1, overflowY: 'auto', padding: '16px' }}>
                                    <div style={{ marginBottom: '16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div style={{ fontSize: '13px', fontWeight: 600 }}>Écritures suggérées</div>
                                        <div className="search-bar" style={{ width: '180px' }}>
                                            <Search size={14} />
                                            <input type="text" placeholder="Filtrer..." style={{ fontSize: '11px', padding: '4px' }} />
                                        </div>
                                    </div>

                                    {loadingSuggestions ? (
                                        <div style={{ textAlign: 'center', padding: '20px', color: 'var(--text3)' }}>
                                            <div className="spinner" style={{ margin: '0 auto 10px auto' }} />
                                            Recherche de correspondances...
                                        </div>
                                    ) : suggestions.length === 0 ? (
                                        <div style={{ textAlign: 'center', padding: '30px', border: '1px dashed var(--border)', borderRadius: '8px', color: 'var(--text3)', fontSize: '13px' }}>
                                            Aucune écriture correspondante trouvée dans le journal de banque.
                                        </div>
                                    ) : (
                                        suggestions.map(s => (
                                            <div key={s.id} style={{
                                                padding: '12px',
                                                border: '1px solid var(--border)',
                                                borderRadius: '8px',
                                                marginBottom: '8px',
                                                display: 'flex',
                                                justifyContent: 'space-between',
                                                alignItems: 'center',
                                                cursor: 'pointer',
                                                transition: 'border-color 0.2s'
                                            }}
                                                onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent)'}
                                                onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border)'}
                                            >
                                                <div>
                                                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '4px' }}>
                                                        <span className="badge" style={{ background: 'var(--bg2)', color: 'var(--text2)', fontSize: '10px' }}>BQ</span>
                                                        <span style={{ fontSize: '13px', fontWeight: 600 }}>{s.description || 'Sans libellé'}</span>
                                                    </div>
                                                    <div style={{ fontSize: '11px', color: 'var(--text3)' }}>Compte : {s.account_code} {s.account_label}</div>
                                                    <div style={{ fontSize: '11px', color: 'var(--text3)' }}>Date : {s.date} | Réf : {s.reference || '-'}</div>
                                                </div>
                                                <div style={{ textAlign: 'right' }}>
                                                    <div style={{ fontWeight: 600, fontSize: '14px', marginBottom: '4px' }}>
                                                        {Number(s.debit) > 0 ? formatAmount(s.debit) : formatAmount(s.credit)} <span style={{ fontSize: '10px', color: 'var(--text3)' }}>MAD</span>
                                                    </div>
                                                    <button
                                                        className="btn btn-primary"
                                                        style={{ padding: '4px 8px', fontSize: '11px', height: 'auto', background: 'var(--success)' }}
                                                        onClick={() => handleLink(s.id)}
                                                        disabled={processing}
                                                    >
                                                        {processing ? '...' : 'Lier'}
                                                    </button>
                                                </div>
                                            </div>
                                        ))
                                    )}

                                    <div style={{ marginTop: '20px', textAlign: 'center' }}>
                                        <p style={{ fontSize: '12px', color: 'var(--text3)', marginBottom: '12px' }}>L'écriture n'existe pas encore ?</p>
                                        <button
                                            className="btn btn-secondary"
                                            style={{ fontSize: '12px' }}
                                            onClick={handleGenerate}
                                            disabled={processing}
                                        >
                                            {processing ? 'Génération...' : 'Générer l\'écriture comptable'}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>

            </div>

            <AccountSelector
                isOpen={showAccountSelector}
                onClose={() => setShowAccountSelector(false)}
                onSelect={onAccountSelected}
                suggestion={aiSuggestion}
            />
        </div>
    )
}

class ErrorBoundary extends Component<{ children: ReactNode }, { hasError: boolean, error: any }> {
    state = { hasError: false, error: null as any };
    static getDerivedStateFromError(error: Error) { return { hasError: true, error }; }
    componentDidCatch(error: Error, errorInfo: ErrorInfo) { console.error("Uncaught:", error, errorInfo); }
    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: 40, color: 'red' }}>
                    <h2>Erreur Critique (Crash React)</h2>
                    <pre style={{ whiteSpace: 'pre-wrap' }}>{this.state.error?.toString()}</pre>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: '11px' }}>{this.state.error?.stack}</pre>
                </div>
            );
        }
        return this.props.children;
    }
}

export default function Rapprochement() {
    return (
        <ErrorBoundary>
            <RapprochementInner />
        </ErrorBoundary>
    )
}
