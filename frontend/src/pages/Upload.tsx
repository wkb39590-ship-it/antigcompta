import { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import apiService from '../api'
import { getCurrentSociete } from '../utils/tokenDecoder'
import {
    Upload as UploadIcon,
    FileText,
    CheckCircle2,
    AlertTriangle,
    AlertCircle,
    ArrowLeft,
    Zap,
    UploadCloud,
    Check
} from 'lucide-react'

export default function Upload() {
    const [file, setFile] = useState<File | null>(null)
    const [dragOver, setDragOver] = useState(false)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [success, setSuccess] = useState('')
    const [currentSociete, setCurrentSociete] = useState<any>(null)
    const [currentStep, setCurrentStep] = useState(0)
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
        setCurrentStep(1) // Réception

        try {
            console.log('[Upload] Starting pipeline with file:', file.name)

            // Étape 1: Upload
            console.log('[Upload] Step 1: Uploading file...')
            const uploaded = await apiService.uploadFacture(file)
            const id = uploaded.id
            setSuccess(`Facture #${id} reçue. Passage à l'analyse...`)
            setCurrentStep(2) // Analyse

            // Étape 2: Extraction automatique
            console.log('[Upload] Step 2: Extracting...')
            await apiService.extractFacture(id)
            setSuccess(`Analyse terminée. Imputation comptable en cours...`)
            setCurrentStep(3) // Imputation

            // Étape 3: Classification automatique
            console.log('[Upload] Step 3: Classifying...')
            await apiService.classifyFacture(id)
            setSuccess(`Imputation terminée. Génération des écritures...`)
            setCurrentStep(4) // Écritures

            // Étape 4: Génération des écritures
            console.log('[Upload] Step 4: Generating entries...')
            await apiService.generateEntries(id)
            setSuccess(`Écritures générées. Contrôle final...`)
            setCurrentStep(5) // Contrôle

            console.log('[Upload] ✅ All steps done!')
            setSuccess(`Traitement complet terminé avec succès !`)

            setTimeout(() => navigate(`/factures/${id}`), 2000)
        } catch (e: any) {
            console.error('[Upload] ❌ Error:', e)
            const msg = e.response?.data?.detail || e.message || 'Erreur inconnue'
            setError(`Erreur: ${typeof msg === 'string' ? msg : JSON.stringify(msg)}`)
        } finally {
            setLoading(false)
        }
    }

    const getStepClass = (step: number) => {
        if (currentStep > step) return 'step done'
        if (currentStep === step) return 'step active'
        return 'step'
    }

    return (
        <div>
            <div className="page-header">
                <h1 className="page-title">Transmission de Documents</h1>
                <p className="page-subtitle">Traitement intégral certifié : Analyse de conformité, imputation PCM et génération d'écritures réglementaires.</p>
            </div>

            {/* Pipeline steps */}
            <div className="pipeline-steps">
                <div className={getStepClass(1)}>Réception</div>
                <span className="step-arrow">→</span>
                <div className={getStepClass(2)}>Analyse</div>
                <span className="step-arrow">→</span>
                <div className={getStepClass(3)}>Imputation</div>
                <span className="step-arrow">→</span>
                <div className={getStepClass(4)}>Écritures</div>
                <span className="step-arrow">→</span>
                <div className={getStepClass(5)}>Contrôle</div>
            </div>

            <div className="two-col">
                {/* Upload zone */}
                <div className="card">
                    <div className="card-header">
                        <div>
                            <div className="card-title">Pièce Justificative</div>
                            <div className="card-subtitle">Formats acceptés : PDF, PNG, JPG</div>
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
                            accept=".pdf,.png,.jpg,.jpeg"
                            style={{ display: 'none' }}
                            onChange={e => setFile(e.target.files?.[0] || null)}
                        />
                        {file ? (
                            <>
                                <div className="upload-icon"><FileText size={48} color="var(--accent)" /></div>
                                <div className="upload-title">{file.name}</div>
                                <div className="upload-subtitle">
                                    {(file.size / 1024).toFixed(1)} KB — Modifier le document
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="upload-icon"><UploadCloud size={48} color="var(--text3)" opacity={0.5} /></div>
                                <div className="upload-title">Déposez vos documents ici</div>
                                <div className="upload-subtitle">ou sélectionnez un fichier sur votre poste</div>
                            </>
                        )}
                    </div>
                </div>

                {/* Options */}
                <div className="card">
                    <div className="card-header">
                        <div className="card-title">Configuration du dossier</div>
                    </div>

                    <div className="form-group">
                        <label className="form-label">Société de destination</label>
                        <div className="form-input" style={{ background: 'var(--bg2)', cursor: 'default', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <CheckCircle2 size={16} color="var(--success)" />
                            <span>{currentSociete?.raison_sociale || 'Société non chargée'}</span>
                        </div>
                        {!currentSociete && (
                            <div>
                                <div style={{ fontSize: '12px', color: 'var(--error)', marginTop: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                                    <AlertTriangle size={14} /> Session de société requise
                                </div>
                                <button
                                    className="btn btn-secondary"
                                    style={{ width: '100%', marginTop: '12px', padding: '10px', fontSize: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
                                    onClick={() => navigate('/ cabinents')}
                                >
                                    <ArrowLeft size={14} /> Sélectionner une société
                                </button>
                            </div>
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
                        style={{ width: '100%', marginTop: '24px', justifyContent: 'center', padding: '14px' }}
                        onClick={handleSubmit}
                        disabled={loading || !file || !currentSociete}
                    >
                        {loading ? (
                            <><div className="spinner" /> Traitement en cours...</>
                        ) : (
                            <><Zap size={18} /> Lancer le Traitement</>
                        )}
                    </button>
                </div>
            </div>
        </div>
    )
}
