import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, Index, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    __table_args__ = (
        Index("ix_interviews_user_created", "user_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    resume_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="SET NULL"), nullable=True
    )
    target_role: Mapped[str] = mapped_column(String(150), nullable=False)
    session_data: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    evaluation: Mapped[dict] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="interview_sessions")

