import React, { useState, useEffect } from 'react';
import { DomainEvolutionEntry } from '../types/euring-types';
import EuringAPI from '../services/api';
import './DomainComparison.css';

interface DomainComparisonProps {
  domain: string;
  version1: string;
  version2: string;
  evolutionEntries: DomainEvolutionEntry[];
  onClose: () => void;
}

interface ComparisonData {
  version1: DomainEvolutionEntry;
  version2: DomainEvolutionEntry;
  differences: {
    fieldsOnlyInV1: string[];
    fieldsOnlyInV2: string[];
    commonFields: string[];
    modifiedFields: string[];
  };
  evolutionPath: DomainEvolutionEntry[];
}

const DomainComparison: React.FC<DomainComparisonProps> = ({
  domain,
  version1,
  version2,
  evolutionEntries,
  onClose
}) => {
  const [comparisonData, setComparisonData] = useState<ComparisonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'fields' | 'evolution'>('overview');

  useEffect(() => {
    generateComparisonData();
  }, [version1, version2, evolutionEntries]);

  const generateComparisonData = () => {
    setLoading(true);
    
    try {
      const v1Entry = evolutionEntries.find(e => e.version === version1);
      const v2Entry = evolutionEntries.find(e => e.version === version2);
      
      if (!v1Entry || !v2Entry) {
        throw new Error('Version data not found');
      }

      // Calculate field differences
      const v1Fields = new Set([
        ...v1Entry.fields_added,
        ...v1Entry.fields_modified
      ]);
      
      const v2Fields = new Set([
        ...v2Entry.fields_added,
        ...v2Entry.fields_modified
      ]);

      const fieldsOnlyInV1 = Array.from(v1Fields).filter(field => !v2Fields.has(field));
      const fieldsOnlyInV2 = Array.from(v2Fields).filter(field => !v1Fields.has(field));
      const commonFields = Array.from(v1Fields).filter(field => v2Fields.has(field));
      
      // Find modified fields between versions
      const modifiedFields = commonFields.filter(field => 
        v1Entry.fields_modified.includes(field) || v2Entry.fields_modified.includes(field)
      );

      // Get evolution path between versions
      const sortedEntries = [...evolutionEntries].sort((a, b) => a.year - b.year);
      const v1Index = sortedEntries.findIndex(e => e.version === version1);
      const v2Index = sortedEntries.findIndex(e => e.version === version2);
      
      const startIndex = Math.min(v1Index, v2Index);
      const endIndex = Math.max(v1Index, v2Index);
      const evolutionPath = sortedEntries.slice(startIndex, endIndex + 1);

      setComparisonData({
        version1: v1Entry,
        version2: v2Entry,
        differences: {
          fieldsOnlyInV1,
          fieldsOnlyInV2,
          commonFields,
          modifiedFields
        },
        evolutionPath
      });
    } catch (error) {
      console.error('Error generating comparison data:', error);
    } finally {
      setLoading(false);
    }
  };

  const calculateCompatibilityScore = () => {
    if (!comparisonData) return 0;
    
    const { differences } = comparisonData;
    const totalFields = differences.fieldsOnlyInV1.length + 
                       differences.fieldsOnlyInV2.length + 
                       differences.commonFields.length;
    
    if (totalFields === 0) return 100;
    
    const compatibleFields = differences.commonFields.length;
    return Math.round((compatibleFields / totalFields) * 100);
  };

  const getCompatibilityLevel = (score: number) => {
    if (score >= 90) return { level: 'Eccellente', color: '#27ae60', icon: '🟢' };
    if (score >= 70) return { level: 'Buona', color: '#f39c12', icon: '🟡' };
    if (score >= 50) return { level: 'Parziale', color: '#e67e22', icon: '🟠' };
    return { level: 'Limitata', color: '#e74c3c', icon: '🔴' };
  };

  const getYearDifference = () => {
    if (!comparisonData) return 0;
    return Math.abs(comparisonData.version2.year - comparisonData.version1.year);
  };

  if (loading) {
    return (
      <div className="domain-comparison">
        <div className="comparison-header">
          <h3>🔍 Confronto Versioni</h3>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Generazione confronto...</p>
        </div>
      </div>
    );
  }

  if (!comparisonData) {
    return (
      <div className="domain-comparison">
        <div className="comparison-header">
          <h3>🔍 Confronto Versioni</h3>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>
        <div className="error-container">
          <p>❌ Errore nel caricamento dei dati di confronto</p>
        </div>
      </div>
    );
  }

  const compatibilityScore = calculateCompatibilityScore();
  const compatibility = getCompatibilityLevel(compatibilityScore);
  const yearDiff = getYearDifference();

  return (
    <div className="domain-comparison">
      <div className="comparison-header">
        <div className="comparison-title">
          <h3>🔍 Confronto Versioni - {EuringAPI.getDomainDisplayName(domain)}</h3>
          <div className="version-comparison-title">
            <span className="version-badge v1">{EuringAPI.getVersionDisplayName(version1)}</span>
            <span className="vs-indicator">vs</span>
            <span className="version-badge v2">{EuringAPI.getVersionDisplayName(version2)}</span>
          </div>
        </div>
        <button className="close-button" onClick={onClose}>✕</button>
      </div>

      <div className="comparison-navigation">
        <button
          className={`nav-tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          📊 Panoramica
        </button>
        <button
          className={`nav-tab ${activeTab === 'fields' ? 'active' : ''}`}
          onClick={() => setActiveTab('fields')}
        >
          📋 Campi
        </button>
        <button
          className={`nav-tab ${activeTab === 'evolution' ? 'active' : ''}`}
          onClick={() => setActiveTab('evolution')}
        >
          📈 Percorso Evolutivo
        </button>
      </div>

      <div className="comparison-content">
        {activeTab === 'overview' && (
          <div className="overview-tab">
            <div className="compatibility-summary">
              <div className="compatibility-score">
                <div className="score-circle" style={{ borderColor: compatibility.color }}>
                  <span className="score-number">{compatibilityScore}%</span>
                  <span className="score-label">Compatibilità</span>
                </div>
                <div className="compatibility-info">
                  <div className="compatibility-level">
                    <span className="level-icon">{compatibility.icon}</span>
                    <span className="level-text" style={{ color: compatibility.color }}>
                      {compatibility.level}
                    </span>
                  </div>
                  <div className="time-difference">
                    <span className="time-icon">⏰</span>
                    <span className="time-text">{yearDiff} anni di differenza</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="summary-stats">
              <div className="stat-card">
                <div className="stat-header">
                  <span className="stat-icon">🔗</span>
                  <h4>Campi Comuni</h4>
                </div>
                <div className="stat-value">{comparisonData.differences.commonFields.length}</div>
                <div className="stat-description">Campi presenti in entrambe le versioni</div>
              </div>

              <div className="stat-card">
                <div className="stat-header">
                  <span className="stat-icon">➕</span>
                  <h4>Solo in {EuringAPI.getVersionDisplayName(version2)}</h4>
                </div>
                <div className="stat-value">{comparisonData.differences.fieldsOnlyInV2.length}</div>
                <div className="stat-description">Campi aggiunti nella versione più recente</div>
              </div>

              <div className="stat-card">
                <div className="stat-header">
                  <span className="stat-icon">➖</span>
                  <h4>Solo in {EuringAPI.getVersionDisplayName(version1)}</h4>
                </div>
                <div className="stat-value">{comparisonData.differences.fieldsOnlyInV1.length}</div>
                <div className="stat-description">Campi rimossi nella versione più recente</div>
              </div>

              <div className="stat-card">
                <div className="stat-header">
                  <span className="stat-icon">🔄</span>
                  <h4>Campi Modificati</h4>
                </div>
                <div className="stat-value">{comparisonData.differences.modifiedFields.length}</div>
                <div className="stat-description">Campi con modifiche tra le versioni</div>
              </div>
            </div>

            <div className="version-details">
              <div className="version-detail-card">
                <h4>{EuringAPI.getVersionDisplayName(version1)} ({comparisonData.version1.year})</h4>
                <p className="version-summary">{comparisonData.version1.changes_summary}</p>
                <div className="version-changes">
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version1.fields_added.length}</span>
                    <span className="change-label">Aggiunti</span>
                  </div>
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version1.fields_removed.length}</span>
                    <span className="change-label">Rimossi</span>
                  </div>
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version1.fields_modified.length}</span>
                    <span className="change-label">Modificati</span>
                  </div>
                </div>
              </div>

              <div className="version-detail-card">
                <h4>{EuringAPI.getVersionDisplayName(version2)} ({comparisonData.version2.year})</h4>
                <p className="version-summary">{comparisonData.version2.changes_summary}</p>
                <div className="version-changes">
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version2.fields_added.length}</span>
                    <span className="change-label">Aggiunti</span>
                  </div>
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version2.fields_removed.length}</span>
                    <span className="change-label">Rimossi</span>
                  </div>
                  <div className="change-stat">
                    <span className="change-count">{comparisonData.version2.fields_modified.length}</span>
                    <span className="change-label">Modificati</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'fields' && (
          <div className="fields-tab">
            {comparisonData.differences.commonFields.length > 0 && (
              <div className="field-group common">
                <div className="field-group-header">
                  <span className="field-icon">🔗</span>
                  <h4>Campi Comuni ({comparisonData.differences.commonFields.length})</h4>
                </div>
                <div className="field-list">
                  {comparisonData.differences.commonFields.map(field => (
                    <span key={field} className="field-tag common">{field}</span>
                  ))}
                </div>
              </div>
            )}

            {comparisonData.differences.fieldsOnlyInV2.length > 0 && (
              <div className="field-group added">
                <div className="field-group-header">
                  <span className="field-icon">➕</span>
                  <h4>Solo in {EuringAPI.getVersionDisplayName(version2)} ({comparisonData.differences.fieldsOnlyInV2.length})</h4>
                </div>
                <div className="field-list">
                  {comparisonData.differences.fieldsOnlyInV2.map(field => (
                    <span key={field} className="field-tag added">{field}</span>
                  ))}
                </div>
              </div>
            )}

            {comparisonData.differences.fieldsOnlyInV1.length > 0 && (
              <div className="field-group removed">
                <div className="field-group-header">
                  <span className="field-icon">➖</span>
                  <h4>Solo in {EuringAPI.getVersionDisplayName(version1)} ({comparisonData.differences.fieldsOnlyInV1.length})</h4>
                </div>
                <div className="field-list">
                  {comparisonData.differences.fieldsOnlyInV1.map(field => (
                    <span key={field} className="field-tag removed">{field}</span>
                  ))}
                </div>
              </div>
            )}

            {comparisonData.differences.modifiedFields.length > 0 && (
              <div className="field-group modified">
                <div className="field-group-header">
                  <span className="field-icon">🔄</span>
                  <h4>Campi Modificati ({comparisonData.differences.modifiedFields.length})</h4>
                </div>
                <div className="field-list">
                  {comparisonData.differences.modifiedFields.map(field => (
                    <span key={field} className="field-tag modified">{field}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'evolution' && (
          <div className="evolution-tab">
            <div className="evolution-path-header">
              <h4>📈 Percorso Evolutivo</h4>
              <p>Cambiamenti tra {EuringAPI.getVersionDisplayName(version1)} e {EuringAPI.getVersionDisplayName(version2)}</p>
            </div>
            
            <div className="evolution-path">
              {comparisonData.evolutionPath.map((entry, index) => (
                <div key={entry.version} className="evolution-step">
                  <div className="step-marker">
                    <span className="step-year">{entry.year}</span>
                  </div>
                  <div className="step-content">
                    <h5>{EuringAPI.getVersionDisplayName(entry.version)}</h5>
                    <p>{entry.changes_summary}</p>
                    
                    {(entry.fields_added.length > 0 || entry.fields_removed.length > 0 || entry.fields_modified.length > 0) && (
                      <div className="step-changes">
                        {entry.fields_added.length > 0 && (
                          <div className="step-change-group">
                            <span className="change-type added">+{entry.fields_added.length}</span>
                            <span className="change-description">campi aggiunti</span>
                          </div>
                        )}
                        {entry.fields_removed.length > 0 && (
                          <div className="step-change-group">
                            <span className="change-type removed">-{entry.fields_removed.length}</span>
                            <span className="change-description">campi rimossi</span>
                          </div>
                        )}
                        {entry.fields_modified.length > 0 && (
                          <div className="step-change-group">
                            <span className="change-type modified">~{entry.fields_modified.length}</span>
                            <span className="change-description">campi modificati</span>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {index < comparisonData.evolutionPath.length - 1 && (
                    <div className="evolution-arrow">↓</div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DomainComparison;