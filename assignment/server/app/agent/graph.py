"""
Discovery Graph
Author: Happy Banda
"""

from langchain_core.language_models import BaseChatModel
from langgraph.graph import StateGraph, END, START

from app.agent.nodes import (
    filter_candidates,
    make_justify_leads,
    make_score_candidates,
    select_top_n,
    should_retry,
    validate_grounding
)

from app.agent.state import DiscoveryState


def build_graph(llm: BaseChatModel):
    builder = StateGraph(DiscoveryState)
    builder.add_node("filter", filter_candidates)
    builder.add_node("score", make_score_candidates(llm))
    builder.add_node("select_top", select_top_n)
    builder.add_node("justify", make_justify_leads(llm))
    builder.add_node("validate", validate_grounding)

    builder.add_edge(START, "filter")
    builder.add_edge("filter", "score")
    builder.add_edge("score", "select_top")
    builder.add_edge("select_top", "justify")
    builder.add_edge("justify", "validate")
    builder.add_conditional_edges(
        "validate",
        should_retry,
        { "retry": "justify", "done": END },
    )

    return builder.compile()


