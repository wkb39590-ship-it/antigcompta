import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'

export default function Upload() {
    const [file, setFile] = useState<File | null>(null)
    const [societeId, setSocieteId] = useState<number>(1)
    const [societes, setSocietes] = useState<any[]>([])
    const [dragOver, setDragOver] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const fileRef = useRef<HTMLInputElement>(null)
    const navigate = useNavigate()

    useEffect(() => {
        apiService.listSocietes()
            .then(data => {
                setSocietes(data)
                if (data.length > 0) setSocieteId(data[0].id)
            })
            .catch(() => {
                // Si pas de sociétés, on utilise 1 par défaut
            })
    }, [])

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault()
        setDragOver(false)
        const f = e.dataTransfer.files[0]
        if (f) setFile(f)
    }

    const handleSubmit = async () => {
        if (!file) { setError('Veuillez sélectionner un fichier'); return }
        setLoading(true)
        setError('')
        setSuccess('')

        try {
            // Étape 1: Upload
            const uploaded = await apiService.uploadFacture(file, societeId)
            const id = uploaded.id
            setSuccess(`✅ Facture #${id} uploadée. Extraction en cours...`)

            // Étape 2: Extraction automatique
            await apiService.extractFacture(id)
            setSuccess(`✅ Extraction terminée. Classification PCM en cours...`)

            // Étape 3: Classification automatique
            await apiService.classifyFacture(id)
            setSuccess(`✅ Classification terminée. Génération des écritures...`)

            // Étape 4: Génération des écritures
            await apiService.generateEntries(id)
            setSuccess(`✅ Pipeline complet! Redirection vers la facture #${id}...`)

            setTimeout(() => navigate(`/factures/${id}`), 1500)
        } catch (e: any) {
            const msg = e.response?.data?.detail || e.message || 'Erreur inconnue'
            setError(`❌ Erreur: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Importer une facture</h1>
                <p className="page-subtitle">Le pipeline complet s'exécute automatiquement: OCR → Extraction → Classification PCM → Écritures</p>
            </div>

            {/* Pipeline steps */}
            <div className="pipeline-steps">
                <div className="step active">1 Upload</div>
                <span className="step-arrow">→</span>
                <div className="step">2 OCR + Gemini</div>
                <span className="step-arrow">→</span>
                <div className="step">3 Classification PCM</div>
                <span className="step-arrow">→</span>
                <div className="step">4 Écritures</div>
                <span className="step-arrow">→</span>
                <div className="step">5 Validation</div>
            </div>

            <div className="two-col">
                {/* Upload zone */}
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">Fichier facture</div>
                            <div className="card-subtitle">PDF, PNG, JPG, WEBP, TIFF</div>
                        </div>
                    </div>

                    <div
                        className={`upload-zone${dragOver ? ' drag-over' : ''}`}
                        onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                        onDragLeave={() => setDragOver(false)}
                        onDrop={handleDrop}
                        onClick={() => fileRef.current?.click()}
                    >
                        <input
                            ref={fileRef}
                            type="file"
                            accept=".pdf,.png,.jpg,.jpeg,.webp,.tif,.tiff"
                            style={{ display: 'none' }}
                            onChange={e => setFile(e.target.files?.[0] || null)}
                        />
                        {file ? (
                            <>
                                <div className="upload-icon">📄</div>
                                <div className="upload-title">{file.name}</div>
                                <div className="upload-subtitle">
                                    {(file.size / 1024).toFixed(1)} KB — Cliquez pour changer
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="upload-icon">☁️</div>
                                <div className="upload-title">Glissez votre facture ici</div>
                                <div className="upload-subtitle">ou cliquez pour parcourir</div>
                            </>
                        )}
                    </div>
                </div>

                {/* Options */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Configuration</div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Société</label>
                        {societes.length > 0 ? (
                            <select
                                className="form-input"
                                value={societeId}
                                onChange={e => setSocieteId(Number(e.target.value))}
                            >
                                {societes.map(s => (
                                    <option key={s.id} value={s.id}>{s.raison_sociale}</option>
                                ))}
                            </select>
                        ) : (
                            <input
                                className="form-input"
                                type="number"
                                value={societeId}
                                onChange={e => setSocieteId(Number(e.target.value))}
                                placeholder="ID de la société (ex: 1)"
                            />
                        )}
                    </div>

                    <div style={{ marginTop: '24px' }}>
                        <div className="card-title" style={{ marginBottom: '12px', fontSize: '13px' }}>
                            🤖 Pipeline automatique
                        </div>
                        {['OCR + Extraction Gemini (Tableau 1 & 2)', 'Classification PCM par ligne', 'Génération écritures comptables', 'Contrôles DGI automatiques'].map((step, i) => (
                            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', fontSize: '13px', color: 'var(--text2)' }}>
                                <span style={{ color: 'var(--accent)' }}>✓</span> {step}
                            </div>
                        ))}
                    </div>

                    {error && <div className="alert alert-error" style={{ marginTop: '16px' }}>{error}</div>}
                    {success && <div className="alert alert-success" style={{ marginTop: '16px' }}>{success}</div>}

                    <button
                        className="btn btn-primary"
                        style={{ width: '100%', marginTop: '24px', justifyContent: 'center', padding: '14px' }}
                        onClick={handleSubmit}
                        disabled={loading || !file}
                    >
                        {loading ? (
                            <><div className="spinner" /> Traitement en cours...</>
                        ) : (
                            '⚡ Lancer le pipeline'
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
