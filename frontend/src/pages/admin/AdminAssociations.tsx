import React, { useState, useEffect } from 'react';
import apiService from '../../api';
import { getAdminUser } from '../../utils/adminTokenDecoder';

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
    <div className="aurora-page">
      <div className="aurora-page-header">
        <div>
          <h1 className="glass-text">Associations</h1>
          <p className="aurora-subtitle">Connectez les collaborateurs aux portefeuilles clients.</p>
        </div>
      </div>

      {error && <div className="aurora-error-toast">{error}</div>}
      {message && <div className="aurora-success-toast">{message}</div>}

      <div className="aurora-content-layout">
        {loading ? (
          <div className="aurora-loader-inline">
            <div className="spinner-aurora"></div>
            <span>Cartographie des flux...</span>
          </div>
        ) : (
          <div className="aurora-assoc-grid">
            <div className="aurora-glass-card aurora-card assoc-form-panel">
              <h2 className="glass-text">Nouvelle Liaison</h2>

              <div className="aurora-step">
                <div className="step-num">01</div>
                <div className="aurora-input-group">
                  <label>Sélectionner le Cabinet</label>
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
                      {cabinets.find(c => c.id === selectedCabinet)?.nom || (cabinets.length > 0 ? cabinets[0].nom : 'Chargement...')}
                    </div>
                  )}
                </div>
              </div>

              {selectedCabinet && (
                <div className="aurora-fade-in">
                  <div className="aurora-step">
                    <div className="step-num">02</div>
                    <div className="aurora-form-row-assoc">
                      <div className="aurora-input-group">
                        <label>Choisir l'Agent</label>
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
                        <label>Attribuer la Société</label>
                        <select
                          className="aurora-select"
                          value={selectedSociete}
                          onChange={(e) => setSelectedSociete(e.target.value ? Number(e.target.value) : '')}
                        >
                          <option value="">-- Sélectionner l'entité --</option>
                          {filteredSocietes.map(s => (
                            <option key={s.id} value={s.id}>{s.raison_sociale}</option>
                          ))}
                        </select>
                      </div>
                    </div>
                  </div>

                  <button
                    className="aurora-btn-submit full-width neon-glow"
                    onClick={handleAssociate}
                    disabled={!selectedAgent || !selectedSociete}
                  >
                    Finaliser l'Affectation 🔗
                  </button>
                </div>
              )}
            </div>

            <div className="aurora-glass-card aurora-card info-panel">
              <div className="info-icon">⚡</div>
              <h3 className="glass-text">Synchronisation</h3>
              <p>L'agent sélectionné recevra immédiatement un accès complet aux données financières de la société choisie.</p>
              <ul className="info-list">
                <li>Visibilité sur les factures OCR</li>
                <li>Génération des écritures comptables</li>
                <li>Validation DGI & Audit Trail</li>
              </ul>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .aurora-page { animation: pageEnter 0.6s ease-out; }
        @keyframes pageEnter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

        .aurora-page-header { margin-bottom: 40px; }
        .aurora-page-header h1 { font-size: 36px; font-weight: 900; margin: 0; letter-spacing: -1px; }
        .aurora-subtitle { color: var(--admin-text-dim); font-size: 14px; font-weight: 500; margin-top: 5px; }

        .aurora-error-toast { background: rgba(239, 68, 68, 0.1); color: #f87171; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(239, 68, 68, 0.2); margin-bottom: 25px; }
        .aurora-success-toast { background: rgba(16, 185, 129, 0.1); color: #10b981; padding: 15px 25px; border-radius: 16px; border: 1px solid rgba(16, 185, 129, 0.2); margin-bottom: 25px; font-weight: 700; text-align: center; }

        .aurora-assoc-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 30px; }
        .assoc-form-panel { padding: 40px; }
        .assoc-form-panel h2 { margin: 0 0 35px 0; font-size: 22px; font-weight: 800; }

        .aurora-step { display: flex; gap: 20px; margin-bottom: 30px; }
        .step-num { width: 40px; height: 40px; border-radius: 12px; background: rgba(255, 255, 255, 0.05); display: flex; align-items: center; justify-content: center; font-weight: 900; color: var(--admin-accent); font-size: 14px; border: 1px solid var(--admin-glass-border); }
        
        .aurora-input-group { flex: 1; }
        .aurora-input-group label { display: block; font-size: 11px; font-weight: 800; color: var(--admin-text-dim); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
        .aurora-select { width: 100%; padding: 15px; border-radius: 14px; border: 1px solid var(--admin-glass-border); background: rgba(255, 255, 255, 0.03); color: white; outline: none; transition: all 0.3s; font-weight: 600; }
        .aurora-select:focus { border-color: var(--admin-accent); background: rgba(255, 255, 255, 0.06); }
        .aurora-select option { background: #1e293b; color: white; }

        .aurora-form-row-assoc { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; flex: 1; }
        .aurora-btn-submit.full-width { width: 100%; margin-top: 10px; padding: 18px; font-size: 15px; }

        .info-panel { padding: 40px; background: rgba(99, 102, 241, 0.05); border-color: rgba(99, 102, 241, 0.1); display: flex; flex-direction: column; align-items: center; text-align: center; }
        .info-icon { width: 60px; height: 60px; border-radius: 20px; background: var(--admin-gradient); margin-bottom: 25px; display: flex; align-items: center; justify-content: center; font-size: 30px; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3); }
        .info-panel h3 { margin: 0 0 15px 0; font-size: 20px; font-weight: 800; }
        .info-panel p { color: var(--admin-text-dim); font-size: 14px; line-height: 1.6; margin-bottom: 25px; }
        .info-list { list-style: none; padding: 0; margin: 0; width: 100%; }
        .info-list li { padding: 12px; font-size: 13px; font-weight: 700; color: var(--admin-text); border-bottom: 1px solid var(--admin-glass-border); display: flex; align-items: center; justify-content: center; gap: 10px; }
        .info-list li:last-child { border-bottom: none; }
        .info-list li::before { content: '✓'; color: #10b981; }

        .aurora-input-readonly {
          padding: 15px; border-radius: 14px; border: 1px solid var(--admin-glass-border);
          background: rgba(255, 255, 255, 0.02); color: var(--admin-accent); font-weight: 700;
        }

        .aurora-fade-in { animation: fadeInScale 0.4s ease-out; }
        @keyframes fadeInScale { from { opacity: 0; transform: scale(0.98); } to { opacity: 1; transform: scale(1); } }

        @media (max-width: 1024px) { .aurora-assoc-grid { grid-template-columns: 1fr; } }
      `}</style>
    </div>
  );
};
