"""
Worker based Schemas
Author: Happy Banda
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class JobStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"

def _new_uuid() -> str:
    return str(uuid.uuid4())

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DiscoveryJob(Base):
    __tablename__ = "discovery_job"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status"), default=JobStatus.QUEUED, nullable=False
    )
    business_description: Mapped[str] = mapped_column(Text, nullable=False)
    target_market: Mapped[str] = mapped_column(String(2), nullable=False)
    buyer_types: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    max_results: Mapped[int] = mapped_column(nullable=False, default=10)

    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    leads: Mapped[list["DiscoveryLead"]] = relationship(
        back_populates="job", cascade="all, delete-orphan",
        order_by="DiscoveryLead.rank"
    )


class DiscoveryLead(Base):
    __tablename__ = "discovery_leads"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_new_uuid)
    job_id: Mapped[str] = mapped_column(
        ForeignKey("discovery_job.id", ondelete="CASCADE"), nullable=False,
        index=True
    )
    rank: Mapped[int] = mapped_column(nullable=False)
    seed_id: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country: Mapped[str] = mapped_column(String(2), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    grounded: Mapped[bool] = mapped_column(default=True, nullable=False)

    job: Mapped[DiscoveryJob] = relationship(back_populates="leads")
