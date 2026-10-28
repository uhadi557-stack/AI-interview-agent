"""LangGraph workflow that handles ONE answer turn.

answer -> evaluate -> (weak and not already a follow-up?) -> follow_up -> END
                                   otherwise              -> END (advance)
"""
from typing import TypedDict

from langgraph.graph import END, StateGraph

from .interviewer import evaluate_answer, generate_followup
from .scoring import WEAK_THRESHOLD, answer_score


class TurnState(TypedDict, total=False):
    question: str
    answer: str
    is_followup: bool
    profile_json: str
    job_prefs: str
    evaluation: dict
    score: float
    next_action: str  # "followup" or "advance"
    followup_question: str


def evaluate_node(state: TurnState) -> TurnState:
    ev = evaluate_answer(
        state["question"], state["answer"], state["profile_json"], state["job_prefs"]
    ).model_dump()
    return {"evaluation": ev, "score": answer_score(ev)}


def route(state: TurnState) -> str:
    weak = state["score"] < WEAK_THRESHOLD
    return "follow_up" if weak and not state["is_followup"] else "advance"


def follow_up_node(state: TurnState) -> TurnState:
    q = generate_followup(
        state["question"], state["answer"], state["evaluation"]["feedback"]
    )
    return {"next_action": "followup", "followup_question": q}


def advance_node(state: TurnState) -> TurnState:
    return {"next_action": "advance"}


def build_graph():
    g = StateGraph(TurnState)
    g.add_node("evaluate", evaluate_node)
    g.add_node("follow_up", follow_up_node)
    g.add_node("advance", advance_node)
    g.set_entry_point("evaluate")
    g.add_conditional_edges("evaluate", route, {"follow_up": "follow_up", "advance": "advance"})
    g.add_edge("follow_up", END)
    g.add_edge("advance", END)
    return g.compile()


turn_graph = build_graph()
