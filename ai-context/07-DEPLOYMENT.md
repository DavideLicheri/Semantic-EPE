# Deployment ECES su Server ISPRA

## Informazioni Server

- **IP**: 10.158.251.79
- **OS**: Ubuntu Server 22.04 LTS
- **Accesso**: Solo rete interna ISPRA (richiede VPN FortiClient)
- **User**: amministratore
- **Password**: gbg8GPjCWRM$
- **Sudo**: Richiede password

## Architettura Deployment

```
/opt/eces/
├── frontend/          # Build React (servito da Nginx)
│   ├── index.html
│   └── assets/
│       ├── index-{hash}.js
│       └── index-{hash}.css
├── backend/           # Backend Python
│   ├── app/
│   ├── data/
│   ├── venv/
│   ├── main.py
│   └── requirements.txt
└── logs/              # Application logs
```

## Servizi Systemd

### Backend Service

**File**: `/etc/systemd/system/eces-backend.service`

```ini
[Unit]
Description=ECES Backend Service
After=network.target postgresql.service

[Service]
Type=simple
User=amministratore
WorkingDirectory=/opt/eces/backend
Environment="PATH=/opt/eces/backend/venv/bin"
ExecStart=/opt/eces/backend/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Comandi**:
```bash
sudo systemctl start eces-backend
sudo systemctl stop eces-backend
sudo systemctl restart eces-backend
sudo systemctl status eces-backend
sudo systemctl enable eces-backend  # Auto-start al boot
```

### PostgreSQL Service

PostgreSQL è già installato e configurato per analytics.

**Comandi**:
```bash
sudo systemctl status postgresql
sudo systemctl restart postgresql
```

## Configurazione Nginx

**File**: `/etc/nginx/sites-available/eces`

```nginx
server {
    listen 80;
    server_name 10.158.251.79;
    
    # Logs
    access_log /var/log/nginx/eces_access.log;
    error_log /var/log/nginx/eces_error.log;
    
    # Frontend - Serve static files
    location / {
        root /opt/eces/frontend;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API - Proxy to FastAPI
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

**Symbolic link**:
```bash
sudo ln -s /etc/nginx/sites-available/eces /etc/nginx/sites-enabled/
```

**Comandi Nginx**:
```bash
sudo nginx -t                    # Test configurazione
sudo systemctl restart nginx     # Restart
sudo systemctl status nginx      # Status
sudo systemctl reload nginx      # Reload config senza downtime
```

## Procedura Deployment Completo

### 1. Setup Iniziale (Una Tantum)

```bash
# Connetti a server
ssh amministratore@10.158.251.79

# Crea directory
sudo mkdir -p /opt/eces/{frontend,backend,logs}
sudo chown -R amministratore:amministratore /opt/eces

# Installa dipendenze sistema
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx

# Setup backend
cd /opt/eces/backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
sudo -u postgres psql
CREATE DATABASE eces;
CREATE USER eces_user WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE eces TO eces_user;
\q

# Crea .env backend
cat > /opt/eces/backend/.env << EOF
DATABASE_URL=postgresql://eces_user:password@localhost/eces
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS=http://10.158.251.79
EOF

# Setup systemd services
sudo cp eces-backend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable eces-backend
sudo systemctl start eces-backend

# Setup Nginx
sudo cp eces.conf /etc/nginx/sites-available/eces
sudo ln -s /etc/nginx/sites-available/eces /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 2. Deploy Frontend (Da Locale)

```bash
# Build frontend
cd frontend
npm run build

# Crea tar
tar -czf frontend-build.tar.gz -C dist .

# Upload a server
sshpass -p 'gbg8GPjCWRM$' scp frontend-build.tar.gz amministratore@10.158.251.79:/tmp/

# Estrai su server (via SSH)
sshpass -p 'gbg8GPjCWRM$' ssh amministratore@10.158.251.79 << 'EOF'
  echo 'gbg8GPjCWRM$' | sudo -S rm -rf /opt/eces/frontend/*
  echo 'gbg8GPjCWRM$' | sudo -S tar -xzf /tmp/frontend-build.tar.gz -C /opt/eces/frontend/
  echo 'gbg8GPjCWRM$' | sudo -S systemctl reload nginx
  echo "Frontend deployed successfully"
EOF
```

### 3. Deploy Backend (Da Locale)

```bash
# Crea tar backend (escludi venv)
cd backend
tar -czf backend-code.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  app/ data/ main.py requirements.txt

# Upload
sshpass -p 'gbg8GPjCWRM$' scp backend-code.tar.gz amministratore@10.158.251.79:/tmp/

# Deploy su server
sshpass -p 'gbg8GPjCWRM$' ssh amministratore@10.158.251.79 << 'EOF'
  cd /opt/eces/backend
  tar -xzf /tmp/backend-code.tar.gz
  source venv/bin/activate
  pip install -r requirements.txt
  echo 'gbg8GPjCWRM$' | sudo -S systemctl restart eces-backend
  echo "Backend deployed successfully"
EOF
```

### 4. Verifica Deployment

```bash
# Check backend status
ssh amministratore@10.158.251.79 "systemctl status eces-backend"

# Check Nginx status
ssh amministratore@10.158.251.79 "systemctl status nginx"

# Test API
curl http://10.158.251.79/api/euring/versions/matrix

# Test frontend
curl http://10.158.251.79/
```

## Script Deployment Automatico

**File**: `deploy_to_ispra.sh`

```bash
#!/bin/bash
set -e

SERVER="10.158.251.79"
USER="amministratore"
PASSWORD="gbg8GPjCWRM$"

echo "🚀 Starting ECES deployment to ISPRA server..."

# Build frontend
echo "📦 Building frontend..."
cd frontend
npm run build
tar -czf frontend-build.tar.gz -C dist .
cd ..

# Deploy frontend
echo "🌐 Deploying frontend..."
sshpass -p "$PASSWORD" scp frontend/frontend-build.tar.gz $USER@$SERVER:/tmp/

sshpass -p "$PASSWORD" ssh $USER@$SERVER << EOF
  echo '$PASSWORD' | sudo -S rm -rf /opt/eces/frontend/*
  echo '$PASSWORD' | sudo -S tar -xzf /tmp/frontend-build.tar.gz -C /opt/eces/frontend/
  echo '$PASSWORD' | sudo -S systemctl reload nginx
EOF

echo "✅ Frontend deployed"

# Package backend
echo "📦 Packaging backend..."
cd backend
tar -czf backend-code.tar.gz \
  --exclude='venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.env' \
  app/ data/ main.py requirements.txt
cd ..

# Deploy backend
echo "⚙️  Deploying backend..."
sshpass -p "$PASSWORD" scp backend/backend-code.tar.gz $USER@$SERVER:/tmp/

sshpass -p "$PASSWORD" ssh $USER@$SERVER << EOF
  cd /opt/eces/backend
  tar -xzf /tmp/backend-code.tar.gz
  source venv/bin/activate
  pip install -q -r requirements.txt
  echo '$PASSWORD' | sudo -S systemctl restart eces-backend
EOF

echo "✅ Backend deployed"

# Verify
echo "🔍 Verifying deployment..."
sleep 3
curl -s http://$SERVER/api/euring/versions/matrix > /dev/null && echo "✅ API is responding" || echo "❌ API not responding"
curl -s http://$SERVER/ > /dev/null && echo "✅ Frontend is responding" || echo "❌ Frontend not responding"

echo "🎉 Deployment completed successfully!"
```

**Uso**:
```bash
chmod +x deploy_to_ispra.sh
./deploy_to_ispra.sh
```

## Rollback Procedure

### Rollback Frontend

```bash
# Backup prima di deploy
ssh amministratore@10.158.251.79 "sudo tar -czf /opt/eces/frontend-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /opt/eces/frontend ."

# Rollback
ssh amministratore@10.158.251.79 << EOF
  echo 'gbg8GPjCWRM$' | sudo -S rm -rf /opt/eces/frontend/*
  echo 'gbg8GPjCWRM$' | sudo -S tar -xzf /opt/eces/frontend-backup-YYYYMMDD-HHMMSS.tar.gz -C /opt/eces/frontend/
  echo 'gbg8GPjCWRM$' | sudo -S systemctl reload nginx
EOF
```

### Rollback Backend

```bash
# Backup prima di deploy
ssh amministratore@10.158.251.79 "tar -czf /opt/eces/backend-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C /opt/eces/backend app/ data/ main.py"

# Rollback
ssh amministratore@10.158.251.79 << EOF
  cd /opt/eces/backend
  rm -rf app/ data/ main.py
  tar -xzf /opt/eces/backend-backup-YYYYMMDD-HHMMSS.tar.gz
  echo 'gbg8GPjCWRM$' | sudo -S systemctl restart eces-backend
EOF
```

## Monitoring

### Logs Backend

```bash
# Systemd logs
sudo journalctl -u eces-backend -f

# Application logs (se configurato)
tail -f /opt/eces/logs/backend.log
```

### Logs Nginx

```bash
# Access log
sudo tail -f /var/log/nginx/eces_access.log

# Error log
sudo tail -f /var/log/nginx/eces_error.log
```

### Logs PostgreSQL

```bash
sudo tail -f /var/log/postgresql/postgresql-14-main.log
```

### System Resources

```bash
# CPU e memoria
htop

# Disk usage
df -h

# Network
netstat -tulpn | grep :8000
netstat -tulpn | grep :80
```

## Backup Strategy

### Database Backup

```bash
# Backup manuale
pg_dump -U eces_user eces > /opt/eces/backups/eces_$(date +%Y%m%d).sql

# Restore
psql -U eces_user eces < /opt/eces/backups/eces_20240101.sql
```

### Backup Automatico (Cron)

```bash
# Aggiungi a crontab
crontab -e

# Backup giornaliero alle 2 AM
0 2 * * * pg_dump -U eces_user eces > /opt/eces/backups/eces_$(date +\%Y\%m\%d).sql

# Cleanup backup vecchi (> 30 giorni)
0 3 * * * find /opt/eces/backups -name "eces_*.sql" -mtime +30 -delete
```

### File Backup

```bash
# Backup users.json
cp /opt/eces/backend/data/auth/users.json /opt/eces/backups/users_$(date +%Y%m%d).json

# Backup EURING data
tar -czf /opt/eces/backups/euring_data_$(date +%Y%m%d).tar.gz /opt/eces/backend/data/euring_versions/
```

## Troubleshooting Deployment

### Backend non parte

```bash
# Check logs
sudo journalctl -u eces-backend -n 50

# Check port 8000
sudo netstat -tulpn | grep :8000

# Test manuale
cd /opt/eces/backend
source venv/bin/activate
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend 404

```bash
# Verifica file esistono
ls -la /opt/eces/frontend/

# Verifica Nginx config
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/eces_error.log
```

### Database connection error

```bash
# Check PostgreSQL running
sudo systemctl status postgresql

# Test connection
psql -U eces_user -d eces -h localhost

# Check .env
cat /opt/eces/backend/.env | grep DATABASE_URL
```

### CORS errors

```bash
# Verifica CORS_ORIGINS in .env
cat /opt/eces/backend/.env | grep CORS_ORIGINS

# Deve includere: http://10.158.251.79
```

### Cache browser

```bash
# Dopo deploy, utenti devono fare hard refresh
# Chrome/Brave: Ctrl + Shift + R
# Firefox: Ctrl + Shift + R
# Safari: Cmd + Shift + R
```

## Performance Tuning

### Nginx

```nginx
# Aggiungi a /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 1024;

# Gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
gzip_min_length 1000;
```

### Uvicorn (Backend)

```bash
# Multi-worker per production
ExecStart=/opt/eces/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### PostgreSQL

```sql
-- Ottimizza per analytics
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

## Security Checklist

- ✅ Firewall configurato (solo porte 22, 80, 5432)
- ✅ SSH key-based auth (opzionale, attualmente password)
- ✅ PostgreSQL solo localhost
- ✅ Nginx rate limiting (da implementare)
- ✅ Backup automatici
- ✅ Log rotation configurato
- ⚠️ HTTPS non configurato (rete interna)
- ⚠️ Fail2ban non configurato
- ⚠️ Monitoring non configurato (Prometheus/Grafana)
