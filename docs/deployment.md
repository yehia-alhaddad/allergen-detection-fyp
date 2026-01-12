---
layout: default
title: Deployment Guide
---

# SafeEats Deployment Guide

## Pre-Deployment Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 20.x+ installed
- [ ] PostgreSQL instance (or SQLite for small deployments)
- [ ] NVIDIA GPU driver (CUDA 11.8+) for GPU acceleration
- [ ] `.env.production` file configured
- [ ] Tests passing locally
- [ ] GitHub Actions CI passing

---

## Environment Configuration

### `.env.production` (Backend)

```bash
# FastAPI
ENVIRONMENT=production
LOG_LEVEL=info
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/safeeats
SQLALCHEMY_ECHO=false

# ML Models
MODEL_PATH=/home/appuser/models
OCR_ENGINE=easyocr
NER_CONFIDENCE_THRESHOLD=0.4

# GPU / CPU
USE_GPU=true
GPU_MEMORY_LIMIT=4000  # MB

# Optional: Gemini Enhancement
GEMINI_API_KEY=your_api_key_here
GEMINI_ENABLE=true

# Security
SECRET_KEY=your-secret-key-min-32-chars
API_RATE_LIMIT=30  # requests per minute
```

### `.env.production.local` (Frontend)

```bash
# Next.js
NODE_ENV=production
NEXTAUTH_URL=https://yourdomain.com
NEXTAUTH_SECRET=your-nextauth-secret

# API
ML_API_URL=https://api.yourdomain.com/detect-text
ML_API_IMAGE_URL=https://api.yourdomain.com/detect-image

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/safeeats

# Analytics (optional)
NEXT_PUBLIC_GA_ID=UA-XXXXXXXXX-X
```

---

## Option 1: Heroku Deployment

### Backend Setup

**1. Create Heroku app**:
```bash
heroku create safeeats-api --stack container
```

**2. Add PostgreSQL**:
```bash
heroku addons:create heroku-postgresql:standard-0 -a safeeats-api
```

**3. Set environment variables**:
```bash
heroku config:set ENVIRONMENT=production -a safeeats-api
heroku config:set MODEL_PATH=/app/models -a safeeats-api
heroku config:set USE_GPU=false -a safeeats-api  # No GPU on Heroku free tier
```

**4. Create Dockerfile** (if not present):
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY models/ models/
COPY data/ data/
COPY scripts/ scripts/

CMD ["python", "-m", "uvicorn", "src.api.allergen_api:app", "--host", "0.0.0.0", "--port", "$PORT"]
```

**5. Create `heroku.yml`**:
```yaml
build:
  docker:
    web: Dockerfile
run:
  web: python -m uvicorn src.api.allergen_api:app --host 0.0.0.0 --port $PORT
```

**6. Deploy**:
```bash
git push heroku main
```

**7. Run migrations**:
```bash
heroku run "python -m alembic upgrade head" -a safeeats-api
```

### Frontend Setup (Vercel)

**1. Deploy with Vercel CLI**:
```bash
cd webapp
npm install -g vercel
vercel --prod
```

**Or link GitHub repo in Vercel dashboard:**
- New project → Import Git repo → Select `webapp` directory
- Set environment variables (ML_API_URL, NEXTAUTH_*)
- Deploy

---

## Option 2: AWS Deployment

### Backend (EC2 + RDS)

**1. Launch EC2 instance**:
```bash
# Ubuntu 22.04 LTS, t3.large (or t3.xlarge if using GPU)
# Security group: allow 22 (SSH), 8000 (app), 443 (HTTPS)
```

**2. SSH and setup**:
```bash
ssh -i key.pem ubuntu@<public-ip>

# Install dependencies
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3-pip python3-venv
sudo apt install -y postgresql-client

# Clone repo
git clone https://github.com/yehia-alhaddad/allergen-detection-fyp.git
cd allergen-detection-fyp

# Setup virtual environment
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Download models (if large, use S3)
aws s3 cp s3://your-bucket/models ./models --recursive
```

**3. Create systemd service** (`/etc/systemd/system/safeeats.service`):
```ini
[Unit]
Description=SafeEats FastAPI Service
After=network.target

[Service]
Type=notify
User=ubuntu
WorkingDirectory=/home/ubuntu/allergen-detection-fyp
Environment="PATH=/home/ubuntu/allergen-detection-fyp/.venv/bin"
Environment="DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/safeeats"
ExecStart=/home/ubuntu/allergen-detection-fyp/.venv/bin/python -m uvicorn src.api.allergen_api:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**4. Start service**:
```bash
sudo systemctl enable safeeats
sudo systemctl start safeeats
sudo systemctl status safeeats
```

