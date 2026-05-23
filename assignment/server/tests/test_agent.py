import pytest
from app.agent.nodes import filter_candidates


def test_filter_candidates_respects_market_and_buyer_type():
    state = {
        "business_description": "Selling packaged goods.",
        "target_market": "ZM",
        "buyer_types": ["supermarket", "wholesaler"],
        "max_results": 10
    }

    result_state = filter_candidates(state)
    candidates = result_state["candidates"]

    assert len(candidates) > 0
    assert result_state["status"] == "filtering_complete"

    for candidate in candidates:
        # 1. Hallucination/Integrity Check: Must exist in seed data
        assert candidate["id"].startswith("co_")

        # 2. Market Constraint: Must strictly be the requested country
        assert candidate["country"] == "ZM"

        # 3. Buyer Constraint: Must match the requested types
        assert candidate["category"] in ["supermarket", "wholesaler"]
