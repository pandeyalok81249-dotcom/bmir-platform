import uuid
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def generate_uuid() -> str:
    return str(uuid.uuid4())


class BMIRUser(Base):
    __tablename__ = "bmir_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(50),
        default="viewer",
        nullable=False,
        index=True
    )  # super_admin, founder, research_admin, research_scientist, research_engineer, external_collaborator, viewer
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default="BMIR")
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    research_interests: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    preferences_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    experiments = relationship("Experiment", back_populates="creator", cascade="all, delete-orphan")
    conversations = relationship("AIConversation", back_populates="user", cascade="all, delete-orphan")
    documents = relationship("KnowledgeDocument", back_populates="uploader", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("BMIRSession", back_populates="user", cascade="all, delete-orphan")


class BMIRSession(Base):
    __tablename__ = "bmir_active_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_jti: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    device_name: Mapped[str] = mapped_column(String(255), default="Desktop Workstation", nullable=False)
    ip_address: Mapped[str] = mapped_column(String(100), default="127.0.0.1", nullable=False)
    location: Mapped[str] = mapped_column(String(255), default="Bhagalpur, Bihar, India", nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    last_active_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("BMIRUser", back_populates="sessions")


class BMIRNotification(Base):
    __tablename__ = "bmir_notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="CASCADE"), nullable=True, index=True)
    category: Mapped[str] = mapped_column(String(50), default="general", nullable=False)  # research, project, collaboration, document, security, account
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Text] = mapped_column(Text, nullable=False)
    link_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class Innovation(Base):
    __tablename__ = "bmir_innovations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    title_hi: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    summary_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    problem_statement: Mapped[str] = mapped_column(Text, nullable=False)
    problem_statement_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    proposed_solution: Mapped[str] = mapped_column(Text, nullable=False)
    proposed_solution_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    technical_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    technical_description_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    development_stage: Mapped[str] = mapped_column(
        String(50), default="Concept", index=True, nullable=False
    )  # Concept, Research, Feasibility, Design, Prototype, Testing, Validation, Commercialization
    
    prototype_status: Mapped[str] = mapped_column(
        String(100), default="Unverified Concept", nullable=False
    )  # e.g., "Research / concept; prototype and validation status not independently verified."
    
    validation_required: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    validation_required_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    collaboration_sought: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collaboration_sought_hi: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    patent_application_no: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    patent_status: Mapped[str] = mapped_column(String(100), default="Not filed / unverified", nullable=False)
    
    co_inventors: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, index=True, nullable=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="Pending verification", index=True, nullable=False
    )  # Verified, Pending verification, Draft, Unpublished, Archived
    
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    patent_records = relationship("PatentRecord", back_populates="innovation")
    feasibility_evaluations = relationship("FeasibilityEvaluation", back_populates="innovation")
    roadmaps = relationship("InnovationRoadmap", back_populates="innovation")


class PatentRecord(Base):
    __tablename__ = "bmir_patent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    innovation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_innovations.id", ondelete="SET NULL"), nullable=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    application_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    provisional_application_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    filing_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provisional_filing_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    publication_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    journal_issue: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    journal_page: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    jurisdiction: Mapped[str] = mapped_column(String(100), default="Indian Patent Office (IPO)", nullable=False)
    lead_inventor: Mapped[str] = mapped_column(String(255), default="Binod Pandey", nullable=False)
    co_inventors: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    applicants: Mapped[str] = mapped_column(String(255), default="Binod Pandey", nullable=False)
    
    patent_type: Mapped[str] = mapped_column(String(50), default="Provisional", nullable=False)  # Idea, Provisional, Complete, Published, Granted, Abandoned
    legal_status: Mapped[str] = mapped_column(String(100), default="Application Filed", nullable=False)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    claims_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="Pending verification", index=True, nullable=False
    )  # Verified, Pending verification, Draft, Unpublished, Archived
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    innovation = relationship("Innovation", back_populates="patent_records")


class ResearchProject(Base):
    __tablename__ = "bmir_research_projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    research_questions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    methodology: Mapped[str] = mapped_column(Text, nullable=False)
    technical_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    progress_pct: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Active", nullable=False)  # Active, Under Review, Planned, Completed
    verification_status: Mapped[str] = mapped_column(
        String(50), default="Verified", index=True, nullable=False
    )  # Verified, Pending verification, Draft, Unpublished, Archived
    
    lead_researcher: Mapped[str] = mapped_column(String(255), default="Binod Pandey", nullable=False)
    team_members: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    experiments = relationship("Experiment", back_populates="project")


