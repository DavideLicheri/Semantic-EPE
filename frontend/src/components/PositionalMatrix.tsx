import React, { useState, useMemo } from 'react';

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

// Callback type for editing a specific property
type EditPropertyCallback = (fieldName: string, version: string, property: string, currentValue: string) => void;

interface PositionalMatrixProps {
  fieldMatrix: FieldRow[];
  selectedVersions: string[];
  editMode: boolean;
  onEditProperty?: EditPropertyCallback;
}

const FIELD_COLORS = [
  '#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6',
  '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b',
  '#2980b9', '#27ae60', '#d35400', '#8e44ad', '#f1c40f',
  '#00bcd4', '#ff5722', '#607d8b', '#4caf50', '#ff9800',
  '#673ab7', '#009688', '#795548', '#03a9f4', '#cddc39',
  '#e91e63', '#00e676', '#ff6f00', '#304ffe', '#76ff03',
  '#d500f9', '#00b8d4', '#ff3d00', '#6200ea', '#aeea00',
  '#c51162', '#00bfa5', '#dd2c00', '#aa00ff', '#64dd17',
];

// Only store the identity of the selected field, not the data itself.
// fieldInfo and color are derived from current props on each render,
// so the panel survives data reloads after save.
interface SelectedFieldKey {
  fieldName: string;
  version: string;
}

interface SelectedField {
  fieldName: string;
  version: string;
  fieldInfo: FieldInfo;
  color: string;
}

