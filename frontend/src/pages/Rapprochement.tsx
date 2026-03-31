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
    ArrowLeft,
    Zap
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
                        RELEVÉ N°<strong style={{ color: 'var(--text)' }}>{selectedReleve.id}</strong> • Période du <strong style={{ color: 'var(--text)' }}>{selectedReleve.date_debut}</strong> au <strong style={{ color: 'var(--text)' }}>{selectedReleve.date_fin}</strong>
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
                                Opérations Bancaires
                                <span className="badge" style={{ marginLeft: '10px', background: 'var(--bg3)', color: 'var(--text2)', fontWeight: 600 }}>
                                    {lignesNonRapprochees.length} à traiter
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
                                    <th>Libellé / Opération</th>
                                    <th style={{ textAlign: 'right' }}>Débit</th>
                                    <th style={{ textAlign: 'right' }}>Crédit</th>
                                    <th style={{ width: '120px', textAlign: 'right' }}>Statut / Action</th>
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
                                                cursor: 'pointer',
                                                borderLeft: isSelected ? '3px solid var(--accent)' : '3px solid transparent'
                                            }}
                                            onClick={() => setSelectedLigne(ligne)}
                                        >
                                            <td style={{ color: 'var(--text3)', width: '90px' }}>{ligne.date_operation}</td>
                                            <td style={{ fontWeight: 500, color: 'var(--text)' }}>
                                                {ligne.description}
                                            </td>
                                            <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--error)' }}>
                                                {Number(ligne.debit) > 0 ? formatAmount(ligne.debit) : ''}
                                            </td>
                                            <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--success)' }}>
                                                {Number(ligne.credit) > 0 ? formatAmount(ligne.credit) : ''}
                                            </td>
                                            <td style={{ padding: '12px', textAlign: 'right', borderBottom: '1px solid var(--border)' }}>
                                                {ligne.is_rapproche ? (
                                                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--success)', fontSize: '11px', fontWeight: 700, background: 'rgba(16, 185, 129, 0.1)', padding: '4px 8px', borderRadius: '4px' }}>
                                                        <CheckCircle2 size={12} /> OK
                                                    </div>
                                                ) : bulkSuggestions[ligne.id] ? (
                                                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
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
                                                            className="btn btn-primary"
                                                            style={{
                                                                padding: '4px 8px',
                                                                fontSize: '10px',
                                                                fontWeight: 700,
                                                                borderRadius: '4px',
                                                                background: bulkSuggestions[ligne.id].type === 'ai' ? 'var(--accent)' : 'var(--success)',
                                                                border: 'none',
                                                                boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                                                            }}
                                                        >
                                                            {bulkSuggestions[ligne.id].type === 'ai' ? `IMPUTER (${bulkSuggestions[ligne.id].account_code})` : 'LIER'}
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <span style={{ fontSize: '11px', color: 'var(--text3)', fontWeight: 600, opacity: 0.6 }}>À TRAITER</span>
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
                                        Sélectionnez une transaction bancaire à gauche pour l'affecter ou la lier.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                                {/* Info Box Transaction */}
                                <div style={{ padding: '16px 20px', background: 'var(--bg2)', borderBottom: '1px solid var(--border)' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                                        <div style={{ fontSize: '10px', color: 'var(--text3)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.05em' }}>
                                            Détail de l'opération
                                        </div>
                                        <button onClick={() => setSelectedLigne(null)} style={{ border: 'none', background: 'none', cursor: 'pointer', color: 'var(--text3)' }}>
                                            <X size={16} />
                                        </button>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <div style={{ fontWeight: 'bold', fontSize: '15px', color: 'var(--text)' }}>{selectedLigne.description}</div>
                                            <div style={{ fontSize: '12px', color: 'var(--text3)', marginTop: '2px' }}>{selectedLigne.date_operation}</div>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{ fontSize: '18px', fontWeight: '800', color: Number(selectedLigne.debit) > 0 ? 'var(--error)' : 'var(--success)' }}>
                                                {Number(selectedLigne.debit) > 0 ? `-${formatAmount(selectedLigne.debit)}` : `+${formatAmount(selectedLigne.credit)}`}
                                                <span style={{ fontSize: '11px', color: 'var(--text3)', marginLeft: '4px' }}>MAD</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Business Actions Sections */}
                                {selectedLigne.is_rapproche ? (
                                    <div style={{ padding: '60px 40px', textAlign: 'center' }}>
                                        <CheckCircle2 size={64} color="var(--success)" style={{ marginBottom: '20px', opacity: 0.8 }} />
                                        <h3 style={{ color: 'var(--text)', marginBottom: '8px' }}>Opération Traitée</h3>
                                        <p style={{ color: 'var(--text3)', fontSize: '14px' }}>
                                            Cette transaction bancaire a déjà été rapprochée avec succès et a généré une écriture comptable.
                                        </p>
                                        <p style={{ color: 'var(--text3)', fontSize: '12px', marginTop: '16px', fontStyle: 'italic' }}>
                                            (La possibilité d'annuler un rapprochement sera bientôt disponible).
                                        </p>
                                    </div>
                                ) : (
                                    <div style={{ flexGrow: 1, overflowY: 'auto' }}>

                                    {/* SECTION 1: SUGGESTION DE LIEN (Si trouvée) */}
                                    {suggestions.filter(s => s.score > 0 || suggestions.length === 1).length > 0 && (
                                        <div style={{ padding: '20px', borderBottom: '1px solid var(--border)', background: 'rgba(16, 185, 129, 0.05)' }}>
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                                                <div style={{ fontSize: '13px', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--success)' }}>
                                                    <Link2 size={16} /> 1. Paiement de facture (Détecté)
                                                </div>
                                                {suggestions[0]?.score > 40 && (
                                                    <span style={{ fontSize: '10px', fontWeight: 700, background: 'var(--success)', color: '#fff', padding: '2px 8px', borderRadius: '4px' }}>CONFIDENCE ÉLEVÉE</span>
                                                )}
                                            </div>
                                            <p style={{ fontSize: '12px', color: 'var(--text2)', marginBottom: '16px' }}>
                                                {suggestions[0]?.score > 0
                                                    ? "Nous avons trouvé une écriture avec des références correspondantes."
                                                    : "Nous avons trouvé une écriture du même montant à cette date."}
                                            </p>

                                            {suggestions.filter(s => s.score > 0 || suggestions.length === 1).slice(0, 3).map((s, idx) => (
                                                <div key={s.id} style={{
                                                    padding: '12px',
                                                    border: idx === 0 && s.score > 0 ? '2px solid var(--success)' : '1px solid var(--border)',
                                                    borderRadius: '8px',
                                                    marginBottom: '10px',
                                                    display: 'flex',
                                                    justifyContent: 'space-between',
                                                    alignItems: 'center',
                                                    background: '#fff',
                                                    boxShadow: idx === 0 && s.score > 0 ? '0 4px 6px rgba(16, 185, 129, 0.1)' : 'none'
                                                }}>
                                                    <div style={{ flex: 1 }}>
                                                        <div style={{ fontWeight: 600, fontSize: '13px' }}>
                                                            {/* Highlight matching parts if possible */}
                                                            {s.description || 'Facture'}
                                                        </div>
                                                        <div style={{ fontSize: '11px', color: 'var(--text3)' }}>
                                                            Réf: <span style={{ fontWeight: 700, color: 'var(--text)' }}>{s.reference || '-'}</span> | {s.account_code}
                                                        </div>
                                                        <div style={{ fontSize: '11px', color: 'var(--text3)' }}>Date écriture: {s.date}</div>
                                                    </div>
                                                    <div style={{ textAlign: 'right', marginLeft: '12px' }}>
                                                        <div style={{ fontWeight: 800, fontSize: '15px', color: 'var(--text)', marginBottom: '4px' }}>
                                                            {formatAmount(Number(s.debit) > 0 ? s.debit : s.credit)}
                                                        </div>
                                                        <button
                                                            className="btn btn-success"
                                                            style={{ padding: '8px 16px', fontSize: '12px', fontWeight: 700 }}
                                                            onClick={() => handleLink(s.id)}
                                                            disabled={processing}
                                                        >
                                                            CONFIRMER
                                                        </button>
                                                    </div>
                                                </div>
                                            ))}
                                            {suggestions.length > 3 && (
                                                <div style={{ fontSize: '11px', color: 'var(--text3)', textAlign: 'center' }}>
                                                    + {suggestions.length - 3} autres correspondances masquées par manque de précision.
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {/* SECTION 2: AFFECTATION (Visible si pas de suggest ou en option secondaire) */}
                                    <div style={{ padding: '20px', borderBottom: '1px solid var(--border)', background: suggestions.length === 0 ? 'rgba(99, 102, 241, 0.03)' : 'transparent' }}>
                                        <div style={{ fontSize: '13px', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px', color: suggestions.length === 0 ? 'var(--accent)' : 'var(--text2)' }}>
                                            <Zap size={16} /> {suggestions.length === 0 ? '1. Nouvelle opération (Sans facture)' : '2. Autre option : Nouvelle imputation'}
                                        </div>
                                        <p style={{ fontSize: '12px', color: 'var(--text2)', marginBottom: '16px' }}>
                                            {suggestions.length === 0
                                                ? "Aucune facture trouvée. Imputez cette opération directement à un compte (ex: Frais, Commissions, Salaires)."
                                                : "Si vous ne voulez pas lier à la facture ci-dessus, créez une nouvelle écriture."}
                                        </p>

                                        <div style={{ display: 'flex', gap: '8px', marginBottom: '12px' }}>
                                            <button
                                                className="btn btn-primary"
                                                style={{
                                                    flex: 1,
                                                    justifyContent: 'center',
                                                    padding: '12px',
                                                    background: suggestions.length > 0 ? 'var(--bg3)' : 'var(--accent)',
                                                    color: suggestions.length > 0 ? 'var(--text2)' : '#fff',
                                                    border: 'none',
                                                    fontWeight: 600
                                                }}
                                                onClick={handleGenerate}
                                                disabled={processing}
                                            >
                                                {processing ? (
                                                    <><div className="spinner" style={{ width: '14px', height: '14px' }} /> Analyse...</>
                                                ) : (
                                                    <>{suggestions.length === 0 ? 'CATEGORIE MANUELLE...' : 'NOUVELLE IMPUTATION'}</>
                                                )}
                                            </button>
                                        </div>

                                        {Number(selectedLigne.debit) > 0 && (
                                            <div style={{ display: 'flex', gap: '8px', marginBottom: '12px', padding: '12px', border: '1px dashed var(--border)', borderRadius: '6px', background: '#fff' }}>
                                                <div style={{ fontSize: '11px', color: 'var(--text3)', display: 'flex', alignItems: 'center', fontWeight: 'bold' }}>
                                                    RACCOURCIS :
                                                </div>
                                                <button
                                                    className="btn btn-secondary"
                                                    style={{
                                                        flex: 1,
                                                        padding: '8px',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        background: 'rgba(239, 68, 68, 0.05)',
                                                        color: 'var(--error)',
                                                        border: '1px solid rgba(239, 68, 68, 0.2)',
                                                    }}
                                                    onClick={() => onAccountSelected('61470000')}
                                                    disabled={processing}
                                                    title="Imputer au compte 61470000"
                                                >
                                                    COMMISSION
                                                </button>
                                                <button
                                                    className="btn btn-secondary"
                                                    style={{
                                                        flex: 1,
                                                        padding: '8px',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        background: 'rgba(245, 158, 11, 0.05)',
                                                        color: '#d97706',
                                                        border: '1px solid rgba(245, 158, 11, 0.2)',
                                                    }}
                                                    onClick={() => onAccountSelected('34552000')}
                                                    disabled={processing}
                                                    title="Imputer au compte 34552000"
                                                >
                                                    TVA
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {/* SECTION 3: RECHERCHE MANUELLE (Affiche si suggestions vides) */}
                                    {suggestions.length === 0 && (
                                        <div style={{ padding: '20px', textAlign: 'center' }}>
                                            {loadingSuggestions ? (
                                                <div style={{ color: 'var(--text3)', fontSize: '12px' }}>
                                                    <div className="spinner" style={{ margin: '0 auto 10px auto' }} />
                                                    Recherche de correspondances...
                                                </div>
                                            ) : (
                                                <div style={{ fontSize: '11px', color: 'var(--text3)', fontStyle: 'italic' }}>
                                                    Avertissement : Si une facture existe, elle devrait apparaître ici automatiquement.
                                                    Vérifiez le montant s'il y a un décalage.
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>
                                )}
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
