"""
Models for request validations and serialization
Author: Happy Banda
"""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

SUPPORTED_MARKETS = {"ZM", "TZ", "KE", "NG", "ZA"}
BuyerType = Literal["distributor", "wholesaler", "supermarket", "horeca"]


class DiscoveryRequest(BaseModel):
    business_description: str = Field(..., min_length=10, max_length=2000)
    target_market: str = Field(..., min_length=2, max_length=2)
    buyer_types: list[BuyerType] = Field(..., min_length=1, max_length=4)
    max_results: int = Field(default=10, ge=1, le=50)

    def model_post_init(self, _context: object) -> None:
        market = self.target_market.upper()
        if market not in SUPPORTED_MARKETS:
            raise ValueError(
                f"Unsupported market '{self.target_market}'"
                f"Must be one of: {sorted(SUPPORTED_MARKETS)}"
            )
        object.__setattr__(self, "target_market", market)


class JobCreatedResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    created_at: datetime
    finished_at: datetime | None
    error_message: str | None


class LeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int
    seed_id: int
    name: str
    country: str
    category: str
    score: float
    justification: str
    grounded: bool


class LeadsResponse(BaseModel):
    job_id: str
    status: str
    leads: list[LeadResponse]

