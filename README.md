# 🦅 Semantic EPE - EURING Code Recognition System

Sistema semantico completo per il riconoscimento e la conversione automatica dei codici EURING tra diverse versioni (1966, 1979, 2000, 2020) con compatibilità EPE ASP.

## 🎯 Panoramica

Il sistema EURING è composto da:
- **Backend API** (FastAPI + Python) per riconoscimento e conversione
- **Frontend Web** (React + TypeScript + Vite) per interfaccia utente
- **Sistema semantico** per conversioni intelligenti tra versioni
- **Batch processing** per elaborazione di grandi volumi

## 🚀 Avvio Rapido

### Prerequisiti
- Python 3.8+
- Node.js 16+
- npm o yarn

### 1. Avvia il Backend
```bash
# Metodo automatico
./start_euring_system.sh

# O manualmente
cd backend
pip install fastapi uvicorn pydantic
PYTHONPATH=. python3 main.py
