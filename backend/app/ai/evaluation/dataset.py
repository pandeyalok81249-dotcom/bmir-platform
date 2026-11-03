"""
Synthetic evaluation benchmark dataset for AI Resume Intelligence Quality Testing.
Contains diverse persona resumes with ground-truth annotations for skills,
experience years, unsupported claims, and section boundaries.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class GroundTruthResume(BaseModel):
    id: str
    persona: str
    target_role: str
    career_stage: str
    resume_text: str
    ground_truth_skills: List[str]
    ground_truth_experience_years: float
    ground_truth_unsupported_claims: List[str] = Field(
        default_factory=list,
        description="Claims in the text that lack metric verification, timeline context, or project evidence"
    )
    expected_sections: List[str] = Field(
        default_factory=lambda: ["EXPERIENCE", "EDUCATION", "SKILLS"]
    )


class GroundTruthJob(BaseModel):
    id: str
    title: str
    company: str
    job_text: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_experience_years: float


BENCHMARK_RESUMES: List[GroundTruthResume] = [
    GroundTruthResume(
        id="synth_res_001_backend",
        persona="Senior Backend / Distributed Systems Engineer",
        target_role="Senior Backend Engineer",
        career_stage="Senior",
        resume_text="""ALEX CHEN
San Francisco, CA | alex.chen@example.com | linkedin.com/in/alexchen-dev | github.com/alexchen

SUMMARY
Senior Backend Engineer with 7 years of experience building fault-tolerant distributed microservices in Go, Python, and PostgreSQL. Architected real-time streaming pipelines processing 45,000 requests/second with 99.99% uptime.

EXPERIENCE
Staff Software Engineer | CloudScale Systems | Jan 2021 – Present (3.5 years)
- Designed and deployed high-throughput event streaming platform using Apache Kafka, Go, and PostgreSQL, reducing message latency from 180ms to 24ms.
- Mentored team of 6 engineers across distributed systems design patterns and Kubernetes cluster operations.
- Optimized database query patterns and Redis cache invalidation strategies, decreasing RDS read replicas and cutting AWS infrastructure costs by $140,000 annually.
- Led migration of 14 monolithic services to microservices orchestrated on Amazon EKS with zero customer downtime during rollout.

Software Engineer II | FinTech Logistics | Jun 2017 – Dec 2020 (3.5 years)
- Engineered automated payment reconciliation pipeline with Python, FastAPI, and SQLAlchemy handling $12M daily transaction volume.
- Implemented Docker containerization and CI/CD pipelines via GitHub Actions, decreasing deployment cycle time by 65%.
- Integrated Stripe and Plaid APIs for ACH transfers and KYC compliance checks.
- Scaled Redis distributed locks to eliminate race conditions in simultaneous balance deduction endpoints.

EDUCATION
B.S. in Computer Science | University of California, Berkeley | 2013 – 2017

SKILLS
Programming: Go, Python, SQL, Bash
Infrastructure & DevOps: Docker, Kubernetes, AWS (EKS, RDS, S3), Terraform, CI/CD, GitHub Actions
Databases & Streaming: PostgreSQL, Redis, Apache Kafka, Elasticsearch
Architecture: Microservices, Distributed Systems, REST APIs, gRPC, Event-Driven Architecture
""",
        ground_truth_skills=[
            "Go", "Python", "SQL", "Bash", "Docker", "Kubernetes", "AWS", "Terraform",
            "PostgreSQL", "Redis", "Apache Kafka", "Elasticsearch", "Microservices",
            "Distributed Systems", "REST APIs", "gRPC", "CI/CD", "GitHub Actions"
        ],
        ground_truth_experience_years=7.0,
        ground_truth_unsupported_claims=[],
        expected_sections=["SUMMARY", "EXPERIENCE", "EDUCATION", "SKILLS"]
    ),

    GroundTruthResume(
        id="synth_res_002_data_science",
        persona="Data Scientist / ML Engineer with unverified claims",
        target_role="Machine Learning Engineer",
        career_stage="Mid-Level",
        resume_text="""PRIYA SHARMA
New York, NY | priya.sharma@example.com | github.com/priyasharma-ml

PROFESSIONAL SUMMARY
Data Scientist with 3.5 years of experience building and deploying machine learning models in Python, PyTorch, and BigQuery. Single-handedly revolutionized enterprise customer retention using cutting-edge deep neural networks that solved all churn forever.

WORK EXPERIENCE
Machine Learning Engineer | DataCore Analytics | Jul 2022 – Present (2 years)
- Built customer churn prediction model using LightGBM, XGBoost, and Scikit-learn, achieving 0.88 ROC-AUC on 2.4M user records.
- Deployed real-time inference APIs using FastAPI and Triton Inference Server on GCP Vertex AI, serving predictions with sub-50ms p95 latency.
- Developed automated feature store pipelines in BigQuery and dbt, reducing feature engineering drift across 15 production models.
- Claimed to single-handedly generate $500,000,000 in direct revenue without any marketing or sales involvement in 3 weeks.

