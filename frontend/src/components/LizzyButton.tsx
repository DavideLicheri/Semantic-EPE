import { useState } from 'react'
import './LizzyButton.css'

// Nessun indirizzo hardcoded: di default punta alla stessa macchina da cui
// l'utente sta già raggiungendo ECES (VPN IP, hostname, ecc.), sulla porta
// dedicata al proxy nginx→Open WebUI (vedi /etc/nginx/sites-available/lizzy-proxy.conf
// sulla VM). VITE_LIZZY_URL resta disponibile come override esplicito se mai servisse.
const LIZZY_URL =
  import.meta.env.VITE_LIZZY_URL ??
  `${window.location.protocol}//${window.location.hostname}:8081`

export default function LizzyButton() {
  const [open, setOpen] = useState(false)

  return (
    <>
      {open && (
        <div className="lizzy-panel">
          <div className="lizzy-panel-header">
            <span>💬 Lizzy</span>
            <button className="lizzy-close-btn" onClick={() => setOpen(false)} aria-label="Chiudi Lizzy">✕</button>
          </div>
          <iframe
            src={LIZZY_URL}
            className="lizzy-iframe"
            title="Lizzy"
            allow="microphone"
            sandbox="allow-same-origin allow-scripts allow-forms allow-popups"
          />
        </div>
      )}
      <button
        className="lizzy-fab"
        onClick={() => setOpen(o => !o)}
        aria-label={open ? 'Chiudi Lizzy' : 'Apri Lizzy'}
      >
        💬 Lizzy
      </button>
    </>
  )
}
