import re

# Rubric weights (sum to 1.0). Tune these and document your choice in the README.
WEIGHTS = {
    "technical_accuracy": 0.30,
    "relevance": 0.20,
    "depth": 0.20,
    "structure": 0.15,
    "clarity": 0.15,
}
WEAK_THRESHOLD = 60  # percent; below this an answer counts as weak

FILLERS = ["um", "uh", "like", "you know", "basically", "actually", "kind of", "sort of"]


def _clamp(value) -> int:
    try:
        return max(0, min(10, int(value)))
    except (TypeError, ValueError):
        return 0


def answer_score(evaluation: dict) -> float:
    """Weighted rubric score as a percentage (0-100)."""
    total = sum(_clamp(evaluation.get(k)) * w for k, w in WEIGHTS.items())
    return round(total * 10, 1)


def delivery_metrics(answer: str, duration_seconds: float) -> dict:
    """Speaking pace and filler words, computed from the transcript."""
    text = answer.lower()
    words = re.findall(r"[a-zA-Z']+", text)
    filler_count = sum(len(re.findall(rf"\b{re.escape(f)}\b", text)) for f in FILLERS)
    wpm = round(len(words) / (duration_seconds / 60)) if duration_seconds >= 5 else None
    return {"word_count": len(words), "filler_count": filler_count, "wpm": wpm}


def aggregate(results: list[dict]) -> dict:
    """Overall percentage + per-dimension averages + delivery summary."""
    if not results:
        return {"overall": 0, "dimensions": {}, "delivery": {}}

    overall = round(sum(r["score"] for r in results) / len(results), 1)
    dimensions = {
        k: round(sum(_clamp(r["evaluation"].get(k)) for r in results) / len(results), 1)
        for k in WEIGHTS
    }
    wpms = [r["delivery"]["wpm"] for r in results if r["delivery"]["wpm"]]
    delivery = {
        "avg_wpm": round(sum(wpms) / len(wpms)) if wpms else None,
        "total_fillers": sum(r["delivery"]["filler_count"] for r in results),
    }
    return {"overall": overall, "dimensions": dimensions, "delivery": delivery}