const PositionalMatrix: React.FC<PositionalMatrixProps> = ({
  fieldMatrix,
  selectedVersions,
  editMode,
  onEditProperty,
}) => {
  const [hoveredField, setHoveredField] = useState<string | null>(null);
  const [showFieldNames, setShowFieldNames] = useState<boolean>(true);
  const [selectedFieldKey, setSelectedFieldKey] = useState<SelectedFieldKey | null>(null);
  const tableRef = React.useRef<HTMLTableElement>(null);

  // Build positional data for each version
  const positionalData = useMemo(() => {
    const data: Record<string, Array<{ charPos: number; fieldName: string; fieldInfo: FieldInfo; colorIndex: number } | null>> = {};
    let maxLength = 0;

    for (const version of selectedVersions) {
      const fields: Array<{ fieldName: string; fieldInfo: FieldInfo }> = [];
      for (const row of fieldMatrix) {
        const info = row.versions[version];
        if (info) {
          fields.push({ fieldName: row.field_name, fieldInfo: info });
        }
      }
      fields.sort((a, b) => a.fieldInfo.position - b.fieldInfo.position);

      const charMap: Array<{ charPos: number; fieldName: string; fieldInfo: FieldInfo; colorIndex: number } | null> = [];
      
      for (const { fieldName, fieldInfo } of fields) {
        const start = fieldInfo.position;
        const end = start + fieldInfo.length - 1;
        while (charMap.length <= end) charMap.push(null);
        const colorIndex = fields.indexOf(fields.find(f => f.fieldName === fieldName)!) % FIELD_COLORS.length;
        for (let i = start; i <= end; i++) {
          charMap[i] = { charPos: i, fieldName, fieldInfo, colorIndex };
        }
        if (end > maxLength) maxLength = end;
      }
      data[version] = charMap;
    }
    return { data, maxLength };
  }, [fieldMatrix, selectedVersions]);

  // Build legend data
  const legendData = useMemo(() => {
    const legends: Record<string, Array<{ fieldName: string; color: string; position: number; length: number; description: string; fieldInfo: FieldInfo }>> = {};
    for (const version of selectedVersions) {
      const fields: Array<{ fieldName: string; fieldInfo: FieldInfo }> = [];
      for (const row of fieldMatrix) {
        const info = row.versions[version];
        if (info) fields.push({ fieldName: row.field_name, fieldInfo: info });
      }
      fields.sort((a, b) => a.fieldInfo.position - b.fieldInfo.position);
      legends[version] = fields.map((f, idx) => ({
        fieldName: f.fieldName,
        color: FIELD_COLORS[idx % FIELD_COLORS.length],
        position: f.fieldInfo.position,
        length: f.fieldInfo.length,
        description: f.fieldInfo.description,
        fieldInfo: f.fieldInfo,
      }));
    }
    return legends;
  }, [fieldMatrix, selectedVersions]);

  const handleFieldSelect = (fieldName: string, version: string) => {
    // Always update selection, don't toggle off
    setSelectedFieldKey({ fieldName, version });
  };

  // Derive the full selectedField from current props data (survives reloads)
  const selectedField: SelectedField | null = useMemo(() => {
    if (!selectedFieldKey) return null;
    const { fieldName, version } = selectedFieldKey;
    const legend = legendData[version];
    if (!legend) return null;
    const item = legend.find(l => l.fieldName === fieldName);
    if (!item) return null;
    return { fieldName, version, fieldInfo: item.fieldInfo, color: item.color };
  }, [selectedFieldKey, legendData]);

  // Build field connections between versions
  // REMOVED: Arrow connections feature was abandoned by user


  if (selectedVersions.length === 0) {
    return <div style={{ padding: '20px', color: '#666' }}>Seleziona almeno una versione.</div>;
  }

  const { data, maxLength } = positionalData;
  const isSelected = (fn: string, v: string) => selectedField?.fieldName === fn && selectedField?.version === v;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* Field Detail Panel - ALWAYS VISIBLE AT TOP */}
      <div style={{
        width: '100%',
        backgroundColor: selectedField ? '#fff' : '#f8f9fa',
        border: selectedField ? '2px solid #007bff' : '2px solid #dee2e6',
        borderRadius: '8px',
        padding: '20px',
        boxShadow: selectedField ? '0 4px 12px rgba(0,123,255,0.15)' : 'none',
        minHeight: '120px',
        transition: 'all 0.3s ease',
      }}>
        {selectedField ? (
          <>
            {/* Header */}
            <div style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '15px',
              paddingBottom: '12px',
              borderBottom: '2px solid #e9ecef',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{
                  display: 'inline-block',
                  width: '20px',
                  height: '20px',
                  backgroundColor: selectedField.color,
                  borderRadius: '4px',
                }} />
                <span style={{ fontWeight: 'bold', fontSize: '1.1em', color: '#2c3e50' }}>{selectedField.fieldName}</span>
                <span style={{
                  display: 'inline-block',
                  padding: '4px 12px',
                  backgroundColor: '#e9ecef',
                  borderRadius: '12px',
                  fontSize: '0.85em',
                  color: '#555',
                }}>EURING {selectedField.version}</span>
              </div>
              <button onClick={() => setSelectedFieldKey(null)} style={{
                background: '#dc3545',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontSize: '1em',
                padding: '6px 12px',
                fontWeight: '500',
              }}>✕ Chiudi</button>
            </div>

            {/* Properties grid */}
            <FieldPropertiesGrid field={selectedField} editMode={editMode} onEditProperty={onEditProperty} />
          </>
        ) : (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            height: '80px',
            color: '#6c757d',
            fontSize: '1em',
          }}>
            <span>👆 Clicca su un campo nella matrice per visualizzarne i dettagli</span>
          </div>
        )}
      </div>

      {/* Matrix + Legend */}
      <div style={{ width: '100%' }}>
        {/* Controls */}
        <div style={{
          display: 'flex', gap: '15px', alignItems: 'center', marginBottom: '15px',
          padding: '10px', backgroundColor: '#f8f9fa', borderRadius: '6px',
        }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer' }}>
            <input type="checkbox" checked={showFieldNames} onChange={(e) => setShowFieldNames(e.target.checked)} />
            Mostra nomi campi
          </label>
          <span style={{ color: '#666', fontSize: '0.9em' }}>Max: {maxLength} car.</span>
          {selectedField && (
            <button onClick={() => setSelectedFieldKey(null)} style={{
              padding: '4px 10px', backgroundColor: '#dc3545', color: 'white',
              border: 'none', borderRadius: '4px', fontSize: '0.8em', cursor: 'pointer',
            }}>✕ Chiudi dettagli</button>
          )}
        </div>

        {/* Matrix Table */}
        <div style={{ position: 'relative', overflowX: 'auto', border: '1px solid #ddd', borderRadius: '8px' }}>
          <table ref={tableRef} style={{ borderCollapse: 'collapse', width: 'auto' }}>
            <thead>
              <tr>
                <th style={{
                  padding: '6px 10px', border: '1px solid #ddd', backgroundColor: '#f8f9fa',
                  position: 'sticky', left: 0, zIndex: 10, fontSize: '0.8em', fontWeight: 'bold',
                  minWidth: '50px', textAlign: 'center',
                }}>Pos</th>
                {selectedVersions.map((year, idx) => (
                  <React.Fragment key={year}>
                    <th style={{
                      padding: '6px 12px', border: '1px solid #ddd', backgroundColor: '#f8f9fa',
                      fontWeight: 'bold', textAlign: 'center', fontSize: '0.9em',
                      minWidth: showFieldNames ? '140px' : '40px',
                    }}>{year}</th>
                    {/* Spacer column between versions (except after last) */}
                    {idx < selectedVersions.length - 1 && (
                      <th style={{
                        padding: '0', border: 'none', backgroundColor: 'transparent',
                        width: '40px', minWidth: '40px', maxWidth: '40px',
                      }}></th>
                    )}
                  </React.Fragment>
                ))}
              </tr>
            </thead>
            <tbody>
              {Array.from({ length: maxLength }, (_, i) => i + 1).map(charPos => (
                <tr key={charPos} style={{ height: '22px' }}>
                  <td style={{
                    padding: '2px 6px', border: '1px solid #eee', backgroundColor: '#f8f9fa',
                    position: 'sticky', left: 0, zIndex: 5, fontSize: '0.75em',
                    textAlign: 'center', color: '#666', fontFamily: 'monospace',
                  }}>{charPos}</td>
                  {selectedVersions.map((year, idx) => {
                    const cell = data[year]?.[charPos];
                    
                    return (
                      <React.Fragment key={year}>
                        {/* Version column */}
                        {!cell ? (
                          <td style={{ padding: '2px', border: '1px solid #f0f0f0', backgroundColor: '#fafafa' }} />
                        ) : (
                          <td style={{
                            padding: '1px 3px',
                            backgroundColor: isSelected(cell.fieldName, year) ? FIELD_COLORS[cell.colorIndex] : hoveredField === `${cell.fieldName}_${year}` ? `${FIELD_COLORS[cell.colorIndex]}60` : `${FIELD_COLORS[cell.colorIndex]}30`,
                            borderTop: cell.fieldInfo.position === charPos ? `2px solid ${FIELD_COLORS[cell.colorIndex]}` : `1px solid ${FIELD_COLORS[cell.colorIndex]}20`,
                            borderBottom: cell.fieldInfo.position + cell.fieldInfo.length - 1 === charPos ? `2px solid ${FIELD_COLORS[cell.colorIndex]}` : `1px solid ${FIELD_COLORS[cell.colorIndex]}20`,
                            borderLeft: `1px solid ${FIELD_COLORS[cell.colorIndex]}40`,
                            borderRight: `1px solid ${FIELD_COLORS[cell.colorIndex]}40`,
                            cursor: 'pointer',
                            color: isSelected(cell.fieldName, year) || hoveredField === `${cell.fieldName}_${year}` ? 'white' : FIELD_COLORS[cell.colorIndex],
                            fontSize: '0.7em', fontFamily: 'monospace',
                            fontWeight: cell.fieldInfo.position === charPos ? 'bold' : 'normal',
                            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                            maxWidth: showFieldNames ? '140px' : '40px',
                            transition: 'background-color 0.15s',
                            outline: isSelected(cell.fieldName, year) ? `2px solid ${FIELD_COLORS[cell.colorIndex]}` : 'none',
                          }}
                            onMouseEnter={() => setHoveredField(`${cell.fieldName}_${year}`)}
                            onMouseLeave={() => setHoveredField(null)}
                            onClick={() => handleFieldSelect(cell.fieldName, year)}
                            title={`${cell.fieldName}: ${cell.fieldInfo.description}`}
                          >
                            {cell.fieldInfo.position === charPos && showFieldNames ? cell.fieldInfo.name : ''}
                          </td>
                        )}
                        
                        {/* Spacer column between versions (except after last) */}
                        {idx < selectedVersions.length - 1 && (
                          <td style={{
                            padding: '0', border: 'none', backgroundColor: 'transparent',
                            width: '40px', minWidth: '40px', maxWidth: '40px',
                            position: 'relative',
                          }} />
                        )}
                      </React.Fragment>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div style={{
          marginTop: '20px', display: 'grid',
          gridTemplateColumns: `repeat(${Math.min(selectedVersions.length, 4)}, 1fr)`, gap: '15px',
        }}>
          {selectedVersions.map(year => (
            <div key={year} style={{
              backgroundColor: '#f8f9fa', padding: '12px', borderRadius: '8px', border: '1px solid #e9ecef',
            }}>
              <h4 style={{ margin: '0 0 10px 0', fontSize: '1em' }}>EURING {year}</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '3px' }}>
                {legendData[year]?.map((item, idx) => {
                  const sel = isSelected(item.fieldName, year);
                  return (
                    <div key={idx} style={{
                      display: 'flex', alignItems: 'center', gap: '6px',
                      fontSize: '0.78em', fontFamily: 'monospace',
                      cursor: 'pointer', padding: '3px 5px', borderRadius: '3px',
                      backgroundColor: sel ? `${item.color}30` : hoveredField === `${item.fieldName}_${year}` ? `${item.color}15` : 'transparent',
                      border: sel ? `2px solid ${item.color}` : '2px solid transparent',
                    }}
                      onMouseEnter={() => setHoveredField(`${item.fieldName}_${year}`)}
                      onMouseLeave={() => setHoveredField(null)}
                      onClick={() => handleFieldSelect(item.fieldName, year)}
                    >
                      <span style={{
                        display: 'inline-block', width: '12px', height: '12px',
                        backgroundColor: item.color, borderRadius: '2px', flexShrink: 0,
                      }} />
                      <span style={{ color: '#333' }}>{item.position}-{item.position + item.length - 1}</span>
                      <span style={{ color: '#666' }}>{item.fieldName}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};


// Helper component for field properties grid
const FieldPropertiesGrid: React.FC<{
  field: SelectedField;
  editMode: boolean;
  onEditProperty?: EditPropertyCallback;
}> = ({ field, editMode, onEditProperty }) => {
  const properties = [
    { key: 'description', label: 'Descrizione', value: field.fieldInfo.description || '' },
    { key: 'data_type', label: 'Tipo dato', value: field.fieldInfo.data_type || '' },
    { key: 'length', label: 'Lunghezza', value: String(field.fieldInfo.length || '') },
    { key: 'position', label: 'Posizione', value: String(field.fieldInfo.position || '') },
    { key: 'semantic_domain', label: 'Dominio semantico', value: field.fieldInfo.semantic_domain || '' },
    { key: 'valid_values', label: 'Valori validi', value: Array.isArray(field.fieldInfo.valid_values) ? field.fieldInfo.valid_values.join(', ') : '' },
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
      gap: '15px',
    }}>
      {properties.map(prop => (
        <div key={prop.key} style={{
          padding: '12px 15px',
          backgroundColor: '#f8f9fa',
          borderRadius: '6px',
          border: '1px solid #e9ecef',
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '6px',
          }}>
            <span style={{
              fontSize: '0.75em',
              color: '#6c757d',
              fontWeight: '600',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
            }}>
              {prop.label}
            </span>
            {editMode && onEditProperty && prop.key !== 'valid_values' && (
              <button
                onClick={() => onEditProperty(field.fieldName, field.version, prop.key, prop.value)}
                style={{
                  background: 'none',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  cursor: 'pointer',
                  padding: '2px 8px',
                  fontSize: '0.75em',
                  color: '#555',
                }}
                title={`Modifica ${prop.label}`}
              >✏️</button>
            )}
          </div>
          <div style={{
            fontSize: '0.9em',
            color: '#2c3e50',
            wordBreak: 'break-word',
            fontWeight: '500',
          }}>
            {prop.value || <span style={{ color: '#bbb', fontStyle: 'italic' }}>—</span>}
            {prop.key === 'valid_values' && field.fieldInfo.valid_values_count != null && field.fieldInfo.valid_values_count > 0 && (
              <span style={{ color: '#6c757d', fontSize: '0.85em', marginLeft: '8px' }}>
                ({field.fieldInfo.valid_values_count} valori)
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};


// ConnectionsOverlay Component - REMOVED: Feature was abandoned by user


export default PositionalMatrix;
