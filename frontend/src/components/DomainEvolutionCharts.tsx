import React, { useState, useEffect } from 'react';
import { DomainEvolutionEntry } from '../types/euring-types';
import EuringAPI from '../services/api';
import './DomainEvolutionCharts.css';

interface DomainEvolutionChartsProps {
  domain: string;
  evolutionEntries: DomainEvolutionEntry[];
}

interface ChartData {
  years: number[];
  fieldsAdded: number[];
  fieldsRemoved: number[];
  fieldsModified: number[];
  cumulativeFields: number[];
  changeIntensity: number[];
}

const DomainEvolutionCharts: React.FC<DomainEvolutionChartsProps> = ({
  domain,
  evolutionEntries
}) => {
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [activeChart, setActiveChart] = useState<'changes' | 'cumulative' | 'intensity'>('changes');

  useEffect(() => {
    generateChartData();
  }, [evolutionEntries]);

  const generateChartData = () => {
    if (!evolutionEntries.length) return;

    // Sort entries by year
    const sortedEntries = [...evolutionEntries].sort((a, b) => a.year - b.year);
    
    const years = sortedEntries.map(entry => entry.year);
    const fieldsAdded = sortedEntries.map(entry => entry.fields_added.length);
    const fieldsRemoved = sortedEntries.map(entry => entry.fields_removed.length);
    const fieldsModified = sortedEntries.map(entry => entry.fields_modified.length);
    
    // Calculate cumulative fields (approximation)
    let cumulativeCount = 0;
    const cumulativeFields = sortedEntries.map(entry => {
      cumulativeCount += entry.fields_added.length - entry.fields_removed.length;
      return Math.max(0, cumulativeCount);
    });
    
    // Calculate change intensity (total changes per version)
    const changeIntensity = sortedEntries.map(entry => 
      entry.fields_added.length + entry.fields_removed.length + entry.fields_modified.length
    );

    setChartData({
      years,
      fieldsAdded,
      fieldsRemoved,
      fieldsModified,
      cumulativeFields,
      changeIntensity
    });
  };

  const getMaxValue = (data: number[]) => Math.max(...data, 1);

  const getBarHeight = (value: number, maxValue: number) => {
    return Math.max((value / maxValue) * 100, 2); // Minimum 2% height for visibility
  };

  const getIntensityColor = (intensity: number, maxIntensity: number) => {
    const ratio = intensity / maxIntensity;
    if (ratio >= 0.8) return '#e74c3c';
    if (ratio >= 0.6) return '#f39c12';
    if (ratio >= 0.4) return '#f1c40f';
    if (ratio >= 0.2) return '#27ae60';
    return '#95a5a6';
  };

  const calculateTotalChanges = () => {
    if (!chartData) return { added: 0, removed: 0, modified: 0 };
    
    return {
      added: chartData.fieldsAdded.reduce((sum, val) => sum + val, 0),
      removed: chartData.fieldsRemoved.reduce((sum, val) => sum + val, 0),
      modified: chartData.fieldsModified.reduce((sum, val) => sum + val, 0)
    };
  };

  const getMostActiveYear = () => {
    if (!chartData) return null;
    
    const maxIntensity = Math.max(...chartData.changeIntensity);
    const maxIndex = chartData.changeIntensity.indexOf(maxIntensity);
    
    return {
      year: chartData.years[maxIndex],
      changes: maxIntensity
    };
  };

  const getStabilityPeriods = () => {
    if (!chartData) return [];
    
    const periods = [];
    let currentPeriodStart = 0;
    
    for (let i = 1; i < chartData.changeIntensity.length; i++) {
      if (chartData.changeIntensity[i] > 2) { // Threshold for "significant change"
        if (i - currentPeriodStart > 1) {
          periods.push({
            start: chartData.years[currentPeriodStart],
            end: chartData.years[i - 1],
            duration: chartData.years[i - 1] - chartData.years[currentPeriodStart]
          });
        }
        currentPeriodStart = i;
      }
    }
    
    return periods.filter(period => period.duration > 0);
  };

  if (!chartData) {
    return (
      <div className="evolution-charts">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Generazione grafici...</p>
        </div>
      </div>
    );
  }

  const totalChanges = calculateTotalChanges();
  const mostActiveYear = getMostActiveYear();
  const stabilityPeriods = getStabilityPeriods();

  return (
    <div className="evolution-charts">
      <div className="charts-header">
        <div className="charts-title">
          <h4>📊 Analisi Grafica - {EuringAPI.getDomainDisplayName(domain)}</h4>
          <p className="charts-subtitle">
            Visualizzazione dell'evoluzione attraverso {chartData.years.length} versioni EURING
          </p>
        </div>
        
        <div className="chart-navigation">
          <button
            className={`chart-nav-button ${activeChart === 'changes' ? 'active' : ''}`}
            onClick={() => setActiveChart('changes')}
          >
            📈 Cambiamenti
          </button>
          <button
            className={`chart-nav-button ${activeChart === 'cumulative' ? 'active' : ''}`}
            onClick={() => setActiveChart('cumulative')}
          >
            📊 Cumulativo
          </button>
          <button
            className={`chart-nav-button ${activeChart === 'intensity' ? 'active' : ''}`}
            onClick={() => setActiveChart('intensity')}
          >
            🔥 Intensità
          </button>
        </div>
      </div>

      <div className="charts-content">
        {activeChart === 'changes' && (
          <div className="changes-chart">
            <div className="chart-container">
              <div className="chart-title">
                <h5>Cambiamenti per Versione</h5>
                <p>Distribuzione di aggiunte, rimozioni e modifiche</p>
              </div>
              
              <div className="stacked-bar-chart">
                <div className="chart-y-axis">
                  {[...Array(6)].map((_, i) => {
                    const maxVal = getMaxValue([
                      ...chartData.fieldsAdded,
                      ...chartData.fieldsRemoved,
                      ...chartData.fieldsModified
                    ]);
                    const value = Math.round((maxVal * (5 - i)) / 5);
                    return (
                      <div key={i} className="y-axis-label">
                        {value}
                      </div>
                    );
                  })}
                </div>
                
                <div className="chart-bars">
                  {chartData.years.map((year, index) => {
                    const maxVal = getMaxValue([
                      ...chartData.fieldsAdded,
                      ...chartData.fieldsRemoved,
                      ...chartData.fieldsModified
                    ]);
                    
                    const addedHeight = getBarHeight(chartData.fieldsAdded[index], maxVal);
                    const removedHeight = getBarHeight(chartData.fieldsRemoved[index], maxVal);
                    const modifiedHeight = getBarHeight(chartData.fieldsModified[index], maxVal);
                    
                    return (
                      <div key={year} className="bar-group">
                        <div className="stacked-bar">
                          <div 
                            className="bar-segment added"
                            style={{ height: `${addedHeight}%` }}
                            title={`${chartData.fieldsAdded[index]} campi aggiunti`}
                          ></div>
                          <div 
                            className="bar-segment modified"
                            style={{ height: `${modifiedHeight}%` }}
                            title={`${chartData.fieldsModified[index]} campi modificati`}
                          ></div>
                          <div 
                            className="bar-segment removed"
                            style={{ height: `${removedHeight}%` }}
                            title={`${chartData.fieldsRemoved[index]} campi rimossi`}
                          ></div>
                        </div>
                        <div className="bar-label">{year}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
              
              <div className="chart-legend">
                <div className="legend-item">
                  <span className="legend-color added"></span>
                  <span>Campi Aggiunti</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color modified"></span>
                  <span>Campi Modificati</span>
                </div>
                <div className="legend-item">
                  <span className="legend-color removed"></span>
                  <span>Campi Rimossi</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeChart === 'cumulative' && (
          <div className="cumulative-chart">
            <div className="chart-container">
              <div className="chart-title">
                <h5>Crescita Cumulativa dei Campi</h5>
                <p>Evoluzione del numero totale di campi nel tempo</p>
              </div>
              
              <div className="line-chart">
                <div className="chart-y-axis">
                  {[...Array(6)].map((_, i) => {
                    const maxVal = getMaxValue(chartData.cumulativeFields);
                    const value = Math.round((maxVal * (5 - i)) / 5);
                    return (
                      <div key={i} className="y-axis-label">
                        {value}
                      </div>
                    );
                  })}
                </div>
                
                <div className="chart-area">
                  <svg className="line-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="areaGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stopColor="#3498db" stopOpacity="0.3"/>
                        <stop offset="100%" stopColor="#3498db" stopOpacity="0.1"/>
                      </linearGradient>
                    </defs>
                    
                    {/* Area fill */}
                    <path
                      d={`M 0 100 ${chartData.cumulativeFields.map((value, index) => {
                        const x = (index / (chartData.cumulativeFields.length - 1)) * 100;
                        const y = 100 - (value / getMaxValue(chartData.cumulativeFields)) * 100;
                        return `L ${x} ${y}`;
                      }).join(' ')} L 100 100 Z`}
                      fill="url(#areaGradient)"
                    />
                    
                    {/* Line */}
                    <path
                      d={`M ${chartData.cumulativeFields.map((value, index) => {
                        const x = (index / (chartData.cumulativeFields.length - 1)) * 100;
                        const y = 100 - (value / getMaxValue(chartData.cumulativeFields)) * 100;
                        return `${index === 0 ? 'M' : 'L'} ${x} ${y}`;
                      }).join(' ')}`}
                      stroke="#3498db"
                      strokeWidth="2"
                      fill="none"
                    />
                    
                    {/* Data points */}
                    {chartData.cumulativeFields.map((value, index) => {
                      const x = (index / (chartData.cumulativeFields.length - 1)) * 100;
                      const y = 100 - (value / getMaxValue(chartData.cumulativeFields)) * 100;
                      return (
                        <circle
                          key={index}
                          cx={x}
                          cy={y}
                          r="1.5"
                          fill="#2980b9"
                          stroke="white"
                          strokeWidth="1"
                        />
                      );
                    })}
                  </svg>
                  
                  <div className="chart-x-axis">
                    {chartData.years.map(year => (
                      <div key={year} className="x-axis-label">{year}</div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeChart === 'intensity' && (
          <div className="intensity-chart">
            <div className="chart-container">
              <div className="chart-title">
                <h5>Intensità dei Cambiamenti</h5>
                <p>Numero totale di modifiche per versione</p>
              </div>
              
              <div className="heatmap-chart">
                <div className="heatmap-bars">
                  {chartData.years.map((year, index) => {
                    const intensity = chartData.changeIntensity[index];
                    const maxIntensity = getMaxValue(chartData.changeIntensity);
                    const color = getIntensityColor(intensity, maxIntensity);
                    const height = getBarHeight(intensity, maxIntensity);
                    
                    return (
                      <div key={year} className="intensity-bar-group">
                        <div 
                          className="intensity-bar"
                          style={{ 
                            height: `${height}%`,
                            backgroundColor: color
                          }}
                          title={`${intensity} cambiamenti totali nel ${year}`}
                        >
                          <span className="intensity-value">{intensity}</span>
                        </div>
                        <div className="intensity-label">{year}</div>
                      </div>
                    );
                  })}
                </div>
                
                <div className="intensity-scale">
                  <div className="scale-label">Bassa</div>
                  <div className="scale-gradient">
                    <div className="scale-color" style={{ backgroundColor: '#95a5a6' }}></div>
                    <div className="scale-color" style={{ backgroundColor: '#27ae60' }}></div>
                    <div className="scale-color" style={{ backgroundColor: '#f1c40f' }}></div>
                    <div className="scale-color" style={{ backgroundColor: '#f39c12' }}></div>
                    <div className="scale-color" style={{ backgroundColor: '#e74c3c' }}></div>
                  </div>
                  <div className="scale-label">Alta</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="charts-insights">
        <h5>📋 Insights Analitici</h5>
        
        <div className="insights-grid">
          <div className="insight-card">
            <div className="insight-header">
              <span className="insight-icon">📊</span>
              <h6>Cambiamenti Totali</h6>
            </div>
            <div className="insight-stats">
              <div className="insight-stat">
                <span className="stat-value added">{totalChanges.added}</span>
                <span className="stat-label">Aggiunti</span>
              </div>
              <div className="insight-stat">
                <span className="stat-value modified">{totalChanges.modified}</span>
                <span className="stat-label">Modificati</span>
              </div>
              <div className="insight-stat">
                <span className="stat-value removed">{totalChanges.removed}</span>
                <span className="stat-label">Rimossi</span>
              </div>
            </div>
          </div>

          {mostActiveYear && (
            <div className="insight-card">
              <div className="insight-header">
                <span className="insight-icon">🔥</span>
                <h6>Anno Più Attivo</h6>
              </div>
              <div className="insight-content">
                <div className="active-year">{mostActiveYear.year}</div>
                <div className="active-changes">{mostActiveYear.changes} cambiamenti</div>
              </div>
            </div>
          )}

          <div className="insight-card">
            <div className="insight-header">
              <span className="insight-icon">📈</span>
              <h6>Trend Evolutivo</h6>
            </div>
            <div className="insight-content">
              <div className="trend-indicator">
                {totalChanges.added > totalChanges.removed ? (
                  <span className="trend-up">📈 Crescita</span>
                ) : totalChanges.added < totalChanges.removed ? (
                  <span className="trend-down">📉 Riduzione</span>
                ) : (
                  <span className="trend-stable">➡️ Stabile</span>
                )}
              </div>
              <div className="trend-description">
                {totalChanges.added > totalChanges.removed 
                  ? 'Il dominio è in espansione'
                  : totalChanges.added < totalChanges.removed
                  ? 'Il dominio si sta semplificando'
                  : 'Il dominio è relativamente stabile'
                }
              </div>
            </div>
          </div>

          {stabilityPeriods.length > 0 && (
            <div className="insight-card">
              <div className="insight-header">
                <span className="insight-icon">⚖️</span>
                <h6>Periodi di Stabilità</h6>
              </div>
              <div className="insight-content">
                {stabilityPeriods.slice(0, 2).map((period, index) => (
                  <div key={index} className="stability-period">
                    <span className="period-range">{period.start}-{period.end}</span>
                    <span className="period-duration">({period.duration} anni)</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default DomainEvolutionCharts;