from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .config import NUM_QUESTIONS
from .cv_parser import extract_text
from .graph import turn_graph
from .interviewer import analyze_cv, final_report, generate_questions
from .scoring import aggregate, delivery_metrics
from .session_store import create_session, get_session

BASE_DIR = Path(__file__).resolve().parent.parent
MAX_UPLOAD_BYTES = 5 * 1024 * 1024

app = FastAPI(title="AI Speaking Interview Agent")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "static" / "index.html")


@app.post("/api/start")
def start_interview(cv: UploadFile = File(...), job_prefs: str = Form("")):
    data = cv.file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "CV is too large (max 5 MB).")
    text = extract_text(data, cv.filename or "cv.txt")
    if len(text) < 200:
        raise HTTPException(400, "Could not read enough text from the CV. Use a text-based PDF.")

    profile = analyze_cv(text, job_prefs)
    questions = generate_questions(profile, job_prefs, NUM_QUESTIONS)
    if not questions:
        raise HTTPException(502, "Could not generate questions. Try again.")

    session = create_session(profile, job_prefs, questions)
    return {
        "session_id": session.id,
        "profile": profile.model_dump(),
        "question": session.current_question,
        "question_number": 1,
        "total_questions": len(questions),
    }


class AnswerIn(BaseModel):
    session_id: str
    answer: str
    duration_seconds: float = 0


@app.post("/api/answer")
def submit_answer(body: AnswerIn):
    s = get_session(body.session_id)
    if not s:
        raise HTTPException(404, "Session not found.")
    if s.report is not None:
        raise HTTPException(400, "Interview already finished.")

    out = turn_graph.invoke(
        {
            "question": s.current_question,
            "answer": body.answer.strip(),
            "is_followup": s.current_is_followup,
            "profile_json": s.profile.model_dump_json(),
            "job_prefs": s.job_prefs,
        }
    )

    s.results.append(
        {
            "question": s.current_question,
            "answer": body.answer.strip(),
            "is_followup": s.current_is_followup,
            "evaluation": out["evaluation"],
            "score": out["score"],
            "delivery": delivery_metrics(body.answer, body.duration_seconds),
        }
    )

    response = {
        "score": out["score"],
        "evaluation": out["evaluation"],
        "delivery": s.results[-1]["delivery"],
        "finished": False,
    }

    if out["next_action"] == "followup":
        s.current_question = out["followup_question"]
        s.current_is_followup = True
        response.update(question=s.current_question, is_followup=True)
        return response

    s.index += 1
    s.current_is_followup = False
    if s.index >= len(s.questions):
        numbers = aggregate(s.results)
        report = final_report(s.results)
        s.report = {**numbers, **report.model_dump()}
        response.update(finished=True, report=s.report)
        return response

    s.current_question = s.questions[s.index]
    response.update(
        question=s.current_question,
        is_followup=False,
        question_number=s.index + 1,
        total_questions=len(s.questions),
    )
    return response
