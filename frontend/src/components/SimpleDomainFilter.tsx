import React from 'react';
import { getAllDomainsInfo } from '../utils/semanticDomains';
import './SimpleDomainFilter.css';

interface SimpleDomainFilterProps {
  selectedDomain: string | null;
  onDomainSelect: (domain: string | null) => void;
  compact?: boolean;
}

const SimpleDomainFilter: React.FC<SimpleDomainFilterProps> = ({
  selectedDomain,
  onDomainSelect,
  compact = false
}) => {
  const allDomains = getAllDomainsInfo();

  return (
    <div className={`simple-domain-filter ${compact ? 'compact' : ''}`}>
      <div className="filter-options">
        <button
          className={`filter-button all-button ${selectedDomain === null ? 'selected' : ''}`}
          onClick={() => onDomainSelect(null)}
        >
          <span className="filter-icon">📊</span>
          {!compact && <span className="filter-label">Tutti</span>}
        </button>
        
        {allDomains.map(({ domain, info }) => (
          <button
            key={domain}
            className={`filter-button ${selectedDomain === domain ? 'selected' : ''}`}
            onClick={() => onDomainSelect(domain)}
            style={{
              borderColor: selectedDomain === domain ? info.color : '#dee2e6',
              backgroundColor: selectedDomain === domain ? info.backgroundColor : 'white',
              color: selectedDomain === domain ? info.textColor : '#495057'
            }}
            title={info.description}
          >
            <span className="filter-icon">{info.icon}</span>
            {!compact && <span className="filter-label">{info.name}</span>}
          </button>
        ))}
      </div>
    </div>
  );
};

export default SimpleDomainFilter;