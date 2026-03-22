# ECES — EURING Code Evolution System

**ISPRA - DG SINA**

[EURING](https://www.euring.org) (European Union for Bird Ringing) è l'organizzazione scientifica che coordina l'inanellamento degli uccelli selvatici in Europa e oltre, raccogliendo e armonizzando i dati provenienti da oltre 40 paesi. Per lo scambio standardizzato di queste informazioni, EURING ha definito nel tempo un codice posizionale — il **codice EURING** — che ha subito diverse revisioni (1966, 1979, 2000, 2020), ciascuna con struttura, lunghezza e semantica dei campi proprie.

ECES nasce per gestire questa evoluzione: permette di confrontare le versioni del codice, mantenere una mappatura semantica cross-versione (EPE ASP) e modificare le definizioni dei campi in modo controllato e persistente.

---

Sistema web completo per la gestione semantica delle versioni del codice EURING (1966, 1979, 2000, 2020). Permette di visualizzare, editare e confrontare la matrice posizionale dei campi EURING, con supporto alla mappatura semantica cross-versione (EPE ASP).

---

## Funzionalità principali

- **Matrice EURING** — visualizzazione comparativa di tutti i campi nelle 4 versioni, con ordinamento EPE e identificazione dei campi aggiuntivi per versione
- **Editor Campi** — modifica interattiva delle proprietà dei campi (descrizione, tipo, posizione, lunghezza, dominio semantico, nome canonico cross-versione, valori ammessi)
- **Aggiunta e cancellazione campi** per singola versione
- **Riconoscimento automatico** della versione di una stringa EURING
- **Conversione semantica** tra versioni
- **Autenticazione** con ruoli (viewer, super_admin)
- **Persistenza SKOS** su file JSON con invalidazione cache

---

## Stack

| Livello | Tecnologie |
|---------|-----------|
| Backend | Python 3.10, FastAPI, Uvicorn |
| Frontend | React 18, TypeScript, Vite |
| Dati | JSON (SKOS-like), SHA-256 auth |

---

## Avvio locale

### Backend

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. python3 main.py
```

Disponibile su **http://localhost:8000** — Docs interattive: http://localhost:8000/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Disponibile su **http://localhost:3000**

---

## Struttura del progetto

```
├── backend/
│   ├── app/
│   │   ├── api/           # Endpoint FastAPI (euring_api.py, auth_api.py)
│   │   ├── auth/          # Autenticazione JWT + ruoli
│   │   ├── models/        # Modelli Pydantic (EuringVersion, FieldDefinition…)
│   │   ├── repositories/  # Persistenza JSON (SKOSRepository)
│   │   └── services/      # Business logic (SKOSManager, LookupTableService…)
│   ├── data/
│   │   ├── auth/          # Utenti (users.json)
│   │   └── euring_versions/
│   │       └── versions/  # euring_1966.json, euring_1979.json, euring_2000.json, euring_2020.json
│   └── main.py
│
└── frontend/
    └── src/
        ├── components/
        │   ├── EuringMatrix.tsx          # Matrice comparativa (vista tabella + positionale)
        │   ├── PositionalMatrixEditor.tsx # Editor campi con pannello laterale
        │   ├── PositionalMatrix.tsx       # Visualizzazione posizionale interattiva
        │   └── ...
        └── services/
            └── api.ts                    # Client API tipizzato
```

---

## Versioni EURING supportate

| Versione | Formato | Note |
|----------|---------|------|
| 1966 | Spazi | Prima versione, campi separati da spazi |
| 1979 | Posizionale fisso | 78 caratteri |
| 2000 | Posizionale fisso | 96 caratteri, standard EPE |
| 2020 | Pipe-delimited | Formato moderno con coordinate decimali |

---

## API principali

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| `GET` | `/api/euring/versions/matrix` | Matrice completa campi × versioni |
| `PUT` | `/api/euring/versions/matrix/field` | Aggiorna proprietà di un campo |
| `POST` | `/api/euring/versions/matrix/field/add` | Aggiunge un campo a una versione |
| `DELETE` | `/api/euring/versions/matrix/field/remove` | Rimuove un campo da una versione |
| `POST` | `/api/euring/recognize` | Riconoscimento versione stringa |
| `POST` | `/api/euring/convert` | Conversione tra versioni |
| `POST` | `/api/auth/login` | Login |
| `GET` | `/api/auth/me` | Utente corrente |

---

## Licenza

Uso interno ISPRA — sviluppato per la gestione dei dati di inanellamento degli uccelli.
