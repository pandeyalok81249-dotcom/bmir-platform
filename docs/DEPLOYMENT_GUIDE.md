# BMIR 2.0 Production Deployment Guide
## Enterprise Cloud Deployment & Operational Runbook

### 1. Prerequisites
- Docker Engine 24.0+ & Docker Compose v2.20+
- Domain name with DNS pointed to host IP (`bmirresearch.in` or custom subdomain)
- Port 80 & 443 open for SSL/TLS reverse proxy

---

### 2. Environment Configuration
Create production `.env` files in root and backend:

```bash
# Root production environment (.env)
POSTGRES_USER=bmir_admin
POSTGRES_PASSWORD=YourStrongComplexPassword_2026!
POSTGRES_DB=bmir_ecosystem

SECRET_KEY=generate_using_openssl_rand_hex_32
ENVIRONMENT=production
DEBUG=False

# Organization
FOUNDER_NAME="Binod Pandey"
FOUNDER_EMAIL="binod.pandey@bmirresearch.in"
ADMIN_EMAIL="admin@bmirresearch.in"
DEFAULT_INITIAL_PASSWORD="SecureInitialPassword_2026!"
BMIR_LOCATION="Bhagalpur, Bihar, India"
BMIR_PHONE="+91 8340 328914"

# Optional Cloud AI Keys (leave blank for local scientific reasoning engine)
GEMINI_API_KEY=""
OPENAI_API_KEY=""
ANTHROPIC_API_KEY=""
```

---

### 3. Docker Deployment

Execute the complete stack using Docker Compose:

```bash
# 1. Build and start containers in detached mode
docker compose -f docker/docker-compose.yml up -d --build

# 2. Verify container health
docker compose -f docker/docker-compose.yml ps

# 3. Seed baseline database records
docker compose -f docker/docker-compose.yml exec backend python app/db_init_and_seed.py
```

---

### 4. Nginx Reverse Proxy with SSL (Let's Encrypt)

```nginx
# /etc/nginx/sites-available/bmirresearch.in
server {
    listen 80;
    server_name bmirresearch.in www.bmirresearch.in;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name bmirresearch.in www.bmirresearch.in;

    ssl_certificate /etc/letsencrypt/live/bmirresearch.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/bmirresearch.in/privkey.pem;

    # Frontend Next.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend FastAPI REST APIs
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

### 5. Automated Backup & Recovery
Automated daily PostgreSQL backup script:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/bmir"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p $BACKUP_DIR

# Dump database with pg_dump
docker exec -t bmir-postgres pg_dump -U bmir_admin -d bmir_ecosystem | gzip > "$BACKUP_DIR/bmir_db_$TIMESTAMP.sql.gz"

# Retain last 30 days
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +30 -delete
```

---

### 6. Health Checks & Verification
- **Backend Health:** `curl https://bmirresearch.in/health` -> `{"status":"healthy","service":"BMIR 2.0 - Bharat Multisector Innovation & Research","version":"1.0.0"}`
- **Database Status:** `curl https://bmirresearch.in/ready` -> `{"status":"ready"}`
- **OpenAPI Documentation:** `https://bmirresearch.in/api/v1/docs`