Junior Data Analyst | MetricFlow Insights | Jan 2021 – Jun 2022 (1.5 years)
- Extracted and transformed clickstream datasets using SQL, Pandas, and Apache Spark for executive dashboards.
- Created Tableau and Looker dashboards tracking key conversion funnels across 400,000 monthly active users.
- Conducted A/B hypothesis testing (t-tests, chi-square) to evaluate checkout funnel redesigns.

EDUCATION
M.S. in Data Science | Columbia University | 2019 – 2020
B.S. in Statistics | Rutgers University | 2015 – 2019

TECHNICAL SKILLS
Languages: Python, SQL, R
Machine Learning: PyTorch, Scikit-learn, XGBoost, LightGBM, HuggingFace Transformers
Data & Cloud: BigQuery, Apache Spark, dbt, GCP Vertex AI, Docker, Git
BI & Tools: Tableau, Looker, Pandas, NumPy
""",
        ground_truth_skills=[
            "Python", "SQL", "R", "PyTorch", "Scikit-learn", "XGBoost", "LightGBM",
            "HuggingFace Transformers", "BigQuery", "Apache Spark", "dbt", "GCP Vertex AI",
            "Docker", "Git", "Tableau", "Looker", "Pandas", "NumPy", "A/B Testing"
        ],
        ground_truth_experience_years=3.5,
        ground_truth_unsupported_claims=[
            "Single-handedly revolutionized enterprise customer retention using cutting-edge deep neural networks that solved all churn forever",
            "Claimed to single-handedly generate $500,000,000 in direct revenue without any marketing or sales involvement in 3 weeks"
        ],
        expected_sections=["PROFESSIONAL SUMMARY", "WORK EXPERIENCE", "EDUCATION", "TECHNICAL SKILLS"]
    ),

    GroundTruthResume(
        id="synth_res_003_product_manager",
        persona="Technical Product Manager",
        target_role="Senior Product Manager",
        career_stage="Senior",
        resume_text="""JORDAN TAYLOR
Austin, TX | jordan.taylor@example.com | linkedin.com/in/jordantaylor-pm

EXECUTIVE SUMMARY
Strategic and technical Product Manager with 6 years leading B2B SaaS platform roadmaps from zero-to-one and scaling through hypergrowth. Adept at bridging customer insights, data analytics, and engineering delivery.

PROFESSIONAL EXPERIENCE
Lead Product Manager | Nexus SaaS | Mar 2021 – Present (3.5 years)
- Owned product vision, roadmap, and quarterly OKRs for flagship B2B analytics platform serving 180 enterprise accounts.
- Increased Net Revenue Retention (NRR) from 104% to 128% over 18 months through self-service upgrade workflows.
- Led cross-functional team of 14 engineers, 2 UX designers, and 2 product marketers using Scrum/Agile methodology.
- Conducted 60+ user interviews to identify workflow friction, leading to redesigned onboarding that lifted activation by 34%.

Product Manager | AgileSphere | Jul 2018 – Feb 2021 (2.5 years)
- Defined user stories, acceptance criteria, and PRDs for developer API integrations and webhooks.
- Partnered with engineering to build rate limiting, API key management, and developer documentation portal.
- Analyzed product telemetry using Amplitude and Mixpanel, driving data-informed backlog prioritization.

EDUCATION
B.A. in Economics & Informatics | University of Texas at Austin | 2014 – 2018

SKILLS & COMPETENCIES
Product: Product Strategy, Roadmap Prioritization, PRD Writing, User Research, OKRs, Agile / Scrum
Analytics & Tools: Amplitude, Mixpanel, Jira, Confluence, Figma, SQL (intermediate)
Domain: B2B SaaS, API Platforms, User Onboarding, Customer Retention
""",
        ground_truth_skills=[
            "Product Strategy", "Roadmap Prioritization", "PRD Writing", "User Research",
            "OKRs", "Agile", "Scrum", "Amplitude", "Mixpanel", "Jira", "Confluence",
            "Figma", "SQL", "B2B SaaS", "APIs", "User Onboarding"
        ],
        ground_truth_experience_years=6.0,
        ground_truth_unsupported_claims=[],
        expected_sections=["EXECUTIVE SUMMARY", "PROFESSIONAL EXPERIENCE", "EDUCATION", "SKILLS & COMPETENCIES"]
    ),

    GroundTruthResume(
        id="synth_res_004_career_switcher",
        persona="Junior Developer / Career Switcher from IT Support",
        target_role="Junior Frontend Engineer",
        career_stage="Entry-Level",
        resume_text="""MARCUS VANCE
Chicago, IL | marcus.vance@example.com | github.com/marcusvance

