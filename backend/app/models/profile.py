import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    career_stage: Mapped[str] = mapped_column(String(50), nullable=True)  # student, entry, mid, senior, switcher
    current_role: Mapped[str] = mapped_column(String(150), nullable=True)
    target_role: Mapped[str] = mapped_column(String(150), nullable=True)
    experience_years: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    education: Mapped[dict] = mapped_column(JSON, default=list, nullable=False)
    preferred_location: Mapped[str] = mapped_column(String(150), nullable=True)
    career_goals: Mapped[str] = mapped_column(Text, nullable=True)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="profile")

