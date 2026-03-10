import React, { useState, useEffect, useMemo } from 'react';
import EuringAPI from '../services/api';
import PositionalMatrix from './PositionalMatrix';
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
    
    // Mostra campo se esiste in almeno una versione selezionata
    return selectedVersions.some(version => getFieldValue(fieldRow, version) !== null);
  };

  const filteredFields = useMemo(() => {
    if (!matrixData) return [];
    
    return matrixData.field_matrix.filter(shouldShowField);
  }, [matrixData, selectedVersions, showEmptyFields]);

  const startEditing = async (fieldName: string, version: string, property: string, currentValue: string) => {
    // Trova le informazioni del campo
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
    
    // For valid_values, load full data from lookup table API
    if (property === 'valid_values') {
      setEditValue(''); // Clear while loading
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
        // Fallback: use valid_values codes from field info
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
        title={editMode ? 'Clicca per modificare i valori' : `${totalCount} valori definiti`}
      >
        {totalCount > 0 ? (
          <>
            📋 {totalCount} {'valori definiti'}
            {editMode && <span style={{ marginLeft: '4px', color: '#17a2b8' }}>✏️</span>}
          </>
        ) : (
          <span style={{ color: '#999' }}>{'Nessun valore'}</span>
        )}
      </div>
    );
  };

  const saveEdit = async () => {
    if (!modalEditData) return;
    
    // Validazione frontend per posizione
    if (modalEditData.property === 'position') {
      const positionValue = parseInt(editValue);
      if (isNaN(positionValue) || positionValue < 0) {
        setSaveStatus({type: 'error', message: 'Posizione non valida'});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        return;
      }
    }
    
    // Validazione frontend per lunghezza
    if (modalEditData.property === 'length') {
      const lengthValue = parseInt(editValue);
      if (isNaN(lengthValue) || lengthValue < 1) {
        setSaveStatus({type: 'error', message: 'Lunghezza non valida'});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        return;
      }
    }
    
    try {
      console.log('Saving edit:', modalEditData, editValue);
      
      // Special handling for valid_values - use lookup table API and don't close modals
      if (modalEditData.property === 'valid_values') {
        await handleValidValuesUpdate();
        return; // Exit completely for valid_values
      }
      
      // Regular field update for non-valid_values properties
      await handleRegularFieldUpdate();
      
    } catch (error) {
      setSaveStatus({type: 'error', message: `${'Errore di connessione:'} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error saving edit:', error);
      
      // Close modal on error for regular fields, but not for valid_values
      if (modalEditData.property !== 'valid_values') {
        setShowEditModal(false);
        setModalEditData(null);
        setEditValue('');
      }
    }
  };

  const handleValidValuesUpdate = async () => {
    // Parse the input - support CODE:DESCRIPTION format (one per line)
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
        // Line without colon, treat as code only
        const code = line.trim();
        if (code) {
          values.push({ code, meaning: code });
        }
      }
    }
    
    if (values.length === 0) {
      setSaveStatus({type: 'error', message: 'Nessun valore inserito'});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      return;
    }
    
    // Create lookup data structure
    const lookupData = {
      name: `${modalEditData!.fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Values`,
      description: `Valid values for ${modalEditData!.fieldName}`,
      values: values
    };
    
    try {
      // Call lookup table update API
      const lookupResult = await EuringAPI.updateFieldLookupTable(
        modalEditData!.fieldName,
        modalEditData!.version,
        lookupData
      );
      
      if (lookupResult.success) {
        setSaveStatus({type: 'success', message: `✅ Salvati ${values.length} valori per ${modalEditData!.fieldName}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);

        // Reload from server to verify persistence (consistent with regular field updates)
        setTimeout(async () => {
          await loadMatrixData(true);
        }, 500);

        // Update local state immediately
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

        // Update the edit value to show saved format
        setEditValue(values.map(v => `${v.code}:${v.meaning}`).join('\n'));
        
      } else {
        setSaveStatus({type: 'error', message: `Errore: ${lookupResult.error}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      }
    } catch (error) {
      setSaveStatus({type: 'error', message: `Errore di connessione: ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
    }
  };

  const handleRegularFieldUpdate = async () => {
    // Regular field update
    const result = await EuringAPI.updateMatrixField(
      modalEditData!.fieldName,
      modalEditData!.version,
      modalEditData!.property,
      editValue,
      `Manual edit via matrix interface at ${new Date().toISOString()}`
    );
    
    if (result.success) {
      console.log('✅ Backend save successful:', result);
      setSaveStatus({type: 'success', message: `✅ Campo ${modalEditData!.fieldName} - ${modalEditData!.property} salvato: ${editValue}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);
      
      // Close modal immediately
      setShowEditModal(false);
      setModalEditData(null);
      setEditValue('');
      
      // Reload data from backend to show exactly what was saved
      // No local state manipulation - what you see is what's in the backend
      // Increased delay to 1000ms to ensure file write completes
      setTimeout(async () => {
        console.log('🔄 Reloading matrix data from backend after 1000ms delay');
        await loadMatrixData(true); // Preserve scroll position
      }, 1000);
      
    } else {
      setSaveStatus({type: 'error', message: `${'Errore nel salvataggio:'} ${result.error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Failed to save edit:', result.error);
      
      // Close modal on error
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
      // Conferma dall'utente
      const confirmed = window.confirm(
        `Vuoi aggiungere il campo "${fieldName}" alla versione ${version}?`
      );
      
      if (!confirmed) return;
      
      console.log('Adding field to version:', fieldName, version);
      
      // Calcola una posizione intelligente per il nuovo campo
      let suggestedPosition = 0;
      
      if (matrixData) {
        // Trova la posizione massima nella versione target
        const versionFields = matrixData.field_matrix
          .map(f => f.versions[version])
          .filter(f => f !== null)
          .map(f => f!.position);
        
        if (versionFields.length > 0) {
          suggestedPosition = Math.max(...versionFields) + 1;
        }
        
        // Se il campo esiste in altre versioni, usa una posizione simile
        const fieldRow = matrixData.field_matrix.find(f => f.field_name === fieldName);
        if (fieldRow) {
          const existingPositions = Object.values(fieldRow.versions)
            .filter(f => f !== null)
            .map(f => f!.position);
          
          if (existingPositions.length > 0) {
            // Usa la posizione media delle altre versioni come suggerimento
            const avgPosition = Math.round(existingPositions.reduce((a, b) => a + b, 0) / existingPositions.length);
            suggestedPosition = Math.max(suggestedPosition, avgPosition);
          }
        }
      }
      
      // Chiedi all'utente di confermare o modificare la posizione
      const positionInput = window.prompt(
        `Inserisci la posizione per il campo "${fieldName}" nella versione ${version} (suggerita: ${suggestedPosition})`,
        suggestedPosition.toString()
      );
      
      if (positionInput === null) return; // Utente ha annullato
      
      const finalPosition = parseInt(positionInput) || suggestedPosition;
      
      // Crea un nuovo campo con valori di default
      const defaultField = {
        position: finalPosition,
        name: fieldName,
        data_type: 'string',
        length: 10,
        description: `Campo ${fieldName} aggiunto alla versione ${version} in posizione ${finalPosition}`,
        valid_values: [],
        semantic_domain: undefined
      };
      
      // Chiama l'API per aggiungere il campo realmente al backend
      console.log('🔄 Calling API to add field to backend...');
      const result = await EuringAPI.addFieldToVersion(
        fieldName,
        version,
        finalPosition,
        'string',
        10,
        `Campo ${fieldName} aggiunto alla versione ${version} in posizione ${finalPosition}`
      );
      
      if (result.success) {
        console.log('✅ Field added successfully to backend:', result);
        
        // Aggiorna anche lo stato locale per feedback immediato
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
          message: `✅ Campo ${fieldName} aggiunto alla versione ${version} in posizione ${finalPosition}`
        });
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        
        // Ricarica i dati per confermare il salvataggio
        // Aumentato delay a 2500ms per dare tempo al backend di scrivere il file
        setTimeout(() => {
          console.log('🔄 Reloading data to confirm field addition after 2.5s delay');
          loadMatrixData(true);
        }, 2500);
        
      } else {
        setSaveStatus({type: 'error', message: `${'Errore aggiunta campo:'} ${result.error}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      }
      
    } catch (error) {
      setSaveStatus({type: 'error', message: `${'Errore aggiunta campo:'} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error adding field:', error);
    }
  };

  const removeFieldFromVersion = async (fieldName: string, version: string) => {
    try {
      // Conferma dall'utente
      const confirmed = window.confirm(
        `Vuoi rimuovere il campo "${fieldName}" dalla versione ${version}?`
      );
      
      if (!confirmed) return;
      
      console.log('Removing field from version:', fieldName, version);
      
      // Rimuovi il campo dalla versione
      if (matrixData) {
        const updatedMatrix = { ...matrixData };
        const fieldIndex = updatedMatrix.field_matrix.findIndex(f => f.field_name === fieldName);
        
        if (fieldIndex !== -1) {
          const field = updatedMatrix.field_matrix[fieldIndex];
          field.versions[version] = null;
          setMatrixData(updatedMatrix);
          
          setSaveStatus({type: 'success', message: `🗑️ Campo ${fieldName} rimosso dalla versione ${version}`});
          setTimeout(() => setSaveStatus({type: null, message: ''}), 3000);
        }
      }
      
    } catch (error) {
      setSaveStatus({type: 'error', message: `${'Errore rimozione campo:'} ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error removing field:', error);
    }
  };

  const loadMatrixData = async (preserveScrollPosition: boolean = false): Promise<void> => {
    // Salva la posizione di scroll corrente se richiesto
    const scrollPosition = preserveScrollPosition ? window.scrollY : 0;
    
    setLoading(true);
    setError(null);

    try {
      console.log('Loading matrix data...');
      const response = await EuringAPI.getEuringVersionsMatrix();
      
      if (response.success) {
        setMatrixData(response);
        // Seleziona tutte le versioni di default solo al primo caricamento
        if (!preserveScrollPosition) {
          setSelectedVersions(response.versions_metadata.map((v: VersionMetadata) => v.year.toString()));
        }
        console.log('Matrix data loaded successfully:', response.field_matrix.length, 'fields');
        
        // Ripristina la posizione di scroll se richiesto
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
        setError(response.error || 'Errore nel caricamento della matrice');
      }
    } catch (err: any) {
      console.error('Matrix loading error:', err);
      setError(err.message || 'Errore di connessione al server');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>📊 {'Matrice EURING'}</h2>
        <p>{'Caricamento dati...'}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 {'Matrice EURING'}</h2>
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24',
          padding: '15px', 
          borderRadius: '5px',
          margin: '10px 0'
        }}>
          <strong>❌ {'Errore:'}</strong> {error}
          <br />
          <button 
            onClick={() => loadMatrixData(false)} // Non preservare la posizione in caso di errore
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
            {'Riprova'}
          </button>
        </div>
      </div>
    );
  }

  if (!matrixData) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 {'Matrice EURING'}</h2>
        <p>{'Nessun dato disponibile'}</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2>📊 Matrice Versioni EURING</h2>
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
                {currentUser.role === 'super_admin' && '✅ Modifica abilitata'}
                {currentUser.role === 'admin' && '👁️ Solo lettura'}
                {currentUser.role === 'user' && '👁️ Solo lettura'}
                {currentUser.role === 'viewer' && `👁️ ${'Solo lettura'}`}
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
                ? 'Login richiesto'
                : currentUser.role !== 'super_admin'
                ? 'Solo Super Admin'
                : 'Super Admin abilitato'
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
            {editMode ? '✏️ ' + 'Modalità Modifica' : '🔒 ' + 'Sola Lettura'}
            {currentUser?.role === 'super_admin' && ' 👑'}
          </button>
          
          <button
            onClick={() => loadMatrixData(true)} // Preserva la posizione di scroll anche per il reload manuale
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
            🔄 {'Ricarica'}
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
              💡 {'Clicca sui valori per modificarli'}
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
          <h4 style={{ margin: '0 0 15px 0' }}>{'Versioni EURING'}</h4>
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
                  ({version.total_fields} {'campi'})
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
            <span>{'Mostra campi vuoti'}</span>
          </label>
        </div>

        {/* View mode toggle */}
        <div style={{ marginTop: '15px' }}>
          <span style={{ fontWeight: 'bold', marginRight: '10px' }}>Visualizzazione:</span>
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
              📋 Tabella campi
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
              🎨 Mappa posizionale
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
            <h5 style={{ margin: '0 0 10px 0', color: '#0c5460' }}>🛠️ {'Modalità modifica attiva'}</h5>
            <div style={{ fontSize: '0.9em', color: '#0c5460' }}>
              • {'Clicca sui valori per modificarli'}<br/>
              • {'Usa + per aggiungere campi'}<br/>
              • {'Usa 🗑️ per rimuovere campi'}<br/>
              • {'Le modifiche vengono salvate automaticamente'}<br/>
              • ⚠️ {'Attenzione: le modifiche sono permanenti'}<br/>
              • {'Scopo: documentazione evoluzione EURING'}
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
            <strong>{'Totale campi:'}</strong> {matrixData.total_fields}
          </div>
          <div>
            <strong>{'Visualizzati:'}</strong> {filteredFields.length}
          </div>
          <div>
            <strong>{'Versioni selezionate:'}</strong> {selectedVersions.length}
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
        key={`matrix-table-${refreshKey}`} // Force re-render when refreshKey changes
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
                {'Campo'}
              </th>
              <th style={{ 
                padding: '12px', 
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '300px'
              }}>
                {'Descrizione'}
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
                        console.log('🖱️ Field name clicked!', {
                          editMode,
                          selectedVersionsCount: selectedVersions.length,
                          selectedVersions,
                          fieldName: fieldRow.field_name
                        });
                        
                        if (editMode && selectedVersions.length > 0) {
                          // Edit name for first selected version
                          const firstVersion = selectedVersions[0];
                          const fieldInfo = getFieldValue(fieldRow, firstVersion);
                          console.log('📋 Field info:', fieldInfo);
                          
                          if (fieldInfo) {
                            // Use fieldInfo.name if available, otherwise use fieldRow.field_name
                            const currentName = fieldInfo.name || fieldRow.field_name;
                            console.log('✏️ Starting edit with name:', currentName);
                            startEditing(fieldRow.field_name, firstVersion, 'name', currentName);
                          } else {
                            console.warn('⚠️ No field info found for version:', firstVersion);
                          }
                        } else {
                          console.warn('⚠️ Cannot edit:', {
                            editMode,
                            selectedVersionsLength: selectedVersions.length
                          });
                        }
                      }}
                    >
                      {fieldRow.field_name}
                      {editMode && selectedVersions.length > 0 && <span style={{ marginLeft: '4px', color: '#007bff', fontSize: '0.8em' }}>✏️</span>}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#666', fontWeight: 'normal' }}>
                      {fieldRow.semantic_meaning}
                    </div>
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
                            ✓ {'Presente'}
                          </div>
                          
                          {/* Campo Descrizione - Editabile */}
                          <div style={{ marginBottom: '4px' }}>
                            <strong>{'Descrizione:'}</strong>
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
                          
                          {/* Dettagli tecnici - Editabili */}
                          <div style={{ color: '#666', fontSize: '0.75em', marginTop: '4px' }}>
                            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', alignItems: 'center' }}>
                              <span>
                                {'Pos:'} 
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
                              
                              {/* Tipo di dato editabile */}
                              <span>
                                {'Tipo:'} 
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
                              
                              {/* Lunghezza editabile */}
                              <span>
                                {'Lung:'} 
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
                              
                              {/* Pulsante rimuovi campo */}
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
                                  title={'Rimuovi campo'}
                                >
                                  🗑️
                                </button>
                              )}
                            </div>
                          </div>
                          
                          {/* Valori Validi - Editabili */}
                          {fieldInfo.valid_values && fieldInfo.valid_values.length > 0 && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>{'Valori:'}</strong>
                              <FieldValuesDisplay
                                fieldName={fieldRow.field_name}
                                version={year}
                                values={fieldInfo.valid_values}
                                valuesCount={fieldInfo.valid_values_count}
                                editMode={editMode}
                                onEdit={async () => {
                                  // Load full values with descriptions for editing
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
                                + {'Aggiungi valori'}
                              </button>
                            </div>
                          )}
                          
                          {/* Dominio Semantico - Editabile */}
                          {fieldInfo.semantic_domain && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>{'Dominio:'}</strong>
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
                                + {'Aggiungi dominio'}
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
                          {'Non presente'}
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
                                + {'Aggiungi campo'}
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
        <h4 style={{ margin: '0 0 15px 0' }}>{'Legenda'}</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#e8f5e8',
              border: '1px solid #4caf50'
            }}></div>
            <span>{'Campo presente'}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#f8f8f8',
              border: '1px solid #ccc'
            }}></div>
            <span>{'Campo assente'}</span>
          </div>
          <div><strong>Pos:</strong> {'Posizione nel record'}</div>
          <div><strong>Tipo:</strong> {'Tipo di dato'}</div>
          <div><strong>Lung:</strong> {'Lunghezza campo'}</div>
          <div><strong>Valori:</strong> {'Valori ammessi'}</div>
        </div>
      </div>
      </>
      )}

      {/* Modal di Editing Zoomato */}
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
                ✏️ {'Modifica Campo'}
              </h3>
              <div style={{ 
                fontSize: '1.1em', 
                color: '#666',
                display: 'flex',
                flexWrap: 'wrap',
                gap: '15px'
              }}>
                <span><strong>{'Campo:'}</strong> {modalEditData.fieldName}</span>
                <span><strong>{'Versione:'}</strong> {modalEditData.version}</span>
                <span><strong>{'Proprietà:'}</strong> {modalEditData.property}</span>
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
                <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>📋 {'Informazioni campo'}</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', fontSize: '0.9em' }}>
                  <div><strong>{'Posizione:'}</strong> {modalEditData.fieldInfo.position}</div>
                  <div><strong>{'Tipo:'}</strong> {modalEditData.fieldInfo.data_type}</div>
                  <div><strong>{'Lunghezza:'}</strong> {modalEditData.fieldInfo.length}</div>
                  {modalEditData.fieldInfo.semantic_domain && (
                    <div><strong>{'Dominio:'}</strong> {EuringAPI.getDomainDisplayName(modalEditData.fieldInfo.semantic_domain)}</div>
                  )}
                </div>
                {modalEditData.fieldInfo.description && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>{'Valore attuale:'}</strong> {modalEditData.fieldInfo.description}
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
                {modalEditData.property === 'name' && `✏️ ${'Modifica nome campo'}`}
                {modalEditData.property === 'description' && `📝 ${'Modifica descrizione'}`}
                {modalEditData.property === 'semantic_domain' && `🏷️ ${'Modifica dominio semantico'}`}
                {modalEditData.property === 'data_type' && `🔧 ${'Modifica tipo dato'}`}
                {modalEditData.property === 'length' && `📏 ${'Modifica lunghezza'}`}
                {modalEditData.property === 'position' && `📍 ${'Modifica posizione'}`}
                {modalEditData.property === 'valid_values' && `📋 ${'Modifica valori ammessi'}`}
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
                    📊 {editValue.split('\n').filter(l => l.trim().length > 0).length} valori attualmente definiti
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
                    placeholder="Inserisci i valori nel formato CODICE:DESCRIZIONE (uno per riga)&#10;&#10;Esempio:&#10;ABT:Albania (Tirana)&#10;AUW:Austria (Wien (Vienna))&#10;BGS:Bulgaria (Sofia)"
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
                        // Sort values alphabetically by code
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
                      🔤 Ordina A-Z
                    </button>
                    <button
                      onClick={() => {
                        // Remove duplicates
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
                          setSaveStatus({type: 'success', message: `Rimossi ${removed} duplicati`});
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
                      🧹 Rimuovi duplicati
                    </button>
                    <button
                      onClick={() => {
                        if (window.confirm('Vuoi cancellare tutti i valori?')) {
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
                      🗑️ Cancella tutto
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
                    💡 <strong>Formato:</strong> CODICE:DESCRIZIONE (uno per riga)<br/>
                    Puoi incollare direttamente una lista di valori.
                  </div>
                </div>
              ) : modalEditData.property === 'name' ? (
                <div>
                  <input
                    type="text"
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    placeholder="Nome campo (es. latitude_sign)"
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
                    ⚠️ <strong>Attenzione:</strong> Modificare il nome del campo può influenzare le conversioni e i parser. Usa nomi descrittivi in snake_case (es. latitude_sign, ring_number).
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
                  <option value="">{'Seleziona dominio...'}</option>
                  <option value="identification_marking">🏷️ {'Identificazione'}</option>
                  <option value="species">🐦 {'Specie'}</option>
                  <option value="demographics">👥 {'Demografia'}</option>
                  <option value="temporal">⏰ {'Temporale'}</option>
                  <option value="spatial">🌍 {'Spaziale'}</option>
                  <option value="biometrics">📏 {'Biometria'}</option>
                  <option value="methodology">🔬 {'Metodologia'}</option>
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
                  <option value="string">📝 {'Stringa'}</option>
                  <option value="integer">🔢 {'Intero'}</option>
                  <option value="float">🔢 {'Decimale'}</option>
                  <option value="date">📅 {'Data'}</option>
                  <option value="code">🏷️ {'Codice'}</option>
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
                  placeholder={modalEditData.property === 'position' ? 'Inserisci posizione' : 'Inserisci lunghezza'}
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
                  placeholder={'Inserisci descrizione...'}
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
                  ? `💡 ${'Ctrl+Enter per salvare, Esc per chiudere'}`
                  : `💡 ${'Ctrl+Enter per salvare, Esc per annullare'}`
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
                  {modalEditData?.property === 'valid_values' ? `❌ ${'Chiudi'}` : `❌ ${'Annulla'}`}
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
                  {modalEditData?.property === 'valid_values' ? `💾 ${'Salva valori'}` : `✅ ${'Salva'}`}
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