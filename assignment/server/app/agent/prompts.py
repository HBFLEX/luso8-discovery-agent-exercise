"""
LLM Prompts
Author: Happy Banda
"""

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


class LeadScore(BaseModel):
    company_id: str = Field(..., description="Exact ID from seed data, e.g. co_0001")
    fit_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score 0.0-1.0")
    justification: str = Field(
        ...,
        description="1-2 sentences ONLY using facts that exist in the provided seed record (name, category, country, product_focus, profile, size_band, etc.). Never invent information."
    )

SCORING_SYSTEM_PROMPT = """You are an expert lead qualification analyst for Luso8 Cloud.

Your ONLY job is to score companies. 

STRICT RULES - FOLLOW EXACTLY:
- NEVER output any thinking, explanation, <think>, or markdown.
- Return ONLY a single valid JSON object.
- Do NOT add any text before or after the JSON.
- Use exactly these field names: "company_id", "fit_score", "justification".
- "fit_score" must be a number between 0.0 and 1.0.
- "justification" must be 1-2 short sentences using ONLY facts from the Seed Record.

Seed Record:
{seed_record}

User Request:
Business Description: {business_description}
Target Market: {target_market}
Buyer Types: {buyer_types}
"""

scoring_prompt = ChatPromptTemplate([
    ("system", SCORING_SYSTEM_PROMPT),
    ("human", "Score this company and return only the JSON object.")
])

