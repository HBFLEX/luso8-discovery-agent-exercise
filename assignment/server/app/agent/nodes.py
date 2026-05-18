"""
Graph Nodes
Author: Happy Banda
"""

import re
from typing import Any

from anyio.streams import file
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel

from app.agent.prompts import (
    JUSTIFICATION_SYSTEM_PROMPT,
    SCORING_SYSTEM_PROMPT,
    JUSTIFICATION_RETRY_HINT
)

from app.agent.state import DiscoveryState, JustifiedLead, ScoredLead


# LLM Structured output guiding

class _ScoringResult(BaseModel):
    scores: list[ScoredLead]


class _JustificationResult(BaseModel):
    justification: str

# Nodes

def filter_candidates(state: DiscoveryState) -> dict[str, Any]:
    """Deterministic filter by country and buyer category."""
    market = state["target_market"]
    buyer_types = set(state["buyer_types"])

    filtered = [
        lead for lead in state["all_leads"]
        if lead["country"] == market and lead["category"] in buyer_types
    ]
    return { "filtered_candidates": filtered }

def make_score_candidates(llm: BaseChatModel):
    """Closure pattern: bind the LLM once, return the node function.

    This keeps the LLM out of the global namespace and makes the node
    trivially testable by passing a fake model.
    """
    scorer = llm.with_structured_output(_ScoringResult)

    def score_candidates(state: DiscoveryState) -> dict[str, Any]:
        candidates = state["filtered_candidates"]
        if not candidates:
            return {"scored_candidates": []}

        lines = "\n".join(
            f"- id={c['id']} | {c['name']} | category={c['category']} | "
            f"size={c['size_band']} | focus={c['product_focus']} | profile={c['profile']}"
            for c in candidates
        )
        user_msg = (
            f"Business description:\n{state['business_description']}\n\n"
            f"Candidates:\n{lines}\n\n"
            "Score every candidate. Return one score object per id."
        )
        result = scorer.invoke([
            SystemMessage(content=SCORING_SYSTEM_PROMPT),
            HumanMessage(content=user_msg),
        ])
        return {"scored_candidates": result.scores} # type: ignore[union-attr]

    return score_candidates

def select_top_n(state: DiscoveryState) -> dict[str, Any]:
    """Deterministic top-N selection."""
    scored = state["scored_candidates"]
    by_id = {c["id"]: c for c in state["filtered_candidates"]}
    top = sorted(scored, key=lambda s: s.score, reverse=True)[: state["max_results"]]
    enriched = [{**by_id[s.id], "score": s.score} for s in top if s.id in by_id]
    return {"top_candidates": enriched}

def make_justify_leads(llm: BaseChatModel):
    justifier = llm.with_structured_output(_JustificationResult)

    def justify_leads(state: DiscoveryState) -> dict[str, Any]:
        retry = state.get("retry_count", 0) > 0
        system = JUSTIFICATION_SYSTEM_PROMPT + (JUSTIFICATION_RETRY_HINT if retry else "")
        results: list[JustifiedLead] = []

        for lead in state["top_candidates"]:
            user_msg = (
                f"Business description:\n{state['business_description']}\n\n"
                "Seed record (the ONLY company you may discuss):\n"
                f"- name: {lead['name']}\n"
                f"- country: {lead['country']}\n"
                f"- category: {lead['category']}\n"
                f"- size_band: {lead['size_band']}\n"
                f"- product_focus: {lead['product_focus']}\n"
                f"- profile: {lead['profile']}\n\n"
                "Write the justification paragraph."
            )
            result = justifier.invoke([
                SystemMessage(content=system),
                HumanMessage(content=user_msg),
            ])
            results.append(JustifiedLead(
                seed_id=lead["id"],
                name=lead["name"],
                country=lead["country"],
                category=lead["category"],
                score=lead["score"],
                justification=result.justification,  # type: ignore[union-attr]
            ))
        return {"justified_leads": results}

    return justify_leads

# Guard hallucinations
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_MIN_TOKEN_LEN = 3

# Generic vocabulary the model may use without grounding.
_STOPWORDS: frozenset[str] = frozenset({
    "the", "and", "for", "with", "this", "that", "their", "they", "are", "has", "have",
    "would", "could", "should", "from", "into", "your", "you", "our", "company", "business",
    "product", "products", "lead", "leads", "fit", "good", "strong", "match", "potential",
    "customer", "customers", "buyer", "buyers", "market", "category", "size", "focus",
    "profile", "based", "given", "makes", "make", "due", "ideal", "well", "very", "across",
    "specifically", "particularly", "which", "where", "while", "also", "both", "more",
    "distributor", "wholesaler", "supermarket", "horeca", "retail", "retailer", "retailers",
    "small", "medium", "large", "national", "regional", "local",
})

def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) >= _MIN_TOKEN_LEN}

def validate_grounding(state: DiscoveryState) -> dict[str, Any]:
    """Flag justifications that introduce tokens not present in the seed record.

    A deterministic check is intentional: asking another LLM to validate output
    just multiplies the hallucination surface area.
    """
    seed_by_id = {c["id"]: c for c in state["filtered_candidates"]}
    business_tokens = _tokens(state["business_description"])

    validated: list[JustifiedLead] = []
    any_failed = False

    for lead in state["justified_leads"]:
        seed = seed_by_id.get(lead.seed_id, {})
        allowed = (
            _tokens(seed.get("name", ""))
            | _tokens(seed.get("size_band", ""))
            | _tokens(seed.get("product_focus", ""))
            | _tokens(seed.get("profile", ""))
            | business_tokens
            | _STOPWORDS
        )
        ungrounded = _tokens(lead.justification) - allowed
        grounded = not ungrounded
        if not grounded:
            any_failed = True
        validated.append(lead.model_copy(update={"grounded": grounded}))

    return {
        "justified_leads": validated,
        "retry_count": state.get("retry_count", 0) + (1 if any_failed else 0),
    }


def should_retry(state: DiscoveryState) -> str:
    any_failed = any(not l.grounded for l in state["justified_leads"])
    if any_failed and state.get("retry_count", 0) <= 1:
        return "retry"
    return "done"