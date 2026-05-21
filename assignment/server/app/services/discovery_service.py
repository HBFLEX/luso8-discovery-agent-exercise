"""
    Author: Happy Banda
"""

from uuid import UUID
from datetime import datetime, timezone
from typing import List

from sqlalchemy.orm import Session
from app.agent.graph import run_discovery_graph
from app.models import DiscoveryJob, DiscoveryLead
from app.schemas import DiscoveryRequest, DiscoveryResult, LeadOut


def create_discovery_job(
        db: Session,
        request: DiscoveryRequest,
) -> DiscoveryJob:
    job = DiscoveryJob(
        status="queued",
        business_description=request.business_description,
        target_market=request.target_market,
        buyer_types=request.buyer_types,
        max_results=request.max_results,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def run_and_save_discovery_job(
        db: Session,
        job: DiscoveryJob,
) -> DiscoveryResult:
    final_state = run_discovery_graph(
        business_description=job.business_description,
        target_market=job.target_market,
        buyer_types=job.buyer_types,
        max_results=job.max_results,
        thread_id=str(job.id),
    )

    scored_leads = final_state.get("scored_leads", [])

    for rank, lead_data in enumerate(scored_leads, start=1):
        lead = DiscoveryLead(
            job_id=job.id,
            company_id=lead_data["company_id"],
            name=lead_data["name"],
            category=lead_data["category"],
            country=lead_data["country"],
            headquarters_city=lead_data.get("headquarters_city", ""),
            fit_score=lead_data["fit_score"],
            justification=lead_data["justification"],
            rank=rank,
        )
        db.add(lead)

    job.status = "done"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(job)

    leads_out = [
        LeadOut(
            id=lead.id,
            name=lead.name,
            category=lead.category,
            country=lead.country,
            headquarters_city=lead.headquarters_city,
            fit_score=lead.fit_score,
            justification=lead.justification,
            rank=lead.rank,
        )
        for lead in job.leads
    ]

    return DiscoveryResult(job_id=job.id, leads=leads_out)

def get_job_status(db: Session, job_id: UUID) -> DiscoveryJob | None:
    return db.query(DiscoveryJob).filter(DiscoveryJob.id == job_id).first()

def get_job_leads(db: Session, job_id: UUID) -> List[DiscoveryLead]:
    return (
        db.query(DiscoveryLead)
        .filter(DiscoveryLead.job_id == job_id)
        .order_by(DiscoveryLead.rank)
        .all()
    )