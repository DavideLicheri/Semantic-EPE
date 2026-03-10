import React, { useState, useEffect, useMemo } from 'react';
import EuringAPI from '../services/api';
import PositionalMatrix from './PositionalMatrix';

// ── Types ──────────────────────────────────────────────────────────────────────

interface FieldInfo {
  position: number;
  name: string;
  data_type: string;
  length: number;
  description: string;
  valid_values: string[];
  valid_values_count?: number;
  semantic_domain?: string;
  canonical_name?: string;
}

interface FieldRow {
  field_name: string;
  description: string;
  semantic_meaning: string;
  epe_order: number;
  versions: Record<string, FieldInfo | null>;
}

interface MatrixData {
  success: boolean;
  versions_metadata: unknown[];
  field_matrix: FieldRow[];
}

interface LookupValue {
  code: string;
  meaning: string;
}

interface EditState {
  fieldName: string;
  version: string;
  fieldInfo: FieldInfo;
  // editable copies
  description: string;
  semanticMeaning: string;
  canonicalName: string;
  dataType: string;
  semanticDomain: string;
  position: number;
  length: number;
  lookupValues: LookupValue[];
  lookupLoaded: boolean;
}

// ── Constants ──────────────────────────────────────────────────────────────────

const VERSIONS = ['1966', '1979', '2000', '2020'];

const SEMANTIC_DOMAINS = [
  { value: '', label: '— nessuno —' },
  { value: 'identification_marking', label: 'Identificazione / Marcatura' },
  { value: 'species', label: 'Specie' },
  { value: 'demographics', label: 'Dati demografici' },
  { value: 'temporal', label: 'Temporale' },
  { value: 'spatial', label: 'Spaziale' },
  { value: 'biometrics', label: 'Biometria' },
  { value: 'methodology', label: 'Metodologia' },
];

const DATA_TYPES = ['string', 'integer', 'float', 'alphanumeric', 'numeric'];

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  border: '1px solid #ced4da',
  borderRadius: '6px',
  fontSize: '0.9em',
  boxSizing: 'border-box',
  fontFamily: 'inherit',
};

// ── Helper components ──────────────────────────────────────────────────────────

const FormField: React.FC<{ label: string; children: React.ReactNode }> = ({ label, children }) => (
  <div>
    <label style={{
      display: 'block', marginBottom: '5px', fontSize: '0.75em',
      fontWeight: '600', color: '#495057', textTransform: 'uppercase', letterSpacing: '0.5px',
    }}>
      {label}
    </label>
    {children}
  </div>
);

// ── Main component ─────────────────────────────────────────────────────────────

interface PositionalMatrixEditorProps {
  currentUser?: { role: string } | null;
}

