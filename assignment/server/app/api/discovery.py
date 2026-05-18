"""
    Discovery API Routes
    Author: Happy Banda
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DiscoveryJob, JobStatus
from app.schemas import (
    DiscoveryRequest,
    JobCreatedResponse,
    JobStatusResponse,
    LeadResponse,
    LeadsResponse
)

from app.services.discovery_service import create_and_run_job

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


@router.post("", response_model=JobCreatedResponse, status_code=status.HTTP_201_CREATED)
def create_discovery(
        request: DiscoveryRequest,
        db: Session = Depends(get_db),
) -> JobCreatedResponse:
    job = create_and_run_job(db, request)
    return JobCreatedResponse(job_id=job.id, status=job.status.value)

@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job(
        job_id: str, db: Session = Depends(get_db)
) -> JobStatusResponse:
    job = db.get(DiscoveryJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return JobStatusResponse(
        job_id=job.id,
        status=job.status.value,
        created_at=job.created_at,
        finished_at=job.finished_at,
        error_message=job.error_message,
    )

@router.get("/{job_id}/leads", response_model=LeadsResponse)
def get_leads(job_id: str, db: Session = Depends(get_db)) -> LeadsResponse:
    job = db.get(DiscoveryJob, job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    if job.status != JobStatus.DONE:
        return LeadsResponse(job_id=job.id, status=job.status.value, leads=[])
    return LeadsResponse(
        job_id=job.id,
        status=job.status.value,
        leads=[LeadResponse.model_validate(lead) for lead in job.leads],
    )