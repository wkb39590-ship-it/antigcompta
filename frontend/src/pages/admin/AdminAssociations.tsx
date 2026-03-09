import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';
import {
  Link,
  Zap,
  Check,
  Users,
  Building2,
  UserCheck,
  ShieldCheck,
  FileSearch,
  History
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

      const cabinetList = Array.isArray(cabData) ? cabData : [];
      setCabinets(cabinetList);
      setAgents(Array.isArray(agData) ? agData : []);
      setSocietes(Array.isArray(socData) ? socData : []);

      // Sélection automatique pour Admin simple
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
      setError('');
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
    <div className="aurora-page-v2">
      <div className="aurora-page-header">
        <div className="header-info">
          <h1 className="hero-title heading-font">Associations</h1>
          <p className="aurora-subtitle">Gestion de la cartographie : Collaborateurs vs Portefeuilles Clients.</p>
        </div>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}
      {message && <div className="aurora-success-toast">{message}</div>}

      <div className="aurora-content-grid">
        {loading ? (
          <div className="aurora-loader-inline">
            <div className="spinner-aurora"></div>
            <span>Initialisation des services système...</span>
          </div>
        ) : (
          <div className="aurora-assoc-centered-layout">
            <div className="aurora-card premium-form assoc-panel">
              <div className="form-header">
                <h2 className="heading-font">Nouvelle Liaison</h2>
                <p>Définissez les droits d'accès pour un agent spécifique</p>
              </div>

              <div className="assoc-steps-container">
                <div className="aurora-step-v2">
                  <div className="step-badge">01</div>
                  <div className="aurora-input-group">
                    <label>Cabinet de Référence</label>
                    {isSuper ? (
                      <select
                        className="aurora-select"
                        value={selectedCabinet}
                        onChange={(e) => {
                          setSelectedCabinet(e.target.value ? Number(e.target.value) : '');
                          setSelectedAgent('');
                          setSelectedSociete('');
                        }}
                      >
                        <option value="">-- Choisir un partenaire --</option>
                        {cabinets.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
                      </select>
                    ) : (
                      <div className="aurora-input-readonly">
                        {cabinets.find(c => c.id === selectedCabinet)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Chargement cabinet...')}
                      </div>
                    )}
                  </div>
                </div>

                {selectedCabinet && (
                  <div className="aurora-fade-in-steps">
                    <div className="aurora-step-v2">
                      <div className="step-badge">02</div>
                      <div className="aurora-form-row-assoc">
                        <div className="aurora-input-group">
                          <label>Collaborateur Cible</label>
                          <select
                            className="aurora-select"
                            value={selectedAgent}
                            onChange={(e) => setSelectedAgent(e.target.value ? Number(e.target.value) : '')}
                          >
                            <option value="">-- Sélectionner l'agent --</option>
                            {filteredAgents.map(a => (
                              <option key={a.id} value={a.id}>{a.prenom} {a.nom}</option>
                            ))}
                          </select>
                        </div>
                        <div className="aurora-input-group">
                          <label>Entité à Attribuer</label>
                          <select
                            className="aurora-select"
                            value={selectedSociete}
                            onChange={(e) => setSelectedSociete(e.target.value ? Number(e.target.value) : '')}
                          >
                            <option value="">-- Sélectionner l'entreprise --</option>
                            {filteredSocietes.map(s => (
                              <option key={s.id} value={s.id}>{s.raison_sociale}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    </div>

                    <button
                      className="aurora-btn-primary full-width assoc-btn"
                      onClick={handleAssociate}
                      disabled={!selectedAgent || !selectedSociete}
                    >
                      <Link size={18} /> <span>Établir la Connexion</span>
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .aurora-page-v2 { animation: pageFadeIn 0.8s ease-out; padding-bottom: 80px; }
        
        .aurora-page-header { margin-bottom: 35px; }
        .hero-title { font-size: 38px; font-weight: 800; margin: 0; letter-spacing: -1.5px; }
        .aurora-subtitle { color: var(--text3); font-size: 14px; font-weight: 500; margin-top: 4px; }

        .aurora-error-toast { background: rgba(239, 68, 68, 0.05); color: #ef4444; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.1); margin-bottom: 25px; font-size: 14px; font-weight: 600; }
        .aurora-success-toast { background: rgba(16, 185, 129, 0.08); color: #10b981; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.15); margin-bottom: 25px; font-weight: 700; text-align: center; }

        .aurora-assoc-centered-layout { display: flex; justify-content: center; align-items: flex-start; }
        .assoc-panel { width: 100%; max-width: 800px; }
        
        .premium-form { padding: 35px; }
        .form-header { margin-bottom: 30px; }
        .form-header h2 { font-size: 22px; font-weight: 800; margin: 0; }
        .form-header p { font-size: 14px; color: var(--text3); margin-top: 4px; }

        .assoc-steps-container { display: flex; flex-direction: column; gap: 20px; }
        
        .aurora-step-v2 { display: flex; gap: 20px; align-items: flex-start; }
        .step-badge { 
          width: 44px; height: 44px; min-width: 44px; border-radius: 12px; 
          background: #f8fafc; border: 1px solid #e2e8f0;
          display: flex; align-items: center; justify-content: center; 
          font-weight: 800; color: var(--accent); font-size: 15px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        
        .aurora-input-group { flex: 1; }
        .aurora-input-group label { display: block; font-size: 11px; font-weight: 800; color: var(--text3); text-transform: uppercase; letter-spacing: 1.2px; margin-bottom: 10px; }
        
        .aurora-select { 
          width: 100%; padding: 15px; border-radius: 14px; border: 1px solid var(--border); 
          background: white; color: var(--text); outline: none; transition: all 0.3s; 
          font-weight: 600; font-family: 'Inter', sans-serif;
        }
        .aurora-select:focus { border-color: var(--accent); box-shadow: 0 0 10px rgba(99, 102, 241, 0.1); }

        .aurora-form-row-assoc { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex: 1; }
        
        .assoc-btn { margin-top: 15px; padding: 18px; display: flex; align-items: center; justify-content: center; gap: 10px; font-size: 15px; }
        .full-width { width: 100%; }

        .info-impact-panel { padding: 35px; background: rgba(99,102,241, 0.02); border: 1px dashed rgba(99,102,241, 0.2); }
        .impact-header { display: flex; align-items: center; gap: 15px; margin-bottom: 25px; }
        .impact-icon-box { 
          width: 54px; height: 54px; border-radius: 16px; 
          background: linear-gradient(145deg, #1e293b, #0f172a);
          color: white;
          display: flex; align-items: center; justify-content: center;
          box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2), inset 0 2px 4px rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.05);
        }
        .impact-header h3 { margin: 0; font-size: 19px; font-weight: 800; }
        
        .impact-desc { color: var(--text2); font-size: 14px; line-height: 1.6; font-weight: 500; margin-bottom: 30px; }
        
        .impact-features { display: flex; flex-direction: column; gap: 20px; }
        .feature-item { display: flex; gap: 15px; padding-bottom: 20px; border-bottom: 1px solid #f1f5f9; }
        .feature-item:last-child { border-bottom: none; }
        .f-icon { 
          width: 32px; height: 32px; min-width: 32px; border-radius: 10px; 
          background: #eff6ff; color: var(--accent);
          display: flex; align-items: center; justify-content: center;
        }
        .f-text { display: flex; flex-direction: column; gap: 2px; }
        .f-text strong { font-size: 13px; font-weight: 800; color: var(--text); }
        .f-text span { font-size: 12px; color: var(--text3); font-weight: 500; }

        .aurora-input-readonly {
          padding: 15px; border-radius: 14px; border: 1px dashed var(--accent);
          background: rgba(99, 102, 241, 0.03); color: var(--accent); font-weight: 700;
          font-size: 14px;
        }

        .aurora-fade-in-steps { animation: slideDown 0.5s ease-out; }
        @keyframes slideDown { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

        .aurora-loader-inline { padding: 60px; text-align: center; display: flex; flex-direction: column; align-items: center; gap: 15px; color: var(--text3); }
        .spinner-aurora { width: 32px; height: 32px; border: 3px solid #f1f5f9; border-top-color: var(--accent); border-radius: 50%; animation: spin 1s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }

        @media (max-width: 1200px) {
          .aurora-assoc-dual-layout { grid-template-columns: 1fr; }
        }
        @media (max-width: 600px) {
          .aurora-form-row-assoc { grid-template-columns: 1fr; }
        }
      `}</style>
    </div>
  );
};
