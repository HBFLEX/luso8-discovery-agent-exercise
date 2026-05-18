"""
Entry point for invoking the agent
Author: Happy Banda
"""

from functools import lru_cache
from typing import Any

# Am using groq for the exercise but we can switch to the preferred model
from langchain_groq import ChatGroq

from app.agent.graph import build_graph
from app.agent.state import JustifiedLead
from app.config import get_settings
from app.seed import SEED_LEADS


@lru_cache
def _compiled_graph():
    settings = get_settings()
    llm = ChatGroq(
        model=settings.llm_model,
        temperature=0,
        max_tokens=2048,
        api_key=settings.groq_api_key # type: ignore[arg-type]
    )

    return build_graph(llm)

def run_discovery(
        *,
        business_description: str,
        target_market: str,
        buyer_types: list[str],
        max_results: int,
) -> list[JustifiedLead]:
    graph = _compiled_graph()
    result: dict[str, Any] = graph.invoke({
        "business_description": business_description,
        "target_market": target_market,
        "buyer_types": buyer_types,
        "max_results": max_results,
        "all_leads": SEED_LEADS,
        "filtered_candidates": [],
        "scored_candidates": [],
        "top_candidates": [],
        "justified_leads": [],
        "retry_count": 0,
    })
    return result["justified_leads"]
