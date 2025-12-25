import React from 'react';
import { getDomainInfo, getDomainClassName } from '../utils/semanticDomains';
import './SemanticDomains.css';

interface SemanticDomainBadgeProps {
  domain: string;
  variant?: 'full' | 'compact' | 'icon-only';
  showTooltip?: boolean;
  onClick?: (domain: string) => void;
  className?: string;
}

const SemanticDomainBadge: React.FC<SemanticDomainBadgeProps> = ({
  domain,
  variant = 'full',
  showTooltip = true,
  onClick,
  className = ''
}) => {
  const domainInfo = getDomainInfo(domain);
  const domainClassName = getDomainClassName(domain);

  const handleClick = () => {
    if (onClick) {
      onClick(domain);
    }
  };

  const badgeClassName = [
    'domain-badge',
    domainClassName,
    variant,
    className,
    onClick ? 'clickable' : ''
  ].filter(Boolean).join(' ');

  return (
    <span
      className={badgeClassName}
      title={showTooltip ? `${domainInfo.name}: ${domainInfo.description}` : undefined}
      onClick={handleClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={(e) => {
        if (onClick && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          handleClick();
        }
      }}
    >
      <span className="domain-icon">{domainInfo.icon}</span>
      {variant !== 'icon-only' && variant !== 'compact' && (
        <span className="domain-name">{domainInfo.name}</span>
      )}
    </span>
  );
};

export default SemanticDomainBadge;