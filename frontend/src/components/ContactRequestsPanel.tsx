/**
 * Richieste di contatto (HANDOFF.md, punti 6-11): un utente che vede
 * "N eventi non condivisi con te" nell'ArchivePanel puo' chiedere il
 * contatto con il/i proprietari nascosti. Questo pannello mostra:
 *  - le richieste RICEVUTE (come proprietario), con un form di risposta a
 *    due decisioni indipendenti: condividere il dato (shared) e/o rivelare
 *    la propria identita' (identity_revealed);
 *  - le richieste INVIATE (come richiedente), dove l'identita' del
 *    proprietario non viene mai mostrata finche' lui non la rivela
 *    esplicitamente (invariante di privacy centrale del progetto).
 */
import { Fragment, useState, useEffect, useCallback } from 'react';
import { EuringAPI } from '../services/api';
import './ContactRequestsPanel.css';

interface ReceivedRequest {
  id: number;
  alias_id: number;
  requester_username: string;
  message: string | null;
  status: 'pending' | 'responded';
  shared: boolean;
  identity_revealed: boolean;
  created_at: string;
  responded_at: string | null;
}

interface SentRequest {
  id: number;
  alias_id: number;
  message: string | null;
  status: 'pending' | 'responded';
  shared: boolean;
  identity_revealed: boolean;
  created_at: string;
  responded_at: string | null;
}

const ContactRequestsPanel = () => {
  const [received, setReceived] = useState<ReceivedRequest[]>([]);
  const [sent, setSent] = useState<SentRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [respondFormOpenFor, setRespondFormOpenFor] = useState<number | null>(null);
  const [shareChoice, setShareChoice] = useState(false);
  const [identityChoice, setIdentityChoice] = useState(false);
  const [responding, setResponding] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [receivedResp, sentResp] = await Promise.all([
        EuringAPI.listReceivedContactRequests(),
        EuringAPI.listSentContactRequests(),
      ]);
      setReceived(receivedResp?.requests || []);
      setSent(sentResp?.requests || []);
    } catch (err: any) {
      setError(err.message || 'Errore nel recupero delle richieste di contatto');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const openRespondForm = (req: ReceivedRequest) => {
    setRespondFormOpenFor(req.id);
    setShareChoice(req.shared);
    setIdentityChoice(req.identity_revealed);
  };

  const submitResponse = async (requestId: number) => {
    setResponding(true);
    try {
      await EuringAPI.respondToContactRequest(requestId, shareChoice, identityChoice);
      setRespondFormOpenFor(null);
      await loadData();
    } catch (err: any) {
      setError(err.message || 'Errore nella risposta alla richiesta');
    } finally {
      setResponding(false);
    }
  };

  const formatDate = (value: string | null) =>
    value ? new Date(value).toLocaleString('it-IT') : '-';

  return (
    <div className="contact-requests-panel">
      <div className="contact-requests-header">
        <div>
          <div className="contact-requests-title">Richieste di contatto</div>
          <div className="contact-requests-subtitle">
            Anelli con eventi condivisi tra piu' proprietari (HANDOFF.md, punti 6-11)
          </div>
        </div>
      </div>

      {error && <div className="error">{error}</div>}
      {loading && <div className="contact-requests-loading">Caricamento...</div>}

      {!loading && (
        <>
          <section className="contact-requests-section">
            <h3>Ricevute (come proprietario)</h3>
            {received.length === 0 && (
              <div className="contact-requests-empty">Nessuna richiesta ricevuta.</div>
            )}
            <table className="contact-requests-table">
              <thead>
                <tr>
                  <th>Anello</th>
                  <th>Richiedente</th>
                  <th>Messaggio</th>
                  <th>Stato</th>
                  <th>Ricevuta il</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {received.map((req) => (
                  <Fragment key={req.id}>
                    <tr>
                      <td>{req.alias_id}</td>
                      <td>{req.requester_username}</td>
                      <td className="contact-requests-message-cell">{req.message || '-'}</td>
                      <td>
                        <span className={`status-badge status-${req.status}`}>
                          {req.status === 'pending' ? 'In attesa' : 'Risposta data'}
                        </span>
                      </td>
                      <td>{formatDate(req.created_at)}</td>
                      <td>
                        <button
                          className="contact-requests-btn"
                          onClick={() => openRespondForm(req)}
                        >
                          {req.status === 'pending' ? 'Rispondi' : 'Modifica risposta'}
                        </button>
                      </td>
                    </tr>
                    {respondFormOpenFor === req.id && (
                      <tr className="contact-requests-detail-row">
                        <td colSpan={6}>
                          <div className="respond-form">
                            <label className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={shareChoice}
                                onChange={(e) => setShareChoice(e.target.checked)}
                              />
                              Condividi i miei eventi di questo anello con {req.requester_username}
                            </label>
                            <label className="checkbox-label">
                              <input
                                type="checkbox"
                                checked={identityChoice}
                                onChange={(e) => setIdentityChoice(e.target.checked)}
                              />
                              Rivela la mia identita' a {req.requester_username}
                            </label>
                            <div className="respond-form-actions">
                              <button
                                onClick={() => submitResponse(req.id)}
                                disabled={responding}
                              >
                                {responding ? 'Invio...' : 'Conferma risposta'}
                              </button>
                              <button
                                onClick={() => setRespondFormOpenFor(null)}
                                disabled={responding}
                              >
                                Annulla
                              </button>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </Fragment>
                ))}
              </tbody>
            </table>
          </section>

          <section className="contact-requests-section">
            <h3>Inviate (come richiedente)</h3>
            {sent.length === 0 && (
              <div className="contact-requests-empty">Nessuna richiesta inviata.</div>
            )}
            <table className="contact-requests-table">
              <thead>
                <tr>
                  <th>Anello</th>
                  <th>Messaggio</th>
                  <th>Stato</th>
                  <th>Condiviso</th>
                  <th>Identita' rivelata</th>
                  <th>Inviata il</th>
                </tr>
              </thead>
              <tbody>
                {sent.map((req) => (
                  <tr key={req.id}>
                    <td>{req.alias_id}</td>
                    <td className="contact-requests-message-cell">{req.message || '-'}</td>
                    <td>
                      <span className={`status-badge status-${req.status}`}>
                        {req.status === 'pending' ? 'In attesa' : 'Risposta data'}
                      </span>
                    </td>
                    <td>{req.status === 'responded' ? (req.shared ? 'Sì' : 'No') : '-'}</td>
                    <td>{req.status === 'responded' ? (req.identity_revealed ? 'Sì' : 'No') : '-'}</td>
                    <td>{formatDate(req.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </div>
  );
};

export default ContactRequestsPanel;