SUMMARY
Passionate software developer transitioning from 3 years in IT operations into Frontend Engineering. Built 5 production-grade React and TypeScript applications with responsive UI, state management, and REST API integration.

PROJECTS & TECHNICAL WORK
TaskPulse Project Management App (Full Stack Project) | 2023
- Built responsive Kanban web app using React, TypeScript, Tailwind CSS, and Node.js with PostgreSQL backend.
- Implemented drag-and-drop state updates with Redux Toolkit and JWT cookie-based authentication.

DevPortfolio (Open Source Contributor) | 2023
- Contributed accessible Material UI components and fixed WCAG 2.1 AA keyboard focus issues.

WORK EXPERIENCE
IT Systems Specialist | Midwest Health Network | Jun 2020 – Oct 2023 (3.3 years)
- Administered Active Directory, Okta SSO, and hardware fleet across 450 corporate staff.
- Automated helpdesk ticketing triage with Python scripting and Jira REST API, saving 12 hours weekly.
- Maintained network switch hardware and VPN tunnels ensuring HIPAA audit compliance.

EDUCATION & CERTIFICATIONS
Full Stack Web Development Certificate | General Assembly | 2023 (500+ hours immersive)
B.S. in Information Systems | DePaul University | 2016 – 2020
AWS Certified Cloud Practitioner | 2022

SKILLS
Frontend: JavaScript (ES6+), TypeScript, React, HTML5, CSS3, Tailwind CSS, Redux
Backend & Tools: Python, Node.js, Express, Git, GitHub, REST APIs, Active Directory, Jira
""",
        ground_truth_skills=[
            "JavaScript", "TypeScript", "React", "HTML5", "CSS3", "Tailwind CSS",
            "Redux", "Python", "Node.js", "Express", "Git", "GitHub", "REST APIs",
            "Active Directory", "Jira", "SQL"
        ],
        ground_truth_experience_years=3.3,
        ground_truth_unsupported_claims=[],
        expected_sections=["SUMMARY", "PROJECTS & TECHNICAL WORK", "WORK EXPERIENCE", "EDUCATION & CERTIFICATIONS", "SKILLS"]
    )
]


BENCHMARK_JOBS: List[GroundTruthJob] = [
    GroundTruthJob(
        id="synth_job_001_senior_backend",
        title="Senior Distributed Systems Engineer",
        company="Global FinTech Innovations",
        job_text="""Senior Distributed Systems Engineer
Global FinTech Innovations - San Francisco, CA

About the Role:
We are seeking a Senior Backend Engineer to architect and scale our real-time core banking settlement platform. You will lead technical design for high-throughput streaming pipelines.

Requirements:
- 5+ years of production experience in Go, Python, or Java.
- Proven experience with distributed microservices architectures and fault-tolerant system design.
- Hands-on expertise with Apache Kafka or RabbitMQ event-driven streaming.
- Deep relational database experience (PostgreSQL or MySQL) including query indexing and connection pooling.
- Strong containerization and orchestration knowledge with Docker and Kubernetes (EKS / GKE).
- Solid cloud infrastructure background on AWS or GCP.

Preferred Qualifications:
- Experience in financial services, payment protocols, or PCI-DSS environments.
- Experience with Redis caching architectures and distributed locks.
- Bachelor's degree in Computer Science or equivalent practical experience.
""",
        required_skills=["Go", "Python", "Microservices", "Distributed Systems", "Apache Kafka", "PostgreSQL", "Docker", "Kubernetes", "AWS"],
        preferred_skills=["Redis", "Financial Services", "PCI-DSS"],
        min_experience_years=5.0
    ),

    GroundTruthJob(
        id="synth_job_002_ml_engineer",
        title="Machine Learning Engineer",
        company="Predictive Health AI",
        job_text="""Machine Learning Engineer
Predictive Health AI - New York, NY

Role Overview:
Join our predictive modeling team to build production ML pipelines that serve real-time clinical risk scores to hospital systems.

Key Qualifications:
- 3+ years experience developing and deploying machine learning models in production environments.
- Expert proficiency in Python and modern ML libraries (Scikit-learn, PyTorch, LightGBM, XGBoost).
- Experience with data warehousing and transformation (BigQuery, Snowflake, or SQL).
- Hands-on deployment with Docker, FastAPI, and model serving platforms (Triton, Vertex AI, or SageMaker).
- Strong statistical foundation, hypothesis testing, and model evaluation metrics (ROC-AUC, PR-AUC).

Nice-to-Have:
- Experience with feature stores (e.g. Feast, dbt).
- Experience handling healthcare data or HIPAA requirements.
""",
        required_skills=["Python", "Machine Learning", "Scikit-learn", "PyTorch", "LightGBM", "XGBoost", "BigQuery", "SQL", "Docker", "FastAPI"],
        preferred_skills=["GCP Vertex AI", "dbt", "Feature Stores", "Healthcare Data"],
        min_experience_years=3.0
    )
]
