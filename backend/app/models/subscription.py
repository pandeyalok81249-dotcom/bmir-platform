import uuid
from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    __table_args__ = (
        Index("ix_subscriptions_user_status", "user_id", "status"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    tier: Mapped[str] = mapped_column(
        String(50),
        default="free",
        nullable=False,
    )  # free, pro, professional
    status: Mapped[str] = mapped_column(
        String(50),
        default="active",
        nullable=False,
    )  # active, trialing, cancelled, expired
    current_period_start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    current_period_end: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    cancel_at_period_end: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
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

    user = relationship("User", back_populates="subscription")


class UserUsageQuota(Base):
    __tablename__ = "user_usage_quotas"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    month_period: Mapped[str] = mapped_column(
        String(7),
        default=lambda: datetime.now(timezone.utc).strftime("%Y-%m"),
        nullable=False,
    )
    resumes_uploaded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    ai_analyses_run: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    interviews_conducted: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    simulations_run: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user = relationship("User", back_populates="usage_quota")
