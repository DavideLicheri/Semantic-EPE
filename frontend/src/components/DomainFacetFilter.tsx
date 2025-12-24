import React from 'react';
import { getAllDomainsInfo } from '../utils/semanticDomains';
import './DomainFacetFilter.css';

interface DomainFacetFilterProps {
  selectedDomains: string[];
  onDomainToggle: (domain: string) => void;
  fieldCounts?: Record<string, number>;
  showCounts?: boolean;
}

const DomainFacetFilter: React.FC<DomainFacetFilterProps> = ({
  selectedDomains,
  onDomainToggle,
  fieldCounts = {},
  showCounts = true
}) => {
  const allDomains = getAllDomainsInfo();

  return (
    <div className="domain-facet-filter">
      <h4 className="facet-title">Filtra per Dominio</h4>
      
      <div className="facet-options">
        {allDomains.map(({ domain, info }) => {
          const isSelected = selectedDomains.includes(domain);
          const count = fieldCounts[domain] || 0;
          
          return (
            <button
              key={domain}
              className={`facet-button ${isSelected ? 'selected' : ''}`}
              onClick={() => onDomainToggle(domain)}
              style={{
                borderColor: info.color,
                backgroundColor: isSelected ? info.backgroundColor : 'white',
                color: isSelected ? info.textColor : '#495057'
              }}
            >
              <span className="facet-icon">{info.icon}</span>
              <span className="facet-label">{info.name}</span>
              {showCounts && count > 0 && (
                <span className="facet-count">({count})</span>
              )}
            </button>
          );
        })}
      </div>
      
      {selectedDomains.length > 0 && (
        <div className="facet-actions">
          <button 
            className="clear-filters-button"
            onClick={() => selectedDomains.forEach(domain => onDomainToggle(domain))}
          >
            ✕ Rimuovi tutti i filtri
          </button>
        </div>
      )}
    </div>
  );
};

export default DomainFacetFilter;