import React, { useState, useEffect, useMemo } from 'react';
import EuringAPI from '../services/api';
import PositionalMatrix from './PositionalMatrix';
import { useTranslation } from '../hooks/useTranslation';
import SemanticFieldEditor from './semantic/SemanticFieldEditor';

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

const PIPE_DELIMITED_VERSIONS = ['2020'];
const isPipeDelimited = (v: string) => PIPE_DELIMITED_VERSIONS.includes(v);

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
  const { t } = useTranslation();
  const [matrixData, setMatrixData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedVersions, setSelectedVersions] = useState<string[]>(['2000', '2020']);
  const [editState, setEditState] = useState<EditState | null>(null);
  const [activeTab, setActiveTab] = useState<'struttura' | 'semantica' | 'storia'>('struttura');
  const [saveStatus, setSaveStatus] = useState<{ type: 'success' | 'error' | null; message: string }>({ type: null, message: '' });
  const [saving, setSaving] = useState(false);
  const savingRef = React.useRef(false);
  const [showAddField, setShowAddField] = useState(false);
  const [newField, setNewField] = useState({ name: '', position: 1, length: 1, dataType: 'string', description: '', version: '2000' });

  const canEdit = currentUser?.role === 'matrix_editor' || currentUser?.role === 'super_admin';
  const [confirmDelete, setConfirmDelete] = useState<{ fieldName: string; version: string } | null>(null);

  // Semantic domains — translated labels
  const SEMANTIC_DOMAINS = [
    { value: '', label: t('editor.semantic_domain.none') },
    { value: 'identification_marking', label: t('editor.semantic_domain.identification_marking') },
    { value: 'species', label: t('editor.semantic_domain.species') },
    { value: 'demographics', label: t('editor.semantic_domain.demographics') },
    { value: 'temporal', label: t('editor.semantic_domain.temporal') },
    { value: 'spatial', label: t('editor.semantic_domain.spatial') },
    { value: 'biometrics', label: t('editor.semantic_domain.biometrics') },
    { value: 'methodology', label: t('editor.semantic_domain.methodology') },
  ];

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

  // ── Conflict detection ────────────────────────────────────────────────────────

  const checkConflicts = (version: string, excludeFieldName: string, pos: number, len: number): string[] => {
    if (!matrixData || pos < 1) return [];
    const conflicts: string[] = [];

    if (isPipeDelimited(version)) {
      for (const row of matrixData.field_matrix) {
        const info = row.versions[version];
        if (!info || info.name === excludeFieldName) continue;
        if (info.position === pos) { conflicts.push(info.name); }
      }
    } else {
      if (len < 1) return [];
      const range = new Set(Array.from({ length: len }, (_, i) => pos + i));
      for (const row of matrixData.field_matrix) {
        const info = row.versions[version];
        if (!info || info.name === excludeFieldName) continue;
        for (let p = info.position; p < info.position + info.length; p++) {
          if (range.has(p)) { conflicts.push(info.name); break; }
        }
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

  // ── Related fields ────────────────────────────────────────────────────────────

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
    setActiveTab('struttura');
    setShowAddField(false);
    loadLookup(fieldName, version);
  };

  const saveProperty = async (property: string, value: string) => {
    if (!editState) return;
    const result = await EuringAPI.updateMatrixField(
      editState.fieldName, editState.version, property, value,
      `Edit via PositionalMatrixEditor at ${new Date().toISOString()}`
    );
    if (!result.success) throw new Error(result.error || 'Unknown error');
  };

  const handleSaveAll = async () => {
    if (!editState || !canEdit) return;
    if (positionConflicts.length > 0) {
      showStatus('error', `${t('editor.save_all')} — conflict: ${positionConflicts.join(', ')}`);
      return;
    }
    setSaving(true);
    try {
      const orig = editState.fieldInfo;
      const row = matrixData?.field_matrix.find(r => r.field_name === editState.fieldName);
      const saves: { label: string; promise: Promise<void> }[] = [];

      if (editState.description !== (orig.description || ''))
        saves.push({ label: 'description', promise: saveProperty('description', editState.description) });
      if (editState.dataType !== (orig.data_type || ''))
        saves.push({ label: 'data_type', promise: saveProperty('data_type', editState.dataType) });
      if (editState.semanticDomain !== (orig.semantic_domain || ''))
        saves.push({ label: 'semantic_domain', promise: saveProperty('semantic_domain', editState.semanticDomain) });
      if (editState.canonicalName !== (orig.canonical_name || ''))
        saves.push({ label: 'canonical_name', promise: saveProperty('canonical_name', editState.canonicalName) });
      if (editState.position !== orig.position)
        saves.push({ label: 'position', promise: saveProperty('position', String(editState.position)) });
      if (editState.length !== orig.length)
        saves.push({ label: 'length', promise: saveProperty('length', String(editState.length)) });
      if (row && editState.semanticMeaning !== (row.semantic_meaning || ''))
        saves.push({ label: 'semantic_meaning', promise: saveProperty('semantic_meaning', editState.semanticMeaning) });

      const results = await Promise.allSettled(saves.map(s => s.promise));
      const failures = results
        .map((r, i) => r.status === 'rejected' ? `${saves[i].label}: ${(r.reason as Error)?.message}` : null)
        .filter(Boolean);

      if (editState.lookupLoaded && editState.lookupValues.length > 0) {
        const lookupData = {
          name: `${editState.fieldName} Values`,
          description: `Valid values for ${editState.fieldName}`,
          values: editState.lookupValues.filter(lv => lv.code.trim()),
        };
        await EuringAPI.updateFieldLookupTable(editState.fieldName, editState.version, lookupData);
      }

      await loadMatrix();
      setEditState(prev => prev ? { ...prev, fieldInfo: { ...prev.fieldInfo, ...{ description: prev.description, data_type: prev.dataType, semantic_domain: prev.semanticDomain as any, canonical_name: prev.canonicalName, position: prev.position, length: prev.length } } } : prev);

      if (failures.length > 0) {
        showStatus('error', `⚠ Partial save. Errors: ${failures.join('; ')}`);
      } else {
        showStatus('success', `✅ "${editState.fieldName}" saved`);
      }
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Save error';
      showStatus('error', `Error: ${msg}`);
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
      if (!result.success) throw new Error(result.error || 'Error');
      showStatus('success', `✅ "${newField.name}" added to version ${newField.version}`);
      setShowAddField(false);
      setNewField({ name: '', position: 1, length: 1, dataType: 'string', description: '', version: '2000' });
      await loadMatrix();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Error';
      showStatus('error', `Error: ${msg}`);
    } finally {
      setSaving(false);
    }
  };

  const handleDeleteField = async () => {
    if (!confirmDelete || !canEdit || savingRef.current) return;
    savingRef.current = true;
    setSaving(true);
    try {
      const result = await EuringAPI.deleteFieldFromVersion(confirmDelete.fieldName, confirmDelete.version);
      if (!result.success) throw new Error(result.error || 'Error');
      showStatus('success', `✅ "${confirmDelete.fieldName}" deleted from version ${confirmDelete.version}`);
      setConfirmDelete(null);
      setEditState(null);
      await loadMatrix();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : 'Error';
      showStatus('error', `Error: ${msg}`);
    } finally {
      savingRef.current = false;
      setSaving(false);
    }
  };

  // ── Render ───────────────────────────────────────────────────────────────────

  if (loading) return <div style={{ padding: '40px', textAlign: 'center', color: '#666' }}>{t('editor.loading')}</div>;
  if (!matrixData) return <div style={{ padding: '40px', color: 'red' }}>{t('editor.error')}</div>;

  const panelOpen = !!editState || showAddField;

  return (
    <div style={{ padding: '20px' }}>

      {/* ── Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.3em' }}>{t('editor.title')}</h2>
          <p style={{ color: '#666', margin: '4px 0 0 0', fontSize: '0.85em' }}>
            {t('editor.subtitle')}
          </p>
        </div>
        {canEdit && (
          <button onClick={() => { setShowAddField(true); setEditState(null); }} style={{
            padding: '8px 16px', backgroundColor: '#28a745', color: 'white',
            border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold',
          }}>
            {t('editor.new_field')}
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', paddingBottom: '10px', borderBottom: '2px solid #e9ecef' }}>
              <div>
                <span style={{ fontWeight: 'bold', fontSize: '1.05em' }}>{editState.fieldName}</span>
                <span style={{ marginLeft: '8px', padding: '3px 10px', backgroundColor: '#e9ecef', borderRadius: '12px', fontSize: '0.8em', color: '#555' }}>
                  EURING {editState.version}
                </span>
              </div>
              <button onClick={() => setEditState(null)} style={{ background: '#6c757d', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', padding: '4px 10px' }}>✕</button>
            </div>

            {/* Tab navigation */}
            <div style={{ display: 'flex', gap: '4px', marginBottom: '16px', borderBottom: '2px solid #e9ecef', paddingBottom: '0' }}>
              {(['struttura', 'semantica', 'storia'] as const).map(tab => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  style={{
                    padding: '6px 14px',
                    border: 'none',
                    borderBottom: activeTab === tab ? '2px solid #007bff' : '2px solid transparent',
                    background: 'none',
                    cursor: 'pointer',
                    fontSize: '0.85em',
                    fontWeight: activeTab === tab ? 700 : 400,
                    color: activeTab === tab ? '#007bff' : '#6c757d',
                    marginBottom: '-2px',
                    textTransform: 'capitalize',
                  }}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </div>

            {/* Semantica tab */}
            {activeTab === 'semantica' && (
              <SemanticFieldEditor matrixData={{
                fieldName: editState.fieldName,
                version: editState.version,
                position: editState.position,
                length: editState.length,
                data_type: editState.dataType,
                semantic_domain: editState.semanticDomain || undefined,
                semantic_meaning: editState.semanticMeaning || undefined,
                description: editState.description || undefined,
              }} />
            )}

            {/* Storia tab */}
            {activeTab === 'storia' && (
              <div style={{ padding: '20px', textAlign: 'center', color: '#adb5bd', fontSize: '0.9em' }}>
                La cronologia delle modifiche sarà disponibile in una versione futura.
              </div>
            )}

            {/* Struttura tab content (existing form) */}
            {activeTab === 'struttura' && <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>

              {/* Description */}
              <FormField label={t('editor.field.description')}>
                <textarea value={editState.description} rows={3}
                  onChange={e => setEditState(p => p ? { ...p, description: e.target.value } : p)}
                  style={inputStyle} />
              </FormField>

              {/* Semantic meaning */}
              <FormField label={t('editor.field.semantic_meaning')}>
                <input value={editState.semanticMeaning}
                  onChange={e => setEditState(p => p ? { ...p, semanticMeaning: e.target.value } : p)}
                  style={inputStyle} />
              </FormField>

              {/* Canonical name */}
              <FormField label={t('editor.field.canonical_name')}>
                <input value={editState.canonicalName} placeholder={t('editor.field.canonical_placeholder')}
                  onChange={e => setEditState(p => p ? { ...p, canonicalName: e.target.value } : p)}
                  style={inputStyle} />
                {relatedFields.length > 0 && (
                  <div style={{ marginTop: '5px', fontSize: '0.8em', color: '#0062cc', backgroundColor: '#e7f0ff', padding: '5px 8px', borderRadius: '4px' }}>
                    {t('editor.field.same_field')} {relatedFields.map(f => `${f.name} (${f.ver})`).join(' • ')}
                  </div>
                )}
              </FormField>

              {/* Semantic domain */}
              <FormField label={t('editor.field.semantic_domain')}>
                <select value={editState.semanticDomain}
                  onChange={e => setEditState(p => p ? { ...p, semanticDomain: e.target.value } : p)}
                  style={inputStyle}>
                  {SEMANTIC_DOMAINS.map(d => <option key={d.value} value={d.value}>{d.label}</option>)}
                </select>
              </FormField>

              {/* Data type */}
              <FormField label={t('editor.field.data_type')}>
                <select value={editState.dataType}
                  onChange={e => setEditState(p => p ? { ...p, dataType: e.target.value } : p)}
                  style={inputStyle}>
                  {DATA_TYPES.map(dt => <option key={dt} value={dt}>{dt}</option>)}
                </select>
              </FormField>

              {/* Position + length */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <FormField label={isPipeDelimited(editState.version) ? t('editor.field.field_index') : t('editor.field.position')}>
                  <input type="number" min={1} value={editState.position}
                    onChange={e => setEditState(p => p ? { ...p, position: Math.max(1, parseInt(e.target.value) || 1) } : p)}
                    style={inputStyle} />
                </FormField>
                <FormField label={isPipeDelimited(editState.version) ? t('editor.field.max_length') : t('editor.field.length')}>
                  <input type="number" min={1} value={editState.length}
                    onChange={e => setEditState(p => p ? { ...p, length: Math.max(1, parseInt(e.target.value) || 1) } : p)}
                    style={inputStyle} />
                </FormField>
              </div>
              {positionConflicts.length > 0 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  {isPipeDelimited(editState.version)
                    ? `⚠ Index ${editState.position} already used by: ${positionConflicts.join(', ')}`
                    : `⚠ Position conflict with: ${positionConflicts.join(', ')}`}
                </div>
              )}
              {editState && !isPipeDelimited(editState.version) && editState.length > 100 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  {t('editor.warn.length_large_prefix')}{editState.length} {t('editor.warn.length_large_suffix')}
                </div>
              )}
              {editState && !isPipeDelimited(editState.version) && (editState.position + editState.length - 1) > 300 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  {t('editor.warn.exceeds_300')}
                </div>
              )}

              {/* Lookup values */}
              <FormField label={t('editor.field.valid_values')}>
                {!editState.lookupLoaded ? (
                  <div style={{ color: '#666', fontSize: '0.85em', padding: '8px' }}>{t('editor.field.loading_values')}</div>
                ) : (
                  <div>
                    {editState.lookupValues.map((lv, idx) => (
                      <div key={idx} style={{ display: 'flex', gap: '6px', marginBottom: '5px', alignItems: 'center' }}>
                        <input value={lv.code} placeholder={t('editor.field.code_placeholder')}
                          onChange={e => {
                            const vals = [...editState.lookupValues];
                            vals[idx] = { ...vals[idx], code: e.target.value };
                            setEditState(p => p ? { ...p, lookupValues: vals } : p);
                          }}
                          style={{ ...inputStyle, width: '75px', flexShrink: 0 }} />
                        <input value={lv.meaning} placeholder={t('editor.field.meaning_placeholder')}
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
                      {t('editor.field.add_code')}
                    </button>
                  </div>
                )}
              </FormField>
            </div>}

            {/* Save / cancel — always visible */}
            <div style={{ marginTop: '20px', display: 'flex', gap: '10px' }}>
              <button onClick={handleSaveAll}
                disabled={saving || positionConflicts.length > 0}
                style={{
                  flex: 1, padding: '10px', fontWeight: 'bold', fontSize: '1em',
                  backgroundColor: positionConflicts.length > 0 ? '#adb5bd' : '#007bff',
                  color: 'white', border: 'none', borderRadius: '6px',
                  cursor: saving || positionConflicts.length > 0 ? 'not-allowed' : 'pointer',
                }}>
                {saving ? t('editor.saving') : t('editor.save_all')}
              </button>
              <button onClick={() => setEditState(null)} style={{ padding: '10px 16px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer' }}>
                {t('editor.cancel')}
              </button>
            </div>

            {/* Delete field */}
            {canEdit && editState && (
              <div style={{ marginTop: '12px', borderTop: '1px solid #f1f1f1', paddingTop: '12px' }}>
                {confirmDelete?.fieldName === editState.fieldName && confirmDelete?.version === editState.version ? (
                  <div style={{ backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', borderRadius: '6px', padding: '10px 12px' }}>
                    <p style={{ margin: '0 0 10px 0', fontSize: '0.85em', color: '#721c24', fontWeight: 'bold' }}>
                      {t('editor.delete.confirm_prefix')}"{editState.fieldName}"{t('editor.delete.confirm_mid')} {editState.version}?
                    </p>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button onClick={handleDeleteField} disabled={saving}
                        style={{ padding: '6px 14px', backgroundColor: '#dc3545', color: 'white', border: 'none', borderRadius: '5px', cursor: 'pointer', fontWeight: 'bold', fontSize: '0.85em' }}>
                        {saving ? t('editor.deleting') : t('editor.delete.yes')}
                      </button>
                      <button onClick={() => setConfirmDelete(null)}
                        style={{ padding: '6px 14px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '5px', cursor: 'pointer', fontSize: '0.85em' }}>
                        {t('editor.cancel')}
                      </button>
                    </div>
                  </div>
                ) : (
                  <button
                    onClick={() => setConfirmDelete({ fieldName: editState.fieldName, version: editState.version })}
                    style={{ width: '100%', padding: '7px', backgroundColor: 'transparent', color: '#dc3545', border: '1px solid #dc3545', borderRadius: '6px', cursor: 'pointer', fontSize: '0.82em' }}>
                    {t('editor.delete_btn')} {editState.version}
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
              <span style={{ fontWeight: 'bold', fontSize: '1.05em' }}>{t('editor.new_field')}</span>
              <button onClick={() => setShowAddField(false)} style={{ background: '#6c757d', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', padding: '4px 10px' }}>✕</button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <FormField label={t('editor.add_field.version')}>
                <select value={newField.version}
                  onChange={e => setNewField(p => ({ ...p, version: e.target.value }))}
                  style={inputStyle}>
                  {VERSIONS.map(v => <option key={v} value={v}>EURING {v}</option>)}
                </select>
              </FormField>

              <FormField label={t('editor.add_field.name')}>
                <input value={newField.name} placeholder={t('editor.add_field.name_placeholder')}
                  onChange={e => setNewField(p => ({ ...p, name: e.target.value }))}
                  style={inputStyle} />
              </FormField>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <FormField label={isPipeDelimited(newField.version) ? t('editor.field.field_index') : t('editor.field.position')}>
                  <input type="number" min={1} value={newField.position}
                    onChange={e => setNewField(p => ({ ...p, position: Math.max(1, parseInt(e.target.value) || 1) }))}
                    style={inputStyle} />
                </FormField>
                <FormField label={isPipeDelimited(newField.version) ? t('editor.field.max_length') : t('editor.field.length')}>
                  <input type="number" min={1} value={newField.length}
                    onChange={e => setNewField(p => ({ ...p, length: Math.max(1, parseInt(e.target.value) || 1) }))}
                    style={inputStyle} />
                </FormField>
              </div>

              {newFieldConflicts.length > 0 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#f8d7da', border: '1px solid #f5c6cb', borderRadius: '6px', color: '#721c24', fontSize: '0.85em' }}>
                  {isPipeDelimited(newField.version)
                    ? `⚠ Index ${newField.position} already used by: ${newFieldConflicts.join(', ')}`
                    : `⚠ Positions ${newField.position}–${newField.position + newField.length - 1} already occupied by: ${newFieldConflicts.join(', ')}`}
                </div>
              )}
              {newFieldConflicts.length === 0 && newField.name && (
                <div style={{ padding: '6px 12px', backgroundColor: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '6px', color: '#155724', fontSize: '0.85em' }}>
                  {isPipeDelimited(newField.version)
                    ? `✓ Index ${newField.position} free`
                    : `✓ Positions ${newField.position}–${newField.position + newField.length - 1} free`}
                </div>
              )}
              {!isPipeDelimited(newField.version) && newField.length > 100 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  {t('editor.warn.length_large_prefix')}{newField.length} {t('editor.warn.length_large_suffix')}
                </div>
              )}
              {!isPipeDelimited(newField.version) && (newField.position + newField.length - 1) > 300 && (
                <div style={{ padding: '8px 12px', backgroundColor: '#fff3cd', border: '1px solid #ffc107', borderRadius: '6px', color: '#856404', fontSize: '0.85em' }}>
                  {t('editor.warn.exceeds_300')}
                </div>
              )}

              <FormField label={t('editor.field.data_type')}>
                <select value={newField.dataType}
                  onChange={e => setNewField(p => ({ ...p, dataType: e.target.value }))}
                  style={inputStyle}>
                  {DATA_TYPES.map(dt => <option key={dt} value={dt}>{dt}</option>)}
                </select>
              </FormField>

              <FormField label={t('editor.field.description')}>
                <textarea value={newField.description} rows={2} placeholder={t('editor.add_field.description_placeholder')}
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
                {saving ? t('editor.add_field.adding') : t('editor.add_field.submit')}
              </button>
              <button onClick={() => setShowAddField(false)} style={{ padding: '10px 16px', backgroundColor: '#f8f9fa', border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer' }}>
                {t('editor.cancel')}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default PositionalMatrixEditor;
