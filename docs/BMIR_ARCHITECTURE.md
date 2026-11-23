# BMIR 2.0 Architectural Blueprint
## Bharat Multisector Innovation & Research Enterprise Ecosystem

### 1. Executive Summary
BMIR 2.0 is an enterprise-grade research and innovation ecosystem built for **Bharat Multisector Innovation & Research**, an independent multidisciplinary research initiative led by **Binod Pandey** based in **Bhagalpur, Bihar, India** ([bmirresearch.in](https://bmirresearch.in)).

The ecosystem comprises two unified products sharing an integrated backend and security boundary:
1. **BMIR International Website:** Premium public-facing portal presenting verified institutional identity, 27 technological innovations, 17 documented patent application records, 4 active multidisciplinary research projects, 11 research domains, and an interactive global collaboration gateway with bilingual (English / Hindi) support.
2. **BMIR AI Research Intelligence Platform:** Secure, authenticated private workspace empowering researchers, engineers, and scientists with multi-model comparative reasoning, 8-step structured innovation discovery, literature deconstruction, prior-art investigation, technical feasibility radar scoring, experiment logging, and RAG knowledge retrieval.

---

### 2. High-Level System Architecture

```
+-----------------------------------------------------------------------------------+
|                            BMIR 2.0 ECOSYSTEM UI                                  |
|                 (Next.js 14 App Router / React / TypeScript / Tailwind)           |
|                                                                                   |
|  [ Public Institutional Portal ]            [ Private AI Research Platform ]      |
|  - Hero, Verified Statistics                - Live Database Metrics Dashboard     |
|  - Founder Bio & Methodology                - Conversational AI Research Assistant|
|  - 27 Innovations Portfolio                 - Multi-Model Reasoning Engine        |
|  - 17 Patent Records & Gazette Data         - 8-Step Innovation Discovery Engine  |
|  - Research Domains & Project Pages         - Literature Extraction & Gaps        |
|  - Interactive Collaboration Portal         - Patent Prior-Art Assistant          |
|  - Global Contact Centre                    - 10-Vector Feasibility Radar         |
|  - Bilingual (English / Hindi) Engine       - Experiment Log & Traceability       |
|                                             - RAG Knowledge Base Search & Upload  |
|                                             - Admin Control & Role Governance     |
+------------------------------------------+----------------------------------------+
                                           |
                                  HTTPS / JSON REST APIs
                                           |
+------------------------------------------v----------------------------------------+
|                          FASTAPI HIGH-THROUGHPUT BACKEND                          |
|                                                                                   |
|  [ Security & Middleware ]                  [ Core API Endpoints (31 Routes) ]    |
|  - Argon2id Password Hashing                - /api/v1/bmir/auth/* (RBAC)          |
|  - JWT Bearer Tokens with Claims            - /api/v1/bmir/innovations/*          |
|  - Role-Based Access Control (7 Roles)      - /api/v1/bmir/patents/*              |
|  - Strict Non-Confidential Data Filtration  - /api/v1/bmir/projects/*             |
|  - Rate Limiting & Security Headers         - /api/v1/bmir/experiments/*          |
|                                             - /api/v1/bmir/collaboration/*        |
|  [ AI Orchestration Gateway ]               - /api/v1/bmir/intelligence/*         |
|  - Google Gemini 1.5 Pro Integration        - /api/v1/bmir/knowledge/* (RAG)      |
|  - OpenAI GPT-4o Gateway                    - /api/v1/bmir/dashboard/stats        |
|  - Anthropic Claude 3.5 Sonnet Gateway      - /api/v1/bmir/ai/*                   |
|  - BMIR Local Deterministic Scientific Eng.                                      |
+------------------------------------------+----------------------------------------+
                                           |
                          SQLAlchemy 2.0 Async ORM / pgvector
                                           |
+------------------------------------------v----------------------------------------+
|                      ENTERPRISE DATABASE & STORAGE LAYER                          |
|                                                                                   |
|  - Primary DB: PostgreSQL 16 + pgvector (with zero-config SQLite local fallback)  |
|  - Cache & Coordination: Redis 7                                                  |
|  - Tables: bmir_users, bmir_innovations, bmir_patent_records,                     |
|            bmir_research_projects, bmir_experiments,                              |
|            bmir_feasibility_evaluations, bmir_innovation_roadmaps,                 |
|            bmir_knowledge_documents, bmir_collaboration_enquiries,                |
|            bmir_ai_conversations, bmir_ai_messages, bmir_audit_logs               |
+-----------------------------------------------------------------------------------+
```

---

### 3. Role-Based Access Control (RBAC) Matrix

| Role | Public Portal | Innovation Data | Experiments | AI Lab Tools | Admin Center | User Role Mod |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Super Admin** | Full | Full (incl. Conf.) | Create & Edit | Full | Full | Full |
| **Founder (Binod Pandey)** | Full | Full (Owner) | Full | Full | Full | Full |
| **Research Admin** | Full | Full | Full | Full | Read/Review | Restricted |
| **Research Scientist** | Full | Read/Create | Create & Run | Full | No | No |
| **Research Engineer** | Full | Read/Create | Create & Run | Full | No | No |
| **External Collaborator** | Full | Public & Assigned | Read Assigned | Assistant/Discovery | No | No |
| **Viewer** | Full | Public Only | Read Concluded | Basic Assistant | No | No |

---

### 4. Non-Fabrication & Statutory Compliance Architecture

In compliance with explicit guidelines and the Indian Patent Act 1970:
1. **Patent Filing vs. Grant:** No provisional or complete specification is represented as a granted patent. The platform explicitly renders publication status (e.g., *Issue 23/2026, page 67482* and *Issue 24/2026, pages 70478 & 70493*) with clear statutory disclaimers.
2. **Co-Inventorship:** Accurately reflects verified joint applicants, including **Dr. Shyam Sundar Mandal** (Hydrogen Gas Cylinder Storage System) and **Akash Rajvanshi** (AI-SHRUTI acoustic assistant, Form 1 verification pending).
3. **No Fabricated Credentials:** The founder profile reflects Binod Pandey's actual identity as an independent inventor in Bhagalpur, Bihar, without invented institutional affiliations or scientific awards.
4. **AI Consensus Policy:** Multi-model consensus is explicitly marked as algorithmic convergence and never scientific proof.

