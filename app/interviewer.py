import json
from typing import Type

from langchain_core.prompts import ChatPromptTemplate

from . import prompts
from .config import MAX_CV_CHARS, get_llm
from .schemas import (
    AnswerEvaluation,
    CandidateProfile,
    FinalReport,
    FollowUp,
    QuestionList,
)


def _run(system: str, human: str, schema: Type, temperature: float = 0.3, **variables):
    prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])
    chain = prompt | get_llm(temperature).with_structured_output(schema)
    return chain.invoke(variables)


def analyze_cv(cv_text: str, job_prefs: str) -> CandidateProfile:
    return _run(
        prompts.ANALYZE_SYSTEM,
        prompts.ANALYZE_HUMAN,
        CandidateProfile,
        temperature=0.0,
        cv_text=cv_text[:MAX_CV_CHARS],
        job_prefs=job_prefs or "none",
    )


def generate_questions(profile: CandidateProfile, job_prefs: str, n: int) -> list[str]:
    result = _run(
        prompts.QUESTIONS_SYSTEM,
        prompts.QUESTIONS_HUMAN,
        QuestionList,
        temperature=0.7,
        n=n,
        profile=profile.model_dump_json(indent=2),
        job_prefs=job_prefs or "none",
    )
    return result.questions[:n]


def evaluate_answer(question: str, answer: str, profile_json: str, job_prefs: str) -> AnswerEvaluation:
    return _run(
        prompts.EVAL_SYSTEM,
        prompts.EVAL_HUMAN,
        AnswerEvaluation,
        temperature=0.0,
        profile=profile_json,
        job_prefs=job_prefs or "none",
        question=question,
        answer=answer or "(no answer)",
    )


def generate_followup(question: str, answer: str, feedback: str) -> str:
    result = _run(
        prompts.FOLLOWUP_SYSTEM,
        prompts.FOLLOWUP_HUMAN,
        FollowUp,
        temperature=0.5,
        question=question,
        answer=answer,
        feedback=feedback,
    )
    return result.question


def final_report(results: list[dict]) -> FinalReport:
    compact = [
        {
            "question": r["question"],
            "score": round(r["score"]),
            "feedback": r["evaluation"]["feedback"],
        }
        for r in results
    ]
    return _run(
        prompts.REPORT_SYSTEM,
        prompts.REPORT_HUMAN,
        FinalReport,
        temperature=0.3,
        results=json.dumps(compact, indent=2),
    )
