import asyncio
import json
import ast
import os
import sys
from datetime import datetime, timezone

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import Base, engine, async_session_maker
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.bmir import (
    BMIRUser,
    Innovation,
    PatentRecord,
    ResearchProject,
    Experiment,
    FeasibilityEvaluation,
    InnovationRoadmap,
    KnowledgeDocument,
    CollaborationEnquiry,
    AIConversation,
    AIMessage,
    AuditLog,
    BMIRSession,
    BMIRNotification,
)
from sqlalchemy import select


# Domain descriptions mapping
DOMAIN_DESCRIPTIONS = {
    "Artificial Intelligence": "Autonomous reasoning, multi-model intelligence, computer vision for agriculture, predictive healthcare analytics, and ethical AI architectures.",
    "Agriculture & Smart Farming": "Decentralized soil diagnostics, autonomous crop sentinels, robotic aquatic farming, post-harvest drying automation, and climate-resilient hybrid seed technology.",
    "Healthcare & Medical Technology": "Acoustic diagnostic algorithms, multi-cancer early detection biosensors, non-invasive hormone screening, and community disease prevention devices.",
    "Infrastructure & Civil Engineering": "Automated rail transit safety, composite freight containers, seismic vibration dampening, and automated structural health monitoring.",
    "Renewable Energy": "Electrochemical green hydrogen generation, high-density composite gas storage cylinders, and zero-emission biofuels.",
    "Environmental Technology": "Hydrological verification platforms, bio-waste circular systems, urban water telemetry, and emission-mitigation systems.",
    "Robotics & Automation": "Deep-water agricultural rovers, industrial automation systems, remote surveillance drones, and mechatronic harvesting assemblies.",
    "Advanced Materials": "Nanostructured composites, high-pressure hydrogen storage alloys, thermal insulating agricultural barrier materials, and biodegradable polymers.",
    "Electronics & IoT": "Low-power edge computing sensors, LoRa-mesh rural telemetry nodes, intelligent solar controllers, and acoustic vibration transducers.",
    "Social Impact Technologies": "Rural livelihood enhancement systems, decentralized artisan processing tools, and civic transparency platforms.",
    "Multidisciplinary Engineering": "Cross-domain scientific instrumentation, multi-physics simulations, and integrated public-benefit engineering prototypes."
}


