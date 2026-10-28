import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

NUM_QUESTIONS = int(os.getenv("NUM_QUESTIONS", "5"))
MAX_CV_CHARS = 12000


def get_llm(temperature: float = 0.3):
    """Provider-agnostic chat model. Switch models via .env only."""
    return init_chat_model(
        os.getenv("LLM_MODEL", "claude-haiku-5-5"),
        model_provider=os.getenv("LLM_PROVIDER", "anthropic"),
        temperature=temperature,
    )
