# BMIR 2.0 Official Production Deployment & Domain Publishing Guide

This comprehensive guide details the exact steps to publish **Bharat Multisector Innovation & Research (BMIR 2.0)** to the live public internet under your official domain: **`https://bmirresearch.in`**.

---

## Architecture Overview

```
                      [ Visitors from Anywhere in the World ]
                                         │
                                         ▼
                     DNS: bmirresearch.in (GoDaddy / Hostinger)
                                         │
                   ┌─────────────────────┴─────────────────────┐
                   ▼                                           ▼
      [ Option A: Cloud Platform ]                 [ Option B: Cloud VPS ]
      Frontend: Vercel (Global CDN)                Ubuntu 24.04 (DigitalOcean / AWS)
      Backend:  Render / Railway                   Nginx + PM2 / Docker
                   │                                           │
                   └─────────────────────┬─────────────────────┘
                                         ▼
                        [ BMIR 2.0 Ecosystem Online ]
```

---

## METHOD 1: Recommended Cloud Deployment (Vercel + Render)
*Best for: Zero server maintenance, automated CI/CD from Git, global CDN speed, and automated SSL.*

### Step 1: Push Your Codebase to GitHub
1. Open PowerShell in your project folder:
   ```powershell
   cd c:\Users\pande\.gemini\antigravity\scratch\resume-intelligence-platform
   git init
   git add .
   git commit -m "BMIR 2.0 Enterprise Release"
   ```
2. Create a private or public repository on [GitHub.com](https://github.com) named `bmir-platform`.
3. Push to GitHub:
   ```powershell
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/bmir-platform.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy the Backend (FastAPI) on Render
1. Go to [Render.com](https://render.com) and create a free account.
2. Click **New +** > **Web Service**.
3. Select your `bmir-platform` GitHub repository.
4. Configure service settings:
   - **Name:** `bmir-api`
   - **Root Directory:** `backend`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. In **Environment Variables**, add:
   - `ENVIRONMENT` = `production`
   - `SECRET_KEY` = `your-secure-random-secret-key-2026`
   - `FOUNDER_EMAIL` = `binod.pandey@bmirresearch.in`
   - `FOUNDER_NAME` = `Binod Pandey`
6. Click **Deploy Web Service**. Render will generate an HTTPS URL (e.g., `https://bmir-api.onrender.com`).

### Step 3: Deploy the Frontend (Next.js) on Vercel
1. Go to [Vercel.com](https://vercel.com) and sign in with GitHub.
2. Click **Add New...** > **Project** and import `bmir-platform`.
3. In **Project Settings**:
   - **Framework Preset:** `Next.js`
   - **Root Directory:** Click edit and select `frontend`.
4. In **Environment Variables**:
   - `BACKEND_API_URL` = `https://bmir-api.onrender.com` (your backend URL from Step 2)
5. Click **Deploy**. Vercel will build and assign a temporary `.vercel.app` URL.

### Step 4: Connect Your Domain (`bmirresearch.in`)
1. In your Vercel Dashboard, go to **Settings** > **Domains**.
2. Type `bmirresearch.in` and click **Add**. Also add `www.bmirresearch.in`.
3. Vercel will display the exact DNS records to add:
   - **A Record**:
     - Name / Host: `@`
     - Value / Destination: `76.76.21.21`
   - **CNAME Record**:
     - Name / Host: `www`
     - Value / Destination: `cname.vercel-dns.com`
4. Log into your domain registrar (GoDaddy, Hostinger, BigRock, Namecheap, etc.) where you purchased `bmirresearch.in`:
   - Open **DNS Management / Zone Editor**.
   - Add or update the A and CNAME records with Vercel's values.
5. Within 5–30 minutes, Vercel will automatically verify the records, issue a **free Let's Encrypt SSL certificate**, and activate `https://bmirresearch.in`.

---

## METHOD 2: All-in-One Cloud Server (VPS via Ubuntu & Nginx)
*Best for: Running everything on a single private Linux virtual machine ($4 to $6/mo on DigitalOcean, Linode, AWS EC2, or Hetzner).*

### Step 1: Create a Linux VPS
- Deploy an **Ubuntu 24.04 LTS** server with at least 2 GB RAM.
- Note the public IPv4 address (e.g. `123.45.67.89`).

### Step 2: Configure Domain DNS
In your domain registrar DNS settings:
- **A Record**: Host `@` → Points to `YOUR_SERVER_IP`
- **A Record**: Host `www` → Points to `YOUR_SERVER_IP`

### Step 3: Server Setup & Dependencies
Connect to your server via SSH:
```bash
ssh root@YOUR_SERVER_IP
```
Install Node.js 20, Python 3.12/3.13, Nginx, and Certbot:
```bash
apt update && apt upgrade -y
apt install -y git curl uvicorn python3-pip python3-venv nginx certbot python3-certbot-nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
npm install -g pm2
```

### Step 4: Clone & Build
```bash
cd /var/www
git clone https://github.com/YOUR_GITHUB_USERNAME/bmir-platform.git bmir
cd /var/www/bmir

# Set up Python backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m app.db_init_and_seed
deactivate

# Set up Next.js frontend
cd ../frontend
npm install
npm run build
```

### Step 5: Start Services with PM2 (24/7 Auto-Restart)
```bash
# Start backend on port 8000
cd /var/www/bmir/backend
pm2 start ".venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000" --name bmir-backend

# Start frontend on port 3000
cd /var/www/bmir/frontend
pm2 start "npm start" --name bmir-frontend

# Save processes so they restart if the server reboots
pm2 save
pm2 startup
```

### Step 6: Configure Nginx as Reverse Proxy
Create `/etc/nginx/sites-available/bmirresearch.in`:
```nginx
server {
    server_name bmirresearch.in www.bmirresearch.in;

    # Frontend routes
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site:
```bash
ln -s /etc/nginx/sites-available/bmirresearch.in /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

### Step 7: Enable Free HTTPS (SSL)
```bash
certbot --nginx -d bmirresearch.in -d www.bmirresearch.in
```
Follow the prompt. Certbot will configure HTTPS and set up automatic 90-day renewal.

---

## Pre-Launch Checklist

- [x] Absolute data accuracy: All statistics correspond to verified SQLite records.
- [x] Zero hardcoded `localhost` in client components (all API calls use relative paths `/api/v1/bmir/*`).
- [x] Dual themes (Dark & Light) tested and responsive across mobile, tablet, and desktop.
- [x] 3D scientific canvas conforms to `prefers-reduced-motion`.
- [x] Founder identity and contact info verified:
  - **Founder:** Binod Pandey
  - **Contact:** +91 8340 328914
  - **Email:** `binod.pandey@bmirresearch.in`
  - **Location:** Bhagalpur, Bihar, India
