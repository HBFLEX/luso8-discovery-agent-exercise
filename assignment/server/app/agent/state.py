"""
Discovery Agent Lang-Graph State Schema
Author: Happy Banda
"""

from typing import Any
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class ScoredLead(BaseModel):
    id: str
    score: float = Field(ge=0.0, le=1.0)
    reason_short: str


class JustifiedLead(BaseModel):
    seed_id: str
    name: str
    country: str
    category: str
    score: float
    justification: str
    grounded: bool = True


class DiscoveryState(TypedDict):
    business_description: str
    target_market: str
    buyer_types: list[str]
    max_results: int
    all_leads: list[dict[str, Any]]

    filtered_candidates: list[dict[str, Any]]
    scored_candidates: list[ScoredLead]
    top_candidates: list[dict[str, Any]]

    justified_leads: list[JustifiedLead]
    retry_count: int


