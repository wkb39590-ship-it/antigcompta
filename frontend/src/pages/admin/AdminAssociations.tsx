import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
  Link,
  Zap,
  Building2,
  Users,
  Fingerprint,
} from 'lucide-react';

interface Agent {
  id: number;
  username: string;
  nom: string;
  prenom: string;
  cabinet_id: number;
}

interface Societe {
  id: number;
  raison_sociale: string;
  cabinet_id: number;
}

interface Cabinet {
  id: number;
  nom: string;
}

export const AdminAssociations: React.FC = () => {
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [societes, setSocietes] = useState<Societe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  const [selectedCabinet, setSelectedCabinet] = useState<number | ''>('');
  const [selectedAgent, setSelectedAgent] = useState<number | ''>('');
  const [selectedSociete, setSelectedSociete] = useState<number | ''>('');

  const adminUser = getAdminUser();
  const isSuper = adminUser?.is_super_admin === true;

  useEffect(() => {
    fetchData();
  }, []);

  const getErrorMessage = (err: any) => {
    const detail = err.response?.data?.detail;
    if (typeof detail === 'string') return detail;
    return err.message || 'Une erreur est survenue';
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cabData, agData, socData] = await Promise.all([
        isSuper ? apiService.adminListCabinets() : Promise.resolve(JSON.parse(localStorage.getItem('cabinets') || '[]')),
        apiService.adminListAgents(),
        apiService.adminListSocietes()
      ]);

      setCabinets(Array.isArray(cabData) ? cabData : []);
      setAgents(Array.isArray(agData) ? agData : []);
      setSocietes(Array.isArray(socData) ? socData : []);

      if (!isSuper && adminUser?.cabinet_id) {
        setSelectedCabinet(adminUser.cabinet_id);
      }
    } catch (err: any) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const handleAssociate = async () => {
    if (!selectedCabinet || !selectedAgent || !selectedSociete) {
      setError('Tous les champs sont requis');
      return;
    }

    try {
      setError('');
      await apiService.adminAssignSocieteToAgent(
        Number(selectedCabinet),
        Number(selectedAgent),
        Number(selectedSociete)
      );

      setMessage('Liaison établie avec succès');
      setTimeout(() => setMessage(''), 3000);
    } catch (err: any) {
      setError(getErrorMessage(err));
    }
  };

  const filteredAgents = selectedCabinet
    ? agents.filter(a => a.cabinet_id === Number(selectedCabinet) && a.id !== adminUser?.id)
    : [];

  const filteredSocietes = selectedCabinet
    ? societes.filter(s => s.cabinet_id === Number(selectedCabinet))
    : [];

  return (
    <div className="assoc-page">
      <div className="page-header-simple">
        <h1>Gestion des Liaisons</h1>
        <p>Assignation des portefeuilles clients aux collaborateurs de l'équipe.</p>
      </div>

      {error && <div className="error-banner">{error}</div>}
      {message && <div className="success-banner">{message}</div>}

      <div className="content-layout">
        {loading ? (
          <div className="placeholder-state">
            <div className="dot-spinner"></div>
            <span>Synchronisation des entités...</span>
          </div>
        ) : (
          <div className="assoc-container">
            <div className="pro-card assoc-card">
              <div className="card-header-line">
                <h3>Nouvelle Affectation</h3>
                <Zap size={14} className="accent-color" />
              </div>

              <div className="assoc-form">
                <div className="assoc-section">
                  <div className="section-step">
                    <div className="step-num">01</div>
                    <div className="field-group">
                      <label>Cabinet Référent</label>
                      {isSuper ? (
                        <select
                          className="pro-select"
                          value={selectedCabinet}
                          onChange={(e) => {
                            setSelectedCabinet(e.target.value ? Number(e.target.value) : '');
                            setSelectedAgent('');
                            setSelectedSociete('');
                          }}
                        >
                          <option value="">Sélectionner un cabinet partenaire...</option>
                          {cabinets.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
                        </select>
                      ) : (
                        <div className="pro-input-read">
                          {cabinets.find(c => c.id === selectedCabinet)?.nom || 'Cabinet local'}
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                <div className={`assoc-section ${selectedCabinet ? 'active' : 'disabled'}`}>
                  <div className="section-step">
                    <div className="step-num">02</div>
                    <div className="fields-grid">
                      <div className="field-group">
                        <label>Agent Cible</label>
                        <div className="select-with-icon">
                          <Users size={14} className="input-icon" />
                          <select
                            className="pro-select has-icon"
                            value={selectedAgent}
                            disabled={!selectedCabinet}
                            onChange={(e) => setSelectedAgent(e.target.value ? Number(e.target.value) : '')}
                          >
                            <option value="">Choisir un agent...</option>
                            {filteredAgents.map(a => (
                              <option key={a.id} value={a.id}>{a.prenom} {a.nom}</option>
                            ))}
                          </select>
                        </div>
                      </div>

                      <div className="field-group">
                        <label>Société à Attribuer</label>
                        <div className="select-with-icon">
                          <Building2 size={14} className="input-icon" />
                          <select
                            className="pro-select has-icon"
                            value={selectedSociete}
                            disabled={!selectedCabinet}
                            onChange={(e) => setSelectedSociete(e.target.value ? Number(e.target.value) : '')}
                          >
                            <option value="">Choisir une société...</option>
                            {filteredSocietes.map(s => (
                              <option key={s.id} value={s.id}>{s.raison_sociale}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  className="btn-primary full-w assoc-submit"
                  disabled={!selectedAgent || !selectedSociete}
                  onClick={handleAssociate}
                >
                  <Link size={16} /> <span>Établir la liaison comptable</span>
                </button>
              </div>
            </div>

            <div className="pro-card help-card">
              <div className="help-icon-box"><Fingerprint size={28} /></div>
              <h4>Règles d'affectation</h4>
              <p>L'assignation d'une société à un collaborateur lui confère des droits de lecture et d'écriture complets sur les dossiers (Factures, Paie, Immo) de cette entité.</p>
              <ul className="help-list">
                <li>Visibilité restreinte au portefeuille</li>
                <li>Audit trail complet des actions</li>
                <li>Traitement temps réel activé</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .assoc-page { padding: 24px; animation: fadeIn 0.4s ease-out; }
        .page-header-simple h1 { font-size: 24px; font-weight: 800; color: #0f172a; margin: 0; }
        .page-header-simple p { font-size: 14px; color: #64748b; margin: 8px 0 24px; }

        .assoc-container { display: grid; grid-template-columns: 1fr 300px; gap: 24px; }
        .pro-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }

        .assoc-card { padding: 32px; }
        .card-header-line { display: flex; justify-content: space-between; align-items: center; margin-bottom: 32px; border-bottom: 1px solid #f1f5f9; padding-bottom: 16px; }
        .card-header-line h3 { margin: 0; font-size: 18px; font-weight: 700; color: #1e293b; }
        .accent-color { color: #3b82f6; }

        .assoc-form { display: flex; flex-direction: column; gap: 32px; }
        .assoc-section { opacity: 1; transition: opacity 0.3s; }
        .assoc-section.disabled { opacity: 0.4; pointer-events: none; }
        
        .section-step { display: flex; gap: 24px; }
        .step-num { width: 36px; height: 36px; border-radius: 4px; background: #f8fafc; border: 1px solid #e2e8f0; display: flex; align-items: center; justify-content: center; font-weight: 600; color: #3b82f6; flex-shrink: 0; font-size: 14px; }
        
        .field-group { flex: 1; }
        .field-group label { display: block; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 8px; }
        .pro-select { width: 100%; padding: 12px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 14px; background: #fff; outline: none; }
        .pro-select:focus { border-color: #3b82f6; }
        .pro-input-read { padding: 12px; background: #f1f5f9; border: 1px solid #e2e8f0; border-radius: 4px; color: #3b82f6; font-weight: 700; font-size: 14px; }

        .fields-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex: 1; }
        .select-with-icon { position: relative; }
        .input-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: #94a3b8; }
        .pro-select.has-icon { padding-left: 36px; }

        .btn-primary { background: #3b82f6; color: white; border: none; padding: 14px; border-radius: 4px; font-weight: 700; font-size: 14px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; transition: background 0.2s; }
        .btn-primary:hover:not(:disabled) { background: #2563eb; }
        .btn-primary:disabled { background: #e2e8f0; color: #94a3b8; cursor: not-allowed; }
        
        .help-card { padding: 24px; background: #f8fafc; border-style: dashed; }
        .help-icon-box { color: #3b82f6; margin-bottom: 16px; }
        .help-card h4 { margin: 0 0 12px; font-size: 15px; font-weight: 700; color: #1e293b; }
        .help-card p { font-size: 13px; color: #64748b; line-height: 1.6; margin: 0 0 20px; }
        .help-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 10px; }
        .help-list li { font-size: 12px; font-weight: 600; color: #475569; display: flex; align-items: center; gap: 8px; }
        .help-list li::before { content: ""; width: 4px; height: 4px; background: #3b82f6; border-radius: 50%; }

        .placeholder-state { padding: 60px; text-align: center; }
        .dot-spinner { width: 24px; height: 24px; border: 3px solid #f1f5f9; border-top-color: #3b82f6; border-radius: 50%; animation: rot 0.8s linear infinite; margin: 0 auto 12px; }
        @keyframes rot { to { transform: rotate(360deg); } }

        .error-banner { padding: 12px; background: #fef2f2; color: #dc2626; font-size: 13px; border-radius: 4px; margin-bottom: 24px; border: 1px solid #fee2e2; font-weight: 600; text-align: center; }
        .success-banner { padding: 12px; background: #f0fdf4; color: #16a34a; font-size: 13px; border-radius: 4px; margin-bottom: 24px; border: 1px solid #dcfce7; font-weight: 700; text-align: center; }

        @media (max-width: 900px) {
          .assoc-container { grid-template-columns: 1fr; }
          .fields-grid { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
};
