import { useState } from 'react'
import './LizzyButton.css'

const LIZZY_URL = import.meta.env.VITE_LIZZY_URL ?? 'http://localhost:3000'

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
