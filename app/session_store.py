import uuid
from dataclasses import dataclass, field
from typing import Optional

from .schemas import CandidateProfile


@dataclass
class Session:
    id: str
    profile: CandidateProfile
    job_prefs: str
    questions: list[str]
    index: int = 0
    current_question: str = ""
    current_is_followup: bool = False
    results: list[dict] = field(default_factory=list)
    report: Optional[dict] = None


# In-memory store: fine for a demo. Replace with Redis/SQLite for production.
_SESSIONS: dict[str, Session] = {}


def create_session(profile: CandidateProfile, job_prefs: str, questions: list[str]) -> Session:
    s = Session(
        id=uuid.uuid4().hex,
        profile=profile,
        job_prefs=job_prefs,
        questions=questions,
        current_question=questions[0],
    )
    _SESSIONS[s.id] = s
    return s


def get_session(session_id: str) -> Optional[Session]:
    return _SESSIONS.get(session_id)
