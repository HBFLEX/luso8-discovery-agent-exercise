"""
    API Contracts & response models
    Author: Happy Banda
"""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Literal, List


class DiscoveryRequest(BaseModel):
    business_description: str = Field(
        ...,
        min_length=20,
        max_length=500,
        description="Description of your business and what you sell"
    )
    target_market: Literal["ZM", "KE", "TZ", "NG", "ZA"] = Field(
        ..., description="Target country (ISO code)"
    )
    buyer_types: List[Literal[
        "distributor", "supermarket", "horeca", "wholesaler",
        "online_retailer", "food_processor", "convenience_chain", "logistics"
    ]] = Field(
        ...,
        min_length=1,
        description="Types of buyers you want to target"
    )
    max_results: int = Field(10, ge=1, le=50)

    @field_validator("buyer_types")
    @classmethod
    def validate_buyer_types(cls, v: List[str]) -> List[str]:
        return list(dict.fromkeys(v))


class JobStatus(BaseModel):
    job_id: UUID
    status: str
    created_at: datetime
    finished_at: datetime | None = None


class LeadOut(BaseModel):
    id: UUID
    name: str
    category: str
    country: str
    headquarters_city: str
    fit_score: float = Field(..., ge=0.0, le=1.0)
    justification: str
    rank: int

class DiscoveryResult(BaseModel):
    job_id: UUID
    leads: List[LeadOut]
    