const PositionalMatrixEditor: React.FC<PositionalMatrixEditorProps> = ({ currentUser }) => {
  const [matrixData, setMatrixData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVersions, setSelectedVersions] = useState<string[]>(['2000', '2020']);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [saveStatus, setSaveStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({ type: null, message: '' });
  const [saving, setSaving] = useState(false);
  const [showAddField, setShowAddField] = useState(false);
  const [newField, setNewField] = useState({ name: '', position: 1, length: 1, dataType: 'string', description: '', version: '2000' });

  const canEdit = currentUser?.role === 'matrix_editor' || currentUser?.role === 'super_admin';
  const [confirmDelete, setConfirmDelete] = useState<{ fieldName: string; version: string } | null>(null);

  // ── Data fetching ────────────────────────────────────────────────────────────

  const loadMatrix = async () => {
    try {
      setLoading(true);
      const data = await EuringAPI.getEuringVersionsMatrix();
      setMatrixData(data);
    } catch (e) {
      console.error('Failed to load matrix:', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadMatrix(); }, []);

  const loadLookup = async (fieldName: string, version: string) => {
    try {
      const result = await EuringAPI.getFieldLookupTable(fieldName, version);
      if (result?.success && result.lookup_table?.values) {
        setEditState(prev => prev ? { ...prev, lookupValues: result.lookup_table.values, lookupLoaded: true } : prev);
      } else {
        setEditState(prev => prev ? { ...prev, lookupLoaded: true } : prev);
      }
    } catch {
      setEditState(prev => prev ? { ...prev, lookupLoaded: true } : prev);
    }
  };

  // ── Conflict detection (client-side) ────────────────────────────────────────

  const checkConflicts = (version: string, excludeFieldName: string, pos: number, len: number): string[] => {
    if (!matrixData || pos < 1 || len < 1) return [];
    const range = new Set(Array.from({ length: len }, (_, i) => pos + i));
    const conflicts: string[] = [];
    for (const row of matrixData.field_matrix) {
      const info = row.versions[version];
      if (!info || info.name === excludeFieldName) continue;
      for (let p = info.position; p < info.position + info.length; p++) {
        if (range.has(p)) { conflicts.push(info.name); break; }
      }
    }
    return conflicts;
  };

  const positionConflicts = useMemo(() => {
    if (!editState) return [];
    return checkConflicts(editState.version, editState.fieldName, editState.position, editState.length);
  }, [editState?.position, editState?.length, editState?.version, editState?.fieldName, matrixData]);

  const newFieldConflicts = useMemo(() => {
    if (!showAddField) return [];
    return checkConflicts(newField.version, newField.name, newField.position, newField.length);
  }, [showAddField, newField.version, newField.name, newField.position, newField.length, matrixData]);

  // ── Related fields (same canonical_name) ────────────────────────────────────

  const relatedFields = useMemo(() => {
    if (!editState?.canonicalName?.trim() || !matrixData) return [];
    const cn = editState.canonicalName.trim();
    const related: { ver: string; name: string }[] = [];
    for (const row of matrixData.field_matrix) {
      for (const [ver, info] of Object.entries(row.versions)) {
        if (!info) continue;
        if (info.canonical_name === cn && !(ver === editState.version && info.name === editState.fieldName)) {
          related.push({ ver, name: info.name });
        }
      }
    }
    return related;
  }, [editState?.canonicalName, matrixData]);

  // ── Handlers ─────────────────────────────────────────────────────────────────

  const showStatus = (type: 'success' | 'error', msg: string) => {
    setSaveStatus({ type, message: msg });
    setTimeout(() => setSaveStatus({ type: null, message: '' }), 5000);
  };

  const handleEditProperty = (fieldName: string, version: string, _property: string, _currentValue: string) => {
    if (!matrixData) return;
    const row = matrixData.field_matrix.find(r => r.field_name === fieldName);
    const info = row?.versions[version];
    if (!info) return;

    const state: EditState = {
      fieldName,
      version,
      fieldInfo: info,
      description: info.description || '',
      semanticMeaning: row?.semantic_meaning || '',
      canonicalName: info.canonical_name || '',
      dataType: info.data_type || 'string',
      semanticDomain: info.semantic_domain || '',
      position: info.position,
      length: info.length,
      lookupValues: [],
      lookupLoaded: false,
    };
    setEditState(state);
    setShowAddField(false);
    loadLookup(fieldName, version);
  };

  const saveProperty = async (property: string, value: string) => {
    if (!editState) return;
    const result = await EuringAPI.updateMatrixField(
      editState.fieldName, editState.version, property, value,
      `Edit via PositionalMatrixEditor at ${new Date().toISOString()}`
    );
    if (!result.success) throw new Error(result.error || 'Errore sconosciuto');
  };

  const handleSaveAll = async () => {
    if (!editState || !canEdit) return;
    if (positionConflicts.length > 0) {
      showStatus('error', `Conflitto di posizione con: ${positionConflicts.join(', ')}`);
      return;
    }
    setSaving(true);
    try {
      const orig = editState.fieldInfo;
      const row = matrixData?.field_matrix.find(r => r.field_name === editState.fieldName);
      const saves: Promise<void>[] = [];

      if (editState.description !== (orig.description || ''))
        saves.push(saveProperty('description', editState.description));
      if (editState.dataType !== (orig.data_type || ''))
        saves.push(saveProperty('data_type', editState.dataType));
      if (editState.semanticDomain !== (orig.semantic_domain || ''))
        saves.push(saveProperty('semantic_domain', editState.semanticDomain));
      if (editState.canonicalName !== (orig.canonical_name || ''))
        saves.push(saveProperty('canonical_name', editState.canonicalName));
      if (editState.position !== orig.position)
        saves.push(saveProperty('position', String(editState.position)));
      if (editState.length !== orig.length)
        saves.push(saveProperty('length', String(editState.length)));
      if (row && editState.semanticMeaning !== (row.semantic_meaning || ''))
        saves.push(saveProperty('semantic_meaning', editState.semanticMeaning));

      await Promise.all(saves);

      // Save lookup values
      if (editState.lookupLoaded && editState.lookupValues.length > 0) {
        const lookupData = {
          name: `${editState.fieldName} Values`,
          description: `Valid values for ${editState.fieldName}`,
          values: editState.lookupValues.filter(lv => lv.code.trim()),
        };
        await EuringAPI.updateFieldLookupTable(editState.fieldName, editState.version, lookupData);
      }

      showStatus('success', `✅ Campo "${editState.fieldName}" salvato`);
      await loadMatrix();
      // Update editState to reflect new saved values
      setEditState(prev => prev ? { ...prev, fieldInfo: { ...prev.fieldInfo, ...{ description: prev.description, data_type: prev.dataType, semantic_domain: prev.semanticDomain as any, canonical_name: prev.canonicalName, position: prev.position, length: prev.length } } } : prev);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Errore nel salvataggio';
      showStatus('error', `Errore: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  const handleAddField = async () => {
    if (newFieldConflicts.length > 0 || !newField.name.trim()) return;
    setSaving(true);
    try {
      const result = await EuringAPI.addFieldToVersion(
        newField.name.trim(), newField.version, newField.position,
        newField.dataType, newField.length, newField.description
      );
      if (!result.success) throw new Error(result.error || 'Errore');
      showStatus('success', `✅ Campo "${newField.name}" aggiunto alla versione ${newField.version}`);
      setShowAddField(false);
      setNewField({ name: '', position: 1, length: 1, dataType: 'string', description: '', version: '2000' });
      await loadMatrix();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Errore';
      showStatus('error', `Errore: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteField = async () => {
    if (!confirmDelete || !canEdit) return;
    setSaving(true);
    try {
      const result = await EuringAPI.deleteFieldFromVersion(confirmDelete.fieldName, confirmDelete.version);
      if (!result.success) throw new Error(result.error || 'Errore');
      showStatus('success', `✅ Campo "${confirmDelete.fieldName}" eliminato dalla versione ${confirmDelete.version}`);
      setConfirmDelete(null);
      setEditState(null);
      await loadMatrix();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Errore';
      showStatus('error', `Errore: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  if (loading) return <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>Caricamento matrice...</div>;
  if (!matrixData) return <div style={{ padding: '40px', color: 'red' }}>Errore nel caricamento dei dati.</div>;

  const panelOpen = !!editState || showAddField;

  return (
    <div style={{ padding: '20px' }}>

      {/* ── Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.3em' }}>Editor Definizioni Campo</h2>
          <p style={{ color: '#666', margin: '4px 0 0 0', fontSize: '0.85em' }}>
            Clicca ✏️ su una proprietà nella matrice per modificarla
          </p>
        </div>
        {canEdit && (
          <button onClick={() => { setShowAddField(true); setEditState(null); }} style={{
            padding: '8px 16px', backgroundColor: '#28a745', color: 'white',
            border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold',
          }}>
            + Nuovo campo
          </button>
        )}
      </div>

      {/* ── Status bar ── */}
      {saveStatus.type && (
        <div style={{
          padding: '10px 15px', marginBottom: '15px', borderRadius: '6px',
          backgroundColor: saveStatus.type === 'success' ? '#d4edda' : '#f8d7da',
          color: saveStatus.type === 'success' ? '#155724' : '#721c24',
          border: `1px solid ${saveStatus.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
        }}>
          {saveStatus.message}
        </div>
      )}

      {/* ── Version selector ── */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px', flexWrap: 'wrap' }}>
        {VERSIONS.map(v => (
          <label key={v} style={{
            display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer',
            padding: '6px 14px', borderRadius: '20px',
            border: selectedVersions.includes(v) ? '2px solid #007bff' : '2px solid #dee2e6',
            backgroundColor: selectedVersions.includes(v) ? '#e7f0ff' : '#fff',
            fontWeight: selectedVersions.includes(v) ? '600' : 'normal',
            transition: 'all 0.15s',
          }}>
            <input type="checkbox" checked={selectedVersions.includes(v)} onChange={e => {
              if (e.target.checked) setSelectedVersions(prev => [...prev, v]);
              else setSelectedVersions(prev => prev.filter(x => x !== v));
            }} style={{ display: 'none' }} />
            EURING {v}
          </label>
        ))}
      </div>

      {/* ── Main layout ── */}
      <div style={{ display: 'flex', gap: '20px', alignItems: 'flex-start' }}>

        {/* Matrix */}
        <div style={{ flex: panelOpen ? '0 0 55%' : '1', maxWidth: panelOpen ? '55%' : '100%', minWidth: 0, overflow: 'auto' }}>
          <PositionalMatrix
            fieldMatrix={matrixData.field_matrix ?? []}
            selectedVersions={selectedVersions}
            editMode={canEdit}
            onEditProperty={canEdit ? handleEditProperty : undefined}
          />
        </div>

        {/* ── Edit panel ── */}
        {editState && (
          <div style={{
            flex: '1', minWidth: '350px', maxWidth: '420px',
            backgroundColor: '#fff', border: '2px solid #007bff', borderRadius: '10px',
            padding: '20px', position: 'sticky', top: '20px', maxHeight: '90vh', overflowY: 'auto',
          }}>
            {/* Field header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', paddingBottom: '12px', borderBottom: '2px solid #e9ecef' }}>
              <div>
                <span style={{ fontWeight: 'bold', fontSize: '1.05em' }}>{editState.fieldName}</span>
                <span style={{ marginLeft: '8px', padding: '3px 10px', backgroundColor: '#e9ecef', borderRadius: '12px', fontSize: '0.8em', color: '#555' }}>
                  EURING {editState.version}
                </span>
              </div>
              <button onClick={() => setEditState(null)} style={{ background: '#6c757d', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', padding: '4px 10px' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

              {/* Description */}
              <FormField label="Descrizione">
                <textarea value={editState.description} rows={3}
                  onChange={e => setEditState(p => p ? { ...p, description: e.target.value } : p)}
                  style={inputStyle} />
              </FormField>

              {/* Semantic meaning */}
              <FormField label="Significato semantico">
                <input value={editState.semanticMeaning}
                  onChange={e => setEditState(p => p ? { ...p, semanticMeaning: e.target.value } : p)}
                  style={inputStyle} />
              </FormField>

              {/* Canonical name */}
              <FormField label="Nome canonico (cross-versione)">
                <input value={editState.canonicalName} placeholder="es. geographic_location"
                  onChange={e => setEditState(p => p ? { ...p, canonicalName: e.target.value } : p)}
                  style={inputStyle} />
                {relatedFields.length > 0 && (
                  <div style={{ marginTop: '5px', fontSize: '0.8em', color: '#0062cc', backgroundColor: '#e7f0ff', padding: '5px 8px', borderRadius: '4px' }}>
                    Stesso campo: {relatedFields.map(f => `${f.name} (${f.ver})`).join(' • ')}
                  </div>
                )}
              </FormField>

              {/* Semantic domain */}
              <FormField label="Dominio semantico">
                <select value={editState.semanticDomain}
                  onChange={e => setEditState(p => p ? { ...p, semanticDomain: e.target.value } : p)}
                  style={inputStyle}>
                  {SEMANTIC_DOMAINS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
                </select>
              </FormField>

              {/* Data type */}
              <FormField label="Tipo dato">
                <select value={editState.dataType}
                  onChange={e => setEditState(p => p ? { ...p, dataType: e.target.value } : p)}
                  style={inputStyle}>
                  {DATA_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </FormField>

              {/* Position + length */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <FormField label="Posizione">
                  <input type="number" min={1} value={editState.position}
                    onChange={e => setEditState(p => p ? { ...p, position: Math.max(1, parseInt(e.target.value) || 1) } : p)}
                    style={inputStyle} />
                </FormField>
                <FormField label="Lunghezza">
                  <input type="number" min={1} value={editState.length}
                    onChange={e => setEditState(p => p ? { ...p, length: Math.max(1, parseInt(e.target.value) || 1) } : p)}
                    style={inputStyle} />
                </FormField>
              </div>
              {positionConflicts.length > 0 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  ⚠ Conflitto posizione con: {positionConflicts.join(', ')}
                </div>
              )}
              {editState && editState.length > 100 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  ⚠ Lunghezza insolitamente grande ({editState.length} caratteri) — verifica che sia corretto
                </div>
              )}
              {editState && (editState.position + editState.length - 1) > 300 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  ⚠ Il campo supera la posizione 300 — verifica posizione e lunghezza
                </div>
              )}

              {/* Lookup values */}
              <FormField label="Valori validi (codice → significato)">
                {!editState.lookupLoaded ? (
                  <div style={{ color: '#666', fontSize: '0.85em', padding: '8px' }}>Caricamento valori...</div>
                ) : (
                  <div>
                    {editState.lookupValues.map((lv, idx) => (
                      <div key={idx} style={{ display: 'flex', gap: '6px', marginBottom: '5px', alignItems: 'center' }}>
                        <input value={lv.code} placeholder="Cod"
                          onChange={e => {
                            const vals = [...editState.lookupValues];
                            vals[idx] = { ...vals[idx], code: e.target.value };
                            setEditState(p => p ? { ...p, lookupValues: vals } : p);
                          }}
                          style={{ ...inputStyle, width: '75px', flexShrink: 0 }} />
                        <input value={lv.meaning} placeholder="Significato"
                          onChange={e => {
                            const vals = [...editState.lookupValues];
                            vals[idx] = { ...vals[idx], meaning: e.target.value };
                            setEditState(p => p ? { ...p, lookupValues: vals } : p);
                          }}
                          style={{ ...inputStyle, flex: 1 }} />
                        <button onClick={() => {
                          const vals = editState.lookupValues.filter((_, i) => i !== idx);
                          setEditState(p => p ? { ...p, lookupValues: vals } : p);
                        }} style={{ background: '#dc3545', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', padding: '5px 8px', flexShrink: 0 }}>✕</button>
                      </div>
                    ))}
                    <button
                      onClick={() => setEditState(p => p ? { ...p, lookupValues: [...p.lookupValues, { code: '', meaning: '' }] } : p)}
                      style={{ padding: '5px 12px', backgroundColor: '#e9ecef', border: '1px solid #ced4da', borderRadius: '4px', cursor: 'pointer', fontSize: '0.85em', marginTop: '4px' }}>
                      + Aggiungi codice
                    </button>
                  </div>
                )}
              </FormField>
            </div>

            {/* Save / cancel */}
            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <button onClick={handleSaveAll}
                disabled={saving || positionConflicts.length > 0}
                style={{
                  flex: 1, padding: '10px', fontWeight: 'bold', fontSize: '1em',
                  backgroundColor: positionConflicts.length > 0 ? '#adb5bd' : '#007bff',
                  color: 'white', border: 'none', borderRadius: '6px',
                  cursor: saving || positionConflicts.length > 0 ? 'not-allowed' : 'pointer',
                }}>
                {saving ? 'Salvataggio...' : '💾 Salva tutto'}
              </button>
              <button onClick={() => setEditState(null)} style={{ padding: '10px 16px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer' }}>
                Annulla
              </button>
            </div>

            {/* Delete field */}
            {canEdit && editState && (
              <div style={{ marginTop: '12px', borderTop: '1px solid #f1f1f1', paddingTop: '12px' }}>
                {confirmDelete?.fieldName === editState.fieldName && confirmDelete?.version === editState.version ? (
                  <div style={{ backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', borderRadius: '6px', padding: '10px 12px' }}>
                    <p style={{ margin: '0 0 10px 0', fontSize: '0.85em', color: '#721c24', fontWeight: 'bold' }}>
                      ⚠ Eliminare "{editState.fieldName}" dalla versione EURING {editState.version}?
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={handleDeleteField} disabled={saving}
                        style={{ padding: '6px 14px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.85em' }}>
                        {saving ? 'Eliminazione...' : 'Sì, elimina'}
                      </button>
                      <button onClick={() => setConfirmDelete(null)}
                        style={{ padding: '6px 14px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '5px', cursor: 'pointer', fontSize: '0.85em' }}>
                        Annulla
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmDelete({ fieldName: editState.fieldName, version: editState.version })}
                    style={{ width: '100%', padding: '7px', backgroundColor: 'transparent', color: '#dc3545', border: '1px solid #dc3545', borderRadius: '6px', cursor: 'pointer', fontSize: '0.82em' }}>
                    🗑 Elimina questo campo dalla versione {editState.version}
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {/* ── Add field panel ── */}
        {showAddField && !editState && (
          <div style={{
            flex: '1', minWidth: '350px', maxWidth: '420px',
            backgroundColor: '#fff', border: '2px solid #28a745', borderRadius: '10px',
            padding: '20px', position: 'sticky', top: '20px',
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', paddingBottom: '12px', borderBottom: '2px solid #e9ecef' }}>
              <span style={{ fontWeight: 'bold', fontSize: '1.05em' }}>+ Nuovo campo</span>
              <button onClick={() => setShowAddField(false)} style={{ background: '#6c757d', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', padding: '4px 10px' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <FormField label="Versione">
                <select value={newField.version}
                  onChange={e => setNewField(p => ({ ...p, version: e.target.value }))}
                  style={inputStyle}>
                  {VERSIONS.map(v => <option key={v} value={v}>EURING {v}</option>)}
                </select>
              </FormField>

              <FormField label="Nome campo">
                <input value={newField.name} placeholder="es. wing_length_measured"
                  onChange={e => setNewField(p => ({ ...p, name: e.target.value }))}
                  style={inputStyle} />
              </FormField>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <FormField label="Posizione">
                  <input type="number" min={1} value={newField.position}
                    onChange={e => setNewField(p => ({ ...p, position: Math.max(1, parseInt(e.target.value) || 1) }))}
                    style={inputStyle} />
                </FormField>
                <FormField label="Lunghezza">
                  <input type="number" min={1} value={newField.length}
                    onChange={e => setNewField(p => ({ ...p, length: Math.max(1, parseInt(e.target.value) || 1) }))}
                    style={inputStyle} />
                </FormField>
              </div>

              {newFieldConflicts.length > 0 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', borderRadius: '6px', color: '#721c24', fontSize: '0.85em' }}>
                  ⚠ Posizioni {newField.position}–{newField.position + newField.length - 1} già occupate da: {newFieldConflicts.join(', ')}
                </div>
              )}
              {newFieldConflicts.length === 0 && newField.name && (
                <div style={{ padding: '6px 12px', backgroundColor: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '6px', color: '#155724', fontSize: '0.85em' }}>
                  ✓ Posizioni {newField.position}–{newField.position + newField.length - 1} libere
                </div>
              )}
              {newField.length > 100 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  ⚠ Lunghezza insolitamente grande ({newField.length} caratteri) — verifica che sia corretto
                </div>
              )}
              {(newField.position + newField.length - 1) > 300 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  ⚠ Il campo supera la posizione 300 — verifica posizione e lunghezza
                </div>
              )}

              <FormField label="Tipo dato">
                <select value={newField.dataType}
                  onChange={e => setNewField(p => ({ ...p, dataType: e.target.value }))}
                  style={inputStyle}>
                  {DATA_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </FormField>

              <FormField label="Descrizione">
                <textarea value={newField.description} rows={2} placeholder="Descrizione del nuovo campo"
                  onChange={e => setNewField(p => ({ ...p, description: e.target.value }))}
                  style={inputStyle} />
              </FormField>
            </div>

            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <button onClick={handleAddField}
                disabled={saving || newFieldConflicts.length > 0 || !newField.name.trim()}
                style={{
                  flex: 1, padding: '10px', fontWeight: 'bold',
                  backgroundColor: newFieldConflicts.length > 0 || !newField.name.trim() ? '#adb5bd' : '#28a745',
                  color: 'white', border: 'none', borderRadius: '6px',
                  cursor: saving || newFieldConflicts.length > 0 || !newField.name.trim() ? 'not-allowed' : 'pointer',
                }}>
                {saving ? 'Aggiunta...' : '+ Aggiungi campo'}
              </button>
              <button onClick={() => setShowAddField(false)} style={{ padding: '10px 16px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer' }}>
                Annulla
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PositionalMatrixEditor;
