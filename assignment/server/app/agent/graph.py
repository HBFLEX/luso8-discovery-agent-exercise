"""
Discovery Graph
Author: Happy Banda
"""

from typing import TypedDict, List, Dict, Any
from uuid import UUID, uuid4

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.nodes import filter_candidates, score_lead


class AgentState(TypedDict):
    job_id: UUID
    business_description: str
    target_market: str
    buyer_types: List[str]
    max_results: int

    candidates: List[Dict[str, Any]]
    scored_leads: List[Dict[str, Any]]

    status: str
    error: str | None


def create_discovery_graph():
    workflow =StateGraph(AgentState)
    workflow.add_node("filter", filter_candidates)
    workflow.add_node("score", score_lead)

    workflow.add_edge(START, "filter")
    workflow.add_edge("filter", "score")
    workflow.add_edge("score", END)

    # using to in-memory checkpoint for now - #TODO i will switch to postgresql later
    memory = MemorySaver()

    graph = workflow.compile(checkpointer=memory)
    return graph

# Singleton graph instance
discovery_graph = create_discovery_graph()


def run_discovery_graph(
        business_description: str,
        target_market: str,
        buyer_types: List[str],
        max_results: int = 10,
        thread_id: str | None = None,
) -> Dict[str, Any]:
    if thread_id is None:
        thread_id = str(uuid4())

    initial_state: AgentState = {
        "job_id": uuid4(),
        "business_description": business_description,
        "target_market": target_market,
        "buyer_types": buyer_types,
        "max_results": max_results,
        "candidates": [],
        "scored_leads": [],
        "status": "queued",
        "error": None,
    }

    final_state = discovery_graph.invoke(
        initial_state,
        config={ "configurable": { "thread_id": thread_id } },
    )

    return final_state

