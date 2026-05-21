"""
    SQLAlchemy models
    Author: Happy Banda
"""

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import String, Float, JSON, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class DiscoveryJob(Base):
    __tablename__ = "discovery_jobs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, index=True)
    status: Mapped[str] = mapped_column(String(20), default="queued", index=True)
    business_description: Mapped[str] = mapped_column(String, nullable=False)
    target_market: Mapped[str] = mapped_column(String(2), nullable=False)
    buyer_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    max_results: Mapped[int] = mapped_column(default=10)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    leads: Mapped[list["DiscoveryLead"]] = relationship(
        "DiscoveryLead", back_populates="job",
        cascade="all, delete-orphan",
    )


class DiscoveryLead(Base):
    __tablename__ = "discovery_leads"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    job_id: Mapped[UUID] = mapped_column(
        ForeignKey("discovery_jobs.id"),
        index=True
    )

    company_id: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    headquarters_city: Mapped[str] = mapped_column(String, nullable=False)
    fit_score: Mapped[float] = mapped_column(Float, nullable=False)
    justification: Mapped[str] = mapped_column(String, nullable=False)
    rank: Mapped[int] = mapped_column(nullable=False)

    job: Mapped[DiscoveryJob] = relationship("DiscoveryJob", back_populates="leads")


