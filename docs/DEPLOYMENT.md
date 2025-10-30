# Deployment Guide

## Production Deployment

### Backend Deployment

#### 1. Environment Setup

Create production environment file:
```bash
cd backend
cp .env.example .env.production
```

Edit `.env.production`:
```
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=False

# CORS
CORS_ORIGINS=["https://your-domain.com"]

# Data Sources
NOAA_SWPC_BASE_URL=https://services.swpc.noaa.gov
NASA_CDDIS_BASE_URL=https://cddis.nasa.gov

# Update Intervals (seconds)
DATA_UPDATE_INTERVAL=300
PREDICTION_UPDATE_INTERVAL=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ionospheric/app.log
```

#### 2. Install Dependencies
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # Production WSGI server
```

#### 3. Run with Gunicorn
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120 \
  --access-logfile /var/log/ionospheric/access.log \
  --error-logfile /var/log/ionospheric/error.log
```

#### 4. Systemd Service

Create `/etc/systemd/system/ionospheric-api.service`:
```ini
[Unit]
Description=Ionospheric Storm Prediction API
After=network.target

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/ionospheric/backend
Environment="PATH=/opt/ionospheric/backend/venv/bin"
ExecStart=/opt/ionospheric/backend/venv/bin/gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable ionospheric-api
sudo systemctl start ionospheric-api
sudo systemctl status ionospheric-api
```

### Frontend Deployment

#### 1. Build for Production
```bash
cd frontend
npm install
npm run build
```

Output: `dist/` directory

#### 2. Environment Configuration

Create `.env.production`:
```
VITE_API_URL=https://api.your-domain.com/api/v1
VITE_WS_URL=wss://api.your-domain.com/api/v1
```

Rebuild:
```bash
npm run build
```

#### 3. Nginx Configuration

Create `/etc/nginx/sites-available/ionospheric`:
```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Frontend
    root /var/www/ionospheric/dist;
    index index.html;

    # Compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket
    location /api/v1/ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 86400;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|svg|ico|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/ionospheric /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### 4. SSL Certificate (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Docker Deployment

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: ionospheric-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - LOG_LEVEL=INFO
    volumes:
      - ./backend:/app
      - ./logs:/var/log/ionospheric
    command: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

  frontend:
    build: ./frontend
    container_name: ionospheric-web
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

### Backend Dockerfile

Create `backend/Dockerfile`:
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Frontend Dockerfile

Create `frontend/Dockerfile`:
```dockerfile
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Deploy
```bash
docker-compose up -d
docker-compose logs -f
```

## Monitoring

### Health Checks
```bash
# Backend
curl http://localhost:8000/api/v1/health

# Check logs
sudo journalctl -u ionospheric-api -f
```

### Performance Monitoring
- Use Prometheus + Grafana for metrics
- Monitor API response times
- Track WebSocket connections
- Monitor memory usage (TensorFlow models)

### Error Tracking
- Configure Sentry or similar for error tracking
- Set up log aggregation (ELK stack)

## Scaling

### Horizontal Scaling
- Deploy multiple backend instances behind load balancer
- Use Redis for session storage if needed
- Share WebSocket connections via Redis pub/sub

### Database (Optional)
For persistent historical data:
- PostgreSQL + TimescaleDB for time-series data
- Store predictions and TEC measurements
- Enable historical analysis beyond current implementation

## Security Checklist

- [ ] Enable HTTPS/WSS only
- [ ] Configure CORS properly
- [ ] Set up rate limiting
- [ ] Use environment variables for secrets
- [ ] Enable firewall (ufw/iptables)
- [ ] Regular security updates
- [ ] Monitor access logs
- [ ] Set up fail2ban for brute force protection

## Backup

### Database Backup (if using)
```bash
pg_dump ionospheric > backup_$(date +%Y%m%d).sql
```

### Configuration Backup
```bash
tar -czf config_backup.tar.gz backend/.env frontend/.env nginx.conf
```

## Rollback

### Backend
```bash
sudo systemctl stop ionospheric-api
cd /opt/ionospheric/backend
git checkout previous-version
sudo systemctl start ionospheric-api
```

### Frontend
```bash
cd /var/www/ionospheric
rm -rf dist
cp -r dist.backup dist
sudo systemctl reload nginx
```
