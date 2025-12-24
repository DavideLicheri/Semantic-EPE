import { useState } from 'react';
import './ResultsPanel.css';

// interface ResultsPanelProps {
//   results: any[];
//   type: 'recognition' | 'conversion';
//   onExport?: (format: 'json' | 'csv' | 'txt') => void;
// }

const ResultsPanel = ({ results, type }: { results: any[], type: 'recognition' | 'conversion' }) => {
  const [exportFormat, setExportFormat] = useState<'json' | 'csv' | 'txt'>('json');

  // const handleExport = () => {
  //   if (onExport) {
  //     onExport(exportFormat);
  //   }
  // };

  const downloadResults = (format: 'json' | 'csv' | 'txt') => {
    let content = '';
    let filename = '';
    let mimeType = '';

    switch (format) {
      case 'json':
        content = JSON.stringify(results, null, 2);
        filename = `euring_${type}_results.json`;
        mimeType = 'application/json';
        break;
      
      case 'csv':
        if (type === 'recognition') {
          const headers = 'Index,Original String,Version,Confidence,Length,Processing Time\n';
          const rows = results.map((result, index) => 
            `${index + 1},"${result.original_string}","${result.version || 'N/A'}",${result.confidence || 0},${result.length || 0},${result.processing_time_ms || 0}`
          ).join('\n');
          content = headers + rows;
        } else {
          const headers = 'Index,Original String,Converted String,Source Version,Target Version,Processing Time\n';
          const rows = results.map((result, index) => 
            `${index + 1},"${result.original_string}","${result.converted_string || 'N/A'}","${result.source_version}","${result.target_version}",${result.processing_time_ms || 0}`
          ).join('\n');
          content = headers + rows;
        }
        filename = `euring_${type}_results.csv`;
        mimeType = 'text/csv';
        break;
      
      case 'txt':
        content = results.map((result, index) => {
          if (type === 'recognition') {
            return `Result #${index + 1}
Original: ${result.original_string}
Version: ${result.version || 'N/A'}
Confidence: ${result.confidence ? Math.round(result.confidence * 100) + '%' : 'N/A'}
Length: ${result.length || 0} characters
Processing Time: ${result.processing_time_ms || 0}ms
${result.success ? 'Status: Success' : 'Status: Failed - ' + (result.error || 'Unknown error')}

`;
          } else {
            return `Conversion #${index + 1}
Original: ${result.original_string}
Converted: ${result.converted_string || 'N/A'}
Source Version: ${result.source_version}
Target Version: ${result.target_version}
Processing Time: ${result.processing_time_ms || 0}ms
${result.success ? 'Status: Success' : 'Status: Failed - ' + (result.error || 'Unknown error')}

`;
          }
        }).join('');
        filename = `euring_${type}_results.txt`;
        mimeType = 'text/plain';
        break;
    }

    // Create and download file
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  if (results.length === 0) {
    return null;
  }

  return (
    <div className="results-panel">
      <div className="results-header">
        <h3>
          {type === 'recognition' ? '🔍 Risultati Riconoscimento' : '🔄 Risultati Conversione'}
        </h3>
        
        <div className="export-controls">
          <select 
            value={exportFormat} 
            onChange={(e) => setExportFormat(e.target.value as 'json' | 'csv' | 'txt')}
            className="format-select"
          >
            <option value="json">JSON</option>
            <option value="csv">CSV</option>
            <option value="txt">TXT</option>
          </select>
          
          <button 
            onClick={() => downloadResults(exportFormat)}
            className="export-btn"
          >
            📥 Esporta {exportFormat.toUpperCase()}
          </button>
        </div>
      </div>

      <div className="results-stats">
        <div className="stat-item">
          <span className="stat-label">Totale:</span>
          <span className="stat-value">{results.length}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Successi:</span>
          <span className="stat-value success">{results.filter(r => r.success).length}</span>
        </div>
        
        <div className="stat-item">
          <span className="stat-label">Errori:</span>
          <span className="stat-value error">{results.filter(r => !r.success).length}</span>
        </div>
        
        {type === 'recognition' && (
          <div className="stat-item">
            <span className="stat-label">Confidenza Media:</span>
            <span className="stat-value">
              {Math.round(
                results
                  .filter(r => r.success && r.confidence)
                  .reduce((sum, r) => sum + r.confidence, 0) / 
                results.filter(r => r.success && r.confidence).length * 100
              ) || 0}%
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResultsPanel;