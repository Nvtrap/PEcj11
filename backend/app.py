import logging
import os
from typing import List, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

import faiss
import numpy as np
from openai import OpenAI

from .rag_index import (
    load_index,
    search_similar,
    keyword_search,
    answer_from_context,
    to_context_dict,
)


load_dotenv()
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set. Please set it in your environment or in a .env file.")

client_kwargs = {"api_key": OPENAI_API_KEY}
openai_base_url = os.getenv("OPENAI_BASE_URL")
if openai_base_url:
    client_kwargs["base_url"] = openai_base_url

client = OpenAI(**client_kwargs)

app = FastAPI(title="FAQ RAG Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    context: List[Dict[str, Any]]


INDEX_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faiss_index.bin")
META_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "faqs_metadata.npy")
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")

faiss_index, metadata = load_index(INDEX_PATH, META_PATH)


def embed_text(texts: List[str]) -> np.ndarray:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )
    vectors = [d.embedding for d in response.data]
    return np.array(vectors, dtype="float32")


def find_similar_items(message: str, top_k: int) -> List[Any]:
    try:
        query_vec = embed_text([message])
        return search_similar(faiss_index, metadata, query_vec, k=top_k)
    except Exception as exc:
        logger.warning("OpenAI embeddings unavailable, using keyword search: %s", exc)
        return keyword_search(metadata, message, k=top_k)


def generate_answer(message: str, similar_items: List[Any]) -> str:
    context_text = "\n\n".join(
        [f"Q: {item['question']}\nA: {item['answer']}" for item in similar_items]
    )

    system_prompt = (
        "Ты FAQ-ассистент компании. Отвечай кратко и по делу на русском языке. "
        "Используй предоставленный контекст с вопросами и ответами. "
        "Если в контексте нет нужной информации, скажи, что не уверен и предложи связаться с поддержкой."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Вопрос пользователя: {message}\n\nКонтекст FAQ:\n{context_text}"},
    ]

    try:
        completion = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            temperature=0.2,
        )
        return completion.choices[0].message.content
    except Exception as exc:
        logger.warning("OpenAI chat unavailable, returning context answer: %s", exc)
        return answer_from_context(similar_items)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message is empty")

    similar_items = find_similar_items(req.message, req.top_k)
    answer = generate_answer(req.message, similar_items)

    return ChatResponse(
        answer=answer,
        context=[to_context_dict(item) for item in similar_items],
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

