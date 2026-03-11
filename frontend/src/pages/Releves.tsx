import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService, { ReleveBancaire } from '../api'
import { getCurrentSociete } from '../utils/tokenDecoder'
import {
    FileText,
    CheckCircle2,
    AlertTriangle,
    AlertCircle,
    ArrowLeft,
    Zap,
    UploadCloud,
    BookOpen,
    Eye,
    Trash2,
    Settings
} from 'lucide-react'

export default function Releves() {
    const [file, setFile] = useState<File | null>(null)
    const [dragOver, setDragOver] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [currentSociete, setCurrentSociete] = useState<any>(null)
    const [releves, setReleves] = useState<ReleveBancaire[]>([])
    const [loadingList, setLoadingList] = useState(true)
    const fileRef = useRef<HTMLInputElement>(null)
    const navigate = useNavigate()

    useEffect(() => {
        const societe = getCurrentSociete()
        if (societe) {
            setCurrentSociete(societe)
            loadReleves()
        } else {
            setError('Aucune session active. Veuillez sélectionner une société d\'abord.')
            setLoadingList(false)
        }
    }, [])

    const loadReleves = async () => {
        setLoadingList(true)
        try {
            const data = await apiService.listReleves()
            setReleves(data)
        } catch (err: any) {
            console.error("Erreur chargement relevés", err)
        } finally {
            setLoadingList(false)
        }
    }

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)
        const f = e.dataTransfer.files[0]
        if (f) setFile(f)
    }

    const handleSubmit = async () => {
        if (!file) { setError('Veuillez sélectionner un relevé bancaire (PDF, JPG, PNG, CSV)'); return }
        setLoading(true)
        setError('')
        setSuccess('')

        try {
            const res = await apiService.uploadReleve(file)
            setSuccess(`Relevé importé et analysé avec succès.`)
            setFile(null)
            loadReleves()
        } catch (e: any) {
            const msg = e.response?.data?.detail || e.message || 'Erreur inconnue'
            setError(`Erreur: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div className="page-header" style={{ marginBottom: '32px' }}>
                <h1 className="page-title" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <BookOpen size={28} color="var(--accent)" /> Relevés Bancaires
                </h1>
                <p className="page-subtitle">Importation et extraction automatique des transactions bancaires pour le rapprochement.</p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

                {/* Section IMPORT */}
                <div>
                    <div className="card">
                        <div className="card-header">
                            <div className="card-title">Importer un Relevé</div>
                            <div className="card-subtitle">Formats : PDF, PNG, JPG, CSV</div>
                        </div>

                        <div
                            className={`upload-zone${dragOver ? ' drag-over' : ''}`}
                            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                            onDragLeave={() => setDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => fileRef.current?.click()}
                            style={{ padding: '30px' }}
                        >
                            <input
                                ref={fileRef}
                                type="file"
                                accept=".pdf,.png,.jpg,.jpeg,.csv,.xlsx"
                                style={{ display: 'none' }}
                                onChange={e => setFile(e.target.files?.[0] || null)}
                            />
                            {file ? (
                                <>
                                    <div className="upload-icon"><FileText size={42} color="var(--accent)" /></div>
                                    <div className="upload-title" style={{ fontSize: '13px' }}>{file.name}</div>
                                    <div className="upload-subtitle">
                                        {(file.size / 1024).toFixed(1)} KB
                                    </div>
                                </>
                            ) : (
                                <>
                                    <div className="upload-icon"><UploadCloud size={42} color="var(--text3)" opacity={0.5} /></div>
                                    <div className="upload-title" style={{ fontSize: '13px' }}>Déposez le relevé ici</div>
                                </>
                            )}
                        </div>

                        {error && (
                            <div className="alert alert-error" style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <AlertCircle size={18} /> {error}
                            </div>
                        )}
                        {success && (
                            <div className="alert alert-success" style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                <CheckCircle2 size={18} /> {success}
                            </div>
                        )}

                        <button
                            className="btn btn-primary"
                            style={{ width: '100%', marginTop: '24px', justifyContent: 'center', padding: '12px' }}
                            onClick={handleSubmit}
                            disabled={loading || !file || !currentSociete}
                        >
                            {loading ? (
                                <><div className="spinner" /> Traitement en cours...</>
                            ) : (
                                <><Settings size={18} /> Lancer le traitement</>
                            )}
                        </button>
                    </div>
                </div>

                {/* Section LISTE */}
                <div className="card">
                    <div className="card-header" style={{ marginBottom: '0', borderBottom: '1px solid var(--border)' }}>
                        <div className="card-title">Relevés enregistrés</div>
                        <div className="card-subtitle">{releves.length} document(s)</div>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        {loadingList ? (
                            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text3)' }}>
                                <div className="spinner" style={{ margin: '0 auto 10px auto' }} />
                                Chargement des relevés...
                            </div>
                        ) : releves.length === 0 ? (
                            <div style={{ padding: '60px 20px', textAlign: 'center', color: 'var(--text3)' }}>
                                <BookOpen size={48} opacity={0.2} style={{ margin: '0 auto 16px auto' }} />
                                <p>Aucun relevé bancaire importé pour cette société.</p>
                            </div>
                        ) : (
                            <table className="data-table" style={{ width: '100%' }}>
                                <thead>
                                    <tr>
                                        <th>Date d'import</th>
                                        <th>Période</th>
                                        <th>Banque</th>
                                        <th style={{ textAlign: 'right' }}>Solde Final</th>
                                        <th style={{ textAlign: 'center' }}>Lignes</th>
                                        <th style={{ textAlign: 'right' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {releves.map(r => (
                                        <tr key={r.id}>
                                            <td style={{ fontSize: '12px', color: 'var(--text2)' }}>
                                                {new Date(r.date_import).toLocaleDateString()}
                                            </td>
                                            <td style={{ fontWeight: 500 }}>
                                                {r.date_debut} - {r.date_fin}
                                            </td>
                                            <td>
                                                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'var(--bg2)', padding: '4px 8px', borderRadius: '4px', fontSize: '11px', fontWeight: 600 }}>
                                                    {r.banque_nom || 'Inconnue'}
                                                </div>
                                            </td>
                                            <td style={{ textAlign: 'right', fontWeight: 600 }}>
                                                {r.solde_final !== null ? (!isNaN(Number(r.solde_final)) ? Number(r.solde_final).toFixed(2) : '0.00') : '-'} <span style={{ fontSize: '10px', color: 'var(--text3)' }}>MAD</span>
                                            </td>
                                            <td style={{ textAlign: 'center' }}>
                                                <span className="badge badge-info">{r.lignes_count} opérations</span>
                                            </td>
                                            <td style={{ textAlign: 'right' }}>
                                                <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                                                    <button
                                                        className="btn btn-secondary"
                                                        style={{ padding: '6px 12px', fontSize: '12px' }}
                                                        onClick={() => navigate(`/releves/${r.id}/rapprochement`)}
                                                    >
                                                        <Eye size={14} /> Rapprocher
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