class Experiment(Base):
    __tablename__ = "bmir_experiments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    project_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_research_projects.id", ondelete="SET NULL"), nullable=True)
    created_by_id: Mapped[str] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="CASCADE"), nullable=False)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    objective: Mapped[str] = mapped_column(Text, nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    methodology: Mapped[Text] = mapped_column(Text, nullable=False)
    materials_used: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    measurements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    observations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    results_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="Ongoing", nullable=False)  # Draft, Ongoing, Concluded, Replicated
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    data_metrics: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    project = relationship("ResearchProject", back_populates="experiments")
    creator = relationship("BMIRUser", back_populates="experiments")


class FeasibilityEvaluation(Base):
    __tablename__ = "bmir_feasibility_evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    innovation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_innovations.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    scientific_feasibility: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)
    engineering_feasibility: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    material_availability: Mapped[float] = mapped_column(Float, default=65.0, nullable=False)
    manufacturing_readiness: Mapped[float] = mapped_column(Float, default=60.0, nullable=False)
    development_complexity: Mapped[float] = mapped_column(Float, default=65.0, nullable=False)
    energy_efficiency: Mapped[float] = mapped_column(Float, default=70.0, nullable=False)
    economic_viability: Mapped[float] = mapped_column(Float, default=80.0, nullable=False)
    environmental_impact: Mapped[float] = mapped_column(Float, default=85.0, nullable=False)
    safety_compliance: Mapped[float] = mapped_column(Float, default=75.0, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, default=71.0, nullable=False)
    
    limitations_and_risks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prerequisites: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence_level: Mapped[str] = mapped_column(String(50), default="Medium", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    innovation = relationship("Innovation", back_populates="feasibility_evaluations")


class InnovationRoadmap(Base):
    __tablename__ = "bmir_innovation_roadmaps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    innovation_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_innovations.id", ondelete="SET NULL"), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    
    phases_json: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, nullable=False)
    estimated_timeline_months: Mapped[int] = mapped_column(Integer, default=12, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="Active", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    innovation = relationship("Innovation", back_populates="roadmaps")


class KnowledgeDocument(Base):
    __tablename__ = "bmir_knowledge_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(50), default="Research Paper", nullable=False)
    domain: Mapped[str] = mapped_column(String(100), nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Text] = mapped_column(Text, nullable=False)
    keywords: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    authors: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    embedding_vector: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verification_status: Mapped[str] = mapped_column(
        String(50), default="Verified", index=True, nullable=False
    )  # Verified, Pending verification, Draft, Unpublished, Archived
    uploaded_by_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="SET NULL"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    uploader = relationship("BMIRUser", back_populates="documents")


class CollaborationEnquiry(Base):
    __tablename__ = "bmir_collaboration_enquiries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    enquiry_number: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    organization: Mapped[str] = mapped_column(String(255), nullable=False)
    organization_type: Mapped[str] = mapped_column(String(100), nullable=False)  # University, Research Lab, Corporate R&D, Investor, Incubator, Independent Researcher
    
    pathway: Mapped[str] = mapped_column(String(100), nullable=False)  # Research Collaboration, Prototype Development, Technical Review, Licensing, Funding
    project_interest: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    proposal_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    status: Mapped[str] = mapped_column(String(50), default="Pending", index=True, nullable=False)  # Pending, Under Review, Approved, Declined
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)


class AIConversation(Base):
    __tablename__ = "bmir_ai_conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="New Research Session", nullable=False)
    module: Mapped[str] = mapped_column(String(50), default="assistant", nullable=False)  # assistant, multi_model, discovery, literature, patent
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("BMIRUser", back_populates="conversations")
    messages = relationship("AIMessage", back_populates="conversation", cascade="all, delete-orphan", order_by="AIMessage.created_at")


class AIMessage(Base):
    __tablename__ = "bmir_ai_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    conversation_id: Mapped[str] = mapped_column(String(36), ForeignKey("bmir_ai_conversations.id", ondelete="CASCADE"), nullable=False)
    
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant, system
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    content: Mapped[Text] = mapped_column(Text, nullable=False)
    citations: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, nullable=True)
    tokens_in: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tokens_out: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    conversation = relationship("AIConversation", back_populates="messages")


class AuditLog(Base):
    __tablename__ = "bmir_audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=generate_uuid, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("bmir_users.id", ondelete="SET NULL"), nullable=True)
    
    action: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user = relationship("BMIRUser", back_populates="audit_logs")
