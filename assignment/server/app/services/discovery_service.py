"""
    Author: Happy Banda
"""

import logging
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.agent.runner import run_discovery
from app.models import DiscoveryJob, DiscoveryLead, JobStatus
from app.schemas import DiscoveryRequest

log = logging.getLogger(__name__)

def create_and_run_job(db: Session, request: DiscoveryRequest) -> DiscoveryJob:
    """Create a job row, run the agent synchronously, persist leads."""
    job = DiscoveryJob(
        status=JobStatus.RUNNING,
        business_description=request.business_description,
        target_market=request.target_market,
        buyer_types=list(request.buyer_types),
        max_results=request.max_results,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    try:
        leads = run_discovery(
            business_description=request.business_description,
            target_market=request.target_market,
            buyer_types=list(request.buyer_types),
            max_results=request.max_results
        )

        for rank, lead in enumerate(leads, start=1):
            db.add(DiscoveryLead(
                job_id=job.id,
                rank=rank,
                seed_id=lead.seed_id,
                name=lead.name,
                country=lead.country,
                category=lead.category,
                score=lead.score,
                justification=lead.justification,
                grounded=lead.grounded,
            ))
        job.status = JobStatus.DONE
        job.finished_at = datetime.now(timezone.utc)

    except Exception as e:
        log.exception("Discovery job failed: job_id=%s", job.id)
        job.status = JobStatus.FAILED
        job.error_message = str(e)[:500]
        job.finished_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(job)
    return job