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
    ArrowLeft,
    Download,
    Plus,
    Loader
} from 'lucide-react'

export default function BulletinPaieDetail() {
    const { id } = useParams<{ id: string }>()
    const navigate = useNavigate()
    const [bulletin, setBulletin] = useState<BulletinPaie | null>(null)
    const [entries, setEntries] = useState<JournalEntry | null>(null)
    const [loading, setLoading] = useState(true)
    const [loadingEntries, setLoadingEntries] = useState(false)
    const [downloading, setDownloading] = useState(false)
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

    const handleDownloadPdf = async () => {
        if (!bulletin) return
        setDownloading(true)
        try {
            const MOIS = ['', 'Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
                'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']
            const filename = `Bulletin_Paie_${(bulletin.employe_nom || 'Employe').replace(/\s+/g, '_')}_${MOIS[bulletin.mois]}_${bulletin.annee}.pdf`
            await apiService.downloadBulletinPdf(bulletin.id, filename)
        } catch (err) {
            alert('Erreur lors de la génération du PDF. Veuillez réessayer.')
        } finally {
            setDownloading(false)
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
                    <button
                        className="btn btn-ghost"
                        onClick={handleDownloadPdf}
                        disabled={downloading}
                        style={{ display: 'flex', alignItems: 'center', gap: '8px' }}
                    >
                        {downloading ? <Loader size={18} className="spin" /> : <Download size={18} />}
                        {downloading ? 'Génération...' : 'Télécharger PDF'}
                    </button>
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
                                    <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}><Calendar size={14} /> Période : du 01/{bulletin.mois.toString().padStart(2, '0')}/{bulletin.annee} au {new Date(bulletin.annee, bulletin.mois, 0).getDate()}/{bulletin.mois.toString().padStart(2, '0')}/{bulletin.annee}</span>
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
                                    <p style={{ marginBottom: '16px' }}>Aucune écriture trouvée pour ce bulletin.</p>
                                    <button className="btn btn-outline" onClick={() => navigate(`/journal?journal=PAYE&showForm=true&ref=PAIE-${bulletin.id}`)} style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '0 auto' }}>
                                        <Plus size={16} /> Saisir l'écriture manuellement
                                     </button>
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

            {/* Modèle de Bulletin pour le PDF (Caché à l'écran) */}
            <div style={{ position: 'absolute', top: '-10000px', left: '-10000px' }}>
                <div id="bulletin-pdf-template" style={{ width: '700px', padding: '30px', background: 'white', color: 'black', fontFamily: 'Arial, sans-serif', fontSize: '11px', boxSizing: 'border-box' }}>

                    {/* En-tête de l'entreprise */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '2px solid black', paddingBottom: '20px', marginBottom: '30px' }}>
                        <div>
                            <h2 style={{ margin: '0 0 5px 0', fontSize: '20px', textTransform: 'uppercase' }}>{bulletin.societe_nom || 'VOTRE SOCIETE'}</h2>
                            <p style={{ margin: '0 0 3px 0' }}>{bulletin.societe_adresse || "Adresse de l'entreprise, CP Ville"}</p>
                            <p style={{ margin: '0 0 3px 0' }}>RC : {bulletin.societe_rc || '123456'}</p>
                            <p style={{ margin: '0 0 3px 0' }}>ICE : {bulletin.societe_ice || '123456789012345'}</p>
                            <p style={{ margin: 0 }}>N° CNSS : {bulletin.societe_cnss || '1234567'}</p>
                        </div>
                        <div style={{ textAlign: 'right' }}>
                            <h1 style={{ margin: '0 0 10px 0', fontSize: '24px', color: '#444' }}>BULLETIN DE PAIE</h1>
                            <p style={{ margin: '0 0 5px 0', fontSize: '14px', fontWeight: 'bold' }}>Période : du 01/{bulletin.mois.toString().padStart(2, '0')}/{bulletin.annee} au {new Date(bulletin.annee, bulletin.mois, 0).getDate()}/{bulletin.mois.toString().padStart(2, '0')}/{bulletin.annee}</p>
                        </div>
                    </div>

                    {/* Informations du salarié */}
                    <div style={{ border: '1px solid black', borderRadius: '4px', padding: '15px', marginBottom: '30px' }}>
                        <div style={{ display: 'flex', gap: '40px' }}>
                            <div style={{ flex: 1 }}>
                                <p style={{ margin: '0 0 8px 0' }}><strong>Nom complet :</strong> {bulletin.employe_nom}</p>
                                <p style={{ margin: '0 0 8px 0' }}><strong>Matricule :</strong> {bulletin.employe_id}</p>
                                <p style={{ margin: '0 0 0 0' }}><strong>Occupation :</strong> Employé</p>
                            </div>
                            <div style={{ flex: 1 }}>
                                <p style={{ margin: '0 0 8px 0' }}><strong>N° CIN :</strong> {bulletin.employe_cin || 'Non renseigné'}</p>
                                <p style={{ margin: '0 0 8px 0' }}><strong>N° CNSS :</strong> {bulletin.employe_cnss || 'Non renseigné'}</p>
                                <p style={{ margin: '0 0 0 0' }}><strong>Date d'embauche :</strong> {bulletin.employe_date_embauche ? new Date(bulletin.employe_date_embauche).toLocaleDateString() : 'Non renseignée'}</p>
                            </div>
                        </div>
                    </div>

                    {/* Tableau des rubriques */}
                    <table style={{ width: '100%', borderCollapse: 'collapse', marginBottom: '30px', border: '1px solid black' }}>
                        <thead>
                            <tr style={{ backgroundColor: '#f0f0f0' }}>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'left', width: '5%' }}>N°</th>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'left', width: '40%' }}>Désignation Rubrique</th>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'right', width: '15%' }}>Base</th>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'right', width: '10%' }}>Taux</th>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'right', width: '15%' }}>A Payer</th>
                                <th style={{ border: '1px solid black', padding: '8px', textAlign: 'right', width: '15%' }}>A Retenir</th>
                            </tr>
                        </thead>
                        <tbody>
                            {/* Gains */}
                            <tr>
                                <td style={{ border: '1px solid black', padding: '8px' }}>100</td>
                                <td style={{ border: '1px solid black', padding: '8px' }}>Salaire de Base</td>
                                <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.salaire_base.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.salaire_base.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                            </tr>
                            {bulletin.prime_anciennete > 0 && (
                                <tr>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>110</td>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>Prime d'ancienneté</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.salaire_base.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.prime_anciennete.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                </tr>
                            )}
                            {bulletin.autres_gains > 0 && (
                                <tr>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>200</td>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>Primes et Heures Sup.</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.autres_gains.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                </tr>
                            )}

                            {/* Retenues */}
                            {bulletin.cnss_salarie > 0 && (
                                <tr>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>700</td>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>CNSS Salarié</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{Math.min(bulletin.salaire_brut, 6000).toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>4.48%</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.cnss_salarie.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                </tr>
                            )}
                            {bulletin.amo_salarie > 0 && (
                                <tr>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>710</td>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>AMO Salarié</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.salaire_brut.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>2.26%</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.amo_salarie.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                </tr>
                            )}
                            {bulletin.ir_retenu > 0 && (
                                <tr>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>750</td>
                                    <td style={{ border: '1px solid black', padding: '8px' }}>I.G.R. / I.R.</td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}></td>
                                    <td style={{ border: '1px solid black', padding: '8px', textAlign: 'right' }}>{bulletin.ir_retenu.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                </tr>
                            )}
                        </tbody>
                        <tfoot>
                            <tr style={{ border: '2px solid black' }}>
                                <td colSpan={2} style={{ padding: '8px', fontWeight: 'bold' }}>TOTAUX</td>
                                <td colSpan={2}></td>
                                <td style={{ padding: '8px', textAlign: 'right', fontWeight: 'bold' }}>{bulletin.salaire_brut.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                                <td style={{ padding: '8px', textAlign: 'right', fontWeight: 'bold' }}>{bulletin.total_retenues.toLocaleString('fr-FR', { minimumFractionDigits: 2 })}</td>
                            </tr>
                        </tfoot>
                    </table>

                    {/* Footer Totaux */}
                    <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '20px' }}>
                        <div style={{ border: '2px solid black', padding: '15px 30px', textAlign: 'center', width: '250px' }}>
                            <p style={{ margin: '0 0 5px 0', fontSize: '14px', fontWeight: 'bold' }}>NET À PAYER</p>
                            <h2 style={{ margin: 0, fontSize: '24px' }}>{bulletin.salaire_net.toLocaleString('fr-FR', { minimumFractionDigits: 2 })} MAD</h2>
                        </div>
                    </div>

                    <div style={{ marginTop: '50px', display: 'flex', justifyContent: 'space-between', padding: '0 20px' }}>
                        <div>
                            <p style={{ margin: 0, textDecoration: 'underline' }}>Signature de l'employeur</p>
                        </div>
                        <div>
                            <p style={{ margin: 0, textDecoration: 'underline' }}>Signature du salarié</p>
                        </div>
                    </div>

                    <div style={{ marginTop: '60px', borderTop: '1px solid #ccc', paddingTop: '10px', textAlign: 'center', fontSize: '10px', color: '#666' }}>
                        Pour vous aider à faire valoir vos droits, conservez ce bulletin de paie sans limitation de durée.
                    </div>
                </div>
            </div>
        </div>
    )
}
