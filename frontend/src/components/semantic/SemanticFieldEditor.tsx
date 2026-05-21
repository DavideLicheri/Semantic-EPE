import React, { useState, useEffect, useCallback } from 'react';
import EuringAPI from '../../services/api';
import './SemanticFieldEditor.css';

// ── Types ──────────────────────────────────────────────────────────────────────

export interface MatrixFieldData {
  fieldName: string;
  version: string;
  position: number;
  length: number;
  data_type: string;
  semantic_domain?: string;
  semantic_meaning?: string;
  description?: string;
  evolution_notes?: string[];
}

interface FieldSemanticData {
  valid_values_type: string | null;
  valid_values: string[] | null;
  valid_values_descriptions: Record<string, string> | null;
  valid_values_source: string | null;
  valid_values_lookup_tool: string | null;
  valid_values_range: Record<string, any> | null;
  description: string | null;
  valid_values_source_info?: {
    valid_values_source?: string;
    valid_values_lookup_tool?: string;
  };
}

const VALID_VALUES_TYPES = [
  { value: 'enumeration', label: 'enumeration' },
  { value: 'external_reference', label: 'external_reference' },
  { value: 'computed', label: 'computed' },
  { value: 'free_numeric', label: 'free_numeric' },
  { value: 'free_text', label: 'free_text' },
  { value: 'free_alphanumeric', label: 'free_alphanumeric' },
];

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '6px 8px',
  border: '1px solid #ced4da',
  borderRadius: '5px',
  fontSize: '0.88em',
  boxSizing: 'border-box',
  fontFamily: 'inherit',
};

// ── Sub-components ─────────────────────────────────────────────────────────────

const SectionLabel: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div style={{
    fontSize: '0.72em', fontWeight: 700, textTransform: 'uppercase',
    letterSpacing: '0.5px', color: '#6c757d', marginBottom: '4px',
  }}>
    {children}
  </div>
);

const ReadOnlyField: React.FC<{ label: string; value?: string | number | null }> = ({ label, value }) => (
  <div style={{ marginBottom: '10px' }}>
    <SectionLabel>{label}</SectionLabel>
    <div style={{ fontSize: '0.88em', color: value ? '#212529' : '#adb5bd', fontStyle: value ? 'normal' : 'italic' }}>
      {value ?? '—'}
    </div>
  </div>
);

// ── ValidValuesList ────────────────────────────────────────────────────────────

