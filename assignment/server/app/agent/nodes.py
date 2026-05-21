"""
    Agent Nodes
    Author: Happy Banda
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from langchain_groq import ChatGroq
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableConfig

from app.agent.prompts import scoring_prompt, LeadScore
from app.config import get_settings

settings = get_settings()

_SEED_DATA: List[Dict[str, Any]] | None = None

def load_seed_data() -> List[Dict[str, Any]]:
    """ Loads leads_seed.json - called only once """
    global _SEED_DATA
    if _SEED_DATA is None:
        seed_path = Path(__file__).parent.parent.parent / "data" / "leads_seed.json"
        with open(seed_path, encoding="utf-8") as f:
            _SEED_DATA = json.load(f)
    return _SEED_DATA

def filter_candidates(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1: Simple but effective filter based on target market and buyer types.
    This keeps token usage low and makes scoring faster.
    """

    seed = load_seed_data()
    target_market = state["target_market"]
    buyer_types = set(state["buyer_types"])

    candidates = [
        company for company in seed
        if company["country"] == target_market and company["category"] in buyer_types
    ]

    # Fallback: if no exact match, return from target market only
    if not candidates:
        candidates = [
            company for company in seed
            if company["country"] == target_market
        ]

    # Limit to 30 candidate max for performance
    candidates = candidates[:30]
    state["candidates"] = candidates
    state["status"] = "filtering_complete"
    return state

def score_lead(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
    """
    Score each candidate.
    """
    llm = ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.llm_model,
        temperature=0.0,
        max_tokens=500,
    )

    parser = PydanticOutputParser(pydantic_object=LeadScore)
    chain = scoring_prompt | llm | parser

    scored_leads = []
    candidates = state.get("candidates", [])

    print(f"🔥 Scoring {len(candidates)} candidates...")  # debug

    for i, company in enumerate(candidates):
        seed_record_str = json.dumps(company, indent=2, ensure_ascii=False)

        try:
            result: LeadScore = chain.invoke({
                "seed_record": seed_record_str,
                "business_description": state["business_description"],
                "target_market": state["target_market"],
                "buyer_types": ", ".join(state["buyer_types"]),
            }, config=config)

            scored_leads.append({
                "company_id": result.company_id,
                "name": company["name"],
                "category": company["category"],
                "country": company["country"],
                "headquarters_city": company.get("headquarters_city", ""),
                "fit_score": round(result.fit_score, 2),
                "justification": result.justification.strip(),
            })
            print(f"✅ Scored {company['name']} → {result.fit_score}")

        except Exception as e:
            print(f"❌ LLM failed for {company['name']}: {type(e).__name__} - {e}")
            # Fallback
            scored_leads.append({
                "company_id": company["id"],
                "name": company["name"],
                "category": company["category"],
                "country": company["country"],
                "headquarters_city": company.get("headquarters_city", ""),
                "fit_score": 0.2,
                "justification": f"Could not evaluate: {str(e)[:100]}",
            })

    scored_leads.sort(key=lambda x: x["fit_score"], reverse=True)
    state["scored_leads"] = scored_leads[:state.get("max_results", 10)]
    state["status"] = "scoring_complete"
    return state

# def score_lead(state: Dict[str, Any], config: RunnableConfig) -> Dict[str, Any]:
#     """
#     Step 2: Score each candidate using structured output + strict prompt.
#     This is where we prevent hallucinations.
#     """
#     llm = ChatGroq(
#         api_key=settings.groq_api_key,
#         model=settings.llm_model,
#         temperature=0.0,
#         max_tokens=500
#     )
#
#     parser = PydanticOutputParser(pydantic_object=LeadScore)
#     chain = scoring_prompt | llm | parser
#
#     scored_leads = []
#
#     for company in state.get("candidates", []):
#         # format the seed record
#         seed_record_str = json.dumps(company, indent=2, ensure_ascii=False)
#
#         try:
#             result: LeadScore = chain.invoke({
#                 "seed_record": seed_record_str,
#                 "business_description": state["business_description"],
#                 "target_market": state["target_market"],
#                 "buyer_types": ", ".join(state["buyer_types"]),
#             }, config=config)
#
#             scored_leads.append({
#                 "company_id": result.company_id,
#                 "name": company["name"],
#                 "category": company["category"],
#                 "country": company["country"],
#                 "headquarters_city": company.get("headquarters_city", ""),
#                 "fit_score": round(result.fit_score, 2),
#                 "justification": result.justification.strip(),
#             })
#         except Exception as e:
#             # Fallback score if model fails
#             scored_leads.append({
#                 "company_id": company["id"],
#                 "name": company["name"],
#                 "category": company["category"],
#                 "country": company["country"],
#                 "headquarters_city": company.get("headquarters_city", ""),
#                 "fit_score": 0.2,
#                 "justification": "Could not evaluate properly due to technical issue.",
#             })
#
#     # Sort by fit_score descending
#     scored_leads.sort(key=lambda x: x["fit_score"], reverse=True)
#     # Take only the top N selected
#     max_results = state.get("max_results", 10)
#     state["scored_leads"] = scored_leads[:max_results]
#     state["status"] = "scoring_complete"
#
#     return state


__all__ = ["filter_candidates", "score_lead", "load_seed_data"]
