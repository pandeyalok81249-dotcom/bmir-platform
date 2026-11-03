import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, Index, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    company: Mapped[str] = mapped_column(String(200), nullable=True)
    job_title: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    extracted_requirements: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="job_descriptions")
    job_matches = relationship("JobMatch", back_populates="job_description", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="job_description")


class JobMatch(Base):
    __tablename__ = "job_matches"
    __table_args__ = (
        Index("ix_job_matches_version_score", "resume_version_id", "match_score"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    resume_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    job_description_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("job_descriptions.id", ondelete="CASCADE"), index=True, nullable=False
    )
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    match_result: Mapped[dict] = mapped_column(JSON, nullable=False)
    methodology_version: Mapped[str] = mapped_column(
        String(20), default="1.0", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    resume_version = relationship("ResumeVersion", back_populates="job_matches")
    job_description = relationship("JobDescription", back_populates="job_matches")


class Skill(Base):
    __tablename__ = "skills"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    normalized_name: Mapped[str] = mapped_column(
        String(100), unique=True, index=True, nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # technical, soft, domain, tool, language


class UserSkill(Base):
    __tablename__ = "user_skills"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    skill_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("skills.id", ondelete="RESTRICT"), nullable=False
    )
    proficiency: Mapped[str] = mapped_column(
        String(30), default="competent", nullable=False
    )
    evidence_source: Mapped[str] = mapped_column(String(50), nullable=True)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "skill_id", name="uq_user_skill"),
    )

