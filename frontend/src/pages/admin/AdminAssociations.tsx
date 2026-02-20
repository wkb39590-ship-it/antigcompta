import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface Cabinet {
  id: number;
  nom: string;
}

interface Societe {
  id: number;
  raison_sociale: string;
  cabinet_id?: number;
}

export const AdminAssociations: React.FC = () => {
  const [cabinets, setCabinets] = useState<Cabinet[]>([]);
  const [societes, setSocietes] = useState<Societe[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedCabinet, setSelectedCabinet] = useState<number | null>(null);
  const [selectedSociete, setSelectedSociete] = useState<number | null>(null);
  const [message, setMessage] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8888';
  const token = localStorage.getItem('admin_token');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [cabRes, socRes] = await Promise.all([
        axios.get(`${API_URL}/admin/cabinets`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        axios.get(`${API_URL}/societes`, {
          params: { token },
        }),
      ]);

      setCabinets(Array.isArray(cabRes.data) ? cabRes.data : []);
      setSocietes(Array.isArray(socRes.data) ? socRes.data : []);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors du chargement');
    } finally {
      setLoading(false);
    }
  };

  const handleAssociate = async () => {
    if (!selectedCabinet || !selectedSociete) {
      setError('Veuillez sélectionner un cabinet et une société');
      return;
    }

    try {
      await axios.post(
        `${API_URL}/admin/cabinets/${selectedCabinet}/societes`,
        { id: selectedSociete },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      setMessage('Association créée avec succès');
      setSelectedCabinet(null);
      setSelectedSociete(null);
      setTimeout(() => setMessage(''), 3000);
      fetchData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erreur lors de l\'association');
    }
  };

  const cabinetSocietes = selectedCabinet
    ? societes.filter((s) => s.cabinet_id === selectedCabinet)
    : [];

  return (
    <div className="page-content">
        <h1>Association Sociétés ↔ Cabinets</h1>

        {error && <div className="error-message">{error}</div>}
        {message && <div className="success-message">{message}</div>}

        {loading ? (
          <div className="loading">Chargement des données...</div>
        ) : (
          <div className="association-container">
            <div className="card">
              <h2>Lier une Société à un Cabinet</h2>

              <div className="form-group">
                <label>Sélectionner un Cabinet</label>
                <select
                  value={selectedCabinet || ''}
                  onChange={(e) =>
                    setSelectedCabinet(
                      e.target.value ? parseInt(e.target.value) : null
                    )
                  }
                >
                  <option value="">-- Choisir un cabinet --</option>
                  {cabinets.map((cab) => (
                    <option key={cab.id} value={cab.id}>
                      {cab.nom}
                    </option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>Sélectionner une Société</label>
                <select
                  value={selectedSociete || ''}
                  onChange={(e) =>
                    setSelectedSociete(
                      e.target.value ? parseInt(e.target.value) : null
                    )
                  }
                >
                  <option value="">-- Choisir une société --</option>
                  {societes
                    .filter((s) => !s.cabinet_id)
                    .map((soc) => (
                      <option key={soc.id} value={soc.id}>
                        {soc.raison_sociale}
                      </option>
                    ))}
                </select>
              </div>

              <button className="btn-primary" onClick={handleAssociate}>
                Créer l'association
              </button>
            </div>

            {selectedCabinet && (
              <div className="card">
                <h2>
                  Sociétés associées à{' '}
                  {cabinets.find((c) => c.id === selectedCabinet)?.nom}
                </h2>

                {cabinetSocietes.length === 0 ? (
                  <p className="empty-state">
                    Aucune société associée à ce cabinet
                  </p>
                ) : (
                  <ul className="societe-list">
                    {cabinetSocietes.map((soc) => (
                      <li key={soc.id}>
                        <span>{soc.raison_sociale}</span>
                        <button className="btn-small btn-danger">
                          Dissocier
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
        )}

        <style>{`
          .page-content {
            max-width: 1000px;
          }

          .page-content h1 {
            color: #2c3e50;
            font-size: 28px;
            margin-top: 0;
          }

          .error-message {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #c33;
          }

          .success-message {
            background: #efe;
            color: #3c3;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
            border-left: 4px solid #3c3;
          }

          .loading {
            text-align: center;
            padding: 40px;
            color: #7f8c8d;
          }

          .association-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
          }

          .card {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }

          .card h2 {
            margin-top: 0;
            color: #2c3e50;
            font-size: 20px;
          }

          .form-group {
            margin-bottom: 20px;
          }

          .form-group label {
            display: block;
            margin-bottom: 8px;
            color: #2c3e50;
            font-weight: 500;
            font-size: 14px;
          }

          .form-group select {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            box-sizing: border-box;
            background: white;
          }

          .form-group select:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
          }

          .btn-primary {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
          }

          .btn-primary:hover {
            background: #5568d3;
            transform: translateY(-2px);
          }

          .societe-list {
            list-style: none;
            padding: 0;
            margin: 0;
          }

          .societe-list li {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #ecf0f1;
            background: #f8f9fa;
            margin-bottom: 10px;
            border-radius: 4px;
          }

          .societe-list li span {
            color: #2c3e50;
            font-weight: 500;
          }

          .btn-small {
            padding: 6px 12px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 12px;
            transition: all 0.2s;
          }

          .btn-small:hover {
            background: #c0392b;
          }

          .empty-state {
            text-align: center;
            padding: 20px;
            color: #95a5a6;
          }

          @media (max-width: 768px) {
            .association-container {
              grid-template-columns: 1fr;
            }
          }
        `}</style>
      </div>
  );
};
