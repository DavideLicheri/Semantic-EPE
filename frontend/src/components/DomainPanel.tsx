import { useState, useEffect } from 'react';
import EuringAPI from '../services/api';
import { DomainInfo, DomainEvolutionData, DomainDocumentationResponse } from '../types/euring-types';
import { DomainFieldsResponse, DomainCompatibilityResponse } from '../types/api-types';
import DomainEvolutionTimeline from './DomainEvolutionTimeline';
import DomainComparison from './DomainComparison';
import DomainEvolutionCharts from './DomainEvolutionCharts';
import './DomainPanel.css';

interface DomainPanelProps {
  // No props needed for now
}

const DomainPanel: React.FC<DomainPanelProps> = () => {
  const [domains, setDomains] = useState<DomainInfo[]>([]);
  const [selectedDomain, setSelectedDomain] = useState<string | null>(null);
  const [domainEvolution, setDomainEvolution] = useState<DomainEvolutionData | null>(null);
  const [domainDocumentation, setDomainDocumentation] = useState<DomainDocumentationResponse['documentation'] | null>(null);
  const [domainFields, setDomainFields] = useState<DomainFieldsResponse | null>(null);
  const [domainCompatibility, setDomainCompatibility] = useState<DomainCompatibilityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [evolutionLoading, setEvolutionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'overview' | 'evolution' | 'charts' | 'documentation' | 'analysis' | 'compatibility' | 'export'>('overview');
  const [comparisonVersions, setComparisonVersions] = useState<{ version1: string; version2: string } | null>(null);
  const [compatibilityVersions, setCompatibilityVersions] = useState<{ fromVersion: string; toVersion: string }>({ fromVersion: '1966', toVersion: '2020' });
  const [exportOptions, setExportOptions] = useState({
    format: 'json',
    includeEvolution: true,
    includeFieldAnalysis: true,
    includeCompatibility: true
  });

  // Load domains list on component mount
  useEffect(() => {
    loadDomains();
  }, []);

  // Load domain-specific data when domain is selected
  useEffect(() => {
    if (selectedDomain) {
      loadDomainData(selectedDomain);
    }
  }, [selectedDomain, activeView]);

  const loadDomains = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await EuringAPI.getDomainsList();
      
      if (response.success && response.domains) {
        setDomains(response.domains);
      } else {
        setError(response.error || 'Failed to load domains');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load domains');
    } finally {
      setLoading(false);
    }
  };

  const loadDomainData = async (domain: string) => {
    try {
      setEvolutionLoading(true);
      setError(null);

      if (activeView === 'evolution') {
        const evolutionResponse = await EuringAPI.getDomainEvolution(domain);
        if (evolutionResponse.success && evolutionResponse.evolution_data) {
          setDomainEvolution(evolutionResponse.evolution_data);
        } else {
          setError(evolutionResponse.error || 'Failed to load domain evolution');
        }
      } else if (activeView === 'charts') {
        // Charts use the same evolution data as timeline
        const evolutionResponse = await EuringAPI.getDomainEvolution(domain);
        if (evolutionResponse.success && evolutionResponse.evolution_data) {
          setDomainEvolution(evolutionResponse.evolution_data);
        } else {
          setError(evolutionResponse.error || 'Failed to load domain evolution');
        }
      } else if (activeView === 'documentation') {
        const docResponse = await EuringAPI.getDomainDocumentation(domain);
        if (docResponse.success && docResponse.documentation) {
          setDomainDocumentation(docResponse.documentation);
        } else {
          setError(docResponse.error || 'Failed to load domain documentation');
        }
      } else if (activeView === 'analysis') {
        const fieldsResponse = await EuringAPI.getDomainFields(domain);
        if (fieldsResponse.success) {
          setDomainFields(fieldsResponse);
        } else {
          setError(fieldsResponse.error || 'Failed to load domain field analysis');
        }
      } else if (activeView === 'compatibility') {
        const compatibilityResponse = await EuringAPI.getDomainCompatibility(
          domain, 
          compatibilityVersions.fromVersion, 
          compatibilityVersions.toVersion
        );
        if (compatibilityResponse.success) {
          setDomainCompatibility(compatibilityResponse);
        } else {
          setError(compatibilityResponse.error || 'Failed to load domain compatibility');
        }
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load domain data');
    } finally {
      setEvolutionLoading(false);
    }
  };

  const handleDomainSelect = (domain: string) => {
    setSelectedDomain(domain);
    setDomainEvolution(null);
    setDomainDocumentation(null);
    setDomainFields(null);
    setDomainCompatibility(null);
    setActiveView('overview');
  };

  const handleViewChange = (view: 'overview' | 'evolution' | 'charts' | 'documentation' | 'analysis' | 'compatibility' | 'export') => {
    setActiveView(view);
    setDomainEvolution(null);
    setDomainDocumentation(null);
    setDomainFields(null);
    setDomainCompatibility(null);
    setComparisonVersions(null); // Clear any active comparison
  };

  const handleCompareVersions = (version1: string, version2: string) => {
    setComparisonVersions({ version1, version2 });
  };

  const handleCloseComparison = () => {
    setComparisonVersions(null);
  };

  const getComplexityColor = (complexity: string) => {
    switch (complexity.toLowerCase()) {
      case 'low': return '#4CAF50';
      case 'medium': return '#FF9800';
      case 'high': return '#F44336';
      case 'very high': return '#4CAF50';
      default: return '#757575';
    }
  };

  const getStabilityColor = (score: number) => {
    if (score >= 7) return '#4CAF50';
    if (score >= 5) return '#FF9800';
    if (score >= 3) return '#F44336';
    return '#4CAF50';
  };

  if (loading) {
    return (
      <div className="domain-panel">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Caricamento domini semantici...</p>
        </div>
      </div>
    );
  }

  if (error && !domains.length) {
    return (
      <div className="domain-panel">
        <div className="error-container">
          <h3>❌ Errore</h3>
          <p>{error}</p>
          <button onClick={loadDomains} className="retry-button">
            Riprova
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="domain-panel">
      <div className="domain-header">
        <h2>🔍 Analisi Domini Semantici EURING</h2>
        <p className="domain-subtitle">
          Esplora l'evoluzione storica dei 7 domini semantici del codice EURING
        </p>
      </div>

      {!selectedDomain ? (
        // Domain Selection View
        <div className="domain-selection">
          <div className="domain-grid">
            {domains.map((domain) => (
              <div
                key={domain.domain}
                className="domain-card"
                onClick={() => handleDomainSelect(domain.domain)}
                style={{ borderColor: domain.color }}
              >
                <div className="domain-card-header">
                  <span className="domain-icon" style={{ fontSize: '2rem' }}>
                    {domain.icon}
                  </span>
                  <h3 className="domain-name">{domain.name}</h3>
                </div>
                
                <p className="domain-description">{domain.description}</p>
                
                <div className="domain-stats">
                  <div className="stat-item">
                    <span className="stat-label">Campi Totali:</span>
                    <span className="stat-value">{domain.statistics.total_fields}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Copertura:</span>
                    <span className="stat-value">{domain.statistics.coverage_percentage}%</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Complessità:</span>
                    <span 
                      className="stat-value complexity-badge"
                      style={{ backgroundColor: getComplexityColor(domain.complexity) }}
                    >
                      {domain.complexity}
                    </span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Stabilità:</span>
                    <span 
                      className="stat-value stability-badge"
                      style={{ backgroundColor: getStabilityColor(domain.stability_score) }}
                    >
                      {domain.stability_score}/10
                    </span>
                  </div>
                </div>

                <div className="domain-features">
                  {domain.has_evolution_data && (
                    <span className="feature-badge evolution">📈 Evoluzione</span>
                  )}
                  <span className="feature-badge versions">
                    📋 {domain.statistics.versions_present}/{domain.statistics.total_versions} Versioni
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        // Domain Detail View
        <div className="domain-detail">
          <div className="domain-detail-header">
            <button 
              className="back-button"
              onClick={() => setSelectedDomain(null)}
            >
              ← Torna ai Domini
            </button>
            
            <div className="selected-domain-info">
              <span className="selected-domain-icon">
                {EuringAPI.getDomainIcon(selectedDomain)}
              </span>
              <h3>{EuringAPI.getDomainDisplayName(selectedDomain)}</h3>
            </div>
          </div>

          <div className="domain-navigation">
            <button
              className={`nav-button ${activeView === 'overview' ? 'active' : ''}`}
              onClick={() => handleViewChange('overview')}
            >
              📊 Panoramica
            </button>
            <button
              className={`nav-button ${activeView === 'evolution' ? 'active' : ''}`}
              onClick={() => handleViewChange('evolution')}
            >
              📈 Evoluzione
            </button>
            <button
              className={`nav-button ${activeView === 'charts' ? 'active' : ''}`}
              onClick={() => handleViewChange('charts')}
            >
              📊 Grafici
            </button>
            <button
              className={`nav-button ${activeView === 'analysis' ? 'active' : ''}`}
              onClick={() => handleViewChange('analysis')}
            >
              🔍 Analisi Campi
            </button>
            <button
              className={`nav-button ${activeView === 'compatibility' ? 'active' : ''}`}
              onClick={() => handleViewChange('compatibility')}
            >
              ⚖️ Compatibilità
            </button>
            <button
              className={`nav-button ${activeView === 'export' ? 'active' : ''}`}
              onClick={() => handleViewChange('export')}
            >
              📤 Esporta
            </button>
            <button
              className={`nav-button ${activeView === 'documentation' ? 'active' : ''}`}
              onClick={() => handleViewChange('documentation')}
            >
              📚 Documentazione
            </button>
          </div>

          <div className="domain-content">
            {evolutionLoading ? (
              <div className="loading-container">
                <div className="loading-spinner"></div>
                <p>Caricamento dati del dominio...</p>
              </div>
            ) : error ? (
              <div className="error-container">
                <h4>❌ Errore nel caricamento</h4>
                <p>{error}</p>
                <button 
                  onClick={() => loadDomainData(selectedDomain)}
                  className="retry-button"
                >
                  Riprova
                </button>
              </div>
            ) : (
              <>
                {activeView === 'overview' && (
                  <div className="domain-overview">
                    {domains.find(d => d.domain === selectedDomain) && (
                      <div className="overview-content">
                        <div className="overview-stats">
                          <div className="stat-card">
                            <h4>📊 Statistiche Generali</h4>
                            <div className="stat-grid">
                              <div className="stat-item">
                                <span className="stat-number">
                                  {domains.find(d => d.domain === selectedDomain)?.statistics.total_fields}
                                </span>
                                <span className="stat-label">Campi Totali</span>
                              </div>
                              <div className="stat-item">
                                <span className="stat-number">
                                  {domains.find(d => d.domain === selectedDomain)?.statistics.versions_present}
                                </span>
                                <span className="stat-label">Versioni Presenti</span>
                              </div>
                              <div className="stat-item">
                                <span className="stat-number">
                                  {domains.find(d => d.domain === selectedDomain)?.statistics.coverage_percentage}%
                                </span>
                                <span className="stat-label">Copertura</span>
                              </div>
                            </div>
                          </div>

                          <div className="stat-card">
                            <h4>📋 Distribuzione per Versione</h4>
                            <div className="version-distribution">
                              {Object.entries(
                                domains.find(d => d.domain === selectedDomain)?.statistics.field_counts_by_version || {}
                              ).map(([version, count]) => (
                                <div key={version} className="version-bar">
                                  <span className="version-label">{EuringAPI.getVersionDisplayName(version)}</span>
                                  <div className="bar-container">
                                    <div 
                                      className="bar-fill"
                                      style={{ 
                                        width: `${(count / Math.max(...Object.values(
                                          domains.find(d => d.domain === selectedDomain)?.statistics.field_counts_by_version || {}
                                        ))) * 100}%` 
                                      }}
                                    ></div>
                                    <span className="bar-value">{count}</span>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>

                        <div className="overview-description">
                          <h4>📝 Descrizione del Dominio</h4>
                          <p>{domains.find(d => d.domain === selectedDomain)?.description}</p>
                          
                          <div className="domain-properties">
                            <div className="property-item">
                              <span className="property-label">Complessità:</span>
                              <span 
                                className="property-value complexity-badge"
                                style={{ 
                                  backgroundColor: getComplexityColor(
                                    domains.find(d => d.domain === selectedDomain)?.complexity || 'medium'
                                  ) 
                                }}
                              >
                                {domains.find(d => d.domain === selectedDomain)?.complexity}
                              </span>
                            </div>
                            <div className="property-item">
                              <span className="property-label">Stabilità:</span>
                              <span 
                                className="property-value stability-badge"
                                style={{ 
                                  backgroundColor: getStabilityColor(
                                    domains.find(d => d.domain === selectedDomain)?.stability_score || 5
                                  ) 
                                }}
                              >
                                {domains.find(d => d.domain === selectedDomain)?.stability_score}/10
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeView === 'evolution' && domainEvolution && (
                  <DomainEvolutionTimeline
                    domain={selectedDomain}
                    evolutionEntries={domainEvolution.evolution_entries}
                    onCompareVersions={handleCompareVersions}
                  />
                )}

                {activeView === 'charts' && domainEvolution && (
                  <DomainEvolutionCharts
                    domain={selectedDomain}
                    evolutionEntries={domainEvolution.evolution_entries}
                  />
                )}

                {activeView === 'documentation' && domainDocumentation && (
                  <div className="domain-documentation">
                    <div className="doc-section">
                      <h4>📚 Informazioni del Dominio</h4>
                      <div className="doc-content">
                        <h5>{domainDocumentation.domain_info.name}</h5>
                        <p><strong>Scopo:</strong> {domainDocumentation.domain_info.purpose}</p>
                        <p><strong>Descrizione:</strong> {domainDocumentation.domain_info.description}</p>
                        
                        <div className="key-concepts">
                          <h6>🔑 Concetti Chiave:</h6>
                          <div className="concept-tags">
                            {domainDocumentation.domain_info.key_concepts.map(concept => (
                              <span key={concept} className="concept-tag">{concept}</span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="doc-section">
                      <h4>📊 Statistiche Documentazione</h4>
                      <div className="doc-stats">
                        <div className="doc-stat">
                          <span className="doc-stat-number">{domainDocumentation.statistics.total_versions}</span>
                          <span className="doc-stat-label">Versioni Totali</span>
                        </div>
                        <div className="doc-stat">
                          <span className="doc-stat-number">{domainDocumentation.statistics.versions_with_domain}</span>
                          <span className="doc-stat-label">Versioni con Dominio</span>
                        </div>
                        <div className="doc-stat">
                          <span className="doc-stat-number">{domainDocumentation.statistics.total_fields_across_versions}</span>
                          <span className="doc-stat-label">Campi Totali</span>
                        </div>
                        <div className="doc-stat">
                          <span className="doc-stat-number">{domainDocumentation.statistics.evolution_entries}</span>
                          <span className="doc-stat-label">Voci Evoluzione</span>
                        </div>
                      </div>
                    </div>

                    {domainDocumentation.usage_guidelines.length > 0 && (
                      <div className="doc-section">
                        <h4>💡 Linee Guida d'Uso</h4>
                        <ul className="usage-guidelines">
                          {domainDocumentation.usage_guidelines.map((guideline, index) => (
                            <li key={index}>{guideline}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {domainDocumentation.related_domains.length > 0 && (
                      <div className="doc-section">
                        <h4>🔗 Domini Correlati</h4>
                        <div className="related-domains">
                          {domainDocumentation.related_domains.map(relatedDomain => (
                            <button
                              key={relatedDomain}
                              className="related-domain-button"
                              onClick={() => handleDomainSelect(relatedDomain)}
                            >
                              {EuringAPI.getDomainIcon(relatedDomain)} {EuringAPI.getDomainDisplayName(relatedDomain)}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {activeView === 'analysis' && domainFields && (
                  <div className="domain-analysis">
                    <div className="analysis-header">
                      <h4>🔍 Analisi Semantica dei Campi</h4>
                      <p>Raggruppamento e analisi dei campi per relazioni semantiche</p>
                    </div>

                    {domainFields.semantic_analysis && (
                      <div className="analysis-summary">
                        <div className="summary-stats">
                          <div className="summary-stat">
                            <span className="stat-number">{domainFields.semantic_analysis.total_fields}</span>
                            <span className="stat-label">Campi Totali</span>
                          </div>
                          <div className="summary-stat">
                            <span className="stat-number">{domainFields.semantic_analysis.total_groups}</span>
                            <span className="stat-label">Gruppi Semantici</span>
                          </div>
                          <div className="summary-stat">
                            <span className="stat-number">{domainFields.semantic_analysis.versions_analyzed}</span>
                            <span className="stat-label">Versioni Analizzate</span>
                          </div>
                          <div className="summary-stat">
                            <span className="stat-number">{domainFields.semantic_analysis.grouping_statistics.average_group_size.toFixed(1)}</span>
                            <span className="stat-label">Dimensione Media Gruppo</span>
                          </div>
                        </div>
                      </div>
                    )}

                    {domainFields.field_groups && domainFields.field_groups.length > 0 && (
                      <div className="field-groups">
                        <h5>📋 Gruppi Semantici</h5>
                        {domainFields.field_groups.map((group) => (
                          <div key={group.group_id} className="field-group">
                            <div className="group-header">
                              <h6>{group.group_name}</h6>
                              <div className="group-metrics">
                                <span className="cohesion-score" style={{
                                  backgroundColor: group.cohesion_score > 0.7 ? '#4CAF50' : 
                                                 group.cohesion_score > 0.5 ? '#FF9800' : '#F44336'
                                }}>
                                  Coesione: {(group.cohesion_score * 100).toFixed(0)}%
                                </span>
                                <span className="field-count">{group.fields.length} campi</span>
                              </div>
                            </div>
                            
                            <div className="group-content">
                              <p className="semantic-theme"><strong>Tema:</strong> {group.semantic_theme}</p>
                              
                              <div className="group-fields">
                                <strong>Campi:</strong>
                                <div className="field-tags">
                                  {group.fields.map(field => (
                                    <span key={field} className="field-tag">{field}</span>
                                  ))}
                                </div>
                              </div>

                              {group.relationships.length > 0 && (
                                <div className="group-relationships">
                                  <strong>Relazioni Semantiche:</strong>
                                  <div className="relationships-list">
                                    {group.relationships.map((rel, relIndex) => (
                                      <div key={relIndex} className="relationship">
                                        <span className="relationship-fields">{rel.field1} ↔ {rel.field2}</span>
                                        <span className="relationship-type">{rel.relationship_type}</span>
                                        <span className="relationship-strength" style={{
                                          backgroundColor: rel.strength > 0.7 ? '#4CAF50' : 
                                                         rel.strength > 0.5 ? '#FF9800' : '#F44336'
                                        }}>
                                          {(rel.strength * 100).toFixed(0)}%
                                        </span>
                                      </div>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {activeView === 'compatibility' && (
                  <div className="domain-compatibility">
                    <div className="compatibility-header">
                      <h4>⚖️ Valutazione Compatibilità</h4>
                      <p>Analisi della compatibilità di conversione tra versioni per questo dominio</p>
                    </div>

                    <div className="version-selector">
                      <div className="version-select-group">
                        <label>Versione di Origine:</label>
                        <select 
                          value={compatibilityVersions.fromVersion}
                          onChange={(e) => {
                            setCompatibilityVersions(prev => ({ ...prev, fromVersion: e.target.value }));
                            setDomainCompatibility(null);
                          }}
                        >
                          <option value="1966">EURING 1966</option>
                          <option value="1979">EURING 1979</option>
                          <option value="2000">EURING 2000</option>
                          <option value="2020">EURING 2020</option>
                        </select>
                      </div>
                      
                      <div className="version-arrow">→</div>
                      
                      <div className="version-select-group">
                        <label>Versione di Destinazione:</label>
                        <select 
                          value={compatibilityVersions.toVersion}
                          onChange={(e) => {
                            setCompatibilityVersions(prev => ({ ...prev, toVersion: e.target.value }));
                            setDomainCompatibility(null);
                          }}
                        >
                          <option value="1966">EURING 1966</option>
                          <option value="1979">EURING 1979</option>
                          <option value="2000">EURING 2000</option>
                          <option value="2020">EURING 2020</option>
                        </select>
                      </div>

                      <button 
                        className="analyze-button"
                        onClick={() => selectedDomain && loadDomainData(selectedDomain)}
                        disabled={evolutionLoading}
                      >
                        {evolutionLoading ? 'Analizzando...' : 'Analizza Compatibilità'}
                      </button>
                    </div>

                    {domainCompatibility && domainCompatibility.compatibility_data && (
                      <div className="compatibility-results">
                        <div className="compatibility-summary">
                          <div className="summary-card">
                            <h5>📊 Riepilogo Compatibilità</h5>
                            <div className="compatibility-level" style={{
                              backgroundColor: domainCompatibility.compatibility_data.summary.overall_compatibility === 'FULL' ? '#4CAF50' :
                                             domainCompatibility.compatibility_data.summary.overall_compatibility === 'PARTIAL' ? '#FF9800' :
                                             domainCompatibility.compatibility_data.summary.overall_compatibility === 'LOSSY' ? '#F44336' : '#4CAF50'
                            }}>
                              {domainCompatibility.compatibility_data.summary.overall_compatibility}
                            </div>
                            
                            <div className="compatibility-metrics">
                              <div className="metric">
                                <span className="metric-label">Conversione con Perdite:</span>
                                <span className={`metric-value ${domainCompatibility.compatibility_data.summary.is_lossy_conversion ? 'warning' : 'success'}`}>
                                  {domainCompatibility.compatibility_data.summary.is_lossy_conversion ? 'Sì' : 'No'}
                                </span>
                              </div>
                              <div className="metric">
                                <span className="metric-label">Avvisi Totali:</span>
                                <span className="metric-value">{domainCompatibility.compatibility_data.summary.total_warnings}</span>
                              </div>
                              <div className="metric">
                                <span className="metric-label">Campi Compatibili:</span>
                                <span className="metric-value">{domainCompatibility.compatibility_data.summary.field_compatibility_count}</span>
                              </div>
                            </div>

                            {domainCompatibility.compatibility_data.summary.loss_types.length > 0 && (
                              <div className="loss-types">
                                <strong>Tipi di Perdita:</strong>
                                <div className="loss-type-tags">
                                  {domainCompatibility.compatibility_data.summary.loss_types.map(lossType => (
                                    <span key={lossType} className="loss-type-tag">{lossType}</span>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        {domainCompatibility.compatibility_data.detailed_analysis && (
                          <div className="detailed-analysis">
                            {domainCompatibility.compatibility_data.detailed_analysis.conversion_warnings.length > 0 && (
                              <div className="analysis-section">
                                <h5>⚠️ Avvisi di Conversione</h5>
                                <ul className="warning-list">
                                  {domainCompatibility.compatibility_data.detailed_analysis.conversion_warnings.map((warning, index) => (
                                    <li key={index} className="warning-item">{warning}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {domainCompatibility.compatibility_data.detailed_analysis.conversion_notes.length > 0 && (
                              <div className="analysis-section">
                                <h5>📝 Note di Conversione</h5>
                                <ul className="notes-list">
                                  {domainCompatibility.compatibility_data.detailed_analysis.conversion_notes.map((note, index) => (
                                    <li key={index} className="note-item">{note}</li>
                                  ))}
                                </ul>
                              </div>
                            )}

                            {domainCompatibility.compatibility_data.detailed_analysis.loss_details.length > 0 && (
                              <div className="analysis-section">
                                <h5>🔍 Dettagli Perdite</h5>
                                <div className="loss-details">
                                  {domainCompatibility.compatibility_data.detailed_analysis.loss_details.map((loss, index) => (
                                    <div key={index} className="loss-detail">
                                      <strong>Tipo:</strong> {loss.type || 'Non specificato'}<br/>
                                      <strong>Descrizione:</strong> {loss.description || 'Nessuna descrizione disponibile'}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}

                {activeView === 'export' && (
                  <div className="domain-export">
                    <div className="export-header">
                      <h4>📤 Esportazione Dati Dominio</h4>
                      <p>Genera report strutturati con i dati di evoluzione, analisi e compatibilità</p>
                    </div>

                    <div className="export-options">
                      <div className="export-format">
                        <label>Formato di Esportazione:</label>
                        <select 
                          value={exportOptions.format}
                          onChange={(e) => setExportOptions(prev => ({ ...prev, format: e.target.value }))}
                        >
                          <option value="json">JSON</option>
                          <option value="csv">CSV</option>
                          <option value="markdown">Markdown</option>
                        </select>
                      </div>

                      <div className="export-content">
                        <h5>Contenuto da Includere:</h5>
                        <div className="export-checkboxes">
                          <label className="export-checkbox">
                            <input 
                              type="checkbox"
                              checked={exportOptions.includeEvolution}
                              onChange={(e) => setExportOptions(prev => ({ ...prev, includeEvolution: e.target.checked }))}
                            />
                            <span>📈 Dati di Evoluzione</span>
                          </label>
                          
                          <label className="export-checkbox">
                            <input 
                              type="checkbox"
                              checked={exportOptions.includeFieldAnalysis}
                              onChange={(e) => setExportOptions(prev => ({ ...prev, includeFieldAnalysis: e.target.checked }))}
                            />
                            <span>🔍 Analisi dei Campi</span>
                          </label>
                          
                          <label className="export-checkbox">
                            <input 
                              type="checkbox"
                              checked={exportOptions.includeCompatibility}
                              onChange={(e) => setExportOptions(prev => ({ ...prev, includeCompatibility: e.target.checked }))}
                            />
                            <span>⚖️ Dati di Compatibilità</span>
                          </label>
                        </div>
                      </div>

                      <button 
                        className="export-button"
                        onClick={async () => {
                          if (!selectedDomain) return;
                          
                          try {
                            setEvolutionLoading(true);
                            const exportResponse = await EuringAPI.exportDomainData(
                              selectedDomain,
                              exportOptions.format,
                              exportOptions.includeEvolution,
                              exportOptions.includeFieldAnalysis,
                              exportOptions.includeCompatibility
                            );
                            
                            if (exportResponse.success && exportResponse.export_data) {
                              // Create and download file
                              const dataStr = JSON.stringify(exportResponse.export_data, null, 2);
                              const dataBlob = new Blob([dataStr], { type: 'application/json' });
                              const url = URL.createObjectURL(dataBlob);
                              const link = document.createElement('a');
                              link.href = url;
                              link.download = `${selectedDomain}_export_${new Date().toISOString().split('T')[0]}.${exportOptions.format}`;
                              document.body.appendChild(link);
                              link.click();
                              document.body.removeChild(link);
                              URL.revokeObjectURL(url);
                            } else {
                              setError(exportResponse.error || 'Export failed');
                            }
                          } catch (err: any) {
                            setError(err.message || 'Export failed');
                          } finally {
                            setEvolutionLoading(false);
                          }
                        }}
                        disabled={evolutionLoading || !selectedDomain}
                      >
                        {evolutionLoading ? 'Esportando...' : `Esporta ${exportOptions.format.toUpperCase()}`}
                      </button>
                    </div>

                    <div className="export-preview">
                      <h5>📋 Anteprima Contenuto</h5>
                      <div className="preview-sections">
                        {exportOptions.includeEvolution && (
                          <div className="preview-section">
                            <span className="section-icon">📈</span>
                            <span className="section-name">Evoluzione Storica</span>
                            <span className="section-description">Timeline dei cambiamenti e matrici di compatibilità</span>
                          </div>
                        )}
                        
                        {exportOptions.includeFieldAnalysis && (
                          <div className="preview-section">
                            <span className="section-icon">🔍</span>
                            <span className="section-name">Analisi Semantica</span>
                            <span className="section-description">Raggruppamenti di campi e relazioni semantiche</span>
                          </div>
                        )}
                        
                        {exportOptions.includeCompatibility && (
                          <div className="preview-section">
                            <span className="section-icon">⚖️</span>
                            <span className="section-name">Compatibilità</span>
                            <span className="section-description">Valutazioni di compatibilità tra versioni</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}

      {/* Domain Comparison Modal */}
      {comparisonVersions && domainEvolution && selectedDomain && (
        <DomainComparison
          domain={selectedDomain}
          version1={comparisonVersions.version1}
          version2={comparisonVersions.version2}
          evolutionEntries={domainEvolution.evolution_entries}
          onClose={handleCloseComparison}
        />
      )}
    </div>
  );
};

export default DomainPanel;