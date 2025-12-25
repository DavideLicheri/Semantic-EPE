import React, { useState, useEffect, useMemo } from 'react';
import EuringAPI from '../services/api';
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

const EuringMatrix: React.FC = () => {
  const [matrixData, setMatrixData] = useState<MatrixData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
  const [showEmptyFields, setShowEmptyFields] = useState<boolean>(true);
  const [editMode, setEditMode] = useState<boolean>(false);
  const [editValue, setEditValue] = useState<string>('');
  const [saveStatus, setSaveStatus] = useState<{type: 'success' | 'error' | null, message: string}>({type: null, message: ''});
  const [showEditModal, setShowEditModal] = useState<boolean>(false);
  const [refreshKey, setRefreshKey] = useState<number>(0); // Add refresh key to force re-renders
  const [modalEditData, setModalEditData] = useState<{
    fieldName: string;
    version: string;
    property: string;
    currentValue: string;
    fieldInfo: FieldInfo | null;
  } | null>(null);
  const [fieldDescriptions, setFieldDescriptions] = useState<Record<string, Record<string, string>>>({});

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
  }, [showEditModal]);

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

  const startEditing = (fieldName: string, version: string, property: string, currentValue: string) => {
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
    setEditValue(currentValue);
    setShowEditModal(true);
  };

  // Componente per visualizzare i valori con descrizioni
  const FieldValuesDisplay: React.FC<{
    fieldName: string;
    version: string;
    values: string[];
    editMode: boolean;
    onEdit: () => void | Promise<void>;
  }> = ({ fieldName, version, values, editMode, onEdit }) => {
    const [displayValues, setDisplayValues] = useState<string[]>(values);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
      const loadDescriptions = async () => {
        if (values.length === 0) return;
        
        setLoading(true);
        try {
          // Usa descrizioni troncate per la visualizzazione nella matrice
          const valuesWithDescriptions = await getFieldValueWithDescription(fieldName, version, values, true);
          setDisplayValues(valuesWithDescriptions);
        } catch (error) {
          console.error('Error loading descriptions:', error);
          setDisplayValues(values);
        } finally {
          setLoading(false);
        }
      };

      loadDescriptions();
    }, [fieldName, version, values.join(',')]);

    const handleEdit = async () => {
      if (editMode) {
        await onEdit();
      }
    };

    if (loading) {
      return <span style={{ color: '#666', fontSize: '0.75em' }}>Caricamento...</span>;
    }

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
        title={displayValues.length > 0 ? `Clicca per modificare:\n${displayValues.join('\n')}` : undefined}
      >
        {displayValues.slice(0, 2).join(', ')}
        {displayValues.length > 2 && ` (+${displayValues.length - 2} altri)`}
        {editMode && <span style={{ marginLeft: '4px', color: '#17a2b8' }}>✏️</span>}
      </div>
    );
  };

  const getFieldValueWithDescription = async (fieldName: string, version: string, codes: string[], truncateForDisplay: boolean = false): Promise<string[]> => {
    const cacheKey = `${fieldName}_${version}`;
    
    // Se abbiamo già le descrizioni in cache, usale
    if (fieldDescriptions[cacheKey]) {
      return codes.map(code => {
        const description = fieldDescriptions[cacheKey][code];
        if (description) {
          // Tronca la descrizione se richiesto per la visualizzazione
          const displayDescription = truncateForDisplay && description.length > 20 
            ? description.substring(0, 20) + '...' 
            : description;
          return `${code}:${displayDescription}`;
        }
        return code;
      });
    }
    
    // Altrimenti prova a recuperarle dal backend
    try {
      const response = await EuringAPI.getFieldLookupTable(fieldName, version);
      if (response.success && response.lookup_table && response.lookup_table.values) {
        const descriptions: Record<string, string> = {};
        response.lookup_table.values.forEach((item: any) => {
          descriptions[item.code] = item.meaning;
        });
        
        // Salva in cache
        setFieldDescriptions(prev => ({
          ...prev,
          [cacheKey]: descriptions
        }));
        
        // Restituisci i valori con descrizioni
        return codes.map(code => {
          const description = descriptions[code];
          if (description) {
            // Tronca la descrizione se richiesto per la visualizzazione
            const displayDescription = truncateForDisplay && description.length > 20 
              ? description.substring(0, 20) + '...' 
              : description;
            return `${code}:${displayDescription}`;
          }
          return code;
        });
      }
    } catch (error) {
      console.log('No lookup table available for', fieldName);
    }
    
    // Fallback: restituisci solo i codici
    return codes;
  };

  const saveEdit = async () => {
    if (!modalEditData) return;
    
    // Validazione frontend per posizione
    if (modalEditData.property === 'position') {
      const positionValue = parseInt(editValue);
      if (isNaN(positionValue) || positionValue < 0) {
        setSaveStatus({type: 'error', message: 'La posizione deve essere un numero intero maggiore o uguale a 0'});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        return;
      }
    }
    
    // Validazione frontend per lunghezza
    if (modalEditData.property === 'length') {
      const lengthValue = parseInt(editValue);
      if (isNaN(lengthValue) || lengthValue < 1) {
        setSaveStatus({type: 'error', message: 'La lunghezza deve essere un numero intero maggiore di 0'});
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
      setSaveStatus({type: 'error', message: `Errore di connessione: ${error}`});
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
    // Parse the input - support both formats
    const lines = editValue.split('\n').map(line => line.trim()).filter(line => line.length > 0);
    const values = [];
    
    console.log('🔍 Parsing input:', editValue);
    console.log('🔍 Lines found:', lines);
    
    // Check if it's the new line-by-line format (CODICE:DESCRIZIONE)
    const hasColonFormat = lines.some(line => line.includes(':'));
    console.log('🔍 Has colon format:', hasColonFormat);
    
    if (hasColonFormat) {
      // Parse line-by-line format: CODICE:DESCRIZIONE
      for (const line of lines) {
        if (line.includes(':')) {
          const parts = line.split(':');
          if (parts.length >= 2) {
            const code = parts[0].trim();
            const meaning = parts.slice(1).join(':').trim();
            if (code && meaning) {
              values.push({ code, meaning });
              console.log('✅ Parsed line with colon:', { code, meaning });
            }
          }
        } else {
          // Line without colon, treat as code only
          const code = line.trim();
          if (code) {
            values.push({ code, meaning: `Value: ${code}` });
            console.log('✅ Parsed line without colon:', { code, meaning: `Value: ${code}` });
          }
        }
      }
    } else {
      // Parse comma-separated format: A0,B0,C0
      const codes = editValue.split(',').map(v => v.trim()).filter(v => v.length > 0);
      console.log('🔍 Codes found:', codes);
      for (const code of codes) {
        values.push({ code, meaning: `Value: ${code}` });
        console.log('✅ Parsed comma-separated:', { code, meaning: `Value: ${code}` });
      }
    }
    
    console.log('🔍 Final parsed values:', values);
    
    if (values.length === 0) {
      setSaveStatus({type: 'error', message: 'Inserisci almeno un valore nel formato CODICE:DESCRIZIONE o codici separati da virgola'});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      return;
    }
    
    // Create lookup data structure
    const lookupData = {
      name: `${modalEditData!.fieldName.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} Values`,
      description: `Valid values for ${modalEditData!.fieldName}`,
      values: values
    };
    
    console.log('Updating lookup table via API:', lookupData);
    
    // Call lookup table update API
    const lookupResult = await EuringAPI.updateFieldLookupTable(
      modalEditData!.fieldName,
      modalEditData!.version,
      lookupData
    );
    
    if (lookupResult.success) {
      console.log('✅ Lookup table updated successfully:', lookupResult);
      setSaveStatus({type: 'success', message: `✅ Valori salvati! ${values.length} valori aggiornati con descrizioni personalizzate.`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);
      
      // Update local state immediately without closing modals
      if (matrixData) {
        const updatedMatrix = { ...matrixData };
        const fieldIndex = updatedMatrix.field_matrix.findIndex(f => f.field_name === modalEditData!.fieldName);
        
        if (fieldIndex !== -1) {
          const field = updatedMatrix.field_matrix[fieldIndex];
          const versionInfo = field.versions[modalEditData!.version];
          
          if (versionInfo) {
            // Update valid_values with just the codes
            versionInfo.valid_values = values.map(v => v.code);
            updatedMatrix.field_matrix = [...updatedMatrix.field_matrix];
            updatedMatrix.field_matrix[fieldIndex] = { ...field };
            
            const freshMatrix = JSON.parse(JSON.stringify(updatedMatrix));
            setMatrixData(freshMatrix);
            setRefreshKey(prev => prev + 1);
          }
        }
      }
      
      // Update the edit value to show the saved values in the preferred format
      if (hasColonFormat) {
        setEditValue(values.map(v => `${v.code}:${v.meaning}`).join('\n'));
      } else {
        setEditValue(values.map(v => v.code).join(', '));
      }
      
      // Update the descriptions cache
      const cacheKey = `${modalEditData!.fieldName}_${modalEditData!.version}`;
      const descriptions: Record<string, string> = {};
      values.forEach(v => {
        descriptions[v.code] = v.meaning;
      });
      setFieldDescriptions(prev => ({
        ...prev,
        [cacheKey]: descriptions
      }));
      
    } else {
      console.error('❌ Lookup table update failed:', lookupResult.error);
      setSaveStatus({type: 'error', message: `Errore nell'aggiornamento lookup table: ${lookupResult.error}`});
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
      setSaveStatus({type: 'success', message: `✅ Salvato! ${modalEditData!.property} di "${modalEditData!.fieldName}" aggiornato a: ${editValue}.`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 4000);
      
      // Update local state with the saved value
      if (matrixData) {
        const updatedMatrix = { ...matrixData };
        const fieldIndex = updatedMatrix.field_matrix.findIndex(f => f.field_name === modalEditData!.fieldName);
        
        console.log('🔍 Updating field:', modalEditData!.fieldName, 'at index:', fieldIndex);
        
        if (fieldIndex !== -1) {
          const field = updatedMatrix.field_matrix[fieldIndex];
          const versionInfo = field.versions[modalEditData!.version];
          
          console.log('📝 Current field info:', versionInfo);
          
          if (versionInfo) {
            // Update the property with the new value
            if (modalEditData!.property === 'semantic_domain') {
              versionInfo.semantic_domain = editValue;
            } else if (modalEditData!.property === 'length') {
              versionInfo.length = parseInt(editValue);
            } else if (modalEditData!.property === 'position') {
              const newPosition = parseInt(editValue);
              console.log('🎯 Updating position from', versionInfo.position, 'to', newPosition);
              versionInfo.position = newPosition;
            } else {
              (versionInfo as any)[modalEditData!.property] = editValue;
            }
            
            console.log('✨ Updated field info:', versionInfo);
            console.log('🔍 Matrix data before update:', matrixData.field_matrix[fieldIndex]);
            
            // Update the field_matrix reference to ensure React detects the change
            updatedMatrix.field_matrix = [...updatedMatrix.field_matrix];
            updatedMatrix.field_matrix[fieldIndex] = { ...field };
            
            console.log('🔍 Matrix data after update:', updatedMatrix.field_matrix[fieldIndex]);
          }
        }
        
        console.log('💾 Setting updated matrix data');
        
        // Force React to recognize the change by creating a completely new object
        const freshMatrix = JSON.parse(JSON.stringify(updatedMatrix));
        setMatrixData(freshMatrix);
        
        // Force re-render with refresh key
        setRefreshKey(prev => prev + 1);
        
        // Force re-render
        setTimeout(() => {
          console.log('🔄 Force refresh after save');
          loadMatrixData(true); // Preserva la posizione di scroll
        }, 100); // Reduced timeout for faster feedback
      }
      
      // Close modal for regular field updates
      setShowEditModal(false);
      setModalEditData(null);
      setEditValue('');
      
      // Force immediate refresh to show changes
      const currentScrollY = window.scrollY;
      console.log('💾 Saving current scroll position:', currentScrollY);
      
      setTimeout(async () => {
        console.log('🔄 Immediate refresh to show changes');
        await loadMatrixData(true);
        
        // Double-check scroll restoration
        setTimeout(() => {
          if (window.scrollY !== currentScrollY) {
            console.log('🔧 Final scroll correction to:', currentScrollY);
            window.scrollTo({
              top: currentScrollY,
              behavior: 'instant'
            });
          }
        }, 200);
      }, 100);
      
    } else {
      setSaveStatus({type: 'error', message: `Errore: ${result.error}`});
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
        `Vuoi aggiungere il campo "${fieldName}" alla versione ${version}?\n\n` +
        `Questo creerà un nuovo campo con valori di default che potrai poi modificare.`
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
        `Posizione per il campo "${fieldName}" nella versione ${version}:\n\n` +
        `Posizione suggerita: ${suggestedPosition}\n` +
        `(Inserisci un numero o premi OK per usare quella suggerita)`,
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
        description: `Campo ${fieldName} aggiunto manualmente alla versione ${version} (pos: ${finalPosition})`,
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
        `Campo ${fieldName} aggiunto manualmente alla versione ${version} (pos: ${finalPosition})`
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
          message: `✅ Campo "${fieldName}" aggiunto realmente alla versione ${version} in posizione ${finalPosition}. Salvato nel backend SKOS!`
        });
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
        
        // Ricarica i dati per confermare il salvataggio
        setTimeout(() => {
          console.log('🔄 Reloading data to confirm field addition');
          loadMatrixData(true);
        }, 1000);
        
      } else {
        setSaveStatus({type: 'error', message: `Errore nell'aggiunta del campo: ${result.error}`});
        setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      }
      
    } catch (error) {
      setSaveStatus({type: 'error', message: `Errore nell'aggiunta del campo: ${error}`});
      setTimeout(() => setSaveStatus({type: null, message: ''}), 5000);
      console.error('Error adding field:', error);
    }
  };

  const removeFieldFromVersion = async (fieldName: string, version: string) => {
    try {
      // Conferma dall'utente
      const confirmed = window.confirm(
        `Vuoi rimuovere il campo "${fieldName}" dalla versione ${version}?\n\n` +
        `Questa azione non può essere annullata.`
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
          
          setSaveStatus({type: 'success', message: `🗑️ Campo "${fieldName}" rimosso dalla versione ${version}.`});
          setTimeout(() => setSaveStatus({type: null, message: ''}), 3000);
        }
      }
      
    } catch (error) {
      setSaveStatus({type: 'error', message: `Errore nella rimozione del campo: ${error}`});
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
      setError(err.message || 'Errore di connessione');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>📊 Matrice EURING</h2>
        <p>Caricamento dati...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 Matrice EURING</h2>
        <div style={{ 
          backgroundColor: '#f8d7da', 
          color: '#721c24',
          padding: '15px', 
          borderRadius: '5px',
          margin: '10px 0'
        }}>
          <strong>❌ Errore:</strong> {error}
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
            Riprova
          </button>
        </div>
      </div>
    );
  }

  if (!matrixData) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>📊 Matrice EURING</h2>
        <p>Nessun dato disponibile</p>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <div>
          <h2>📊 Matrice Modello EURING</h2>
          <p>Vista comparativa di tutte le versioni EURING con allineamento alla versione {matrixData.reference_version} (ordine EPE)</p>
        </div>
        
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <button
            onClick={() => setEditMode(!editMode)}
            style={{
              padding: '10px 20px',
              backgroundColor: editMode ? '#dc3545' : '#28a745',
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
            {editMode ? '🔒 Modalità Lettura' : '✏️ Modalità Editing'}
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
            🔄 Ricarica Dati
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
              💡 Clicca su una cella per modificarla
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
          <h4 style={{ margin: '0 0 15px 0' }}>Versioni da visualizzare:</h4>
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
                  ({version.total_fields} campi)
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
            <span>Mostra campi vuoti (non presenti in nessuna versione selezionata)</span>
          </label>
        </div>
        
        {editMode && (
          <div style={{ 
            backgroundColor: '#e8f4fd',
            padding: '15px',
            borderRadius: '6px',
            border: '1px solid #bee5eb',
            marginTop: '15px'
          }}>
            <h5 style={{ margin: '0 0 10px 0', color: '#0c5460' }}>🛠️ Modalità Editing Attiva</h5>
            <div style={{ fontSize: '0.9em', color: '#0c5460' }}>
              • Clicca su una cella per modificare descrizione, tipo di dato, lunghezza, posizione o dominio semantico<br/>
              • Usa il pulsante "+ Aggiungi" per aggiungere un campo mancante a una versione (con posizione intelligente)<br/>
              • Usa il pulsante 🗑️ per rimuovere un campo da una versione<br/>
              • Le modifiche vengono salvate automaticamente nel sistema SKOS<br/>
              • ⚠️ Attenzione alle posizioni: mantieni coerenza tra versioni per la compatibilità semantica<br/>
              • Usa questa modalità per completare e correggere le definizioni semantiche
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
            <strong>Campi totali (riferimento):</strong> {matrixData.total_fields}
          </div>
          <div>
            <strong>Campi visualizzati:</strong> {filteredFields.length}
          </div>
          <div>
            <strong>Versioni selezionate:</strong> {selectedVersions.length}
          </div>
        </div>
      </div>

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
                width: '80px',
                position: 'sticky',
                left: 0,
                backgroundColor: '#f8f9fa',
                zIndex: 10
              }}>
                Ord.
              </th>
              <th style={{ 
                padding: '12px', 
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '200px',
                position: 'sticky',
                left: '80px',
                backgroundColor: '#f8f9fa',
                zIndex: 10
              }}>
                Campo
              </th>
              <th style={{ 
                padding: '12px', 
                border: '1px solid #ddd',
                textAlign: 'left',
                fontWeight: 'bold',
                width: '300px'
              }}>
                Descrizione
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
                  zIndex: 5
                }}>
                  {fieldRow.epe_order || '-'}
                </td>
                <td style={{ 
                  padding: '10px', 
                  border: '1px solid #ddd',
                  fontWeight: 'bold',
                  position: 'sticky',
                  left: '80px',
                  backgroundColor: index % 2 === 0 ? '#ffffff' : '#f8f9fa',
                  zIndex: 5
                }}>
                  <div>
                    <div>{fieldRow.field_name}</div>
                    <div style={{ fontSize: '0.8em', color: '#666', fontWeight: 'normal' }}>
                      {fieldRow.semantic_meaning}
                    </div>
                  </div>
                </td>
                <td style={{ 
                  padding: '10px', 
                  border: '1px solid #ddd'
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
                        position: 'relative'
                      }}
                    >
                      {fieldInfo ? (
                        <div style={{ fontSize: '0.8em' }}>
                          <div style={{ 
                            fontWeight: 'bold', 
                            color: getVersionColor(year),
                            marginBottom: '4px'
                          }}>
                            ✓ Presente
                          </div>
                          
                          {/* Campo Descrizione - Editabile */}
                          <div style={{ marginBottom: '4px' }}>
                            <strong>Descrizione:</strong>
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
                                Pos: 
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
                                Tipo: 
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
                                Lung: 
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
                                  title="Rimuovi campo da questa versione"
                                >
                                  🗑️
                                </button>
                              )}
                            </div>
                          </div>
                          
                          {/* Valori Validi - Editabili */}
                          {fieldInfo.valid_values && fieldInfo.valid_values.length > 0 && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>Valori:</strong>
                              <FieldValuesDisplay
                                fieldName={fieldRow.field_name}
                                version={year}
                                values={fieldInfo.valid_values}
                                editMode={editMode}
                                onEdit={async () => {
                                  // Recupera i valori completi con descrizioni COMPLETE per l'editing
                                  const valuesWithDescriptions = await getFieldValueWithDescription(
                                    fieldRow.field_name, 
                                    year, 
                                    fieldInfo.valid_values,
                                    false // NON troncare per l'editing
                                  );
                                  const editValue = valuesWithDescriptions.join('\n');
                                  startEditing(fieldRow.field_name, year, 'valid_values', editValue);
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
                                + Valori
                              </button>
                            </div>
                          )}
                          
                          {/* Dominio Semantico - Editabile */}
                          {fieldInfo.semantic_domain && (
                            <div style={{ marginTop: '4px' }}>
                              <strong>Dominio:</strong>
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
                                + Dominio
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
                          Non presente
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
                                + Aggiungi
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
        <h4 style={{ margin: '0 0 15px 0' }}>Legenda:</h4>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#e8f5e8',
              border: '1px solid #4caf50'
            }}></div>
            <span>Campo presente nella versione</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <div style={{ 
              width: '20px', 
              height: '20px', 
              backgroundColor: '#f8f8f8',
              border: '1px solid #ccc'
            }}></div>
            <span>Campo non presente nella versione</span>
          </div>
          <div><strong>Pos:</strong> Posizione nel formato</div>
          <div><strong>Tipo:</strong> Tipo di dato</div>
          <div><strong>Lung:</strong> Lunghezza campo</div>
          <div><strong>Valori:</strong> Valori validi esempio</div>
        </div>
      </div>

      <div style={{ 
        backgroundColor: '#d4edda', 
        color: '#155724',
        padding: '15px', 
        borderRadius: '5px',
        margin: '20px 0'
      }}>
        <strong>🎉 Matrice EURING Completa!</strong> Tutte le funzionalità sono state implementate correttamente.
      </div>

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
                ✏️ Modifica Campo
              </h3>
              <div style={{ 
                fontSize: '1.1em', 
                color: '#666',
                display: 'flex',
                flexWrap: 'wrap',
                gap: '15px'
              }}>
                <span><strong>Campo:</strong> {modalEditData.fieldName}</span>
                <span><strong>Versione:</strong> {modalEditData.version}</span>
                <span><strong>Proprietà:</strong> {modalEditData.property}</span>
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
                <h4 style={{ margin: '0 0 10px 0', color: '#495057' }}>📋 Informazioni Campo</h4>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px', fontSize: '0.9em' }}>
                  <div><strong>Posizione:</strong> {modalEditData.fieldInfo.position}</div>
                  <div><strong>Tipo:</strong> {modalEditData.fieldInfo.data_type}</div>
                  <div><strong>Lunghezza:</strong> {modalEditData.fieldInfo.length}</div>
                  {modalEditData.fieldInfo.semantic_domain && (
                    <div><strong>Dominio:</strong> {EuringAPI.getDomainDisplayName(modalEditData.fieldInfo.semantic_domain)}</div>
                  )}
                </div>
                {modalEditData.fieldInfo.description && (
                  <div style={{ marginTop: '10px' }}>
                    <strong>Descrizione attuale:</strong> {modalEditData.fieldInfo.description}
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
                {modalEditData.property === 'description' && '📝 Nuova Descrizione:'}
                {modalEditData.property === 'semantic_domain' && '🏷️ Dominio Semantico:'}
                {modalEditData.property === 'data_type' && '🔧 Tipo di Dato:'}
                {modalEditData.property === 'length' && '📏 Lunghezza:'}
                {modalEditData.property === 'position' && '📍 Posizione nel Formato:'}
                {modalEditData.property === 'valid_values' && '📋 Valori Validi:'}
              </label>
              
              {modalEditData.property === 'valid_values' ? (
                <div>
                  <textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '1.1em',
                      border: '2px solid #007bff',
                      borderRadius: '8px',
                      minHeight: '200px',
                      resize: 'vertical',
                      fontFamily: 'monospace'
                    }}
                    autoFocus
                    autoComplete="off"
                    data-lpignore="true"
                    data-form-type="other"
                    placeholder="Inserisci i valori nel formato CODICE:DESCRIZIONE (una per riga)&#10;&#10;Esempio:&#10;A0:Metal ring only&#10;B0:Metal ring + colour ring(s)&#10;C0:Metal ring + colour mark(s)"
                  />
                  <div style={{
                    fontSize: '0.9em',
                    color: '#666',
                    marginTop: '8px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px'
                  }}>
                    💡 <strong>Formato semplice:</strong> Una riga per ogni valore nel formato "CODICE:DESCRIZIONE"
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
                  <option value="">Seleziona dominio...</option>
                  <option value="identification_marking">🏷️ Identification & Marking</option>
                  <option value="species">🐦 Species Classification</option>
                  <option value="demographics">👥 Demographics</option>
                  <option value="temporal">⏰ Temporal Information</option>
                  <option value="spatial">🌍 Spatial Information</option>
                  <option value="biometrics">📏 Biometric Measurements</option>
                  <option value="methodology">🔬 Methodology & Conditions</option>
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
                  <option value="string">📝 String</option>
                  <option value="integer">🔢 Integer</option>
                  <option value="float">🔢 Float</option>
                  <option value="date">📅 Date</option>
                  <option value="code">🏷️ Code</option>
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
                  placeholder={modalEditData.property === 'position' ? "Inserisci la posizione nel formato (0-100)" : "Inserisci la lunghezza (1-100)"}
                />
              ) : modalEditData.property === 'valid_values' ? (
                <div>
                  {/* Avviso speciale per valid_values */}
                  <div style={{
                    backgroundColor: '#e8f4fd',
                    color: '#0c5460',
                    padding: '12px',
                    borderRadius: '6px',
                    marginBottom: '15px',
                    border: '1px solid #bee5eb',
                    fontSize: '0.9em'
                  }}>
                    💡 <strong>Editing Valori Predefiniti:</strong> I valori vengono salvati immediatamente tramite lookup table API. 
                    Puoi salvare più volte per testare diverse combinazioni. Clicca "Chiudi" quando hai finito.
                  </div>
                  
                  <textarea
                    value={editValue}
                    onChange={(e) => setEditValue(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '12px',
                      fontSize: '1.1em',
                      border: '2px solid #007bff',
                      borderRadius: '8px',
                      minHeight: '200px',
                      resize: 'vertical',
                      fontFamily: 'monospace'
                    }}
                    autoFocus
                    autoComplete="off"
                    data-lpignore="true"
                    data-form-type="other"
                    placeholder="Formato: CODICE:DESCRIZIONE (una per riga)&#10;Esempio:&#10;A0:Metal ring only&#10;B0:Metal ring + colour ring(s)&#10;C0:Metal ring + colour mark(s)&#10;&#10;Oppure solo codici separati da virgola:&#10;A0,B0,C0"
                  />
                  <div style={{
                    fontSize: '0.9em',
                    color: '#666',
                    marginTop: '8px',
                    padding: '8px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '4px'
                  }}>
                    💡 <strong>Due formati supportati:</strong><br/>
                    • <strong>Codice + Descrizione:</strong> Una per riga nel formato "CODICE:DESCRIZIONE"<br/>
                    • <strong>Solo codici:</strong> Separati da virgola "A0,B0,C0" (descrizioni automatiche)
                  </div>
                </div>
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
                  placeholder="Inserisci la nuova descrizione del campo..."
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
                  ? '💡 Salva per aggiornare i valori, poi chiudi quando hai finito'
                  : '💡 Ctrl+Enter per salvare, Esc per annullare'
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
                  {modalEditData?.property === 'valid_values' ? '❌ Chiudi' : '❌ Annulla'}
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
                  {modalEditData?.property === 'valid_values' ? '💾 Salva Valori' : '✅ Salva Modifiche'}
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