const ValidValuesList: React.FC<{
  values: string[];
  onChange: (vals: string[]) => void;
  disabled?: boolean;
}> = ({ values, onChange, disabled }) => {
  const addValue = () => onChange([...values, '']);
  const removeValue = (i: number) => onChange(values.filter((_, idx) => idx !== i));
  const updateValue = (i: number, v: string) => {
    const next = [...values];
    next[i] = v;
    onChange(next);
  };

  return (
    <div>
      {values.map((v, i) => (
        <div key={i} style={{ display: 'flex', gap: '5px', marginBottom: '4px', alignItems: 'center' }}>
          <input
            value={v}
            onChange={e => updateValue(i, e.target.value)}
            disabled={disabled}
            style={{ ...inputStyle, flex: 1 }}
          />
          {!disabled && (
            <button
              onClick={() => removeValue(i)}
              style={{ background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', padding: '4px 7px', fontSize: '0.85em' }}
            >✕</button>
          )}
        </div>
      ))}
      {!disabled && (
        <button
          onClick={addValue}
          style={{ padding: '4px 10px', background: '#e9ecef', border: '1px solid #ced4da', borderRadius: '4px', cursor: 'pointer', fontSize: '0.82em', marginTop: '2px' }}
        >
          + Aggiungi valore
        </button>
      )}
    </div>
  );
};

// ── ValidValuesDescriptions ───────────────────────────────────────────────────

const ValidValuesDescriptions: React.FC<{
  values: string[];
  descriptions: Record<string, string>;
  onChange: (d: Record<string, string>) => void;
}> = ({ values, descriptions, onChange }) => {
  const update = (code: string, desc: string) => onChange({ ...descriptions, [code]: desc });

  if (values.length === 0) return <div style={{ color: '#adb5bd', fontSize: '0.85em', fontStyle: 'italic' }}>Nessun valore definito</div>;

  return (
    <div>
      {values.map(code => (
        <div key={code} style={{ display: 'flex', gap: '6px', marginBottom: '4px', alignItems: 'center' }}>
          <div style={{
            width: '50px', flexShrink: 0, padding: '5px 6px',
            background: '#e9ecef', borderRadius: '4px', fontSize: '0.85em',
            fontFamily: 'monospace', textAlign: 'center', fontWeight: 600,
          }}>
            {code || '?'}
          </div>
          <input
            value={descriptions[code] ?? ''}
            onChange={e => update(code, e.target.value)}
            placeholder="Descrizione…"
            style={{ ...inputStyle, flex: 1 }}
          />
        </div>
      ))}
    </div>
  );
};

// ── SyncConfirmDialog ─────────────────────────────────────────────────────────

interface Change { field: string; before: any; after: any; }

const SyncConfirmDialog: React.FC<{
  changes: Change[];
  onConfirm: () => void;
  onCancel: () => void;
}> = ({ changes, onConfirm, onCancel }) => (
  <div style={{
    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.45)',
    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999,
  }}>
    <div style={{
      background: '#fff', borderRadius: '10px', padding: '24px', maxWidth: '480px', width: '90%',
      boxShadow: '0 8px 32px rgba(0,0,0,0.18)',
    }}>
      <h3 style={{ margin: '0 0 12px 0', fontSize: '1.05em' }}>Conferma aggiornamento</h3>
      <p style={{ fontSize: '0.85em', color: '#6c757d', margin: '0 0 12px 0' }}>
        Modalità Update sovrascriverà i seguenti campi:
      </p>
      <div style={{ borderRadius: '6px', border: '1px solid #dee2e6', overflow: 'hidden', marginBottom: '16px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.83em' }}>
          <thead>
            <tr style={{ background: '#f8f9fa' }}>
              <th style={{ padding: '6px 10px', textAlign: 'left', fontWeight: 600 }}>Campo</th>
              <th style={{ padding: '6px 10px', textAlign: 'left', fontWeight: 600, color: '#dc3545' }}>Prima</th>
              <th style={{ padding: '6px 10px', textAlign: 'left', fontWeight: 600, color: '#28a745' }}>Dopo</th>
            </tr>
          </thead>
          <tbody>
            {changes.map((c, i) => (
              <tr key={i} style={{ borderTop: '1px solid #dee2e6' }}>
                <td style={{ padding: '5px 10px', fontFamily: 'monospace' }}>{c.field}</td>
                <td style={{ padding: '5px 10px', color: '#6c757d' }}>{String(c.before ?? '—')}</td>
                <td style={{ padding: '5px 10px', fontWeight: 600 }}>{String(c.after ?? '—')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
        <button onClick={onCancel} style={{ padding: '7px 16px', background: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer' }}>
          Annulla
        </button>
        <button onClick={onConfirm} style={{ padding: '7px 16px', background: '#dc3545', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold' }}>
          Procedi
        </button>
      </div>
    </div>
  </div>
);

// ── Main component ─────────────────────────────────────────────────────────────

interface SemanticFieldEditorProps {
  matrixData: MatrixFieldData;
}

const SemanticFieldEditor: React.FC<SemanticFieldEditorProps> = ({ matrixData }) => {
  const [jsonData, setJsonData] = useState<FieldSemanticData | null>(null);
  const [draft, setDraft] = useState<FieldSemanticData | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMode, setSyncMode] = useState<'append' | 'update'>('append');
  const [status, setStatus] = useState<{ type: 'success' | 'error' | 'info' | null; msg: string }>({ type: null, msg: '' });
  const [confirmChanges, setConfirmChanges] = useState<Change[] | null>(null);
  const [pendingSyncDir, setPendingSyncDir] = useState<'matrix_to_json' | 'json_to_matrix' | null>(null);
  const [lastSaved, setLastSaved] = useState<string | null>(null);

  const isDirty = draft !== null && JSON.stringify(draft) !== JSON.stringify(jsonData);

  const showStatus = (type: 'success' | 'error' | 'info', msg: string) => {
    setStatus({ type, msg });
    setTimeout(() => setStatus({ type: null, msg: '' }), 5000);
  };

  const loadSemantic = useCallback(async () => {
    setLoading(true);
    try {
      const data = await EuringAPI.getFieldSemantic(matrixData.fieldName, matrixData.version);
      const sem: FieldSemanticData = {
        valid_values_type: data.valid_values_type ?? null,
        valid_values: data.valid_values ?? null,
        valid_values_descriptions: data.valid_values_descriptions ?? null,
        valid_values_source: data.valid_values_source ?? null,
        valid_values_lookup_tool: data.valid_values_lookup_tool ?? null,
        valid_values_range: data.valid_values_range ?? null,
        description: data.description ?? null,
      };
      setJsonData(sem);
      setDraft(JSON.parse(JSON.stringify(sem)));
    } catch (e: any) {
      showStatus('error', `Errore caricamento: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [matrixData.fieldName, matrixData.version]);

  useEffect(() => {
    loadSemantic();
  }, [loadSemantic]);

  const updateDraft = (patch: Partial<FieldSemanticData>) => {
    setDraft(prev => prev ? { ...prev, ...patch } : prev);
  };

  const handleSave = async () => {
    if (!draft) return;
    setSaving(true);
    try {
      await EuringAPI.updateFieldSemantic(matrixData.fieldName, matrixData.version, {
        valid_values_type: draft.valid_values_type,
        valid_values: draft.valid_values,
        valid_values_descriptions: draft.valid_values_descriptions,
        valid_values_source: draft.valid_values_source,
        valid_values_lookup_tool: draft.valid_values_lookup_tool,
        valid_values_range: draft.valid_values_range,
        description: draft.description,
      });

      try {
        await EuringAPI.reloadEuringData();
      } catch {
        showStatus('info', 'Salvataggio completato. Riavvia ECES per applicare: sudo systemctl restart eces');
        setSaving(false);
        return;
      }

      const newSnapshot = JSON.parse(JSON.stringify(draft));
      setJsonData(newSnapshot);
      setLastSaved(new Date().toLocaleString('it-IT'));
      showStatus('success', '✅ Salvato e ricaricato');
    } catch (e: any) {
      showStatus('error', `Errore salvataggio: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleRestore = () => {
    if (jsonData) setDraft(JSON.parse(JSON.stringify(jsonData)));
  };

  const initiateSync = (dir: 'matrix_to_json' | 'json_to_matrix') => {
    if (isDirty) {
      showStatus('info', 'Salva le modifiche prima di sincronizzare');
      return;
    }
    setPendingSyncDir(dir);
    if (syncMode === 'update') {
      // Preview changes first via API call, then show dialog
      performSync(dir, true);
    } else {
      performSync(dir, false);
    }
  };

  const performSync = async (dir: 'matrix_to_json' | 'json_to_matrix', previewOnly: boolean) => {
    setSyncing(true);
    try {
      const result = await EuringAPI.syncFieldSemantic(
        matrixData.fieldName, dir, previewOnly ? 'update' : syncMode, matrixData.version
      );
      if (previewOnly && result.changes?.length > 0) {
        setConfirmChanges(result.changes);
        setSyncing(false);
        return;
      }
      if (previewOnly && (!result.changes || result.changes.length === 0)) {
        showStatus('info', 'Nessuna modifica da applicare');
        setSyncing(false);
        setPendingSyncDir(null);
        return;
      }
      await loadSemantic();
      showStatus('success', `✅ Sincronizzazione completata (${result.changes?.length ?? 0} campi aggiornati)`);
      setPendingSyncDir(null);
    } catch (e: any) {
      showStatus('error', `Errore sync: ${e.message}`);
    } finally {
      setSyncing(false);
    }
  };

  const confirmSync = async () => {
    setConfirmChanges(null);
    if (pendingSyncDir) await performSync(pendingSyncDir, false);
  };

  if (loading) return <div style={{ padding: '20px', color: '#666', textAlign: 'center' }}>Caricamento dati semantici…</div>;
  if (!draft) return <div style={{ padding: '20px', color: '#dc3545' }}>Errore nel caricamento dei dati</div>;

  const vvt = draft.valid_values_type;
  const showEnumeration = vvt === 'enumeration';
  const showExternal = vvt === 'external_reference';
  const showRange = vvt === 'free_numeric';

  return (
    <div className="sem-editor">

      {/* Status bar */}
      {status.type && (
        <div className={`sem-status sem-status--${status.type}`}>{status.msg}</div>
      )}

      {/* Two-column layout */}
      <div className="sem-columns">

        {/* Left: matrix structural data */}
        <div className="sem-col sem-col--matrix">
          <div className="sem-col-header">Definizione Matrice</div>
          <ReadOnlyField label="Posizione" value={matrixData.position} />
          <ReadOnlyField label="Data Type" value={matrixData.data_type} />
          <ReadOnlyField label="Lunghezza" value={matrixData.length} />
          <ReadOnlyField label="Dominio Semantico" value={matrixData.semantic_domain} />
          <ReadOnlyField label="Significato Semantico" value={matrixData.semantic_meaning} />
          <ReadOnlyField label="Descrizione Strutturale" value={matrixData.description} />
          {matrixData.evolution_notes && matrixData.evolution_notes.length > 0 && (
            <div style={{ marginBottom: '10px' }}>
              <SectionLabel>Note Evoluzione</SectionLabel>
              {matrixData.evolution_notes.map((n, i) => (
                <div key={i} style={{ fontSize: '0.82em', color: '#495057', marginBottom: '3px' }}>• {n}</div>
              ))}
            </div>
          )}
        </div>

        {/* Right: JSON semantic editor */}
        <div className="sem-col sem-col--json">
          <div className="sem-col-header">JSON Semantico{isDirty && <span className="sem-dirty-dot" title="Modifiche non salvate" />}</div>

          {/* valid_values_type */}
          <div style={{ marginBottom: '10px' }}>
            <SectionLabel>Tipo Valori (valid_values_type)</SectionLabel>
            <select
              value={draft.valid_values_type ?? ''}
              onChange={e => updateDraft({ valid_values_type: e.target.value || null })}
              style={inputStyle}
            >
              <option value="">— non specificato —</option>
              {VALID_VALUES_TYPES.map(t => <option key={t.value} value={t.value}>{t.label}</option>)}
            </select>
          </div>

          {/* enumeration fields */}
          {showEnumeration && (
            <>
              <div style={{ marginBottom: '10px' }}>
                <SectionLabel>Valori Ammessi (valid_values)</SectionLabel>
                <ValidValuesList
                  values={draft.valid_values ?? []}
                  onChange={vals => updateDraft({ valid_values: vals.length ? vals : null })}
                />
              </div>
              <div style={{ marginBottom: '10px' }}>
                <SectionLabel>Descrizioni (valid_values_descriptions)</SectionLabel>
                <ValidValuesDescriptions
                  values={draft.valid_values ?? []}
                  descriptions={draft.valid_values_descriptions ?? {}}
                  onChange={d => updateDraft({ valid_values_descriptions: Object.keys(d).length ? d : null })}
                />
              </div>
            </>
          )}

          {/* external_reference fields */}
          {showExternal && (
            <>
              <div style={{ marginBottom: '10px' }}>
                <SectionLabel>Fonte Esterna (valid_values_source)</SectionLabel>
                <input
                  value={draft.valid_values_source ?? ''}
                  onChange={e => updateDraft({ valid_values_source: e.target.value || null })}
                  placeholder="es. EURING Species List 2024"
                  style={inputStyle}
                />
              </div>
              <div style={{ marginBottom: '10px' }}>
                <SectionLabel>Lookup Tool</SectionLabel>
                <input
                  value={draft.valid_values_lookup_tool ?? ''}
                  onChange={e => updateDraft({ valid_values_lookup_tool: e.target.value || null })}
                  placeholder="es. /api/euring/species"
                  style={inputStyle}
                />
              </div>
            </>
          )}

          {/* free_numeric fields */}
          {showRange && (
            <div style={{ marginBottom: '10px' }}>
              <SectionLabel>Range Numerico (valid_values_range)</SectionLabel>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                {(['min', 'max', 'unit', 'precision'] as const).map(k => (
                  <div key={k}>
                    <div style={{ fontSize: '0.72em', color: '#6c757d', marginBottom: '2px' }}>{k}</div>
                    <input
                      value={(draft.valid_values_range?.[k] ?? '') as string}
                      onChange={e => {
                        const val = e.target.value;
                        const rng = { ...(draft.valid_values_range ?? {}) };
                        if (val === '') delete rng[k];
                        else rng[k] = k === 'unit' ? val : Number(val);
                        updateDraft({ valid_values_range: Object.keys(rng).length ? rng : null });
                      }}
                      type={k === 'unit' ? 'text' : 'number'}
                      placeholder={k}
                      style={inputStyle}
                    />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* description (semantic) */}
          <div style={{ marginBottom: '10px' }}>
            <SectionLabel>Descrizione Semantica</SectionLabel>
            <textarea
              value={draft.description ?? ''}
              rows={3}
              onChange={e => updateDraft({ description: e.target.value || null })}
              style={inputStyle}
            />
          </div>
        </div>
      </div>

      {/* Sync mode selector + action bar */}
      <div className="sem-footer">
        <div className="sem-sync-mode">
          <label className="sem-radio">
            <input type="radio" checked={syncMode === 'append'} onChange={() => setSyncMode('append')} />
            <span>Append</span>
          </label>
          <label className="sem-radio">
            <input type="radio" checked={syncMode === 'update'} onChange={() => setSyncMode('update')} />
            <span>Update</span>
          </label>
          {syncMode === 'update' && (
            <span className="sem-update-warning">⚠ Update sovrascrive i dati esistenti</span>
          )}
        </div>

        <div className="sem-actions">
          <button
            onClick={() => initiateSync('json_to_matrix')}
            disabled={syncing || saving}
            className="sem-btn sem-btn--sync"
            title="JSON → Matrice"
          >
            {syncing && pendingSyncDir === 'json_to_matrix' ? '…' : '← JSON aggiorna Matrice'}
          </button>
          <button
            onClick={() => initiateSync('matrix_to_json')}
            disabled={syncing || saving}
            className="sem-btn sem-btn--sync"
            title="Matrice → JSON"
          >
            {syncing && pendingSyncDir === 'matrix_to_json' ? '…' : 'Matrice aggiorna JSON →'}
          </button>
          <button
            onClick={handleSave}
            disabled={saving || !isDirty}
            className={`sem-btn sem-btn--save${isDirty ? ' sem-btn--dirty' : ''}`}
          >
            {saving ? 'Salvataggio…' : 'Salva'}
          </button>
          <button
            onClick={handleRestore}
            disabled={!isDirty}
            className="sem-btn sem-btn--restore"
          >
            Ripristina
          </button>
        </div>

        {lastSaved && (
          <div className="sem-meta">
            Aggiornato: {lastSaved}
          </div>
        )}
      </div>

      {/* Confirm dialog for Update mode */}
      {confirmChanges !== null && (
        <SyncConfirmDialog
          changes={confirmChanges}
          onConfirm={confirmSync}
          onCancel={() => { setConfirmChanges(null); setPendingSyncDir(null); }}
        />
      )}
    </div>
  );
};

export default SemanticFieldEditor;
