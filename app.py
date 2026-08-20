import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI(title="HR Onboarding Expert")
INDEX_PATH = Path(__file__).with_name("index.html")

SYSTEM_PROMPT = (
    "You are a friendly HR onboarding expert that helps new and current employees. "
    "You answer common questions about onboarding steps, company policies, benefits basics, "
    "time-off, and where to find internal resources, in clear, welcoming, professional language. "
    "Only answer from the policy information the company has provided; if something is unclear, "
    "sensitive, or specific to an individual's situation - such as pay, disputes, or personal "
    "records - direct them to the HR team or the official HR system rather than guessing. Never "
    "invent policies or share personal employee data. Be supportive and concise."
)


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[Message]


@app.get("/")
async def home() -> FileResponse:
    return FileResponse(INDEX_PATH)


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, str]:
    required_settings = ("AZURE_ENDPOINT", "AZURE_DEPLOYMENT", "AZURE_API_KEY")
    placeholder_values = ("paste-your-key", "<your-resource>")
    missing_settings = [
        name
        for name in required_settings
        if not os.environ.get(name)
        or any(value in os.environ[name] for value in placeholder_values)
    ]
    if missing_settings:
        logger.error("Missing required environment settings: %s", ", ".join(missing_settings))
        raise HTTPException(
            status_code=500,
            detail="The HR assistant is not configured yet. Check the server environment settings.",
        )

    try:
        client = OpenAI(
            base_url=os.environ["AZURE_ENDPOINT"],
            api_key=os.environ["AZURE_API_KEY"],
        )
        response = client.chat.completions.create(
            model=os.environ["AZURE_DEPLOYMENT"],
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                *[message.model_dump() for message in request.messages],
            ],
        )
        reply = response.choices[0].message.content
        if not reply:
            raise RuntimeError("The model returned an empty response")
        return {"reply": reply}
    except Exception:
        logger.exception("HR assistant request failed")
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble answering right now. Please try again.",
        )