**5. Setup Nginx** (`/etc/nginx/sites-available/safeeats`):
```nginx
upstream safeeats {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    client_max_body_size 10M;

    location / {
        proxy_pass http://safeeats;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        proxy_pass http://safeeats;
    }
}
```

**6. Enable SSL with Let's Encrypt**:
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot certonly --standalone -d api.yourdomain.com
```

### Frontend (Amplify / Vercel)

Deploy via Vercel as above, or:

**AWS Amplify**:
```bash
npm install -g @aws-amplify/cli
amplify init
amplify add hosting
amplify publish
```

---

## Option 3: Docker Compose (Single Server)

Create `docker-compose.prod.yml`:

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: safeeats
      POSTGRES_USER: safeeats
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  fastapi:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://safeeats:${DB_PASSWORD}@postgres:5432/safeeats
      ENVIRONMENT: production
      USE_GPU: false
    ports:
      - "8000:8000"
    depends_on:
      - postgres
    restart: always
    healthcheck:
      test: curl --fail http://localhost:8000/health || exit 1
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl/:/etc/nginx/ssl:ro
    depends_on:
      - fastapi

volumes:
  postgres_data:
```

**Deploy**:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

---

## Post-Deployment Verification

### 1. Health Check
```bash
curl https://api.yourdomain.com/health
```

Expected:
```json
{
  "status": "healthy",
  "models_loaded": true
}
```

### 2. Smoke Test
```bash
curl -X POST https://api.yourdomain.com/detect-text \
  -H "Content-Type: application/json" \
  -d '{"cleaned_text": "Contains milk"}'
```

### 3. Frontend Load Test
Open `https://yourdomain.com` and test:
- [ ] Signup/login
- [ ] Upload image
- [ ] Scan with camera
- [ ] Enter text
- [ ] View history

---

## Monitoring & Logging

### Backend Logs
```bash
# Heroku
heroku logs -t -a safeeats-api

# AWS EC2
sudo journalctl -u safeeats -f

# Docker
docker-compose logs -f fastapi
```

### Prometheus Metrics (Optional)
Add to `src/api/allergen_api.py`:
```python
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

### Uptime Monitoring
Set up monitoring service:
- **UptimeRobot**: Free tier pings `/health` every 5 minutes
- **Sentry**: Automatic error tracking

---

## Scaling Considerations

| Component | Single Server | Multi-Server |
|-----------|---|---|
| Backend | Systemd service | Kubernetes / ECS |
| Frontend | Vercel / Amplify | Vercel / Amplify |
| Database | RDS single-AZ | RDS multi-AZ |
| Cache | Redis (optional) | Redis cluster |
| Load Balancer | None | AWS ALB / Nginx |

---

## Cost Estimates (Monthly)

| Platform | Service | Cost |
|----------|---------|------|
| **Heroku** | Web dyno (1x) | $50 |
| | PostgreSQL | $50 |
| | **Total** | **$100** |
| **AWS** | EC2 t3.large | $60 |
| | RDS multi-AZ | $150 |
| | **Total** | **$210** |
| **Vercel** | Pro plan | $20 |
| **DigitalOcean** | App + DB | $80 |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Models too large | Compress or use S3/CDN; lazy load on startup |
| Cold start >10s | Reduce model size; use GPU for warmup |
| Rate limit errors | Increase rate limit; add caching layer |
| High memory usage | Reduce batch size; enable memory profiling |

---

## CI/CD Pipeline (GitHub Actions)

Existing `.github/workflows/ci.yml` runs tests on every push. To auto-deploy:

```yaml
deploy:
  runs-on: ubuntu-latest
  needs: [python, webapp]
  if: github.ref == 'refs/heads/main'
  steps:
    - uses: actions/checkout@v4
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.13.15
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "safeeats-api"
```

---

## Disaster Recovery

### Backup Database
```bash
# Heroku
heroku pg:backups:capture -a safeeats-api

# AWS RDS
aws rds create-db-snapshot --db-instance-identifier safeeats
```

### Restore from Backup
```bash
heroku pg:backups:restore [backup-id] -a safeeats-api
```

---

**Need help?** Check [GitHub Issues](https://github.com/yehia-alhaddad/allergen-detection-fyp/issues) or contact the development team.
