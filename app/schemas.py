from typing import List

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    name: str = Field(default="", description="Candidate name if present")
    target_role: str = Field(default="", description="Most likely role they are aiming for")
    skills: List[str] = Field(default_factory=list)
    experience_summary: str = Field(description="2-3 sentence summary of experience")
    projects: List[str] = Field(default_factory=list)
    claims_to_verify: List[str] = Field(
        default_factory=list,
        description="Specific CV claims worth probing in an interview",
    )


class QuestionList(BaseModel):
    questions: List[str]


class AnswerEvaluation(BaseModel):
    relevance: int = Field(description="0-10: does it answer the question asked")
    technical_accuracy: int = Field(description="0-10: is the content correct")
    depth: int = Field(description="0-10: specifics, trade-offs, examples")
    structure: int = Field(description="0-10: logical flow, e.g. STAR for behavioral")
    clarity: int = Field(description="0-10: concise, easy to follow when spoken")
    feedback: str = Field(description="Max 3 sentences of direct feedback")
    stronger_answer: str = Field(description="A model answer, 4-6 spoken-style sentences")


class FollowUp(BaseModel):
    question: str


class FinalReport(BaseModel):
    strengths: List[str]
    weaknesses: List[str]
    advice: List[str]
