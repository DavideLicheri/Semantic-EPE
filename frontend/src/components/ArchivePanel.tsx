import { Fragment, useState, useEffect, useCallback } from 'react';
import { EuringAPI } from '../services/api';
import { authService } from '../services/auth';
import './ArchivePanel.css';

interface FacetValue {
  value: string;
  count: number;
}

type Visibility = 'public' | 'private' | 'shared';

interface CanonicalRow {
  id: number;
  canonical_string: string;
  field_count: number;
  first_seen: string;
  last_seen: string;
  occurrence_count: number;
  visibility: Visibility;
  alias_id: number | null;
}

interface SearchResponse {
  success: boolean;
  total: number;
  page: number;
  page_size: number;
  results: CanonicalRow[];
  facets: Record<string, FacetValue[]>;
}

interface LifeHistoryFullEvent {
  kind: 'full';
  id: number;
  canonical_string: string;
  field_count: number;
  visibility: Visibility;
  is_own: boolean;
  first_seen: string | null;
  last_seen: string | null;
  occurrence_count: number;
}

interface LifeHistoryHiddenEvent {
  kind: 'hidden';
  year: string | null;
  country: string | null;
  species_code: string | null;
}

type LifeHistoryEvent = LifeHistoryFullEvent | LifeHistoryHiddenEvent;

interface AliasSummary {
  success: boolean;
  alias_id: number;
  visible_count: number;
  total_count: number;
  hidden_count: number;
  life_history: LifeHistoryEvent[];
}

const VISIBILITY_LABELS: Record<Visibility, string> = {
  public: 'Pubblico',
  private: 'Privato',
  shared: 'Condiviso',
};

const FACET_LABELS: Record<string, string> = {
  'ringing scheme': 'Scheme di inanellamento',
  'species concluded': 'Specie conclusa',
  'sex concluded': 'Sesso concluso',
  'age concluded': "Età conclusa",
  'condition': 'Condizione',
  'circumstances': 'Circostanze',
};

const PAGE_SIZE = 20;

const ArchivePanel = () => {
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [page, setPage] = useState(1);
  const [data, setData] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [expandedRowId, setExpandedRowId] = useState<number | null>(null);
  const [aliasSummaries, setAliasSummaries] = useState<Record<number, AliasSummary>>({});
  const [summaryLoading, setSummaryLoading] = useState<Record<number, boolean>>({});
  const [contactFormOpenFor, setContactFormOpenFor] = useState<number | null>(null);
  const [contactMessage, setContactMessage] = useState('');
  const [contactSending, setContactSending] = useState(false);
  const [contactResult, setContactResult] = useState<Record<number, string>>({});

  const isAuthenticated = authService.isAuthenticated();

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await EuringAPI.searchArchive(filters, page, PAGE_SIZE);
      setData(response);
    } catch (err: any) {
      setError(err.message || 'Errore nella ricerca');
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const toggleFilter = (field: string, value: string) => {
    setPage(1);
    setFilters((prev) => {
      const next = { ...prev };
      if (next[field] === value) {
        delete next[field];
      } else {
        next[field] = value;
      }
      return next;
    });
  };

  const clearFilters = () => {
    setPage(1);
    setFilters({});
  };

  const toggleRowDetail = async (row: CanonicalRow) => {
    if (expandedRowId === row.id) {
      setExpandedRowId(null);
      return;
    }
    setExpandedRowId(row.id);
    setContactFormOpenFor(null);
    setContactMessage('');

    if (row.alias_id != null && !aliasSummaries[row.id] && !summaryLoading[row.id]) {
      setSummaryLoading((prev) => ({ ...prev, [row.id]: true }));
      try {
        const summary = await EuringAPI.getAliasSummary(row.alias_id);
        setAliasSummaries((prev) => ({ ...prev, [row.id]: summary }));
      } catch {
        // silenzioso in UI: il badge di visibilità resta comunque leggibile
      } finally {
        setSummaryLoading((prev) => ({ ...prev, [row.id]: false }));
      }
    }
  };

  const sendContactRequest = async (row: CanonicalRow) => {
    if (row.alias_id == null) return;
    setContactSending(true);
    try {
      const response = await EuringAPI.createContactRequest(row.alias_id, contactMessage || undefined);
      setContactResult((prev) => ({
        ...prev,
        [row.id]: response?.success !== false
          ? 'Richiesta di contatto inviata.'
          : (response?.message || 'Invio della richiesta non riuscito.'),
      }));
      setContactFormOpenFor(null);
      setContactMessage('');
    } catch (err: any) {
      setContactResult((prev) => ({
        ...prev,
        [row.id]: err.message || 'Invio della richiesta non riuscito.',
      }));
    } finally {
      setContactSending(false);
    }
  };

  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1;

  return (
    <div className="archive-panel">
      <div className="archive-header">
        <div>
          <div className="archive-title">Archivio EURING 2020</div>
          <div className="archive-subtitle">Ricerca a faccette sulle stringhe archiviate</div>
        </div>
        <div className="archive-total-badge">
          {data ? `${data.total.toLocaleString('it-IT')} stringhe` : '...'}
        </div>
      </div>

      {error && <div className="error">{error}</div>}

      <div className="archive-body">
        <aside className="archive-sidebar">
          {Object.keys(FACET_LABELS).map((field) => {
            const facetValues = data?.facets?.[field] || [];
            if (facetValues.length === 0) return null;
            return (
              <div className="facet-group" key={field}>
                <div className="facet-group-title">{FACET_LABELS[field]}</div>
                {facetValues.map((fv) => (
                  <label className="facet-option" key={fv.value}>
                    <input
                      type="checkbox"
                      checked={filters[field] === fv.value}
                      onChange={() => toggleFilter(field, fv.value)}
                    />
                    <span className="facet-option-label">{fv.value}</span>
                    <span className="facet-option-count">{fv.count}</span>
                  </label>
                ))}
              </div>
            );
          })}
          {Object.keys(filters).length > 0 && (
            <button className="archive-clear-btn" onClick={clearFilters}>
              Rimuovi tutti i filtri
            </button>
          )}
        </aside>

        <main className="archive-results">
          {loading ? (
            <div className="archive-loading">Caricamento...</div>
          ) : (
            <>
              <div className="archive-table-wrapper">
                <table className="archive-table">
                  <thead>
                    <tr>
                      <th>Stringa canonica</th>
                      <th>Campi</th>
                      <th>Prima vista</th>
                      <th>Occorrenze</th>
                      <th>Visibilità</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.results || []).map((row) => {
                      const summary = aliasSummaries[row.id];
                      const isExpanded = expandedRowId === row.id;
                      return (
                        <Fragment key={row.id}>
                          <tr>
                            <td className="archive-string-cell" title={row.canonical_string}>
                              {row.canonical_string}
                            </td>
                            <td>{row.field_count}</td>
                            <td>{new Date(row.first_seen).toLocaleDateString('it-IT')}</td>
                            <td>{row.occurrence_count}</td>
                            <td>
                              <span className={`visibility-badge visibility-${row.visibility}`}>
                                {VISIBILITY_LABELS[row.visibility] || row.visibility}
                              </span>
                            </td>
                            <td>
                              {row.alias_id != null && (
                                <button
                                  className="archive-detail-btn"
                                  onClick={() => toggleRowDetail(row)}
                                >
                                  {isExpanded ? 'Chiudi' : 'Dettagli anello'}
                                </button>
                              )}
                            </td>
                          </tr>
                          {isExpanded && (
                            <tr key={`${row.id}-detail`} className="archive-detail-row">
                              <td colSpan={6}>
                                {summaryLoading[row.id] && <div>Caricamento riepilogo anello...</div>}
                                {!summaryLoading[row.id] && summary && (
                                  <div className="archive-detail-content">
                                    <div>
                                      Eventi visibili per te: <strong>{summary.visible_count}</strong> su{' '}
                                      <strong>{summary.total_count}</strong> totali per questo anello.
                                    </div>
                                    {summary.life_history && summary.life_history.length > 0 && (
                                      <div className="life-history">
                                        <div className="life-history-title">Storia di vita dell'anello</div>
                                        {summary.life_history.map((ev, idx) =>
                                          ev.kind === 'full' ? (
                                            <div className="life-history-item life-history-full" key={`full-${ev.id}`}>
                                              <span className="life-history-date">
                                                {ev.first_seen ? new Date(ev.first_seen).toLocaleDateString('it-IT') : '?'}
                                              </span>
                                              <span className={`visibility-badge visibility-${ev.visibility}`}>
                                                {VISIBILITY_LABELS[ev.visibility] || ev.visibility}
                                              </span>
                                              <span className="life-history-string" title={ev.canonical_string}>
                                                {ev.canonical_string}
                                              </span>
                                              {ev.is_own && <span className="life-history-own">(tuo)</span>}
                                            </div>
                                          ) : (
                                            <div className="life-history-item life-history-hidden" key={`hidden-${idx}`}>
                                              <span className="life-history-placeholder">
                                                {ev.year || '????'} · {ev.country || '??'} · specie {ev.species_code || '?'} — non condiviso
                                              </span>
                                            </div>
                                          )
                                        )}
                                      </div>
                                    )}
                                    {summary.hidden_count > 0 && (
                                      <div className="archive-hidden-note">
                                        {summary.hidden_count} evento/i non condivisi con te.
                                        {isAuthenticated ? (
                                          contactFormOpenFor === row.id ? (
                                            <div className="contact-request-form">
                                              <textarea
                                                value={contactMessage}
                                                onChange={(e) => setContactMessage(e.target.value)}
                                                placeholder="Messaggio facoltativo per il/i proprietario/i..."
                                                rows={2}
                                              />
                                              <div className="contact-request-actions">
                                                <button
                                                  onClick={() => sendContactRequest(row)}
                                                  disabled={contactSending}
                                                >
                                                  {contactSending ? 'Invio...' : 'Invia richiesta'}
                                                </button>
                                                <button
                                                  onClick={() => setContactFormOpenFor(null)}
                                                  disabled={contactSending}
                                                >
                                                  Annulla
                                                </button>
                                              </div>
                                            </div>
                                          ) : (
                                            <button
                                              className="archive-detail-btn"
                                              onClick={() => setContactFormOpenFor(row.id)}
                                            >
                                              Richiedi contatto
                                            </button>
                                          )
                                        ) : (
                                          <span> Accedi per richiedere il contatto con il proprietario.</span>
                                        )}
                                      </div>
                                    )}
                                    {contactResult[row.id] && (
                                      <div className="archive-contact-result">{contactResult[row.id]}</div>
                                    )}
                                  </div>
                                )}
                              </td>
                            </tr>
                          )}
                        </Fragment>
                      );
                    })}
                    {data && data.results.length === 0 && (
                      <tr>
                        <td colSpan={6} className="archive-empty">
                          Nessuna stringa trovata con questi filtri.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {data && data.total > 0 && (
                <div className="archive-pagination">
                  <button disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                    Precedente
                  </button>
                  <span>
                    Pagina {page} di {totalPages}
                  </span>
                  <button disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                    Successiva
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
  );
};

export default ArchivePanel;
