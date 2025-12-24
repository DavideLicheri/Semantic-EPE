/**
 * Semantic Domains Utility
 * Gestisce colori, icone e visualizzazione dei 7 domini semantici EURING
 */

export enum SemanticDomain {
  IDENTIFICATION_MARKING = "identification_marking",
  SPECIES = "species", 
  DEMOGRAPHICS = "demographics",
  TEMPORAL = "temporal",
  SPATIAL = "spatial",
  BIOMETRICS = "biometrics",
  METHODOLOGY = "methodology"
}

export interface DomainInfo {
  name: string;
  description: string;
  icon: string;
  color: string;
  backgroundColor: string;
  borderColor: string;
  textColor: string;
  stability_score: number;
  complexity: string;
}

export const DOMAIN_INFO: Record<SemanticDomain, DomainInfo> = {
  [SemanticDomain.IDENTIFICATION_MARKING]: {
    name: "Identificazione & Marcaggio",
    description: "Anelli, schemi, marcaggi metallici e sistemi di verifica",
    icon: "🏷️",
    color: "#FF6B6B",
    backgroundColor: "#FFE5E5",
    borderColor: "#FF6B6B",
    textColor: "#CC2E2E",
    stability_score: 3,
    complexity: "Alto"
  },
  [SemanticDomain.SPECIES]: {
    name: "Classificazione Specie",
    description: "Codici specie, tassonomia e sistemi di identificazione",
    icon: "🐦",
    color: "#4ECDC4",
    backgroundColor: "#E5F9F7",
    borderColor: "#4ECDC4",
    textColor: "#2E8B87",
    stability_score: 7,
    complexity: "Medio"
  },
  [SemanticDomain.DEMOGRAPHICS]: {
    name: "Demografia",
    description: "Sistemi di classificazione età e sesso",
    icon: "👥",
    color: "#45B7D1",
    backgroundColor: "#E5F3FB",
    borderColor: "#45B7D1",
    textColor: "#2E7BA7",
    stability_score: 6,
    complexity: "Medio"
  },
  [SemanticDomain.TEMPORAL]: {
    name: "Informazioni Temporali",
    description: "Formati data e ora e loro evoluzione",
    icon: "⏰",
    color: "#FFA07A",
    backgroundColor: "#FFF0E5",
    borderColor: "#FFA07A",
    textColor: "#CC6B47",
    stability_score: 2,
    complexity: "Alto"
  },
  [SemanticDomain.SPATIAL]: {
    name: "Informazioni Spaziali",
    description: "Coordinate, accuratezza posizione e codifica geografica",
    icon: "🌍",
    color: "#98D8C8",
    backgroundColor: "#E8F5F2",
    borderColor: "#98D8C8",
    textColor: "#5FA896",
    stability_score: 1,
    complexity: "Molto Alto"
  },
  [SemanticDomain.BIOMETRICS]: {
    name: "Misure Biometriche",
    description: "Ala, peso, becco, tarso, grasso, muscolo e muta",
    icon: "📏",
    color: "#F7DC6F",
    backgroundColor: "#FEFBEA",
    borderColor: "#F7DC6F",
    textColor: "#C4A942",
    stability_score: 4,
    complexity: "Alto"
  },
  [SemanticDomain.METHODOLOGY]: {
    name: "Metodologia & Condizioni",
    description: "Metodi cattura, condizioni, codici manipolazione e procedure",
    icon: "🔬",
    color: "#81C784",
    backgroundColor: "#E8F5E8",
    borderColor: "#81C784",
    textColor: "#4CAF50",
    stability_score: 5,
    complexity: "Medio"
  }
};

/**
 * Ottiene le informazioni di un dominio semantico
 */
export function getDomainInfo(domain: string): DomainInfo {
  const domainKey = domain as SemanticDomain;
  return DOMAIN_INFO[domainKey] || {
    name: domain.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    description: `Dominio ${domain}`,
    icon: "📊",
    color: "#95A5A6",
    backgroundColor: "#F8F9FA",
    borderColor: "#95A5A6", 
    textColor: "#5D6D7E",
    stability_score: 5,
    complexity: "Medio"
  };
}

/**
 * Genera uno stile CSS per un dominio semantico
 */
export function getDomainStyle(domain: string, variant: 'full' | 'subtle' | 'border' | 'text' = 'full'): React.CSSProperties {
  const info = getDomainInfo(domain);
  
  switch (variant) {
    case 'full':
      return {
        backgroundColor: info.backgroundColor,
        borderLeft: `4px solid ${info.borderColor}`,
        color: info.textColor,
        padding: '4px 8px',
        borderRadius: '4px'
      };
    
    case 'subtle':
      return {
        backgroundColor: info.backgroundColor,
        color: info.textColor,
        padding: '2px 6px',
        borderRadius: '3px',
        fontSize: '0.85em'
      };
    
    case 'border':
      return {
        borderLeft: `3px solid ${info.color}`,
        paddingLeft: '8px'
      };
    
    case 'text':
      return {
        color: info.color,
        fontWeight: 'bold'
      };
    
    default:
      return {};
  }
}

/**
 * Genera una classe CSS per un dominio semantico
 */
export function getDomainClassName(domain: string): string {
  return `semantic-domain-${domain.toLowerCase().replace('_', '-')}`;
}

/**
 * Ottiene l'icona di un dominio semantico
 */
export function getDomainIcon(domain: string): string {
  return getDomainInfo(domain).icon;
}

/**
 * Ottiene il colore principale di un dominio semantico
 */
export function getDomainColor(domain: string): string {
  return getDomainInfo(domain).color;
}

/**
 * Genera CSS personalizzato per i domini semantici
 */
export function generateDomainCSS(): string {
  let css = `
/* Semantic Domains CSS - Auto-generated */
.domain-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.85em;
  font-weight: 500;
  border-radius: 4px;
  padding: 2px 6px;
  margin: 1px;
  white-space: nowrap;
}

.domain-icon {
  font-size: 1.1em;
}

.domain-name {
  font-size: 0.9em;
}

/* Specific domain styles */
`;

  Object.entries(DOMAIN_INFO).forEach(([domain, info]) => {
    const className = getDomainClassName(domain);
    css += `
.${className} {
  background-color: ${info.backgroundColor};
  color: ${info.textColor};
  border: 1px solid ${info.borderColor}20;
}

.${className}:hover {
  background-color: ${info.color}20;
  border-color: ${info.borderColor};
}

.field-${className} {
  border-left: 3px solid ${info.color};
  background: linear-gradient(90deg, ${info.backgroundColor} 0%, transparent 100%);
}

.matrix-cell-${className} {
  background-color: ${info.backgroundColor};
  border-left: 2px solid ${info.color};
}
`;
  });

  return css;
}
/**
 * Mappa i domini semantici per ordinamento per stabilità
 */
export function getDomainsByStability(): SemanticDomain[] {
  return Object.values(SemanticDomain).sort((a, b) => {
    const aInfo = getDomainInfo(a);
    const bInfo = getDomainInfo(b);
    return bInfo.stability_score - aInfo.stability_score;
  });
}

/**
 * Ottiene tutti i domini con le loro informazioni
 */
export function getAllDomainsInfo(): Array<{domain: SemanticDomain, info: DomainInfo}> {
  return Object.entries(DOMAIN_INFO).map(([domain, info]) => ({
    domain: domain as SemanticDomain,
    info
  }));
}