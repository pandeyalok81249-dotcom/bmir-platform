# Production Deployment Guide
## AI Resume Intelligence Platform

This guide outlines the production deployment procedure using Docker, PostgreSQL 16, Redis 7, and FastAPI.

---

### 1. Prerequisites

- Virtual Server (Ubuntu 22.04 LTS or Debian 12 with 4GB+ RAM, 2+ vCPUs recommended)
- Docker Engine >= 26.0 & Docker Compose >= 2.24
- Domain name with DNS A records pointing to server IP
- SSL Certificate (Let's Encrypt / Certbot)

---

### 2. Environment Variables Configuration

Create `/app/.env` on the host:

```env
# Application Settings
ENVIRONMENT=production
DEBUG=False
PROJECT_NAME="AI Resume Intelligence Platform"
API_V1_STR="/api/v1"

# Security (Generate using: openssl rand -hex 32)
SECRET_KEY="<generate-64-char-hex-secret>"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Production Database (PostgreSQL with asyncpg)
DATABASE_URL="postgresql+asyncpg://postgres:secure_production_password@postgres:5432/resume_intelligence"

# Cache & Asynchronous Broker
REDIS_URL="redis://redis:6379/0"

# Multi-Provider AI Credentials
OPENAI_API_KEY="sk-..."
OPENAI_DEFAULT_MODEL="gpt-4o-mini"
GEMINI_API_KEY="AIzaSy..."
GEMINI_DEFAULT_MODEL="gemini-1.5-flash"
PREFERRED_AI_PROVIDER="gemini"

# Google Sign-In OAuth
GOOGLE_CLIENT_ID="<client-id>.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="<client-secret>"

# Encrypted Document Storage (Local or S3)
STORAGE_BACKEND="local"
LOCAL_STORAGE_PATH="./uploads"

# CORS Allowed Origins
BACKEND_CORS_ORIGINS=["https://app.yourdomain.com", "https://api.yourdomain.com"]
```

---

### 3. Deploying with Docker Compose

1. Clone repository to server:
   ```bash
   git clone https://github.com/your-org/resume-intelligence-platform.git
   cd resume-intelligence-platform
   ```

2. Start the database and cache services:
   ```bash
   docker compose -f docker/docker-compose.yml up -d postgres redis
   ```

3. Run Alembic migrations against the database:
   ```bash
   docker compose -f docker/docker-compose.yml run --rm backend alembic upgrade head
   ```

4. Launch the application stack:
   ```bash
   docker compose -f docker/docker-compose.yml up -d --build
   ```

5. Verify container health:
   ```bash
   docker compose -f docker/docker-compose.yml ps
   curl -f http://localhost:8000/health
   ```

---

### 4. Reverse Proxy & SSL Configuration (Nginx)

```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    client_max_body_size 12M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 5. Database Backup Automation

Configure daily cron backup:
```bash
0 2 * * * docker exec resume_intel_postgres pg_dump -U postgres resume_intelligence | gzip > /backups/db_$(date +\%Y\%m\%d).sql.gz
```

