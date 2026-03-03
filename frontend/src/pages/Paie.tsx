import React, { useState, useEffect } from 'react';
import {
    Users,
    Plus,
    Search,
    FileText,
    Calendar,
    ChevronRight,
    Download,
    CheckCircle2,
    Clock,
    AlertCircle,
    Printer,
    ChevronLeft,
    TrendingUp,
    Wallet,
    ArrowUpRight,
    Filter,
    MoreHorizontal,
    Eye
} from 'lucide-react';
import apiService, { BulletinPaie, Employe } from '../api';

const Paie = () => {
    const [bulletins, setBulletins] = useState<BulletinPaie[]>([]);
    const [employes, setEmployes] = useState<Employe[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedId, setSelectedId] = useState<number | null>(null);
    const [activeTab, setActiveTab] = useState<'all' | 'draft' | 'validated'>('all');
    const [searchTerm, setSearchTerm] = useState('');

    // State for new bulletin
    const [newPaie, setNewPaie] = useState({
        employe_id: '',
        mois: new Date().getMonth() + 1,
        annee: new Date().getFullYear(),
        primes: 0,
        heures_sup: 0
    });

    const [preview, setPreview] = useState<BulletinPaie | null>(null);
    const [isCalculating, setIsCalculating] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [bulletinsRes, employesRes] = await Promise.all([
                apiService.listBulletins(),
                apiService.listEmployes('ACTIF')
            ]);
            console.log('[DEBUG Frontend] Bulletins fetched:', bulletinsRes.length);
            console.log('[DEBUG Frontend] Employees fetched:', employesRes.length, employesRes);
            setBulletins(bulletinsRes);
            setEmployes(employesRes);
        } catch (error) {
            console.error('Error fetching data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCalculate = async () => {
        if (!newPaie.employe_id) return;
        try {
            setIsCalculating(true);
            const res = await apiService.calculateBulletin({
                employe_id: parseInt(newPaie.employe_id),
                mois: newPaie.mois,
                annee: newPaie.annee,
                primes: newPaie.primes,
                heures_sup: newPaie.heures_sup
            });
            setPreview(res);
        } catch (error) {
            console.error('Calculation error:', error);
        } finally {
            setIsCalculating(false);
        }
    };

    const handleSave = async () => {
        try {
            await apiService.saveBulletin({
                employe_id: parseInt(newPaie.employe_id),
                mois: newPaie.mois,
                annee: newPaie.annee,
                primes: newPaie.primes,
                heures_sup: newPaie.heures_sup
            });
            setIsModalOpen(false);
            setPreview(null);
            fetchData();
        } catch (error) {
            console.error('Save error:', error);
        }
    };

    const handleValidate = async (id: number) => {
        if (!window.confirm('Voulez-vous valider ce bulletin ? Cela générera les écritures comptables.')) return;
        try {
            await apiService.validateBulletin(id);
            // Re-fetch only after validation to see changes
            fetchData();
        } catch (error) {
            console.error('Validation error:', error);
        }
    };

    const selectedBulletin = bulletins.find(b => b.id === selectedId) || null;

    const filteredBulletins = bulletins.filter(b => {
        const matchesTab = activeTab === 'all' ||
            (activeTab === 'draft' && b.statut === 'BROUILLON') ||
            (activeTab === 'validated' && b.statut === 'VALIDE');
        const matchesSearch = (b.employe_nom || '').toLowerCase().includes(searchTerm.toLowerCase());
        return matchesTab && matchesSearch;
    });

    const getStatusBadge = (status: string) => {
        if (status === 'VALIDE') {
            return (
                <span className="badge badge-validated">
                    <CheckCircle2 className="w-3 h-3" /> Validé
                </span>
            );
        }
        return (
            <span className="badge badge-draft">
                <Clock className="w-3 h-3" /> Brouillon
            </span>
        );
    };

    if (selectedBulletin) {
        return (
            <div className="container-pro animate-in fade-in slide-in-from-right duration-300">
                <button
                    onClick={() => setSelectedId(null)}
                    className="flex items-center text-slate-400 hover:text-indigo-400 mb-8 transition-all group"
                >
                    <ChevronLeft className="w-5 h-5 mr-1 group-hover:-translate-x-1 transition-transform" />
                    Retour au tableau de bord
                </button>

                <div className="aurora-card overflow-hidden">
                    {/* Header - PaySlip Style */}
                    <div className="p-8 border-b border-white/5 bg-white/5 flex flex-col md:flex-row justify-between items-start md:items-center gap-6">
                        <div className="flex items-center gap-6">
                            <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 flex items-center justify-center border border-indigo-500/30 text-indigo-400">
                                <FileText className="w-8 h-8" />
                            </div>
                            <div>
                                <h1 className="text-3xl font-black tracking-tight mb-2">
                                    Bulletin <span className="glass-text">#{selectedBulletin.id}</span>
                                </h1>
                                <div className="flex items-center gap-4 text-sm font-medium text-slate-400">
                                    <span className="flex items-center">
                                        <Calendar className="w-4 h-4 mr-1.5" />
                                        {new Date(selectedId ? 2024 : 2024, selectedBulletin.mois - 1).toLocaleString('fr-FR', { month: 'long' })} {selectedBulletin.annee}
                                    </span>
                                    <span className="w-1 h-1 bg-slate-700 rounded-full"></span>
                                    <span className="flex items-center">
                                        <Users className="w-4 h-4 mr-1.5" />
                                        {selectedBulletin.employe_nom}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center gap-3">
                            {getStatusBadge(selectedBulletin.statut)}
                            <button className="p-3 bg-slate-800 text-slate-300 hover:text-white rounded-xl border border-white/5 transition-all">
                                <Printer className="w-5 h-5" />
                            </button>
                            <button className="p-3 bg-slate-800 text-slate-300 hover:text-white rounded-xl border border-white/5 transition-all">
                                <Download className="w-5 h-5" />
                            </button>
                            {selectedBulletin.statut === 'BROUILLON' && (
                                <button
                                    onClick={() => handleValidate(selectedBulletin.id)}
                                    className="btn btn-primary px-6"
                                >
                                    Valider la paie
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Summary Boxes */}
                    <div className="p-8 pb-0">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-white/5 p-5 rounded-2xl border border-white/5">
                                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-2">Salaire Brut</p>
                                <p className="text-2xl font-black">{selectedBulletin.salaire_brut.toLocaleString()} <span className="text-sm font-normal text-slate-500">MAD</span></p>
                            </div>
                            <div className="bg-white/5 p-5 rounded-2xl border border-white/5">
                                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-2">Retenues Totales</p>
                                <p className="text-2xl font-black text-rose-500">{selectedBulletin.total_retenues.toLocaleString()} <span className="text-sm font-normal text-slate-500">MAD</span></p>
                            </div>
                            <div className="bg-white/5 p-5 rounded-2xl border border-white/5">
                                <p className="text-[11px] font-bold text-slate-500 uppercase tracking-widest mb-2">Charges Patronales</p>
                                <p className="text-2xl font-black text-amber-500">{selectedBulletin.cout_total_employeur ? (selectedBulletin.cout_total_employeur - selectedBulletin.salaire_brut).toFixed(2) : '-'} <span className="text-sm font-normal text-slate-500">MAD</span></p>
                            </div>
                            <div className="bg-indigo-600/10 p-5 rounded-2xl border border-indigo-500/20 relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-3 opacity-10">
                                    <TrendingUp className="w-12 h-12" />
                                </div>
                                <p className="text-[11px] font-bold text-indigo-400 uppercase tracking-widest mb-2">Net à Payer</p>
                                <p className="text-2xl font-black text-indigo-400">{selectedBulletin.salaire_net.toLocaleString()} <span className="text-sm font-normal opacity-50">MAD</span></p>
                            </div>
                        </div>
                    </div>

                    {/* Lignes du Bulletin */}
                    <div className="p-8">
                        <div className="table-wrap">
                            <table>
                                <thead>
                                    <tr>
                                        <th className="rounded-l-xl">Désignation</th>
                                        <th className="text-right">Base / Nombre</th>
                                        <th className="text-right">Taux / Prix U.</th>
                                        <th className="text-right">Gains (+)</th>
                                        <th className="text-right rounded-r-xl">Retenues (-)</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {selectedBulletin.lignes.map((ligne, idx) => (
                                        <tr key={idx} className="hover:bg-white/[0.02] transition-colors border-b border-white/5">
                                            <td className="py-5 font-semibold text-slate-200">{ligne.libelle}</td>
                                            <td className="py-5 text-right font-mono text-slate-400">{ligne.base_calcul?.toLocaleString() || '-'}</td>
                                            <td className="py-5 text-right font-mono text-slate-400">{ligne.taux ? `${(ligne.taux * 100).toFixed(2)}%` : '-'}</td>
                                            <td className="py-5 text-right font-bold text-slate-200">
                                                {ligne.type_ligne === 'GAIN' ? ligne.montant.toLocaleString() : ''}
                                            </td>
                                            <td className="py-5 text-right font-bold text-rose-500/80">
                                                {ligne.type_ligne === 'RETENUE' ? ligne.montant.toLocaleString() : ''}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                                <tfoot>
                                    <tr className="border-t-2 border-white/10">
                                        <td colSpan={3} className="pt-10 pb-4 text-xl font-bold">TOTAL NET À PAYER</td>
                                        <td colSpan={2} className="pt-10 pb-4 text-right">
                                            <span className="text-4xl font-black glass-text tracking-tighter">
                                                {selectedBulletin.salaire_net.toLocaleString()} MAD
                                            </span>
                                        </td>
                                    </tr>
                                </tfoot>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="container-pro aurora-bg-page animate-in fade-in duration-500">
            {/* Header */}
            <div className="page-header flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12">
                <div>
                    <h1 className="text-[40px] font-black tracking-tighter leading-none mb-3">
                        Gestion des <span className="glass-text">Paies</span>
                    </h1>
                    <p className="text-slate-400 text-lg font-medium">Calculez, éditez et validez les bulletins de paie selon le PCM.</p>
                </div>
                <button
                    onClick={() => setIsModalOpen(true)}
                    className="btn btn-primary px-8 py-4 rounded-2xl neon-glow group"
                >
                    <Plus className="w-5 h-5 group-hover:rotate-90 transition-transform" />
                    Nouveau Bulletin
                </button>
            </div>

            {/* Quick Stats */}
            <div className="stats-grid mb-12">
                <div className="stat-card">
                    <Users className="stat-icon" />
                    <p className="stat-value">{employes.length}</p>
                    <p className="stat-label">Employés Actifs</p>
                </div>
                <div className="stat-card">
                    <Clock className="stat-icon text-amber-500" />
                    <p className="stat-value">{bulletins.filter(b => b.statut === 'BROUILLON').length}</p>
                    <p className="stat-label">En attente (Brouillons)</p>
                </div>
                <div className="stat-card relative">
                    <div className="absolute top-0 right-0 p-3">
                        <ArrowUpRight className="w-5 h-5 text-indigo-400 animate-pulse" />
                    </div>
                    <Wallet className="stat-icon text-indigo-500" />
                    <p className="stat-value">
                        {bulletins
                            .filter(b => b.mois === new Date().getMonth() + 1)
                            .reduce((acc, b) => acc + b.salaire_net, 0)
                            .toLocaleString()}
                    </p>
                    <p className="stat-label">Net Total (Mois en cours)</p>
                </div>
            </div>

            {/* Main Listing Section */}
            <div className="aurora-card">
                <div className="p-6 border-b border-white/5 flex flex-col md:flex-row md:items-center justify-between gap-6">
                    <div className="flex bg-white/5 p-1 rounded-xl glass-panel">
                        <button
                            onClick={() => setActiveTab('all')}
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'all' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Tous
                        </button>
                        <button
                            onClick={() => setActiveTab('draft')}
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'draft' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Brouillons
                        </button>
                        <button
                            onClick={() => setActiveTab('validated')}
                            className={`px-6 py-2 rounded-lg text-sm font-bold transition-all ${activeTab === 'validated' ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20' : 'text-slate-500 hover:text-slate-300'}`}
                        >
                            Validés
                        </button>
                    </div>

                    <div className="relative flex-1 max-w-sm">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                        <input
                            type="text"
                            placeholder="Rechercher par employé..."
                            className="form-input pl-11 py-3 bg-white/5 border-white/5 focus:border-indigo-500/50 rounded-xl"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                </div>

                <div className="table-wrap">
                    <table>
                        <thead>
                            <tr className="bg-white/5">
                                <th className="px-8 py-5">Période</th>
                                <th className="px-8 py-5">Employé</th>
                                <th className="px-8 py-5 text-right">Salaire Brut</th>
                                <th className="px-8 py-5 text-right">Salaire Net</th>
                                <th className="px-8 py-5">Statut</th>
                                <th className="px-8 py-5 text-right">Détails</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {loading ? (
                                <tr>
                                    <td colSpan={6} className="px-8 py-20 text-center">
                                        <div className="flex flex-col items-center">
                                            <div className="spinner border-4 w-12 h-12 mb-4"></div>
                                            <p className="text-slate-500 font-medium">Chargement des données paie...</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : filteredBulletins.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-8 py-20 text-center">
                                        <div className="flex flex-col items-center">
                                            <FileText className="w-16 h-16 text-slate-700 mb-4 opacity-50" />
                                            <p className="text-slate-500 text-lg mb-6">Aucun bulletin trouvé.</p>
                                            <button
                                                onClick={() => setIsModalOpen(true)}
                                                className="btn btn-ghost"
                                            >
                                                Créer mon premier bulletin
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ) : (
                                filteredBulletins.map((b) => (
                                    <tr
                                        key={b.id}
                                        className="group hover:bg-white/[0.03] transition-all cursor-pointer"
                                        onClick={() => setSelectedId(b.id)}
                                    >
                                        <td className="px-8 py-6">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-slate-400 group-hover:bg-indigo-600/20 group-hover:text-indigo-400 transition-all">
                                                    <Calendar className="w-5 h-5" />
                                                </div>
                                                <div>
                                                    <span className="block font-black text-slate-200 uppercase tracking-tighter text-sm">
                                                        {new Date(2024, b.mois - 1).toLocaleString('fr-FR', { month: 'short' })}
                                                    </span>
                                                    <span className="block text-xs text-slate-500 font-bold">{b.annee}</span>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-8 py-6">
                                            <span className="font-bold text-slate-200 text-base">{b.employe_nom}</span>
                                        </td>
                                        <td className="px-8 py-6 text-right">
                                            <span className="font-mono text-slate-400">{b.salaire_brut.toLocaleString()} <span className="text-[10px] opacity-50">MAD</span></span>
                                        </td>
                                        <td className="px-8 py-6 text-right">
                                            <span className="font-bold text-indigo-400 text-lg tracking-tight">{b.salaire_net.toLocaleString()} <span className="text-[10px] opacity-70">MAD</span></span>
                                        </td>
                                        <td className="px-8 py-6">
                                            {getStatusBadge(b.statut)}
                                        </td>
                                        <td className="px-8 py-6 text-right">
                                            <div className="inline-flex p-3 rounded-xl bg-slate-800 text-slate-500 group-hover:bg-indigo-600 group-hover:text-white transition-all shadow-lg">
                                                <ChevronRight className="w-5 h-5" />
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Creation Modal - Premium Glassmorphism */}
            {isModalOpen && (
                <div className="fixed inset-0 z-[200] flex items-center justify-center p-4">
                    <div
                        className="absolute inset-0 bg-slate-950/80 backdrop-blur-md"
                        onClick={() => { setIsModalOpen(false); setPreview(null); }}
                    ></div>

                    <div className="aurora-card w-full max-w-4xl relative z-10 animate-in zoom-in-95 duration-200 overflow-hidden">
                        <div className="p-8 border-b border-white/5 flex justify-between items-center">
                            <div>
                                <h2 className="text-2xl font-black tracking-tight mb-1">Calcul de <span className="glass-text">Paie Mensuelle</span></h2>
                                <p className="text-slate-500 font-medium">Configurez les variables pour générer le bulletin.</p>
                            </div>
                            <button
                                onClick={() => { setIsModalOpen(false); setPreview(null); }}
                                className="p-3 bg-white/5 text-slate-500 hover:text-white rounded-2xl transition-all"
                            >
                                <Plus className="w-6 h-6 rotate-45" />
                            </button>
                        </div>

                        <div className="p-8 grid grid-cols-1 lg:grid-cols-2 gap-10">
                            {/* Input Side */}
                            <div className="space-y-6">
                                <div className="form-group">
                                    <label className="form-label">Sélection de l'Employé</label>
                                    <div className="relative">
                                        <Users className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
                                        <select
                                            className="form-input pl-11 bg-white/5 focus:bg-white/10"
                                            value={newPaie.employe_id}
                                            onChange={(e) => setNewPaie({ ...newPaie, employe_id: e.target.value })}
                                        >
                                            <option value="" className="bg-slate-900">Choisir un membre...</option>
                                            {employes.map(emp => (
                                                <option key={emp.id} value={emp.id} className="bg-slate-900">{emp.prenom} {emp.nom}</option>
                                            ))}
                                        </select>
                                    </div>
                                </div>

                                <div className="two-col">
                                    <div className="form-group">
                                        <label className="form-label">Mois</label>
                                        <input
                                            type="number" min="1" max="12"
                                            className="form-input bg-white/5"
                                            value={newPaie.mois}
                                            onChange={(e) => setNewPaie({ ...newPaie, mois: parseInt(e.target.value) })}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Année</label>
                                        <input
                                            type="number"
                                            className="form-input bg-white/5"
                                            value={newPaie.annee}
                                            onChange={(e) => setNewPaie({ ...newPaie, annee: parseInt(e.target.value) })}
                                        />
                                    </div>
                                </div>

                                <div className="two-col">
                                    <div className="form-group">
                                        <label className="form-label">Primes Exceptionnelles (MAD)</label>
                                        <input
                                            type="number"
                                            className="form-input bg-white/5 font-bold text-indigo-400"
                                            value={newPaie.primes}
                                            onChange={(e) => setNewPaie({ ...newPaie, primes: parseFloat(e.target.value) })}
                                        />
                                    </div>
                                    <div className="form-group">
                                        <label className="form-label">Heures Supplémentaires (MAD)</label>
                                        <input
                                            type="number"
                                            className="form-input bg-white/5 font-bold text-indigo-400"
                                            value={newPaie.heures_sup}
                                            onChange={(e) => setNewPaie({ ...newPaie, heures_sup: parseFloat(e.target.value) })}
                                        />
                                    </div>
                                </div>

                                <button
                                    onClick={handleCalculate}
                                    disabled={!newPaie.employe_id || isCalculating}
                                    className={`w-full py-4 rounded-xl flex items-center justify-center gap-3 font-black tracking-widest transition-all ${isCalculating
                                        ? 'bg-slate-800 text-slate-500'
                                        : 'bg-white text-slate-950 hover:bg-indigo-400 shadow-xl shadow-white/5'
                                        }`}
                                >
                                    {isCalculating ? (
                                        <div className="w-5 h-5 border-2 border-slate-600 border-t-slate-400 rounded-full animate-spin"></div>
                                    ) : (
                                        <>CALCULER LA SIMULATION <ArrowUpRight className="w-5 h-5" /></>
                                    )}
                                </button>
                            </div>

                            {/* Preview Side */}
                            <div className="bg-white/5 rounded-3xl p-8 border border-white/5 flex flex-col justify-between relative overflow-hidden">
                                {preview ? (
                                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                                        <div className="flex justify-between items-start mb-10">
                                            <div>
                                                <h3 className="text-xs font-black text-slate-500 uppercase tracking-widest mb-1">Résumé de Simulation</h3>
                                                <p className="text-xl font-bold text-slate-100">Détails Estimés</p>
                                            </div>
                                            <div className="px-3 py-1 bg-indigo-500/20 text-indigo-400 text-[10px] font-black rounded-lg border border-indigo-500/20">PREVIEW</div>
                                        </div>

                                        <div className="space-y-6">
                                            <div className="flex justify-between items-end">
                                                <span className="text-slate-500 font-medium">Salaire Brut Imposable</span>
                                                <span className="font-bold text-slate-200">
                                                    {preview.salaire_brut.toLocaleString()} <span className="text-xs opacity-50">MAD</span>
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-end">
                                                <span className="text-slate-500 font-medium">Cotisations Sociales</span>
                                                <span className="font-bold text-rose-500">
                                                    -{preview.total_retenues.toLocaleString()} <span className="text-xs opacity-50">MAD</span>
                                                </span>
                                            </div>
                                            <div className="flex justify-between items-end">
                                                <span className="text-slate-500 font-medium">Coût Total Entreprise</span>
                                                <span className="font-bold text-amber-500">
                                                    {preview.cout_total_employeur?.toLocaleString()} <span className="text-xs opacity-50">MAD</span>
                                                </span>
                                            </div>

                                            <div className="pt-8 mt-8 border-t border-white/5">
                                                <p className="text-[10px] font-black text-indigo-400 uppercase tracking-[0.2em] mb-2 text-center">Net à Percevoir</p>
                                                <p className="text-6xl font-black text-center tracking-tighter glass-text leading-none mb-10">
                                                    {preview.salaire_net.toLocaleString()}
                                                </p>

                                                <button
                                                    onClick={handleSave}
                                                    className="w-full py-5 bg-indigo-600 text-white rounded-2xl font-black tracking-widest hover:bg-indigo-500 transition-all shadow-2xl shadow-indigo-600/30 active:scale-95"
                                                >
                                                    GÉNÉRER LE BULLETIN OFFICIEL
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="flex-1 flex flex-col items-center justify-center text-center py-10">
                                        <div className="w-20 h-20 bg-slate-800 rounded-3xl flex items-center justify-center text-slate-600 mb-6 border border-white/5">
                                            <TrendingUp className="w-10 h-10" />
                                        </div>
                                        <p className="text-slate-500 font-medium max-w-[200px]">
                                            Complétez le formulaire pour voir l'estimation du salaire net.
                                        </p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Paie;
