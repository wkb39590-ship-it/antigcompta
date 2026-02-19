import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'
import { getCurrentSociete } from '../utils/tokenDecoder'

export default function Upload() {
    const [file, setFile] = useState<File | null>(null)
    const [dragOver, setDragOver] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [currentSociete, setCurrentSociete] = useState<any>(null)
    const fileRef = useRef<HTMLInputElement>(null)
    const navigate = useNavigate()

    useEffect(() => {
        // Get current societe from session token
        const societe = getCurrentSociete()
        
        if (societe) {
            setCurrentSociete(societe)
            setError('')
        } else {
            setError('Aucune session active. Veuillez sélectionner une société d\'abord.')
        }
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
            console.log('[Upload] Starting pipeline with file:', file.name)
            console.log('[Upload] Session token:', localStorage.getItem('session_token') ? '✅ Present' : '❌ Missing')

            // Étape 1: Upload (societe_id is extracted from session_token by backend)
            console.log('[Upload] Step 1: Uploading file...')
            const uploaded = await apiService.uploadFacture(file)
            const id = uploaded.id
            console.log('[Upload] ✅ Upload successful, facture ID:', id)
            setSuccess(`✅ Facture #${id} uploadée. Extraction en cours...`)

            // Étape 2: Extraction automatique
            console.log('[Upload] Step 2: Extracting...')
            await apiService.extractFacture(id)
            console.log('[Upload] ✅ Extraction done')
            setSuccess(`✅ Extraction terminée. Classification PCM en cours...`)

            // Étape 3: Classification automatique
            console.log('[Upload] Step 3: Classifying...')
            await apiService.classifyFacture(id)
            console.log('[Upload] ✅ Classification done')
            setSuccess(`✅ Classification terminée. Génération des écritures...`)

            // Étape 4: Génération des écritures
            console.log('[Upload] Step 4: Generating entries...')
            await apiService.generateEntries(id)
            console.log('[Upload] ✅ All steps done!')
            setSuccess(`✅ Pipeline complet! Redirection vers la facture #${id}...`)

            setTimeout(() => navigate(`/factures/${id}`), 1500)
        } catch (e: any) {
            console.error('[Upload] ❌ Error:', e)
            if (e.response) {
                console.error('[Upload] Response status:', e.response.status)
                console.error('[Upload] Response data:', e.response.data)
            } else if (e.request) {
                console.error('[Upload] Request made but no response:', e.request)
            } else {
                console.error('[Upload] Error message:', e.message)
            }
            
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
                        <label className="form-label">Société sélectionnée</label>
                        <div className="form-input" style={{ background: 'var(--bg2)', cursor: 'default', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <span style={{ fontSize: '16px' }}>✓</span>
                            <span>{currentSociete?.raison_sociale || 'Société non chargée'}</span>
                        </div>
                        {!currentSociete && (
                            <div>
                                <div style={{ fontSize: '12px', color: 'var(--error)', marginTop: '8px' }}>
                                    ⚠️ Veuillez d'abord sélectionner une société
                                </div>
                                <button
                                    className="btn btn-secondary"
                                    style={{ width: '100%', marginTop: '12px', padding: '10px', fontSize: '12px' }}
                                    onClick={() => navigate('/cabinets')}
                                >
                                    ← Retour à la sélection
                                </button>
                            </div>
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
                        disabled={loading || !file || !currentSociete}
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
