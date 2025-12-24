#!/bin/bash

echo "🚀 Avvio Demo EURING con ngrok per condivisione remota"
echo "=================================================="

# Controlla se ngrok è installato
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok non trovato. Installalo con:"
    echo "   npm install -g ngrok"
    echo "   oppure scarica da https://ngrok.com/download"
    exit 1
fi

echo "✅ ngrok trovato"

# Avvia backend in background
echo "🔧 Avvio backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Aspetta che il backend si avvii
sleep 3

# Avvia frontend in background  
echo "🎨 Avvio frontend..."
cd frontend
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!
cd ..

# Aspetta che il frontend si avvii
sleep 5

echo "🌐 Avvio tunnel ngrok..."

# Avvia ngrok per backend
ngrok http 8000 &
NGROK_BACKEND_PID=$!

# Avvia ngrok per frontend
ngrok http 5173 &
NGROK_FRONTEND_PID=$!

echo ""
echo "🎉 Setup completato!"
echo ""
echo "📋 ISTRUZIONI:"
echo "1. Vai su http://localhost:4040 per vedere gli URL ngrok"
echo "2. Copia l'URL del backend (porta 8000) e aggiornalo in frontend/src/services/api.ts"
echo "3. Ricompila il frontend: cd frontend && npm run build"
echo "4. Condividi l'URL del frontend (porta 5173) con i colleghi"
echo ""
echo "🛑 Per fermare tutto: Ctrl+C e poi esegui:"
echo "   kill $BACKEND_PID $FRONTEND_PID $NGROK_BACKEND_PID $NGROK_FRONTEND_PID"

# Mantieni lo script attivo
wait