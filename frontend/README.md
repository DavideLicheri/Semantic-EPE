# 🎨 EURING Frontend - Interfaccia Utente

Frontend React + TypeScript + Vite per il sistema EURING Code Recognition.

## 🚀 Avvio Rapido

### Prerequisiti
- Node.js 16+ 
- npm o yarn
- Backend EURING in esecuzione su http://localhost:8000

### Installazione e Avvio

```bash
# Dalla directory root del progetto
./start_frontend.sh

# O manualmente:
cd frontend
npm install
npm run dev
```

Il frontend sarà disponibile su **http://localhost:3000**

## 🏗️ Architettura

```
frontend/
├── src/
│   ├── components/          # Componenti React
│   │   ├── RecognitionPanel.tsx    # Pannello riconoscimento
│   │   ├── ConversionPanel.tsx     # Pannello conversione
│   │   └── ResultsPanel.tsx        # Pannello risultati
│   ├── services/           # Servizi API
│   │   └── api.ts         # Client API per backend
│   ├── types/             # Definizioni TypeScript
│   │   ├── api-types.ts   # Tipi API
│   │   └── euring-types.ts # Tipi EURING
│   ├── App.tsx            # Componente principale
│   ├── main.tsx           # Entry point
│   └── index.css          # Stili globali
├── index.html             # Template HTML
├── package.json           # Dipendenze
└── vite.config.ts         # Configurazione Vite
```

## 🎯 Funzionalità

### 🔍 Pannello Riconoscimento
- **Riconoscimento singolo**: Analizza una stringa EURING
- **Riconoscimento batch**: Analizza più stringhe (max 100)
- **Analisi dettagliata**: Include discriminanti e metriche
- **Esempi integrati**: Carica esempi per ogni versione
- **Validazione input**: Controlli di formato in tempo reale

### 🔄 Pannello Conversione
- **Conversione singola**: Converti tra versioni EURING
- **Conversione batch**: Converti più stringhe (max 50)
- **Auto-rilevamento**: Rileva automaticamente versione sorgente
- **Conversione semantica**: Mantiene integrità semantica
- **Note dettagliate**: Mostra note di conversione

### 📊 Risultati
- **Visualizzazione chiara**: Risultati organizzati e leggibili
- **Metriche performance**: Tempi di elaborazione e confidenza
- **Copia negli appunti**: Copia risultati con un click
- **Export multipli**: JSON, CSV, TXT
- **Statistiche**: Riepilogo successi/errori

## 🎨 Design

### Tema e Colori
- **Gradiente principale**: `#667eea` → `#764ba2`
- **Sfondo**: Gradiente blu-viola
- **Cards**: Bianco con ombre sottili
- **Successo**: Verde `#28a745`
- **Errore**: Rosso `#dc3545`
- **Warning**: Giallo `#ffc107`

### Responsive Design
- **Desktop**: Layout a colonne ottimizzato
- **Tablet**: Layout adattivo con stack verticale
- **Mobile**: Interfaccia touch-friendly

### Accessibilità
- **Contrasti**: WCAG AA compliant
- **Keyboard navigation**: Supporto completo
- **Screen readers**: ARIA labels appropriati
- **Focus indicators**: Visibili e chiari

## 🔧 Configurazione

### Proxy API
Il frontend è configurato per proxy delle chiamate API:
```typescript
// vite.config.ts
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    }
  }
}
```

### Variabili Ambiente
Crea `.env.local` per configurazioni personalizzate:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

## 📡 Integrazione API

### Client API
```typescript
import { EuringAPI } from './services/api';

// Riconoscimento
const result = await EuringAPI.recognize({
  euring_string: "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
  include_analysis: true
});

// Conversione
const conversion = await EuringAPI.convert({
  euring_string: "5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750",
  source_version: "1966",
  target_version: "2020",
  use_semantic: true
});
```

### Gestione Errori
- **Network errors**: Retry automatico
- **API errors**: Messaggi user-friendly
- **Validation errors**: Feedback in tempo reale
- **Loading states**: Indicatori di caricamento

## 🧪 Testing

