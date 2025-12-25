import React, { useState } from 'react';
import { DomainEvolutionEntry } from '../types/euring-types';
import EuringAPI from '../services/api';
import './DomainEvolutionTimeline.css';

interface DomainEvolutionTimelineProps {
  domain: string;
  evolutionEntries: DomainEvolutionEntry[];
  onCompareVersions?: (version1: string, version2: string) => void;
}

const DomainEvolutionTimeline: React.FC<DomainEvolutionTimelineProps> = ({
  domain,
  evolutionEntries,
  onCompareVersions
}) => {
  const [selectedVersions, setSelectedVersions] = useState<string[]>([]);
  const [expandedEntries, setExpandedEntries] = useState<Set<string>>(new Set());

  const handleVersionSelect = (version: string) => {
    setSelectedVersions(prev => {
      if (prev.includes(version)) {
        return prev.filter(v => v !== version);
      } else if (prev.length < 2) {
        return [...prev, version];
      } else {
        // Replace the first selected version
        return [prev[1], version];
      }
    });
  };

  const handleCompare = () => {
    if (selectedVersions.length === 2 && onCompareVersions) {
      onCompareVersions(selectedVersions[0], selectedVersions[1]);
    }
  };

  const toggleExpanded = (version: string) => {
    setExpandedEntries(prev => {
      const newSet = new Set(prev);
      if (newSet.has(version)) {
        newSet.delete(version);
      } else {
        newSet.add(version);
      }
      return newSet;
    });
  };

  const getChangeTypeIcon = (changeType: 'added' | 'removed' | 'modified') => {
    switch (changeType) {
      case 'added': return '➕';
      case 'removed': return '➖';
      case 'modified': return '🔄';
      default: return '📝';
    }
  };

  const calculateChangeImpact = (entry: DomainEvolutionEntry) => {
    const totalChanges = entry.fields_added.length + entry.fields_removed.length + entry.fields_modified.length;
    if (totalChanges === 0) return 'none';
    if (totalChanges <= 2) return 'low';
    if (totalChanges <= 5) return 'medium';
    return 'high';
  };

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'none': return '#95a5a6';
      case 'low': return '#27ae60';
      case 'medium': return '#f39c12';
      case 'high': return '#e74c3c';
      default: return '#6c757d';
    }
  };

  // Sort entries by year (newest first for timeline display)
  const sortedEntries = [...evolutionEntries].sort((a, b) => b.year - a.year);

  return (
    <div className="evolution-timeline-container">
      <div className="timeline-header">
        <div className="timeline-title">
          <h4>📈 Evoluzione Storica - {EuringAPI.getDomainDisplayName(domain)}</h4>
          <p className="timeline-subtitle">
            Traccia i cambiamenti nel dominio attraverso {evolutionEntries.length} versioni EURING
          </p>
        </div>
        
        {selectedVersions.length === 2 && (
          <div className="comparison-controls">
            <div className="selected-versions">
              <span className="selected-version">{EuringAPI.getVersionDisplayName(selectedVersions[0])}</span>
              <span className="vs-indicator">vs</span>
              <span className="selected-version">{EuringAPI.getVersionDisplayName(selectedVersions[1])}</span>
            </div>
            <button 
              className="compare-button"
              onClick={handleCompare}
            >
              🔍 Confronta Versioni
            </button>
          </div>
        )}
      </div>

      <div className="evolution-timeline">
        <div className="timeline-line"></div>
        
        {sortedEntries.map((entry) => {
          const isExpanded = expandedEntries.has(entry.version);
          const isSelected = selectedVersions.includes(entry.version);
          const impact = calculateChangeImpact(entry);
          const totalChanges = entry.fields_added.length + entry.fields_removed.length + entry.fields_modified.length;

          return (
            <div 
              key={entry.version} 
              className={`timeline-entry ${isSelected ? 'selected' : ''} ${impact}`}
            >
              <div 
                className="timeline-marker"
                style={{ backgroundColor: getImpactColor(impact) }}
                onClick={() => handleVersionSelect(entry.version)}
              >
                <div className="marker-content">
                  <span className="marker-year">{entry.year}</span>
                  <div className="marker-indicator">
                    {isSelected && <span className="selection-check">✓</span>}
                  </div>
                </div>
              </div>

              <div className="timeline-content">
                <div className="entry-header" onClick={() => toggleExpanded(entry.version)}>
                  <div className="entry-title">
                    <h5>{EuringAPI.getVersionDisplayName(entry.version)}</h5>
                    <span className="entry-year">({entry.year})</span>
                  </div>
                  
                  <div className="entry-summary">
                    <span className="changes-count">
                      {totalChanges} {totalChanges === 1 ? 'cambiamento' : 'cambiamenti'}
                    </span>
                    <span 
                      className="impact-badge"
                      style={{ backgroundColor: getImpactColor(impact) }}
                    >
                      {impact === 'none' ? 'Nessun cambiamento' : 
                       impact === 'low' ? 'Impatto basso' :
                       impact === 'medium' ? 'Impatto medio' : 'Impatto alto'}
                    </span>
                    <button className="expand-button">
                      {isExpanded ? '▼' : '▶'}
                    </button>
                  </div>
                </div>

                <div className="entry-description">
                  <p>{entry.changes_summary}</p>
                </div>

                {isExpanded && (
                  <div className="entry-details">
                    {entry.fields_added.length > 0 && (
                      <div className="change-group added">
                        <div className="change-header">
                          <span className="change-icon">{getChangeTypeIcon('added')}</span>
                          <span className="change-label">Campi Aggiunti ({entry.fields_added.length})</span>
                        </div>
                        <div className="change-items">
                          {entry.fields_added.map(field => (
                            <span key={field} className="change-item added">{field}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {entry.fields_removed.length > 0 && (
                      <div className="change-group removed">
                        <div className="change-header">
                          <span className="change-icon">{getChangeTypeIcon('removed')}</span>
                          <span className="change-label">Campi Rimossi ({entry.fields_removed.length})</span>
                        </div>
                        <div className="change-items">
                          {entry.fields_removed.map(field => (
                            <span key={field} className="change-item removed">{field}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {entry.fields_modified.length > 0 && (
                      <div className="change-group modified">
                        <div className="change-header">
                          <span className="change-icon">{getChangeTypeIcon('modified')}</span>
                          <span className="change-label">Campi Modificati ({entry.fields_modified.length})</span>
                        </div>
                        <div className="change-items">
                          {entry.fields_modified.map(field => (
                            <span key={field} className="change-item modified">{field}</span>
                          ))}
                        </div>
                      </div>
                    )}

                    {entry.format_changes.length > 0 && (
                      <div className="change-group format">
                        <div className="change-header">
                          <span className="change-icon">📋</span>
                          <span className="change-label">Cambiamenti di Formato</span>
                        </div>
                        <div className="format-changes">
                          {entry.format_changes.map((change, changeIndex) => (
                            <div key={changeIndex} className="format-change">{change}</div>
                          ))}
                        </div>
                      </div>
                    )}

                    {entry.semantic_notes.length > 0 && (
                      <div className="semantic-notes">
                        <div className="notes-header">
                          <span className="notes-icon">📝</span>
                          <span className="notes-label">Note Semantiche</span>
                        </div>
                        <ul className="notes-list">
                          {entry.semantic_notes.map((note, noteIndex) => (
                            <li key={noteIndex} className="semantic-note">{note}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      <div className="timeline-legend">
        <h6>Legenda Impatto:</h6>
        <div className="legend-items">
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#95a5a6' }}></span>
            <span>Nessun cambiamento</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#27ae60' }}></span>
            <span>Impatto basso (1-2 cambiamenti)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#f39c12' }}></span>
            <span>Impatto medio (3-5 cambiamenti)</span>
          </div>
          <div className="legend-item">
            <span className="legend-color" style={{ backgroundColor: '#e74c3c' }}></span>
            <span>Impatto alto (6+ cambiamenti)</span>
          </div>
        </div>
        
        <div className="timeline-instructions">
          <p>💡 <strong>Istruzioni:</strong> Clicca sui marker per selezionare fino a 2 versioni da confrontare. Clicca sulle voci per espandere i dettagli.</p>
        </div>
      </div>
    </div>
  );
};

export default DomainEvolutionTimeline;