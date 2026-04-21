import React, { useState, useEffect, useMemo } from 'react';
import EuringAPI from '../services/api';
import PositionalMatrix from './PositionalMatrix';
import { useTranslation } from '../hooks/useTranslation';
import './EuringMatrix.css';

interface VersionMetadata {
  year: number;
  id: string;
  name: string;
  description: string;
  total_fields: number;
}

interface FieldInfo {
  position: number;
  name: string;
  data_type: string;
  length: number;
  description: string;
  valid_values: string[];
  valid_values_count?: number;
  semantic_domain?: string;
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
  versions_metadata: VersionMetadata[];
  field_matrix: FieldRow[];
  reference_version: number;
  total_fields: number;
  processing_time_ms: number;
  error?: string;
}

interface EuringMatrixProps {
  currentUser?: {
    id: string;
    username: string;
    email: string;
    full_name: string;
    role: 'super_admin' | 'admin' | 'matrix_editor' | 'user' | 'viewer';
    department?: string;
    is_active: boolean;
  } | null;
}

const EuringMatrix: React.FC<EuringMatrixProps> = ({ currentUser }) => {
  const { t } = useTranslation();
  const [matrixData, setMatrixData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
  const [showEmptyFields, setShowEmptyFields] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editValue, setEditValue] = useState<string>('');
  const [saveStatus, setSaveStatus] = useState<{type: 'success' | 'error' | null, message: string}>({type: null, message: ''});
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [refreshKey, setRefreshKey] = useState<number>(0);
  const [viewMode, setViewMode] = useState<'table' | 'positional'>('table');
  const [modalEditData, setModalEditData] = useState<{
    fieldName: string;
    version: string;
    property: string;
    currentValue: string;
    fieldInfo: FieldInfo | null;
  } | null>(null);

  useEffect(() => {
    loadMatrixData();
  }, []);

  // Gestione tasti di scelta rapida per il modal
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (showEditModal) {
        if (event.key === 'Enter' && (event.ctrlKey || event.metaKey)) {
          event.preventDefault();
          saveEdit();
        } else if (event.key === 'Escape') {
          event.preventDefault();
          cancelEdit();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showEditModal, editValue, modalEditData]);

  const toggleVersion = (year: string) => {
    setSelectedVersions(prev =>
      prev.includes(year)
        ? prev.filter(v => v !== year)
        : [...prev, year].sort()
    );
  };

  const getVersionColor = (year: string): string => {
    const colors: Record<string, string> = {
      '1966': '#e74c3c',
      '1979': '#f39c12',
      '2000': '#3498db',
      '2020': '#27ae60'
    };
    return colors[year] || '#95a5a6';
  };

  const getFieldValue = (fieldRow: FieldRow, version: string): FieldInfo | null => {
    return fieldRow.versions[version] || null;
  };

  const shouldShowField = (fieldRow: FieldRow): boolean => {
    if (showEmptyFields) return true;
    return selectedVersions.some(version => getFieldValue(fieldRow, version) !== null);
  };

  const filteredFields = useMemo(() => {
    if (!matrixData) return [];
    return matrixData.field_matrix.filter(shouldShowField);
  }, [matrixData, selectedVersions, showEmptyFields]);

  const startEditing = async (fieldName: string, version: string, property: string, currentValue: string) => {
    const fieldRow = matrixData?.field_matrix.find(f => f.field_name === fieldName);
    const fieldInfo = fieldRow?.versions[version] || null;

    setModalEditData({
      fieldName,
      version,
      property,
      currentValue,
      fieldInfo
    });
    setShowEditModal(true);

    if (property === 'valid_values') {
      setEditValue('');
      try {
        const response = await EuringAPI.getFieldLookupTable(fieldName, version);
        if (response.success && response.lookup_table && response.lookup_table.values) {
          const lines = response.lookup_table.values.map((item: any) =>
            `${item.code}:${item.meaning}`
          );
          setEditValue(lines.join('\n'));
        } else if (currentValue !== '__LOADING__') {
          setEditValue(currentValue);
        }
      } catch (error) {
        console.error('Error loading lookup table:', error);
        if (fieldInfo?.valid_values && fieldInfo.valid_values.length > 0) {
          setEditValue(fieldInfo.valid_values.join('\n'));
        } else if (currentValue !== '__LOADING__') {
          setEditValue(currentValue);
        }
      }
    } else {
      setEditValue(currentValue);
    }
  };

  // Componente per visualizzare i valori con descrizioni
  const FieldValuesDisplay: React.FC<{
    fieldName: string;
    version: string;
    values: string[];
    valuesCount?: number;
    editMode: boolean;
    onEdit: () => void | Promise<void>;
  }> = ({ values, valuesCount, editMode, onEdit }) => {
    const { t } = useTranslation();
    const totalCount = valuesCount || values.length;

    const handleEdit = async () => {
      if (editMode) {
        await onEdit();
      }
    };

    return (
      <div
        style={{
          color: '#17a2b8',
          cursor: editMode ? 'pointer' : 'default',
          padding: '2px',
          borderRadius: '2px',
          backgroundColor: editMode ? 'rgba(23,162,184,0.1)' : 'transparent',
          fontSize: '0.75em',
          fontFamily: 'monospace'
        }}
        onClick={handleEdit}
        title={editMode ? t('euring.values.click_edit') : `${totalCount} ${t('euring.values.count_defined')}`}
      >
        {totalCount > 0 ? (
          <>
            📋 {totalCount} {t('euring.values.count_defined')}
            {editMode && <span style={{ marginLeft: '4px', color: '#17a2b8' }}>✏️</span>}
          </>
        ) : (
          <span style={{ color: '#999' }}>{t('euring.values.none')}</span>
        )}
      </div>
    );
  };

  const saveEdit = async () => {
    if (!modalEditData) return;

    if (modalEditData.property === 'position') {
      const positionValue = parseInt(editValue);
      if (isNaN(positionValue) || positionValue < 0) {
        setSaveStatus({type: 'error', message: t('euring.validation.invalid_pos')});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        return;
      }
    }

    if (modalEditData.property === 'length') {
      const lengthValue = parseInt(editValue);
      if (isNaN(lengthValue) || lengthValue < 1) {
        setSaveStatus({type: 'error', message: t('euring.validation.invalid_len')});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        return;
      }
    }

    try {
      console.log('Saving edit:', modalEditData, editValue);

      if (modalEditData.property === 'valid_values') {
        await handleValidValuesUpdate();
        return;
      }

      await handleRegularFieldUpdate();

    } catch (error) {
      setSaveStatus({type: 'error', message: `${t('euring.save.connection_error')} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error saving edit:', error);

      if (modalEditData.property !== 'valid_values') {
        setShowEditModal(false);
        setModalEditData(null);
        setEditValue('');
      }
    }
  };

  const handleValidValuesUpdate = async () => {
    const lines = editValue.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    const values: Array<{code: string, meaning: string}> = [];

    for (const line of lines) {
      if (line.includes(':')) {
        const colonIndex = line.indexOf(':');
        const code = line.substring(0, colonIndex).trim();
        const meaning = line.substring(colonIndex + 1).trim();
        if (code && meaning) {
          values.push({ code, meaning });
        }
      } else {
        const code = line.trim();
        if (code) {
          values.push({ code, meaning: code });
        }
      }
    }

    if (values.length === 0) {
      setSaveStatus({type: 'error', message: t('euring.validation.no_values')});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      return;
    }

    const lookupData = {
      name: `${modalEditData!.fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Values`,
      description: `Valid values for ${modalEditData!.fieldName}`,
      values: values
    };

    try {
      const lookupResult = await EuringAPI.updateFieldLookupTable(
        modalEditData!.fieldName,
        modalEditData!.version,
        lookupData
      );

      if (lookupResult.success) {
        setSaveStatus({type: 'success', message: `✅ Saved ${values.length} values for ${modalEditData!.fieldName}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);

        setTimeout(async () => {
          await loadMatrixData(true);
        }, 500);

        if (matrixData) {
          const updatedMatrix = JSON.parse(JSON.stringify(matrixData));
          const fieldIndex = updatedMatrix.field_matrix.findIndex((f: FieldRow) => f.field_name === modalEditData!.fieldName);

          if (fieldIndex !== -1) {
            const versionInfo = updatedMatrix.field_matrix[fieldIndex].versions[modalEditData!.version];
            if (versionInfo) {
              versionInfo.valid_values = values.map(v => v.code);
              versionInfo.valid_values_count = values.length;
              setMatrixData(updatedMatrix);
              setRefreshKey(prev => prev + 1);
            }
          }
        }

        setEditValue(values.map(v => `${v.code}:${v.meaning}`).join('\n'));

      } else {
        setSaveStatus({type: 'error', message: `${t('euring.save.error_prefix')} ${lookupResult.error}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      }
    } catch (error) {
      setSaveStatus({type: 'error', message: `${t('euring.save.connection_error')} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
    }
  };

  const handleRegularFieldUpdate = async () => {
    const result = await EuringAPI.updateMatrixField(
      modalEditData!.fieldName,
      modalEditData!.version,
      modalEditData!.property,
      editValue,
      `Manual edit via matrix interface at ${new Date().toISOString()}`
    );

    if (result.success) {
      console.log('✅ Backend save successful:', result);
      setSaveStatus({type: 'success', message: `✅ ${modalEditData!.fieldName} - ${modalEditData!.property}: ${editValue}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);

      setShowEditModal(false);
      setModalEditData(null);
      setEditValue('');

      setTimeout(async () => {
        console.log('🔄 Reloading matrix data from backend after 1000ms delay');
        await loadMatrixData(true);
      }, 1000);

    } else {
      setSaveStatus({type: 'error', message: `${t('euring.save.save_error')} ${result.error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Failed to save edit:', result.error);

      setShowEditModal(false);
      setModalEditData(null);
      setEditValue('');
    }
  };

  const cancelEdit = () => {
    setShowEditModal(false);
    setModalEditData(null);
    setEditValue('');
  };

  const addFieldToVersion = async (fieldName: string, version: string) => {
    try {
      const confirmed = window.confirm(
        `${t('euring.cell.add_field')} "${fieldName}" → v${version}?`
      );

      if (!confirmed) return;

      console.log('Adding field to version:', fieldName, version);

      let suggestedPosition = 0;

      if (matrixData) {
        const versionFields = matrixData.field_matrix
          .map(f => f.versions[version])
          .filter(f => f !== null)
          .map(f => f!.position);

        if (versionFields.length > 0) {
          suggestedPosition = Math.max(...versionFields) + 1;
        }

        const fieldRow = matrixData.field_matrix.find(f => f.field_name === fieldName);
        if (fieldRow) {
          const existingPositions = Object.values(fieldRow.versions)
            .filter(f => f !== null)
            .map(f => f!.position);

          if (existingPositions.length > 0) {
            const avgPosition = Math.round(existingPositions.reduce((a, b) => a + b, 0) / existingPositions.length);
            suggestedPosition = Math.max(suggestedPosition, avgPosition);
          }
        }
      }

      const positionInput = window.prompt(
        `${t('euring.modal.placeholder_pos')} "${fieldName}" v${version} (→ ${suggestedPosition})`,
        suggestedPosition.toString()
      );

      if (positionInput === null) return;

      const finalPosition = parseInt(positionInput) || suggestedPosition;

      const defaultField = {
        position: finalPosition,
        name: fieldName,
        data_type: 'string',
        length: 10,
        description: `${fieldName} v${version} @${finalPosition}`,
        valid_values: [],
        semantic_domain: undefined
      };

      console.log('🔄 Calling API to add field to backend...');
      const result = await EuringAPI.addFieldToVersion(
        fieldName,
        version,
        finalPosition,
        'string',
        10,
        `${fieldName} v${version} @${finalPosition}`
      );

      if (result.success) {
        console.log('✅ Field added successfully to backend:', result);

        if (matrixData) {
          const updatedMatrix = { ...matrixData };
          const fieldIndex = updatedMatrix.field_matrix.findIndex(f => f.field_name === fieldName);

          if (fieldIndex !== -1) {
            const field = updatedMatrix.field_matrix[fieldIndex];
            field.versions[version] = defaultField;
            setMatrixData(updatedMatrix);
          }
        }

        setSaveStatus({
          type: 'success',
          message: `✅ ${fieldName} → v${version} @${finalPosition}`
        });
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);

        setTimeout(() => {
          console.log('🔄 Reloading data to confirm field addition after 2.5s delay');
          loadMatrixData(true);
        }, 2500);

      } else {
        setSaveStatus({type: 'error', message: `${t('euring.save.add_error')} ${result.error}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      }

    } catch (error) {
      setSaveStatus({type: 'error', message: `${t('euring.save.add_error')} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error adding field:', error);
    }
  };

  const removeFieldFromVersion = async (fieldName: string, version: string) => {
    try {
      const confirmed = window.confirm(
        `${t('euring.cell.remove_field')} "${fieldName}" v${version}?`
      );

      if (!confirmed) return;

      console.log('Removing field from version:', fieldName, version);

      if (matrixData) {
        const updatedMatrix = { ...matrixData };
        const fieldIndex = updatedMatrix.field_matrix.findIndex(f => f.field_name === fieldName);

        if (fieldIndex !== -1) {
          const field = updatedMatrix.field_matrix[fieldIndex];
          field.versions[version] = null;
          setMatrixData(updatedMatrix);

          setSaveStatus({type: 'success', message: `🗑️ ${fieldName} ← v${version}`});
          setTimeout(() => setSaveStatus({type: null, message: ''}), 3000);
        }
      }

    } catch (error) {
      setSaveStatus({type: 'error', message: `${t('euring.save.remove_error')} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error removing field:', error);
    }
  };

  const loadMatrixData = async (preserveScrollPosition: boolean = false): Promise<void> => {
    const scrollPosition = preserveScrollPosition ? window.scrollY : 0;

    setLoading(true);
    setError(null);

    try {
      console.log('Loading matrix data...');
      const response = await EuringAPI.getEuringVersionsMatrix();

      if (response.success) {
        setMatrixData(response);
        if (!preserveScrollPosition) {
          setSelectedVersions(response.versions_metadata.map((v: VersionMetadata) => v.year.toString()));
        }
        console.log('Matrix data loaded successfully:', response.field_matrix.length, 'fields');

        if (preserveScrollPosition && scrollPosition > 0) {
          setTimeout(() => {
            console.log('📍 Restoring scroll to position:', scrollPosition);
            window.scrollTo({
              top: scrollPosition,
              behavior: 'instant'
            });
          }, 100);
        }
      } else {
        setError(response.error || t('euring.error.loading'));
      }
    } catch (err: any) {
      console.error('Matrix loading error:', err);
      setError(err.message || t('euring.error.connection'));
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>📊 {t('euring.title')}</h2>
        <p>{t('euring.loading')}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 {t('euring.title')}</h2>
        <div style={{
          backgroundColor: '#f8d7da',
          color: '#721c24',
          padding: '15px',
          borderRadius: '5px',
          margin: '10px 0'
        }}>
          <strong>❌ {t('euring.save.error_prefix')}</strong> {error}
          <br />
          <button
            onClick={() => loadMatrixData(false)}
            style={{
              marginTop: '10px',
              padding: '8px 16px',
              backgroundColor: '#dc3545',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
          >
            {t('euring.error.retry')}
          </button>
        </div>
      </div>
    );
  }

  if (!matrixData) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 {t('euring.title')}</h2>
        <p>{t('euring.no_data')}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2>📊 {t('euring.title')}</h2>
          <p>Confronto campi tra versioni EURING (riferimento: {matrixData.reference_version})</p>

          {/* User Info */}
          {currentUser && (
            <div style={{
              backgroundColor: currentUser.role === 'super_admin' ? '#fff3cd' : '#d1ecf1',
              border: `1px solid ${currentUser.role === 'super_admin' ? '#ffeaa7' : '#bee5eb'}`,
              borderRadius: '6px',
              padding: '10px',
              marginTop: '10px',
              fontSize: '13px'
            }}>
              <span style={{ fontWeight: 'bold' }}>
                👤 {currentUser.full_name} ({currentUser.role === 'super_admin' ? 'Super Admin' : currentUser.role === 'admin' ? 'Admin' : currentUser.role === 'user' ? 'User' : 'Viewer'})
              </span>
              <span style={{ marginLeft: '10px', color: '#666' }}>
                {currentUser.role === 'super_admin' && t('euring.user.edit_enabled')}
                {currentUser.role === 'admin' && t('euring.user.read_only')}
                {currentUser.role === 'user' && t('euring.user.read_only')}
                {currentUser.role === 'viewer' && t('euring.user.read_only')}
              </span>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setEditMode(!editMode)}
            disabled={!currentUser || currentUser.role !== 'super_admin'}
            title={
              !currentUser
                ? t('euring.btn.login_required')
                : currentUser.role !== 'super_admin'
                ? t('euring.btn.super_admin_only')
                : t('euring.btn.super_admin_enabled')
            }
            style={{
              padding: '10px 20px',
              backgroundColor: editMode ? '#dc3545' : '#28a745',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: (!currentUser || currentUser.role !== 'super_admin') ? 'not-allowed' : 'pointer',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              opacity: (!currentUser || currentUser.role !== 'super_admin') ? 0.6 : 1
            }}
          >
            {editMode ? `✏️ ${t('euring.btn.edit_mode')}` : `🔒 ${t('euring.btn.read_only')}`}
            {currentUser?.role === 'super_admin' && ' 👑'}
          </button>

          <button
            onClick={() => loadMatrixData(true)}
            style={{
              padding: '10px 20px',
              backgroundColor: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}
          >
            🔄 {t('euring.btn.reload')}
          </button>

          {editMode && (
            <div style={{
              backgroundColor: '#fff3cd',
              color: '#856404',
              padding: '8px 12px',
              borderRadius: '4px',
              fontSize: '0.9em',
              border: '1px solid #ffeaa7'
            }}>
              💡 {t('euring.btn.click_to_edit')}
            </div>
          )}

          {/* Notifiche di salvataggio */}
          {saveStatus.type && (
            <div style={{
              backgroundColor: saveStatus.type === 'success' ? '#d4edda' : '#f8d7da',
              color: saveStatus.type === 'success' ? '#155724' : '#721c24',
              padding: '8px 12px',
              borderRadius: '4px',
              fontSize: '0.9em',
              border: `1px solid ${saveStatus.type === 'success' ? '#c3e6cb' : '#f5c6cb'}`,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span>{saveStatus.type === 'success' ? '✅' : '❌'}</span>
              <span>{saveStatus.message}</span>
            </div>
          )}
        </div>
      </div>

      {/* Controlli */}
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        margin: '20px 0',
        border: '1px solid #e9ecef'
      }}>
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ margin: '0 0 15px 0' }}>{t('euring.ctrl.versions')}</h4>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            {matrixData.versions_metadata.map(version => (
              <label
                key={version.year}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  cursor: 'pointer',
                  padding: '8px 12px',
                  borderRadius: '6px',
                  border: `2px solid ${getVersionColor(version.year.toString())}`,
                  backgroundColor: selectedVersions.includes(version.year.toString())
                    ? `${getVersionColor(version.year.toString())}20`
                    : 'white'
                }}
              >
                <input
                  type="checkbox"
                  checked={selectedVersions.includes(version.year.toString())}
                  onChange={() => toggleVersion(version.year.toString())}
                  style={{ margin: 0 }}
                />
                <span style={{
                  fontWeight: 'bold',
                  color: getVersionColor(version.year.toString())
                }}>
                  {version.year}
                </span>
                <span style={{ fontSize: '0.9em', color: '#666' }}>
                  ({version.total_fields} {t('euring.ctrl.fields_suffix')})
                </span>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: 'pointer'
          }}>
            <input
              type="checkbox"
              checked={showEmptyFields}
              onChange={(e) => setShowEmptyFields(e.target.checked)}
              style={{ margin: 0 }}
            />
            <span>{t('euring.ctrl.show_empty')}</span>
          </label>
        </div>

        {/* View mode toggle */}
        <div style={{ marginTop: '15px' }}>
          <span style={{ fontWeight: 'bold', marginRight: '10px' }}>{t('euring.ctrl.view')}</span>
          <div style={{ display: 'inline-flex', gap: '0', borderRadius: '6px', overflow: 'hidden', border: '1px solid #dee2e6' }}>
            <button
              onClick={() => setViewMode('table')}
              style={{
                padding: '6px 16px',
                backgroundColor: viewMode === 'table' ? '#007bff' : '#fff',
                color: viewMode === 'table' ? '#fff' : '#333',
                border: 'none',
                cursor: 'pointer',
                fontSize: '0.9em',
                fontWeight: viewMode === 'table' ? 'bold' : 'normal',
              }}
            >
              {t('euring.ctrl.table')}
            </button>
            <button
              onClick={() => setViewMode('positional')}
              style={{
                padding: '6px 16px',
                backgroundColor: viewMode === 'positional' ? '#007bff' : '#fff',
                color: viewMode === 'positional' ? '#fff' : '#333',
                border: 'none',
                borderLeft: '1px solid #dee2e6',
                cursor: 'pointer',
                fontSize: '0.9em',
                fontWeight: viewMode === 'positional' ? 'bold' : 'normal',
              }}
            >
              {t('euring.ctrl.positional')}
            </button>
          </div>
        </div>

        {editMode && (
          <div style={{
            backgroundColor: '#e8f4fd',
            padding: '15px',
            borderRadius: '6px',
            border: '1px solid #bee5eb',
            marginTop: '15px'
          }}>
            <h5 style={{ margin: '0 0 10px 0', color: '#0c5460' }}>🛠️ {t('euring.edit.active')}</h5>
            <div style={{ fontSize: '0.9em', color: '#0c5460' }}>
              • {t('euring.edit.hint_click')}<br/>
              • {t('euring.edit.hint_add')}<br/>
              • {t('euring.edit.hint_remove')}<br/>
              • {t('euring.edit.hint_save')}<br/>
              • ⚠️ {t('euring.edit.hint_warning')}<br/>
              • {t('euring.edit.hint_purpose')}
            </div>
          </div>
        )}
      </div>

      {/* Statistiche */}
      <div style={{
        backgroundColor: '#e8f4fd',
        padding: '15px',
        borderRadius: '8px',
        margin: '20px 0',
        border: '1px solid #bee5eb'
      }}>
        <div style={{ display: 'flex', gap: '30px', flexWrap: 'wrap' }}>
          <div>
            <strong>{t('euring.stats.total')}</strong> {matrixData.total_fields}
          </div>
          <div>
            <strong>{t('euring.stats.shown')}</strong> {filteredFields.length}
          </div>
          <div>
            <strong>{t('euring.stats.selected')}</strong> {selectedVersions.length}
          </div>
        </div>
      </div>

      {/* View content based on mode */}
      {viewMode === 'positional' ? (
        <PositionalMatrix
          fieldMatrix={matrixData.field_matrix}
          selectedVersions={selectedVersions}
          editMode={editMode}
          onEditProperty={(fieldName, version, property, currentValue) => {
            startEditing(fieldName, version, property, currentValue);
          }}
        />
      ) : (
      <>
      {/* Tabella completa */}
      <div
        key={`matrix-table-${refreshKey}`}
        style={{
          overflowX: 'auto',
          border: '1px solid #ddd',
          borderRadius: '8px'
        }}
      >
        <table style={{
          width: '100%',
          borderCollapse: 'collapse',
          minWidth: '800px'
        }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa' }}>
              <th style={{
                padding: '12px',
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '50px',
                position: 'sticky',
                left: 0,
                backgroundColor: '#f8f9fa',
                zIndex: 110,
                boxShadow: '2px 0 5px rgba(0,0,0,0.1)'
              }}>
                {'#'}
              </th>
              <th style={{
                padding: '12px',
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '200px',
                position: 'sticky',
                left: '50px',
                backgroundColor: '#f8f9fa',
                zIndex: 109,
                boxShadow: '2px 0 5px rgba(0,0,0,0.1)'
              }}>
                {t('euring.table.field')}
              </th>
              <th style={{
                padding: '12px',
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '300px'
              }}>
                {t('euring.table.description')}
              </th>
              {selectedVersions.map(year => (
                <th
                  key={year}
                  style={{
                    padding: '12px',
                    border: '1px solid #ddd',
                    textAlign: 'center',
                    fontWeight: 'bold',
                    backgroundColor: `${getVersionColor(year)}20`,
                    borderTop: `3px solid ${getVersionColor(year)}`,
                    width: '150px'
                  }}
                >
                  <div>
                    <div style={{ color: getVersionColor(year), fontSize: '1.1em' }}>
                      {year}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666' }}>
                      {matrixData.versions_metadata.find(v => v.year.toString() === year)?.name}
                    </div>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredFields.map((fieldRow, index) => (
              <tr key={fieldRow.field_name} style={{
                backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa'
              }}>
                <td style={{
                  padding: '10px',
                  border: '1px solid #ddd',
                  textAlign: 'center',
                  fontWeight: 'bold',
                  color: '#666',
                  position: 'sticky',
                  left: 0,
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                  zIndex: 100,
                  boxShadow: '2px 0 5px rgba(0,0,0,0.1)',
                  fontSize: '0.85em',
                  width: '50px'
                }}>
                  {index + 1}
                </td>
                <td style={{
                  padding: '10px',
                  border: '1px solid #ddd',
                  fontWeight: 'bold',
                  position: 'sticky',
                  left: '50px',
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                  zIndex: 99,
                  boxShadow: '2px 0 5px rgba(0,0,0,0.1)'
                }}>
                  <div>
                    <div
                      style={{
                        cursor: editMode ? 'pointer' : 'default',
                        padding: '2px',
                        borderRadius: '2px',
                        backgroundColor: editMode ? 'rgba(0,123,255,0.1)' : 'transparent'
                      }}
                      onClick={() => {
                        if (editMode && selectedVersions.length > 0) {
                          const firstVersion = selectedVersions[0];
                          const fieldInfo = getFieldValue(fieldRow, firstVersion);
                          if (fieldInfo) {
                            const currentName = fieldInfo.name || fieldRow.field_name;
                            startEditing(fieldRow.field_name, firstVersion, 'name', currentName);
                          }
                        }
                      }}
                    >
                      {fieldRow.field_name}
                      {editMode && selectedVersions.length > 0 && <span style={{ marginLeft: '4px', color: '#007bff', fontSize: '0.8em' }}>✏️</span>}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666', fontWeight: 'normal' }}>
                      {fieldRow.semantic_meaning}
                    </div>
                    {(fieldRow as any).canonical_name && (
                      <div style={{ fontSize: '0.75em', color: '#0062cc', fontWeight: 'normal', marginTop: '2px' }}>
                        🔗 {(fieldRow as any).canonical_name}
                      </div>
                    )}
                  </div>
                </td>
                <td style={{
                  padding: '10px',
                  border: '1px solid #ddd',
                  zIndex: 1
                }}>
                  {fieldRow.description}
                </td>
                {selectedVersions.map(year => {
                  const fieldInfo = getFieldValue(fieldRow, year);
                  return (
                    <td
                      key={year}
                      style={{
                        padding: '8px',
                        border: '1px solid #ddd',
                        backgroundColor: fieldInfo ? `${getVersionColor(year)}10` : '#f8f8f8',
                        position: 'relative',
                        zIndex: 1
                      }}
                    >
                      {fieldInfo ? (
                        <div style={{ fontSize: '0.8em' }}>
                          <div style={{
                            fontWeight: 'bold',
                            color: getVersionColor(year),
                            marginBottom: '4px'
                          }}>
                            {t('euring.cell.present')}
                          </div>

                          {/* Campo Descrizione */}
                          <div style={{ marginBottom: '4px' }}>
                            <strong>{t('euring.cell.desc_label')}</strong>
                            <div
                              style={{
                                color: '#666',
                                cursor: editMode ? 'pointer' : 'default',
                                padding: '2px',
                                borderRadius: '2px',
                                backgroundColor: editMode ? 'rgba(0,123,255,0.1)' : 'transparent'
                              }}
                              onClick={() => editMode && startEditing(fieldRow.field_name, year, 'description', fieldInfo.description)}
                            >
                              {fieldInfo.description}
                              {editMode && <span style={{ marginLeft: '4px', color: '#007bff' }}>✏️</span>}
                            </div>
                          </div>

                          {/* Dettagli tecnici */}
                          <div style={{ color: '#666', fontSize: '0.75em', marginTop: '4px' }}>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
                              <span>
                                {t('euring.cell.pos_label')}
                                <span
                                  style={{
                                    cursor: editMode ? 'pointer' : 'default',
                                    padding: '1px 2px',
                                    borderRadius: '2px',
                                    backgroundColor: editMode ? 'rgba(0,123,255,0.1)' : 'transparent'
                                  }}
                                  onClick={() => editMode && startEditing(fieldRow.field_name, year, 'position', fieldInfo.position.toString())}
                                >
                                  {fieldInfo.position}
                                  {editMode && <span style={{ marginLeft: '2px', color: '#007bff' }}>✏️</span>}
                                </span>
                              </span>

                              <span>
                                {t('euring.cell.type_label')}
                                <span
                                  style={{
                                    cursor: editMode ? 'pointer' : 'default',
                                    padding: '1px 2px',
                                    borderRadius: '2px',
                                    backgroundColor: editMode ? 'rgba(0,123,255,0.1)' : 'transparent'
                                  }}
                                  onClick={() => editMode && startEditing(fieldRow.field_name, year, 'data_type', fieldInfo.data_type)}
                                >
                                  {fieldInfo.data_type}
                                  {editMode && <span style={{ marginLeft: '2px', color: '#007bff' }}>✏️</span>}
                                </span>
                              </span>

                              <span>
                                {t('euring.cell.len_label')}
                                <span
                                  style={{
                                    cursor: editMode ? 'pointer' : 'default',
                                    padding: '1px 2px',
                                    borderRadius: '2px',
                                    backgroundColor: editMode ? 'rgba(0,123,255,0.1)' : 'transparent'
                                  }}
                                  onClick={() => editMode && startEditing(fieldRow.field_name, year, 'length', fieldInfo.length.toString())}
                                >
                                  {fieldInfo.length}
                                  {editMode && <span style={{ marginLeft: '2px', color: '#007bff' }}>✏️</span>}
                                </span>
                              </span>

                              {editMode && (
                                <button
                                  style={{
                                    padding: '1px 4px',
                                    backgroundColor: '#dc3545',
                                    color: 'white',
                                    border: 'none',
                                    borderRadius: '2px',
                                    fontSize: '0.6em',
                                    cursor: 'pointer',
                                    marginLeft: '8px'
                                  }}
                                  onClick={() => removeFieldFromVersion(fieldRow.field_name, year)}
                                  title={t('euring.cell.remove_field')}
                                >
                                  🗑️
                                </button>
                              )}
                            </div>
                          </div>

                          {/* Valori Validi */}
                          {fieldInfo.valid_values && fieldInfo.valid_values.length > 0 && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>{t('euring.cell.values_label')}</strong>
                              <FieldValuesDisplay
                                fieldName={fieldRow.field_name}
                                version={year}
                                values={fieldInfo.valid_values}
                                valuesCount={fieldInfo.valid_values_count}
                                editMode={editMode}
                                onEdit={async () => {
                                  startEditing(fieldRow.field_name, year, 'valid_values', '__LOADING__');
                                }}
                              />
                            </div>
                          )}

                          {/* Aggiungi valori se non presenti */}
                          {editMode && (!fieldInfo.valid_values || fieldInfo.valid_values.length === 0) && (
                            <div style={{ marginTop: '4px' }}>
                              <button
                                style={{
                                  padding: '2px 6px',
                                  backgroundColor: '#17a2b8',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  fontSize: '0.7em',
                                  cursor: 'pointer'
                                }}
                                onClick={() => startEditing(fieldRow.field_name, year, 'valid_values', '')}
                              >
                                {t('euring.cell.add_values')}
                              </button>
                            </div>
                          )}

                          {/* Dominio Semantico */}
                          {fieldInfo.semantic_domain && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>{t('euring.cell.domain_label')}</strong>
                              <div
                                style={{
                                  color: '#4CAF50',
                                  cursor: editMode ? 'pointer' : 'default',
                                  padding: '2px',
                                  borderRadius: '2px',
                                  backgroundColor: editMode ? 'rgba(76,175,80,0.1)' : 'transparent',
                                  fontSize: '0.75em'
                                }}
                                onClick={() => editMode && startEditing(fieldRow.field_name, year, 'semantic_domain', fieldInfo.semantic_domain || '')}
                              >
                                {EuringAPI.getDomainDisplayName(fieldInfo.semantic_domain)}
                                {editMode && <span style={{ marginLeft: '4px', color: '#4CAF50' }}>✏️</span>}
                              </div>
                            </div>
                          )}

                          {/* Aggiungi dominio se non presente */}
                          {editMode && !fieldInfo.semantic_domain && (
                            <div style={{ marginTop: '4px' }}>
                              <button
                                style={{
                                  padding: '2px 6px',
                                  backgroundColor: '#4CAF50',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  fontSize: '0.7em',
                                  cursor: 'pointer'
                                }}
                                onClick={() => startEditing(fieldRow.field_name, year, 'semantic_domain', '')}
                              >
                                {t('euring.cell.add_domain')}
                              </button>
                            </div>
                          )}
                        </div>
                      ) : (
                        <div style={{
                          textAlign: 'center',
                          color: '#ccc',
                          fontStyle: 'italic'
                        }}>
                          {t('euring.cell.absent')}
                          {editMode && (
                            <div style={{ marginTop: '4px' }}>
                              <button
                                style={{
                                  padding: '4px 8px',
                                  backgroundColor: '#28a745',
                                  color: 'white',
                                  border: 'none',
                                  borderRadius: '3px',
                                  fontSize: '0.7em',
                                  cursor: 'pointer'
                                }}
                                onClick={() => {
                                  addFieldToVersion(fieldRow.field_name, year);
                                }}
                              >
                                {t('euring.cell.add_field')}
                              </button>
                            </div>
                          )}
                        </div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legenda */}
      <div style={{
        backgroundColor: '#f8f9fa',
        padding: '20px',
        borderRadius: '8px',
        margin: '20px 0',
        border: '1px solid #e9ecef'
      }}>
        <h4 style={{ margin: '0 0 15px 0' }}>{t('euring.legend.title')}</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '20px',
              height: '20px',
              backgroundColor: '#e8f5e8',
              border: '1px solid #4caf50'
            }}></div>
            <span>{t('euring.legend.present')}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{
              width: '20px',
              height: '20px',
              backgroundColor: '#f8f8f8',
              border: '1px solid #ccc'
            }}></div>
            <span>{t('euring.legend.absent')}</span>
          </div>
          <div><strong>Pos:</strong> {t('euring.legend.pos')}</div>
          <div><strong>Tipo:</strong> {t('euring.legend.type')}</div>
          <div><strong>Lung:</strong> {t('euring.legend.len')}</div>
          <div><strong>Valori:</strong> {t('euring.legend.values')}</div>
        </div>
      </div>
      </>
      )}

      {/* Modal di Editing */}
      {showEditModal && modalEditData && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.7)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '20px'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '30px',
            maxWidth: '600px',
            width: '100%',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
            transform: 'scale(1.02)',
            transition: 'all 0.3s ease-out'
          }}>
            {/* Header del Modal */}
            <div style={{
              borderBottom: '2px solid #f0f0f0',
              paddingBottom: '20px',
              marginBottom: '25px'
            }}>
              <h3 style={{
                margin: '0 0 10px 0',
                color: '#333',
                fontSize: '1.4em',
                display: 'flex',
                alignItems: 'center',
                gap: '10px'
              }}>
                {t('euring.modal.title')}
              </h3>
              <div style={{
                fontSize: '1.1em',
                color: '#666',
                display: 'flex',
                flexWrap: 'wrap',
                gap: '15px'
              }}>
                <span><strong>{t('euring.modal.field')}</strong> {modalEditData.fieldName}</span>
                <span><strong>{t('euring.modal.version')}</strong> {modalEditData.version}</span>
                <span><strong>{t('euring.modal.property')}</strong> {modalEditData.property}</span>
              </div>
            </div>

            {/* Informazioni del Campo */}
            {modalEditData.fieldInfo && (
              <div style={{
                backgroundColor: '#f8f9fa',
                padding: '15px',
                borderRadius: '8px',
                marginBottom: '25px',
                border: '1px solid #e9ecef'
              }}>
                <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>{t('euring.modal.info_title')}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', fontSize: '0.9em' }}>
                  <div><strong>{t('euring.modal.position')}</strong> {modalEditData.fieldInfo.position}</div>
                  <div><strong>{t('euring.modal.type')}</strong> {modalEditData.fieldInfo.data_type}</div>
                  <div><strong>{t('euring.modal.length')}</strong> {modalEditData.fieldInfo.length}</div>
                  {modalEditData.fieldInfo.semantic_domain && (
                    <div><strong>{t('euring.modal.domain')}</strong> {EuringAPI.getDomainDisplayName(modalEditData.fieldInfo.semantic_domain)}</div>
                  )}
                </div>
                {modalEditData.fieldInfo.description && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>{t('euring.modal.current_value')}</strong> {modalEditData.fieldInfo.description}
                  </div>
                )}
              </div>
            )}

            {/* Campo di Editing */}
            <div style={{ marginBottom: '30px' }}>
              <label style={{
                display: 'block',
                marginBottom: '10px',
                fontWeight: 'bold',
                fontSize: '1.1em',
                color: '#333'
              }}>
                {modalEditData.property === 'name' && t('euring.modal.edit_name')}
                {modalEditData.property === 'description' && t('euring.modal.edit_desc')}
                {modalEditData.property === 'semantic_domain' && t('euring.modal.edit_domain')}
                {modalEditData.property === 'data_type' && t('euring.modal.edit_type')}
                {modalEditData.property === 'length' && t('euring.modal.edit_length')}
                {modalEditData.property === 'position' && t('euring.modal.edit_position')}
                {modalEditData.property === 'valid_values' && t('euring.modal.edit_values')}
              </label>

              {modalEditData.property === 'valid_values' ? (
                <div>
                  {/* Summary */}
                  <div style={{
                    backgroundColor: '#e8f4fd',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    marginBottom: '12px',
                    fontSize: '0.9em',
                    color: '#0c5460'
                  }}>
                    📊 {editValue.split('\n').filter(l => l.trim().length > 0).length} {t('euring.modal.values_count')}
                  </div>

                  <textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '1em',
                      border: '2px solid #007bff',
                      borderRadius: '8px',
                      minHeight: '300px',
                      maxHeight: '50vh',
                      resize: 'vertical',
                      fontFamily: 'monospace',
                      lineHeight: '1.5'
                    }}
                    autoFocus
                    autoComplete="off"
                    data-lpignore="true"
                    data-form-type="other"
                    placeholder={`${t('euring.modal.format_hint')}\n\nABT:Albania (Tirana)\nAUW:Austria (Wien (Vienna))\nBGS:Bulgaria (Sofia)`}
                  />

                  {/* Action buttons for valid_values */}
                  <div style={{
                    display: 'flex',
                    gap: '8px',
                    marginTop: '8px',
                    flexWrap: 'wrap'
                  }}>
                    <button
                      onClick={() => {
                        const lines = editValue.split('\n').filter(l => l.trim().length > 0);
                        lines.sort((a, b) => a.localeCompare(b));
                        setEditValue(lines.join('\n'));
                      }}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.85em',
                        cursor: 'pointer'
                      }}
                    >
                      {t('euring.modal.sort_az')}
                    </button>
                    <button
                      onClick={() => {
                        const lines = editValue.split('\n').filter(l => l.trim().length > 0);
                        const seen = new Set<string>();
                        const unique = lines.filter(line => {
                          const code = line.split(':')[0]?.trim();
                          if (code && !seen.has(code)) {
                            seen.add(code);
                            return true;
                          }
                          return false;
                        });
                        const removed = lines.length - unique.length;
                        setEditValue(unique.join('\n'));
                        if (removed > 0) {
                          setSaveStatus({type: 'success', message: `${removed} duplicates removed`});
                          setTimeout(() => setSaveStatus({type: null, message: ''}), 3000);
                        }
                      }}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#6c757d',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.85em',
                        cursor: 'pointer'
                      }}
                    >
                      {t('euring.modal.remove_dupes')}
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm(t('euring.modal.clear_all') + '?')) {
                          setEditValue('');
                        }
                      }}
                      style={{
                        padding: '6px 12px',
                        backgroundColor: '#dc3545',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.85em',
                        cursor: 'pointer'
                      }}
                    >
                      {t('euring.modal.clear_all')}
                    </button>
                  </div>

                  <div style={{
                    fontSize: '0.85em',
                    color: '#666',
                    marginTop: '10px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px'
                  }}>
                    💡 <strong>{t('euring.modal.format_hint')}</strong><br/>
                    {t('euring.modal.paste_hint')}
                  </div>
                </div>
              ) : modalEditData.property === 'name' ? (
                <div>
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    placeholder="latitude_sign"
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '1.1em',
                      border: '2px solid #007bff',
                      borderRadius: '8px'
                    }}
                    autoFocus
                    autoComplete="off"
                    data-lpignore="true"
                  />
                  <div style={{
                    fontSize: '0.85em',
                    color: '#666',
                    marginTop: '10px',
                    padding: '8px',
                    backgroundColor: '#fff3cd',
                    borderRadius: '4px',
                    border: '1px solid #ffc107'
                  }}>
                    ⚠️ {t('euring.modal.name_warning')}
                  </div>
                </div>
              ) : modalEditData.property === 'semantic_domain' ? (
                <select
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '1.1em',
                    border: '2px solid #007bff',
                    borderRadius: '8px',
                    backgroundColor: 'white'
                  }}
                  autoFocus
                  autoComplete="off"
                  data-lpignore="true"
                >
                  <option value="">{t('euring.modal.select_domain')}</option>
                  <option value="identification_marking">{t('euring.domain.identification')}</option>
                  <option value="species">{t('euring.domain.species')}</option>
                  <option value="demographics">{t('euring.domain.demographics')}</option>
                  <option value="temporal">{t('euring.domain.temporal')}</option>
                  <option value="spatial">{t('euring.domain.spatial')}</option>
                  <option value="biometrics">{t('euring.domain.biometrics')}</option>
                  <option value="methodology">{t('euring.domain.methodology')}</option>
                </select>
              ) : modalEditData.property === 'data_type' ? (
                <select
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '1.1em',
                    border: '2px solid #007bff',
                    borderRadius: '8px',
                    backgroundColor: 'white'
                  }}
                  autoFocus
                  autoComplete="off"
                  data-lpignore="true"
                >
                  <option value="string">{t('euring.type.string')}</option>
                  <option value="integer">{t('euring.type.integer')}</option>
                  <option value="float">{t('euring.type.float')}</option>
                  <option value="date">{t('euring.type.date')}</option>
                  <option value="code">{t('euring.type.code')}</option>
                </select>
              ) : modalEditData.property === 'length' || modalEditData.property === 'position' ? (
                <input
                  type="number"
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '1.1em',
                    border: '2px solid #007bff',
                    borderRadius: '8px'
                  }}
                  autoFocus
                  autoComplete="off"
                  data-lpignore="true"
                  data-form-type="other"
                  min={modalEditData.property === 'position' ? "0" : "1"}
                  max={modalEditData.property === 'position' ? "100" : "100"}
                  placeholder={modalEditData.property === 'position' ? t('euring.modal.placeholder_pos') : t('euring.modal.placeholder_len')}
                />
              ) : (
                <textarea
                  value={editValue}
                  onChange={(e) => setEditValue(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '12px',
                    fontSize: '1.1em',
                    border: '2px solid #007bff',
                    borderRadius: '8px',
                    minHeight: '100px',
                    resize: 'vertical'
                  }}
                  autoFocus
                  autoComplete="off"
                  data-lpignore="true"
                  data-form-type="other"
                  placeholder={t('euring.modal.placeholder_desc')}
                />
              )}
            </div>

            {/* Pulsanti di Azione */}
            <div style={{
              display: 'flex',
              gap: '15px',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderTop: '1px solid #f0f0f0',
              paddingTop: '20px'
            }}>
              <div style={{ fontSize: '0.9em', color: '#666' }}>
                {modalEditData?.property === 'valid_values'
                  ? t('euring.modal.shortcut_save_close')
                  : t('euring.modal.shortcut_save_cancel')
                }
              </div>
              <div style={{ display: 'flex', gap: '15px' }}>
                <button
                  onClick={cancelEdit}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#6c757d',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1.1em',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  {modalEditData?.property === 'valid_values' ? t('euring.modal.btn_close') : t('euring.modal.btn_cancel')}
                </button>
                <button
                  onClick={saveEdit}
                  style={{
                    padding: '12px 24px',
                    backgroundColor: '#28a745',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    fontSize: '1.1em',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  {modalEditData?.property === 'valid_values' ? t('euring.modal.btn_save_values') : t('euring.modal.btn_save')}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default EuringMatrix;
