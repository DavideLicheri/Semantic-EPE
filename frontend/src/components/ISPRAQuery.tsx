/**
 * ISPRAQuery — interrogazione live del triplestore ISPRA EPE
 * Filtri: schema di inanellamento | specie (EURING 2000) | anno
 */
import { useState, useEffect } from 'react'
import axios from 'axios'

const API = 'http://localhost:8000/api/ispra'

interface Scheme {
  uri: string
  code: string
  label: string
}

interface Taxon {
  uri: string
  code: string
  label: string
}

interface Occurrence {
  date: string
  event_type: 'first_capture' | 'recapture'
  place_code: string | null
}

interface Record {
  organism_uri: string
  ring_id: string
  scheme_code: string
  species_code: string
  ring_date: string | null
  ring_place_code: string | null
  occurrences: Occurrence[]
}

export default function ISPRAQuery() {
  const [schemes, setSchemes] = useState<Scheme[]>([])
  const [taxa, setTaxa] = useState<Taxon[]>([])
  const [years, setYears] = useState<number[]>([])
  const [records, setRecords] = useState<Record[]>([])

  const [selectedScheme, setSelectedScheme] = useState('')
  const [selectedTaxon, setSelectedTaxon] = useState('')
  const [selectedYear, setSelectedYear] = useState<number | ''>('')

  const [loadingSchemes, setLoadingSchemes] = useState(false)
  const [loadingTaxa, setLoadingTaxa] = useState(false)
  const [loadingYears, setLoadingYears] = useState(false)
  const [loadingRecords, setLoadingRecords] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Carica schemi al mount
  useEffect(() => {
    setLoadingSchemes(true)
    setError(null)
    axios.get<Scheme[]>(`${API}/schemes`)
      .then(r => setSchemes(r.data))
      .catch(e => setError(`Errore caricamento schemi: ${e.message}`))
      .finally(() => setLoadingSchemes(false))
  }, [])

  // Carica specie quando cambia lo schema
  useEffect(() => {
    if (!selectedScheme) return
    setSelectedTaxon('')
    setSelectedYear('')
    setTaxa([])
    setYears([])
    setRecords([])
    setLoadingTaxa(true)
    setError(null)
    axios.get<Taxon[]>(`${API}/species`, { params: { scheme: selectedScheme } })
      .then(r => setTaxa(r.data))
      .catch(e => setError(`Errore caricamento specie: ${e.message}`))
      .finally(() => setLoadingTaxa(false))
  }, [selectedScheme])

  // Carica anni quando cambia la specie
  useEffect(() => {
    if (!selectedScheme || !selectedTaxon) return
    setSelectedYear('')
    setYears([])
    setRecords([])
    setLoadingYears(true)
    setError(null)
    axios.get<number[]>(`${API}/years`, {
      params: { scheme: selectedScheme, taxon: selectedTaxon }
    })
      .then(r => setYears(r.data))
      .catch(e => setError(`Errore caricamento anni: ${e.message}`))
      .finally(() => setLoadingYears(false))
  }, [selectedScheme, selectedTaxon])

  const handleQuery = () => {
    if (!selectedScheme || !selectedTaxon || selectedYear === '') return
    setLoadingRecords(true)
    setError(null)
    setRecords([])
    axios.get<Record[]>(`${API}/records`, {
      params: { scheme: selectedScheme, taxon: selectedTaxon, year: selectedYear }
    })
      .then(r => setRecords(r.data))
      .catch(e => setError(`Errore query: ${e.message}`))
      .finally(() => setLoadingRecords(false))
  }

  const speciesCode = selectedTaxon ? selectedTaxon.split('/').pop() : ''

  return (
    <div style={{ padding: '24px', maxWidth: '1100px', margin: '0 auto' }}>
      <h2 style={{ marginBottom: '6px' }}>Interrogazione ISPRA EPE</h2>
      <p style={{ color: '#666', marginBottom: '24px', fontSize: '14px' }}>
        Query live su <code>dati.isprambiente.it/sparql</code> — modello Darwin-SW 1.0
      </p>

      {/* ── Filtri ── */}
      <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '20px' }}>

        {/* Schema */}
        <div style={{ flex: '1', minWidth: '220px' }}>
          <label style={labelStyle}>Schema di inanellamento</label>
          <select
            value={selectedScheme}
            onChange={e => setSelectedScheme(e.target.value)}
            style={selectStyle}
            disabled={loadingSchemes}
          >
            <option value="">
              {loadingSchemes ? 'Caricamento...' : '— seleziona —'}
            </option>
            {schemes.map(s => (
              <option key={s.uri} value={s.uri}>{s.label} ({s.code})</option>
            ))}
          </select>
        </div>

        {/* Specie */}
        <div style={{ flex: '1', minWidth: '220px' }}>
          <label style={labelStyle}>Specie (EURING 2000)</label>
          <select
            value={selectedTaxon}
            onChange={e => setSelectedTaxon(e.target.value)}
            style={selectStyle}
            disabled={!selectedScheme || loadingTaxa}
          >
            <option value="">
              {loadingTaxa ? 'Caricamento...' : '— seleziona —'}
            </option>
            {taxa.map(t => (
              <option key={t.uri} value={t.uri}>{t.label} ({t.code})</option>
            ))}
          </select>
        </div>

        {/* Anno */}
        <div style={{ flex: '0 0 160px' }}>
          <label style={labelStyle}>Anno occorrenza</label>
          <select
            value={selectedYear}
            onChange={e => setSelectedYear(e.target.value ? Number(e.target.value) : '')}
            style={selectStyle}
            disabled={!selectedTaxon || loadingYears}
          >
            <option value="">
              {loadingYears ? 'Caricamento...' : '— seleziona —'}
            </option>
            {years.map(y => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>

        {/* Bottone */}
        <div style={{ flex: '0 0 auto', display: 'flex', alignItems: 'flex-end' }}>
          <button
            onClick={handleQuery}
            disabled={!selectedScheme || !selectedTaxon || selectedYear === '' || loadingRecords}
            style={{
              padding: '9px 22px',
              background: '#2563eb',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 600,
              opacity: (!selectedScheme || !selectedTaxon || selectedYear === '') ? 0.5 : 1,
            }}
          >
            {loadingRecords ? 'Query...' : 'Cerca'}
          </button>
        </div>
      </div>

      {/* ── Errore ── */}
      {error && (
        <div style={{ background: '#fee2e2', border: '1px solid #fca5a5', borderRadius: '6px', padding: '12px', marginBottom: '16px', color: '#991b1b' }}>
          {error}
        </div>
      )}

      {/* ── Risultati ── */}
      {records.length > 0 && (
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
            <h3 style={{ margin: 0 }}>
              {records.length} individui — specie {speciesCode} — anno {selectedYear}
            </h3>
            <span style={{ fontSize: '13px', color: '#666' }}>
              {records.reduce((n, r) => n + r.occurrences.length, 0)} occorrenze totali
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={tableStyle}>
              <thead>
                <tr style={{ background: '#f1f5f9' }}>
                  <th style={thStyle}>Anello</th>
                  <th style={thStyle}>Schema</th>
                  <th style={thStyle}>Specie</th>
                  <th style={thStyle}>Data inanellamento</th>
                  <th style={thStyle}>Luogo inanell.</th>
                  <th style={thStyle}>Occorrenze nell'anno</th>
                </tr>
              </thead>
              <tbody>
                {records.map((rec, i) => (
                  <tr key={rec.organism_uri} style={{ background: i % 2 === 0 ? '#fff' : '#f8fafc' }}>
                    <td style={tdStyle}><code style={{ fontSize: '13px' }}>{rec.ring_id}</code></td>
                    <td style={tdStyle}>{rec.scheme_code}</td>
                    <td style={tdStyle}>{rec.species_code}</td>
                    <td style={tdStyle}>{rec.ring_date ?? '—'}</td>
                    <td style={tdStyle}>{rec.ring_place_code ?? '—'}</td>
                    <td style={{ ...tdStyle, padding: 0 }}>
                      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <tbody>
                          {rec.occurrences.map((occ, j) => (
                            <tr key={j} style={{ borderBottom: j < rec.occurrences.length - 1 ? '1px solid #e2e8f0' : 'none' }}>
                              <td style={{ padding: '4px 10px', width: '110px' }}>{occ.date}</td>
                              <td style={{ padding: '4px 10px' }}>
                                <span style={{
                                  display: 'inline-block',
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '12px',
                                  fontWeight: 600,
                                  background: occ.event_type === 'first_capture' ? '#dcfce7' : '#dbeafe',
                                  color: occ.event_type === 'first_capture' ? '#166534' : '#1e40af',
                                }}>
                                  {occ.event_type === 'first_capture' ? 'Inanell.' : 'Ricattura'}
                                </span>
                              </td>
                              <td style={{ padding: '4px 10px', fontSize: '12px', color: '#64748b' }}>{occ.place_code ?? '—'}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {!loadingRecords && records.length === 0 && selectedYear !== '' && !error && (
        <p style={{ color: '#64748b', textAlign: 'center', padding: '40px' }}>
          Nessun dato trovato per la combinazione selezionata.
        </p>
      )}
    </div>
  )
}

// ── Stili ─────────────────────────────────────────────────

const labelStyle: React.CSSProperties = {
  display: 'block',
  fontSize: '13px',
  fontWeight: 600,
  marginBottom: '6px',
  color: '#374151',
}

const selectStyle: React.CSSProperties = {
  width: '100%',
  padding: '8px 10px',
  border: '1px solid #d1d5db',
  borderRadius: '6px',
  fontSize: '14px',
  background: '#fff',
}

const tableStyle: React.CSSProperties = {
  width: '100%',
  borderCollapse: 'collapse',
  border: '1px solid #e2e8f0',
  borderRadius: '8px',
  overflow: 'hidden',
  fontSize: '14px',
}

const thStyle: React.CSSProperties = {
  padding: '10px 12px',
  textAlign: 'left',
  fontWeight: 700,
  fontSize: '13px',
  color: '#374151',
  borderBottom: '2px solid #e2e8f0',
}

const tdStyle: React.CSSProperties = {
  padding: '8px 12px',
  verticalAlign: 'top',
  borderBottom: '1px solid #f1f5f9',
}
