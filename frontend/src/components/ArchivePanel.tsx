import { useState, useEffect, useCallback } from 'react';
import { EuringAPI } from '../services/api';
import './ArchivePanel.css';

interface FacetValue {
  value: string;
  count: number;
}

interface CanonicalRow {
  id: number;
  canonical_string: string;
  field_count: number;
  first_seen: string;
  last_seen: string;
  occurrence_count: number;
}

interface SearchResponse {
  success: boolean;
  total: number;
  page: number;
  page_size: number;
  results: CanonicalRow[];
  facets: Record<string, FacetValue[]>;
}

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
                    </tr>
                  </thead>
                  <tbody>
                    {(data?.results || []).map((row) => (
                      <tr key={row.id}>
                        <td className="archive-string-cell" title={row.canonical_string}>
                          {row.canonical_string}
                        </td>
                        <td>{row.field_count}</td>
                        <td>{new Date(row.first_seen).toLocaleDateString('it-IT')}</td>
                        <td>{row.occurrence_count}</td>
                      </tr>
                    ))}
                    {data && data.results.length === 0 && (
                      <tr>
                        <td colSpan={4} className="archive-empty">
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
