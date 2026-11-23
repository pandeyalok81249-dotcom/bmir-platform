# PROJECT BMIR 2.0
## Bharat Multisector Innovation & Research
### Enterprise AI Research, Innovation, Engineering & Global Collaboration Ecosystem

![BMIR 2.0 Architecture](https://img.shields.io/badge/BMIR-2.0%20Enterprise-blue)
![Frontend](https://img.shields.io/badge/Frontend-Next.js%2014%20|%20TypeScript%20|%20Tailwind-cyan)
![Backend](https://img.shields.io/badge/Backend-FastAPI%20|%20Python%203.14-emerald)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20|%20pgvector%20|%20SQLite-indigo)
![Tests](https://img.shields.io/badge/Tests-8%2F8%20Passed%20(100%25)-brightgreen)

---

## 1. Organization Identity

- **Organization:** Bharat Multisector Innovation & Research (BMIR)
- **Founder / Independent Inventor:** Binod Pandey
- **Location:** Bhagalpur, Bihar, India - 812001
- **Official Website:** [https://bmirresearch.in](https://bmirresearch.in)
- **Direct Research Line:** +91 8340 328914
- **Official Email:** contact@bmirresearch.in
- **Core Positioning:** *"Research Beyond Boundaries. Innovation for a Better World."*
- **Mission:** To develop, investigate, evaluate, and advance innovative technologies through multidisciplinary research and responsible applications of artificial intelligence.
- **Vision:** To create an internationally accessible research and innovation ecosystem connecting inventors, scientists, engineers, academic institutions, technology companies, and industries.

> [!IMPORTANT]
> **Strict Non-Fabrication Compliance:** All public claims reflect verified Indian Patent Office (IPO) application records and official gazette publications. In strict accordance with the Indian Patent Act 1970, application filing and gazette publication do NOT constitute a granted patent. BMIR makes no fabricated claims of institutional partnerships, awards, or patent grants without verified documentation.

---

## 2. Product Architecture

BMIR 2.0 delivers **TWO connected enterprise products** under one unified system:

### A. BMIR International Website (Public Institutional Portal)
- **Home:** Hero section with animated scientific elements, verified impact metrics (27 innovations, 17 patent records, 3 gazette publications, 15 filed innovations), and bilingual English/Hindi interface.
- **About BMIR:** Vision, mission, research philosophy, authentic founder profile for Binod Pandey, and 4-step innovation methodology.
- **Innovation Portfolio:** Searchable, filterable database of 27 verified multidisciplinary innovations across 12 sectors with development stage tracking and technical detail modals.
- **Research Projects:** Active structured investigations (KRISHI-BODH ONE, Hydrogen Production & Storage, AI-SHRUTI Acoustic Health Assistant, MAKHANA-ROVER) with research questions, methodologies, progress bars, and linked experiments.
- **Patent & IP Documentation Centre:** Verifiable IPO filing records, application numbers, official gazette issue/page references, co-inventorship details (**Dr. Shyam Sundar Mandal** & **Akash Rajvanshi**), and prominent statutory disclaimers.
- **Research Domains:** 11 dedicated divisions (Artificial Intelligence, Smart Agriculture, Healthcare Tech, Civil Infrastructure, Renewable Energy, Environmental Tech, Robotics, Advanced Materials, Defence & Safety, Social Impact, Multidisciplinary Engineering).
- **Collaboration Portal:** Dedicated pathways for Universities, Testing Labs, Corporate R&D, and Tech Startups with live proposal submission generating instant reference codes (`BMIR-ENQ-2026-XXXX`).
- **Global Contact Centre:** Direct research contacts in Bhagalpur, Bihar, meeting scheduler, and international communication lines.

### B. BMIR AI Research Intelligence Platform (Private Authenticated Workspace)
- **Private Research Dashboard:** Real database metrics, domain distribution charts, development stage classifications, and live audit activity stream.
- **AI Research Assistant:** Conversational scientific reasoning agent with context memory, citation grounding from indexed RAG documents, and PDF/DOCX proposal export.
- **Multi-Model Intelligence Engine:** Side-by-side comparative reasoning across OpenAI GPT-4o, Google Gemini 1.5 Pro, Anthropic Claude 3.5 Sonnet, and BMIR Scientific Engine, extracting key agreements, contradictions, missing empirical evidence, and consolidated syntheses.
- **AI Innovation Discovery Engine:** 8-step structured invention exploration pipeline converting raw problems into engineered concepts with feasibility scores.
- **AI Research Literature Assistant:** Dissects scientific papers, extracts methodologies, quantitative findings, and unresolved research gaps with OpenAlex and Crossref links.
- **Patent Research Assistant:** Prior-art similarity pointers, international IPC/CPC classification guidance, and structured claim formulation framework with legal disclaimers.
- **Technical Feasibility Engine:** 10-vector radar chart evaluation (scientific, engineering, materials, manufacturing, complexity, energy, economic, environmental, safety).
- **Innovation Roadmap Generator:** Milestone-driven development planning with risk matrices and timeline phases.
- **Research Experiment Management:** Empirical lab notebook tracking hypotheses, materials, sensor measurements, quantitative observations, and version control.
- **RAG Knowledge Base:** Semantic vector search, full document viewer, and document indexing.
- **Admin Control Centre:** Role-based access governance, collaboration enquiry review (approve, under review, decline), AI provider gateway telemetry, and audit logs.

---

## 3. Technology Stack

- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Lucide React, Framer Motion, Recharts.
- **Backend:** Python 3.14 / 3.13, FastAPI, SQLAlchemy 2.0 Async ORM, Pydantic v2, JWT (HS256), Argon2id password hashing, HTTPX.
- **Database:** PostgreSQL 16 with pgvector (production) with zero-config Async SQLite fallback (`bmir_platform.db`) for immediate local execution.
- **Cache & Queue:** Redis 7.
- **Security:** Rate limiting, security headers, role-based access control (7 roles), encrypted transit, strict non-confidential data filtration.

---

## 4. Quick Start (Local Development)

### Backend Setup:
```bash
cd backend
python -m venv .venv

# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Initialize & seed authentic BMIR database
python app/db_init_and_seed.py

# Start FastAPI server on port 8000
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup:
```bash
cd frontend
npm install

# Build production assets:
npm run build

# Start Next.js on port 3000:
npm run dev
```

Visit [http://localhost:3000](http://localhost:3000) to view the portal.

---

## 5. Verified Credentials for Immediate Platform Testing

The system is seeded with authentic accounts for instant evaluation:

| Account | Email | Password | Role |
|---|---|---|---|
| **Founder / Principal Researcher** | `binod.pandey@bmirresearch.in` | `Bmir@2026!Enterprise` | `founder` |
| **Super Administrator** | `admin@bmirresearch.in` | `Bmir@2026!Enterprise` | `super_admin` |
| **Research Scientist** | `priya.sharma@bmirresearch.in` | `Bmir@2026!Enterprise` | `research_scientist` |
| **Research Engineer** | `rajesh.kumar@bmirresearch.in` | `Bmir@2026!Enterprise` | `research_engineer` |

---

## 6. Verification Test Suite

All 8 critical integration test suites pass with 100% success:

```bash
cd backend
.venv\Scripts\python.exe -m pytest tests/test_bmir_integration.py -v
```

```
tests/test_bmir_integration.py::test_health_check PASSED                 [ 12%]
tests/test_bmir_integration.py::test_public_innovations_endpoint PASSED  [ 25%]
tests/test_bmir_integration.py::test_innovations_filtering_and_search PASSED [ 37%]
tests/test_bmir_integration.py::test_patents_records PASSED              [ 50%]
tests/test_bmir_integration.py::test_research_projects_endpoint PASSED   [ 62%]
tests/test_bmir_integration.py::test_auth_login_founder_and_admin PASSED [ 75%]
tests/test_bmir_integration.py::test_collaboration_proposal_submission_and_admin_review PASSED [ 87%]
tests/test_bmir_integration.py::test_ai_reasoning_and_multi_model PASSED [100%]

======================= 8 passed in 48.57s ========================
```

---

## 7. License & Intellectual Property Rights

© 2026 Bharat Multisector Innovation & Research (BMIR). All rights reserved.  
Founded by **Binod Pandey**, Bhagalpur, Bihar, India.
