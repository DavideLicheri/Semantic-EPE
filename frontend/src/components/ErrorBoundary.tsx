import React from 'react';

interface Props {
  children: React.ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[ErrorBoundary] Errore nel componente:', error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          margin: '40px auto', maxWidth: '600px',
          padding: '32px', borderRadius: '10px',
          backgroundColor: '#f8d7da', border: '1px solid #f5c6cb',
          color: '#721c24', fontFamily: 'inherit',
        }}>
          <h3 style={{ margin: '0 0 12px 0', fontSize: '1.1em' }}>
            ⚠ {this.props.fallbackTitle || 'Errore nel componente'}
          </h3>
          <p style={{ margin: '0 0 16px 0', fontSize: '0.9em', color: '#856404', backgroundColor: '#fff3cd', padding: '10px', borderRadius: '6px', border: '1px solid #ffc107' }}>
            <strong>Dettaglio:</strong> {this.state.error?.message || 'Errore sconosciuto'}
          </p>
          <p style={{ margin: '0 0 20px 0', fontSize: '0.85em', color: '#721c24' }}>
            Si è verificato un errore inatteso. Prova a ricaricare il componente oppure aggiorna la pagina.
          </p>
          <div style={{ display: 'flex', gap: '10px' }}>
            <button
              onClick={this.handleReset}
              style={{
                padding: '8px 18px', backgroundColor: '#dc3545', color: 'white',
                border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: 'bold',
              }}>
              🔄 Ricarica componente
            </button>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '8px 18px', backgroundColor: '#f8f9fa', color: '#333',
                border: '1px solid #dee2e6', borderRadius: '6px', cursor: 'pointer',
              }}>
              Aggiorna pagina
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
