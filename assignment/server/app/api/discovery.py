"""
    Discovery Endpoints
    Author: Happy Banda
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.schemas import DiscoveryRequest, JobStatus, DiscoveryResult
from app.services.discovery_service import (
    create_discovery_job,
    run_and_save_discovery_job,
    get_job_status,
    get_job_leads
)

router = APIRouter(prefix="/api", tags=["discovery"])

@router.post("/discovery", response_model=JobStatus, status_code=status.HTTP_201_CREATED)
async def start_discovery(request: DiscoveryRequest, db: Session = Depends(get_db)):
    job = create_discovery_job(db, request)

    try:
        run_and_save_discovery_job(db, job)
    except Exception as e:
        job.status = "failed"
        db.commit()
        raise HTTPException(
            status_code=500,
            detail=f"Agent failed: {str(e)}"
        ) from e

    return JobStatus(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )

@router.get("/discovery/{job_id}", response_model=JobStatus)
async def get_discovery_status(job_id: UUID, db: Session = Depends(get_db)):
    job = get_job_status(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatus(
        job_id=job.id,
        status=job.status,
        created_at=job.created_at,
        finished_at=job.finished_at,
    )

@router.get("/discovery/{job_id}/leads", response_model=DiscoveryResult)
async def get_discovery_leads(job_id: UUID, db: Session = Depends(get_db)):
    job = get_job_status(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "done":
        raise HTTPException(
            status_code=400,
            detail="Job is still running or failed. Status: " + job.status
        )

    leads = get_job_leads(db, job_id)

    return DiscoveryResult(
        job_id=job.id,
        leads=[
            {
                "id": lead.id,
                "name": lead.name,
                "category": lead.category,
                "country": lead.country,
                "headquarters_city": lead.headquarters_city,
                "fit_score": lead.fit_score,
                "justification": lead.justification,
                "rank": lead.rank,
            }
            for lead in leads
        ],
    )

@router.get("/healthz")
def health_check():
    return { "status": "ok" }