### Test Manuali
1. **Riconoscimento**: Testa con stringhe di esempio
2. **Conversione**: Verifica conversioni bidirezionali
3. **Batch**: Testa con multiple stringhe
4. **Export**: Verifica download file
5. **Responsive**: Testa su diversi dispositivi

### Esempi di Test
```typescript
// Stringhe di test per ogni versione
const testStrings = {
  '1966': '5320 TA12345 3 11022023 5215N 01325E 10 2 050 0115 0750',
  '1979': '05320ISA12345 099200501199505215215N01325E10321--0500115--075010--001090------',
  '2000': 'IABA0SA...7285004ZZ1187011870H0ZUMM55U-----0105200600600IA13+452409+009033908200400000---00086',
  '2020': '05320|ISA12345|0|09920|3|2|20230521|1430|52.25412|-1.34521|1|10|01|0|0|135.5|19.5|4|2|0|0|2'
};
```

## 🚀 Build e Deploy

### Build di Produzione
```bash
npm run build
```

### Preview Build
```bash
npm run preview
```

### Deploy
Il build genera file statici in `dist/` pronti per deploy su:
- **Netlify**: Drag & drop della cartella `dist`
- **Vercel**: Connessione GitHub automatica
- **Apache/Nginx**: Servire file statici
- **AWS S3**: Hosting statico

### Configurazione Server
Per SPA routing, configura il server per servire `index.html` per tutte le route:

**Nginx:**
```nginx
location / {
  try_files $uri $uri/ /index.html;
}
```

**Apache:**
```apache
RewriteEngine On
RewriteRule ^(?!.*\.).*$ /index.html [L]
```

## 📱 Utilizzo

### Workflow Tipico

1. **Avvia Backend**
   ```bash
   ./start_euring_system.sh
   ```

2. **Avvia Frontend**
   ```bash
   ./start_frontend.sh
   ```

3. **Accedi all'Interfaccia**
   - Apri http://localhost:3000
   - Scegli tab "Riconoscimento" o "Conversione"

4. **Riconoscimento**
   - Incolla stringa EURING
   - Abilita analisi dettagliata se necessario
   - Clicca "Riconosci"
   - Visualizza risultati con confidenza e metriche

5. **Conversione**
   - Incolla stringa EURING
   - Seleziona versioni sorgente e target
   - Abilita auto-rilevamento (consigliato)
   - Clicca "Converti"
   - Copia risultato o esporta

6. **Batch Processing**
   - Abilita modalità batch
   - Incolla multiple stringhe (una per riga)
   - Processa fino a 100 riconoscimenti o 50 conversioni
   - Esporta risultati in JSON/CSV/TXT

## 🔍 Troubleshooting

### Problemi Comuni

**Frontend non si avvia:**
```bash
# Pulisci cache e reinstalla
rm -rf node_modules package-lock.json
npm install
```

**API non raggiungibile:**
- Verifica che il backend sia in esecuzione su porta 8000
- Controlla configurazione proxy in `vite.config.ts`
- Verifica CORS nel backend

**Build fallisce:**
```bash
# Controlla errori TypeScript
npm run lint
npx tsc --noEmit
```

**Performance lente:**
- Riduci numero stringhe in batch
- Disabilita analisi dettagliata se non necessaria
- Controlla connessione di rete

### Debug

**Console del Browser:**
- Apri DevTools (F12)
- Controlla tab Console per errori JavaScript
- Controlla tab Network per chiamate API

**Logs API:**
- Le chiamate API sono loggate automaticamente
- Controlla console per request/response details

## 📚 Risorse

- **Vite**: https://vitejs.dev/
- **React**: https://react.dev/
- **TypeScript**: https://www.typescriptlang.org/
- **Axios**: https://axios-http.com/

## 🎉 Conclusione

Il frontend EURING fornisce un'interfaccia moderna e intuitiva per:
- ✅ Riconoscimento automatico versioni EURING
- ✅ Conversione semantica tra versioni
- ✅ Batch processing ottimizzato
- ✅ Export risultati multipli formati
- ✅ Design responsive e accessibile

**Sistema completo e pronto per l'uso!** 🚀