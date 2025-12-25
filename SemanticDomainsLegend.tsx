import React from 'react';
import { getAllDomainsInfo, getDomainsByStability } from '../utils/semanticDomains';
import SemanticDomainBadge from './SemanticDomainBadge';
import './SemanticDomains.css';

interface SemanticDomainsLegendProps {
  title?: string;
  compact?: boolean;
  sortByStability?: boolean;
  onDomainClick?: (domain: string) => void;
  selectedDomains?: string[];
  showStats?: boolean;
}

const SemanticDomainsLegend: React.FC<SemanticDomainsLegendProps> = ({
  title = "Domini Semantici EURING",
  compact = false,
  sortByStability = true,
  onDomainClick,
  selectedDomains = [],
  showStats = false
}) => {
  const allDomains = getAllDomainsInfo();
  
  // Ordina per stabilità se richiesto
  const sortedDomains = sortByStability 
    ? getDomainsByStability().map(domain => 
        allDomains.find(d => d.domain === domain)!
      )
    : allDomains;

  return (
    <div className="domain-legend">
      <div className="domain-legend-title">{title}</div>
      
      <div className="domain-legend-items">
        {sortedDomains.map(({ domain, info }) => (
          <div 
            key={domain} 
            className={`domain-legend-item ${selectedDomains.includes(domain) ? 'selected' : ''}`}
          >
            <SemanticDomainBadge
              domain={domain}
              variant={compact ? 'compact' : 'full'}
              onClick={onDomainClick}
              className={selectedDomains.includes(domain) ? 'selected' : ''}
            />
            
            {showStats && (
              <div className="domain-stats">
                <span className="stability-score" title="Punteggio di stabilità">
                  ⭐ {info.stability_score}/7
                </span>
                <span className="complexity" title="Complessità">
                  🔧 {info.complexity}
                </span>
              </div>
            )}
          </div>
        ))}
      </div>
      
      {showStats && (
        <div className="legend-footer">
          <small>
            ⭐ Stabilità: più alto = meno cambiamenti tra versioni | 
            🔧 Complessità: difficoltà di mapping semantico
          </small>
        </div>
      )}
    </div>
  );
};

export default SemanticDomainsLegend;