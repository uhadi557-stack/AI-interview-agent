# AI Speaking Interview Agent

Upload a CV, answer interview questions out loud, and get a rubric-based score per answer plus an overall percentage.

## Features
- CV analysis (PDF/text) into a structured profile
- Personalised questions: CV-claim probes, technical, behavioural
- Voice in/out via the browser (Web Speech API)
- Rubric scoring: technical accuracy, relevance, depth, structure, clarity (weighted)
- LangGraph turn workflow: weak answers trigger one follow-up question
- Stronger model answer for weak responses
- Delivery metrics: words per minute, filler words
- Final report: overall %, dimension breakdown, strengths, weaknesses, practice plan

## Setup (Windows)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then add your API key
uvicorn app.main:app --reload
```
Open http://127.0.0.1:8000 in Chrome or Edge.

## Architecture
```
Browser (mic + speakers) --> FastAPI --> CV parser --> LLM (profile, questions)
                                  \--> LangGraph turn: evaluate -> follow_up | advance
                                  \--> scoring (weights, delivery) --> final report
```

## Limitations
- Sessions are in memory (lost on restart)
- Voice recognition uses the browser's service (Chrome sends audio to Google)
- Scores are LLM-based; validate them against human ratings before trusting them