async def init_and_seed():
    print("Initializing BMIR 2.0 Database Tables...")
    async with engine.begin() as conn:
        # Create all tables defined in Base
        await conn.run_sync(Base.metadata.create_all)
    print("Tables created successfully.")

    async with async_session_maker() as session:
        # 1. Check if founder already seeded
        result = await session.execute(select(BMIRUser).where(BMIRUser.email == settings.FOUNDER_EMAIL))
        founder = result.scalar_one_or_none()

        if not founder:
            print("Seeding Users...")
            founder = BMIRUser(
                email=settings.FOUNDER_EMAIL,
                password_hash=get_password_hash(settings.DEFAULT_INITIAL_PASSWORD),
                full_name=settings.FOUNDER_NAME,
                role="founder",
                designation="Founder & Independent Inventor",
                organization="Bharat Multisector Innovation & Research (BMIR)",
                bio="Independent inventor and founder of Bharat Multisector Innovation & Research (BMIR). Leading multidisciplinary engineering investigations across smart agriculture, clean hydrogen containment, and community acoustic diagnostic instruments.",
                phone="+91 8340 328914",
                research_interests="Smart Farming Automation, Composite Hydrogen Storage, Acoustic Medical Biomarkers, Wetland Mechatronics",
                email_verified=True,
                is_active=True,
                preferences_json={"theme": "dark", "email_notifications": True, "digest_frequency": "daily"},
            )
            admin = BMIRUser(
                email=settings.ADMIN_EMAIL,
                password_hash=get_password_hash(settings.DEFAULT_INITIAL_PASSWORD),
                full_name="BMIR System Administrator",
                role="super_admin",
                designation="Enterprise Systems & Security Lead",
                organization="BMIR",
                email_verified=True,
                is_active=True,
            )
            scientist = BMIRUser(
                email="priya.sharma@bmirresearch.in",
                password_hash=get_password_hash(settings.DEFAULT_INITIAL_PASSWORD),
                full_name="Dr. Priya Sharma",
                role="research_scientist",
                designation="Lead AI & Bioengineering Scientist",
                organization="BMIR",
                email_verified=True,
                is_active=True,
            )
            engineer = BMIRUser(
                email="rajesh.kumar@bmirresearch.in",
                password_hash=get_password_hash(settings.DEFAULT_INITIAL_PASSWORD),
                full_name="Rajesh Kumar",
                role="research_engineer",
                designation="Mechatronics & Robotics Lead",
                organization="BMIR",
                email_verified=True,
                is_active=True,
            )
            session.add_all([founder, admin, scientist, engineer])
            await session.flush()
            print("Users seeded successfully.")

        # 2. Check if innovations already seeded
        innov_check = await session.execute(select(Innovation).limit(1))
        if not innov_check.scalar_one_or_none():
            print("Seeding authentic 27 BMIR Innovations...")
            raw_data_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "bmir_data_array.js")
            if not os.path.exists(raw_data_file):
                raw_data_file = "bmir_data_array.js"

            innovations_list = []
            if os.path.exists(raw_data_file):
                with open(raw_data_file, "r", encoding="utf-8") as f:
                    raw_items = ast.literal_eval(f.read())
            else:
                raw_items = []

            code_prefix_map = {
                "Agriculture": "AGR",
                "Healthcare": "HLT",
                "Urban safety": "URB",
                "Railways": "RLW",
                "Governance": "GOV",
                "Water": "WTR",
                "Export": "EXP",
                "Defence": "DEF",
                "Energy": "ENG",
                "Research": "RES",
                "Rural development": "RUR",
                "Education": "EDU",
            }

            for idx, item in enumerate(raw_items):
                title = item[0]
                sector = item[1]
                desc_en = item[2]
                desc_hi = item[3]
                pat_no = item[4].strip() if len(item) > 4 and item[4] else None
                prob_en = item[5] if len(item) > 5 else desc_en
                sol_en = item[6] if len(item) > 6 else desc_en
                val_en = item[7] if len(item) > 7 else "Independent laboratory review & prototype verification required."
                collab_en = item[8] if len(item) > 8 else "Institutional research & engineering validation partners."
                prob_hi = item[9] if len(item) > 9 else desc_hi
                sol_hi = item[10] if len(item) > 10 else desc_hi
                val_hi = item[11] if len(item) > 11 else ""
                collab_hi = item[12] if len(item) > 12 else ""
                status_raw = item[13] if len(item) > 13 else "Not filed / unverified"

                prefix = code_prefix_map.get(sector, "GEN")
                code = f"BMIR-{prefix}-{idx+1:03d}"

                # Determine development stage responsibly (never claiming verified working when unverified)
                if "Complete" in status_raw or "Published" in status_raw:
                    dev_stage = "Prototype"
                    proto_status = "Engineering prototype under laboratory testing; external validation pending."
                elif "Provisional" in status_raw:
                    dev_stage = "Feasibility"
                    proto_status = "Laboratory concept & technical feasibility documented; prototype pending."
                else:
                    dev_stage = "Concept"
                    proto_status = "Research concept formulation; prototype not independently verified."

                # Verification status strictly defined
                if pat_no in ["202631023777", "202631058488", "202631093158"]:
                    verif_status = "Verified"
                elif pat_no:
                    verif_status = "Pending verification"
                else:
                    verif_status = "Draft"

                # Co-inventors
                co_inventors = None
                if pat_no == "202631065492" or "Hydrogen Gas Cylinder" in title:
                    co_inventors = "Dr. Shyam Sundar Mandal (Co-Inventor & Joint Applicant)"
                elif pat_no == "202631067840" or "AI-SHRUTI" in title:
                    co_inventors = "Akash Rajvanshi (Inventor-Reported; Form 1 Verification Pending)"

                innov = Innovation(
                    project_code=code,
                    title=title,
                    title_hi=desc_hi if len(desc_hi) < 60 else title,
                    domain=sector,
                    summary=desc_en,
                    summary_hi=desc_hi,
                    problem_statement=prob_en,
                    problem_statement_hi=prob_hi,
                    proposed_solution=sol_en,
                    proposed_solution_hi=sol_hi,
                    technical_description=f"{title} represents an engineered solution addressing {sector} challenges. {sol_en} Requires validation: {val_en}",
                    technical_description_hi=f"{desc_hi} {sol_hi}",
                    development_stage=dev_stage,
                    prototype_status=proto_status,
                    validation_required=val_en,
                    validation_required_hi=val_hi,
                    collaboration_sought=collab_en,
                    collaboration_sought_hi=collab_hi,
                    patent_application_no=pat_no,
                    patent_status=status_raw,
                    co_inventors=co_inventors,
                    is_published=True,
                    is_confidential=False,
                    verification_status=verif_status,
                )
                session.add(innov)
                innovations_list.append(innov)

            await session.flush()
            print(f"Seeded {len(innovations_list)} innovations.")

            # 3. Seed Patent Records for verified records
            print("Seeding authentic Patent Records...")
            patents_metadata = [
                {
                    "title": "Hybrid Maize Seed Production",
                    "app_no": "202631048563",
                    "prov_no": "202631038831",
                    "filing_date": "16/04/2026",
                    "prov_date": "28/03/2026",
                    "pub_date": "05/06/2026",
                    "issue": "Issue 23/2026",
                    "page": "67482",
                    "type": "Published",
                    "status": "Official Journal Published",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Journal published; official IPO gazette issue verified. Publication is not patent grant.",
                },
                {
                    "title": "Intelligent Maize Dryer & Conditioning System",
                    "app_no": "202631058488",
                    "prov_no": "202631056728",
                    "filing_date": "07/05/2026",
                    "prov_date": "04/05/2026",
                    "pub_date": "12/06/2026",
                    "issue": "Issue 24/2026",
                    "page": "70478",
                    "type": "Published",
                    "status": "Official Journal Published",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Complete specification filed and published in IPO Journal. Publication is not patent grant.",
                },
                {
                    "title": "Hydrogen Gas Cylinder Storage System",
                    "app_no": "202631065492",
                    "prov_no": None,
                    "filing_date": "21/05/2026",
                    "prov_date": None,
                    "pub_date": "12/06/2026",
                    "issue": "Issue 24/2026",
                    "page": "70493",
                    "type": "Published",
                    "status": "Official Journal Published",
                    "lead": "Binod Pandey",
                    "co": "Dr. Shyam Sundar Mandal (Co-Inventor & Joint Applicant)",
                    "notes": "Evidenced in IPO Journal 24/2026 p. 70493. Jointly filed with Dr. Shyam Sundar Mandal.",
                },
                {
                    "title": "Hydrogen & Oxygen Production System",
                    "app_no": "202631064356",
                    "prov_no": None,
                    "filing_date": "21/05/2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": "Dr. Shyam Sundar Mandal",
                    "notes": "Provisional patent application filed. Complete specification and journal publication pending.",
                },
                {
                    "title": "AGRI-SENTINEL Autonomous Crop Monitoring Drone",
                    "app_no": "202631084588",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Provisional filing record documented in inventor register. Formal examination pending.",
                },
                {
                    "title": "MAKHANA-ROVER Wetland Agriculture Machine",
                    "app_no": "202631107125",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Provisional application for aquatic seed harvesting mechanism.",
                },
                {
                    "title": "AI-SHRUTI Acoustic Diagnostic Assistant",
                    "app_no": "202631067840",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": "Akash Rajvanshi (Inventor-Reported)",
                    "notes": "Provisional application for sound-based preliminary health assessment.",
                },
                {
                    "title": "PRAHARI Urban Safety & Surveillance Network",
                    "app_no": "202631084211",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Provisional filing for multi-sensor urban hazard detection.",
                },
                {
                    "title": "BHF-WAGON Bulk Freight Wagon Enclosure",
                    "app_no": "202631090804",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Provisional patent application for enclosed railway freight container safety.",
                },
                {
                    "title": "AI-EFCS Export Quality Assessment System",
                    "app_no": "202631121003",
                    "prov_no": None,
                    "filing_date": "2026",
                    "prov_date": None,
                    "pub_date": None,
                    "issue": None,
                    "page": None,
                    "type": "Provisional",
                    "status": "Provisional Application Filed",
                    "lead": "Binod Pandey",
                    "co": None,
                    "notes": "Provisional application for optical and chemical grading of agricultural exports.",
                },
            ]

            for pmeta in patents_metadata:
                # Find matching innovation if possible
                matching_innov = next((inv for inv in innovations_list if inv.patent_application_no == pmeta["app_no"]), None)
                p_verif = "Verified" if pmeta.get("type") == "Published" or pmeta.get("pub_date") else "Pending verification"
                prec = PatentRecord(
                    innovation_id=matching_innov.id if matching_innov else None,
                    title=pmeta["title"],
                    application_number=pmeta["app_no"],
                    provisional_application_number=pmeta["prov_no"],
                    filing_date=pmeta["filing_date"],
                    provisional_filing_date=pmeta["prov_date"],
                    publication_date=pmeta["pub_date"],
                    journal_issue=pmeta["issue"],
                    journal_page=pmeta["page"],
                    jurisdiction="Indian Patent Office (IPO / Kolkata)",
                    lead_inventor=pmeta["lead"],
                    co_inventors=pmeta["co"],
                    applicants=pmeta["lead"],
                    patent_type=pmeta["type"],
                    legal_status=pmeta["status"],
                    verification_notes=pmeta["notes"],
                    verification_status=p_verif,
                    is_confidential=False,
                )
                session.add(prec)

            await session.flush()
            print("Patent records seeded.")

            # 4. Seed Research Projects
            print("Seeding Research Projects...")
            projects_data = [
                {
                    "code": "BMIR-PRJ-01",
                    "title": "KRISHI-BODH: Real-time Multi-spectral Soil & Crop Diagnostic Unit",
                    "domain": "Agriculture & Smart Farming",
                    "objective": "To develop a low-cost field deployable spectroscopic and NPK sensor system empowering smallholder farmers in Bihar with localized soil conditioning recommendations.",
                    "questions": "Can near-infrared reflectance paired with microfluidic electrochemical sensors yield reliable soil nitrogen estimation within +/- 8% margin in flood-plain soils?",
                    "methodology": "Design of custom PCB with multi-spectral photodiodes, micro-controller calibration, comparative laboratory wet chemistry testing across 12 soil variants in Bhagalpur district.",
                    "progress": 35,
                    "status": "Active",
                    "lead": "Binod Pandey",
                    "members": "Dr. Priya Sharma, Rajesh Kumar",
                },
                {
                    "code": "BMIR-PRJ-02",
                    "title": "Clean Hydrogen Production & Safe Composite Storage",
                    "domain": "Renewable Energy",
                    "objective": "Investigating high-pressure structural containment and alkaline membrane electrolysis efficiencies for decentralized green hydrogen applications.",
                    "questions": "What structural composite layering provides optimal burst pressure and weight ratio for localized storage under 200 bar without micro-fissuring?",
                    "methodology": "Finite element stress analysis, filament wound carbon-glass hybrid cylinder prototyping, hydrostatic burst testing under controlled conditions.",
                    "progress": 45,
                    "status": "Active",
                    "lead": "Binod Pandey",
                    "members": "Dr. Shyam Sundar Mandal (Co-Investigator)",
                },
                {
                    "code": "BMIR-PRJ-03",
                    "title": "AI-SHRUTI: Acoustic Biomarker Recognition for Respiratory Screening",
                    "domain": "Healthcare & Medical Technology",
                    "objective": "Creating a lightweight edge-AI acoustic model to identify pulmonary wheezing, rhonchi and stridor from smartphone microphone recordings in rural primary clinics.",
                    "questions": "How can ambient background noise in rural health centres be filtered without losing critical acoustic frequency components of breath sounds?",
                    "methodology": "Spectrogram feature extraction, mel-frequency cepstral coefficients (MFCC), noise subtraction using directional micro-arrays, double-blind clinical annotation.",
                    "progress": 30,
                    "status": "Active",
                    "lead": "Binod Pandey",
                    "members": "Dr. Priya Sharma, Akash Rajvanshi",
                },
                {
                    "code": "BMIR-PRJ-04",
                    "title": "MAKHANA-ROVER: Aquatic Wetland Harvesting System",
                    "domain": "Robotics & Automation",
                    "objective": "Designing an amphibious harvesting rover to mechanize the dangerous and laborious manual harvesting of gorgon nut (Euryale ferox) seeds from deep muddy wetlands.",
                    "questions": "Can an inverted vacuum-auger mechanism extract thorny bottom-sediment seeds without crushing delicate seed kernels or disturbing aquatic ecology?",
                    "methodology": "Waterproof flotation hull modeling, buoyant Archimedean screw propulsion tests, hydrodynamic silt separation chamber design.",
                    "progress": 25,
                    "status": "Planned",
                    "lead": "Binod Pandey",
                    "members": "Rajesh Kumar",
                },
            ]

            seeded_projects = []
            for pdata in projects_data:
                prj_verif = "Verified" if pdata["status"] == "Active" else "Pending verification"
                prj = ResearchProject(
                    project_code=pdata["code"],
                    title=pdata["title"],
                    domain=pdata["domain"],
                    objective=pdata["objective"],
                    research_questions=pdata["questions"],
                    methodology=pdata["methodology"],
                    progress_pct=pdata["progress"],
                    status=pdata["status"],
                    lead_researcher=pdata["lead"],
                    team_members=pdata["members"],
                    verification_status=prj_verif,
                )
                session.add(prj)
                seeded_projects.append(prj)

            await session.flush()
            print("Research projects seeded.")

            # 5. Seed Experiments for Active Projects
            print("Seeding Research Experiments...")
            exp1 = Experiment(
                project_id=seeded_projects[0].id,
                created_by_id=founder.id,
                title="NIR Spectroscopic Calibration Curve for Gangetic Alluvial Soil Nitrogen",
                domain="Agriculture & Smart Farming",
                objective="Derive reflectance absorbance correlation at 1450nm and 1940nm for moisture-compensated nitrogen estimation.",
                hypothesis="Absorbance ratio at 1450nm normalized by moisture index correlates with Kjeldahl nitrogen with R^2 > 0.82.",
                methodology="Tested 45 prepared soil samples with moisture range 5% to 30%. Recorded 10 spectrophotometer sweeps per specimen.",
                materials_used="Alluvial soil specimens, NIR spectrometer probe, Kjeldahl digestion apparatus, analytical balance.",
                measurements="Spectral reflectance values from 900nm to 2100nm at 10nm increments. Chemical Kjeldahl reference values.",
                observations="Moisture above 22% causes non-linear scattering requiring polynomial baseline correction.",
                results_summary="Linear correlation achieved R^2 = 0.84 after polynomial background subtraction. Field sensor prototype PCB routed.",
                status="Concluded",
                version=2,
                data_metrics={
                    "r_squared": 0.842,
                    "samples_tested": 45,
                    "error_margin_pct": 6.8,
                    "moisture_limit_pct": 22.0
                }
            )
            exp2 = Experiment(
                project_id=seeded_projects[1].id,
                created_by_id=founder.id,
                title="Hydrostatic Pressure Stress Test on Hybrid Carbon-Fiber Cylinder Liner",
                domain="Renewable Energy",
                objective="Determine plastic deformation threshold and safety margin under cyclic pressurization up to 250 bar.",
                hypothesis="Filament winding angle of 54.7 degrees produces equal hoop and longitudinal stress resistance up to 280 bar.",
                methodology="Water pressurized hydraulic test rig, ultrasonic wall-thickness gauges, strain gauges positioned at hoop and dome junctions.",
                materials_used="Aluminum 6061-T6 seamless liner, T700 carbon fiber roving, epoxy matrix, calibrated hydraulic pressure pump.",
                measurements="Strain micro-displacements at 50 bar increments up to 260 bar sustained for 15 minutes.",
                observations="Zero leakage or delamination observed at 200 bar operating pressure. Micro-strain remained within elastic limits.",
                results_summary="Hydrostatic hold succeeded at 220 bar without plastic strain. Burst safety factor calculated at 2.4x.",
                status="Ongoing",
                version=1,
                data_metrics={
                    "max_pressure_bar": 260,
                    "elastic_limit_bar": 235,
                    "safety_factor": 2.4,
                    "hold_duration_min": 15
                }
            )
            session.add_all([exp1, exp2])

            # 6. Seed Feasibility Evaluation & Roadmap
            print("Seeding Feasibility & Roadmaps...")
            first_innov = innovations_list[0] if innovations_list else None
            second_innov = next((inv for inv in innovations_list if "Intelligent Maize" in inv.title), first_innov)
            
            fe = FeasibilityEvaluation(
                innovation_id=second_innov.id if second_innov else None,
                title=f"Technical & Economic Feasibility Review: {second_innov.title if second_innov else 'Intelligent Maize Conditioning'}",
                scientific_feasibility=86.0,
                engineering_feasibility=82.0,
                material_availability=88.0,
                manufacturing_readiness=78.0,
                development_complexity=72.0,
                energy_efficiency=85.0,
                economic_viability=90.0,
                environmental_impact=88.0,
                safety_compliance=84.0,
                overall_score=83.6,
                limitations_and_risks="Requires high-temp rated optical moisture sensors and continuous power stability in rural mandi environments.",
                prerequisites="Fabrication of secondary rotary conditioning chamber and pilot trial with Bhagalpur grain producers.",
                confidence_level="High"
            )
            session.add(fe)

            rd = InnovationRoadmap(
                innovation_id=second_innov.id if second_innov else None,
                title="Commercial Pilot & Institutional Validation Roadmap (2026-2027)",
                phases_json=[
                    {
                        "phase": "Phase 1: Laboratory Scale Benchmarking",
                        "duration": "Months 1-3",
                        "milestones": ["Sensor array calibration", "Thermal simulation model verification"],
                        "deliverables": "Technical validation report and calibrated sensor schematics",
                        "risks": "Sensor drift in high humidity conditions"
                    },
                    {
                        "phase": "Phase 2: Working Pilot Unit Fabrication",
                        "duration": "Months 4-7",
                        "milestones": ["Fabricate 500kg/hr prototype", "Integrate automated airflow louvers"],
                        "deliverables": "Operational pilot machinery ready for field trial",
                        "risks": "Component supply chain lead times"
                    },
                    {
                        "phase": "Phase 3: Multi-Centre Agricultural Trials",
                        "duration": "Months 8-11",
                        "milestones": ["Trials with farmer producer organisations (FPOs)", "Aflatoxin prevention quantification"],
                        "deliverables": "Verified agronomic impact data signed by partner agricultural institute",
                        "risks": "Seasonal maize harvesting window constraints"
                    },
                    {
                        "phase": "Phase 4: Technology Transfer & Licensing",
                        "duration": "Month 12",
                        "milestones": ["Licensing briefing package", "Institutional commercialization agreements"],
                        "deliverables": "Production blueprints and commercial licensing agreements",
                        "risks": "Regulatory clearance timelines"
                    }
                ],
                estimated_timeline_months=12,
                status="Active"
            )
            session.add(rd)

            # 7. Seed Knowledge Documents
            print("Seeding Knowledge Base Documents...")
            kd1 = KnowledgeDocument(
                title="Post-Harvest Moisture Dynamics and Aflatoxin Mitigation in Eastern Gangetic Maize",
                doc_type="Research Paper",
                domain="Agriculture & Smart Farming",
                abstract="Investigation of rapid drying kinetics in high-moisture Zea mays harvests across Bihar to suppress Aspergillus flavus proliferation.",
                content="""Abstract: High ambient humidity during the harvest season in eastern India causes maize grain moisture levels to remain above 18%, accelerating mold growth and aflatoxin contamination. Conventional solar drying requires 4-6 days, during which substantial dry-matter loss occurs. This study evaluates an automated dehumidified warm-air drying mechanism incorporating multi-point capacitive sensing to achieve safe moisture storage thresholds (<13%) within 8 hours. Controlled experimental runs demonstrated a 94% reduction in aflatoxin accumulation compared to open sun-dried controls.""",
                keywords="Maize, Post-harvest, Moisture kinetics, Aflatoxin, Smart drying, BMIR",
                authors="Binod Pandey et al.",
                source_url="https://bmirresearch.in/publications/maize-drying-kinetics",
                is_confidential=False,
                verification_status="Verified",
                uploaded_by_id=founder.id,
                embedding_vector=[0.025, 0.081, -0.043, 0.12, 0.05, 0.088, -0.012, 0.09]  # Normalized mock embedding
            )
            kd2 = KnowledgeDocument(
                title="Electrochemical Efficiency and Structural Safety of Composite Hydrogen Storage Cylinders",
                doc_type="Technical Report",
                domain="Renewable Energy",
                abstract="Comprehensive engineering evaluation of high-pressure composite cylinders under cyclic hydraulic loading and thermal stress.",
                content="""Abstract: Decentralized clean hydrogen infrastructure requires lightweight, leak-proof containment vessels with high volumetric efficiency. This report details hydrostatic pressure cycling of a 6061-T6 aluminum liner wrapped in filament-wound carbon/epoxy composite at a nominal service pressure of 200 bar. Analytical burst calculations and strain-gauge monitoring reveal a minimum safety factor of 2.4 under ambient conditions. Guidelines for manufacturing quality assurance and pressure relief integration are documented.""",
                keywords="Green Hydrogen, Storage Cylinder, Carbon Composite, Burst Safety, Clean Energy",
                authors="Binod Pandey, Dr. Shyam Sundar Mandal",
                source_url="https://bmirresearch.in/publications/hydrogen-storage-evaluation",
                is_confidential=False,
                verification_status="Verified",
                uploaded_by_id=founder.id,
                embedding_vector=[0.091, -0.012, 0.142, 0.063, -0.035, 0.077, 0.11, 0.04]
            )
            session.add_all([kd1, kd2])

            # 8. Seed Initial Collaboration Enquiries
            print("Seeding Collaboration Enquiries...")
            ce1 = CollaborationEnquiry(
                enquiry_number="BMIR-ENQ-2026-001",
                full_name="Dr. Anil Deshmukh",
                email="a.deshmukh@agri-tech-institute.ac.in",
                phone="+91 98230 45671",
                organization="National Institute of Post-Harvest Technology",
                organization_type="University",
                pathway="Research Collaboration",
                project_interest="Intelligent Maize Dryer & Conditioning System",
                message="We are interested in collaborating on field-validation trials of your automated drying mechanism across our regional research stations during the upcoming kharif harvest.",
                proposal_summary="Joint trial agreement for testing sensor accuracy and grain quality across 5 metric ton batches.",
                status="Under Review",
                internal_notes="Reviewed by Binod Pandey. Initial meeting scheduled for technical specification exchange."
            )
            ce2 = CollaborationEnquiry(
                enquiry_number="BMIR-ENQ-2026-002",
                full_name="Sarah Jenkins",
                email="s.jenkins@veritas-cleantech.org",
                phone="+44 20 7946 0912",
                organization="Veritas Clean Energy Foundation",
                organization_type="Corporate R&D",
                pathway="Prototype Development",
                project_interest="Hydrogen Gas Cylinder Storage System",
                message="We have reviewed your publication in IPO Journal 24/2026 regarding composite hydrogen containment. We would like to explore prototyping grant assistance and testing support.",
                proposal_summary="Potential grant-supported testing at an ISO-certified European pressure testing facility.",
                status="Pending",
                internal_notes="Requires preliminary NDA before sharing complete engineering drawings."
            )
            session.add_all([ce1, ce2])

            # 9. Seed Audit Logs
            print("Seeding Audit Log...")
            audit = AuditLog(
                user_id=admin.id,
                action="SYSTEM_INIT_AND_SEED",
                resource_type="Database",
                resource_id="bmir_platform",
                details={
                    "innovations_count": len(innovations_list),
                    "patents_count": len(patents_metadata),
                    "projects_count": len(projects_data),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                },
                ip_address="127.0.0.1"
            )
            session.add(audit)

            # 10. Seed Initial Notifications & Active Session
            n1 = BMIRNotification(
                user_id=founder.id,
                category="collaboration",
                title="Institutional Collaboration Proposal",
                content="National Institute of Post-Harvest Technology requested joint pilot trials for Intelligent Maize Dryer.",
                link_url="collaboration_mgmt",
                is_read=False,
            )
            n2 = BMIRNotification(
                user_id=founder.id,
                category="patent",
                title="IPO Gazette Publication Verified",
                content="Patent Application 202631023777 verified in IPO Journal Issue 23/2026.",
                link_url="patents",
                is_read=True,
            )
            n3 = BMIRNotification(
                user_id=founder.id,
                category="security",
                title="Zero-Trust Integrity Initialized",
                content="Server-side session management and role-based access control active.",
                link_url="security_settings",
                is_read=False,
            )
            s1 = BMIRSession(
                user_id=founder.id,
                token_jti="session-founder-primary",
                device_name="Primary Desktop Workstation (Chrome)",
                ip_address="127.0.0.1",
                location="Bhagalpur, Bihar, India",
                is_active=True,
            )
            session.add_all([n1, n2, n3, s1])

            await session.commit()
            print("Seeding successfully completed!")
        else:
            print("Innovations already seeded in database.")

if __name__ == "__main__":
    asyncio.run(init_and_seed())
