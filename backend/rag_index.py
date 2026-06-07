import json
import os
import re
from typing import List, Tuple, Any

import faiss
import numpy as np


def read_faiss_index(index_path: str) -> faiss.IndexFlatL2:
    """Load FAISS index via Python I/O (faiss.read_index fails on non-ASCII paths on Windows)."""
    with open(index_path, "rb") as f:
        data = f.read()
    return faiss.deserialize_index(np.frombuffer(data, dtype=np.uint8))


def write_faiss_index(index: faiss.IndexFlatL2, index_path: str) -> None:
    """Save FAISS index via Python I/O (faiss.write_index fails on non-ASCII paths on Windows)."""
    data = faiss.serialize_index(index)
    with open(index_path, "wb") as f:
        f.write(data)


def load_index(index_path: str, meta_path: str) -> Tuple[faiss.IndexFlatL2, np.ndarray]:
    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        raise RuntimeError(
            "FAISS index or metadata not found. "
            "Run `python backend/build_index.py` first to build the RAG index."
        )

    index = read_faiss_index(index_path)
    metadata = np.load(meta_path, allow_pickle=True)
    return index, metadata


def search_similar(
    index: faiss.IndexFlatL2,
    metadata: np.ndarray,
    query_vec: np.ndarray,
    k: int = 3,
) -> List[Any]:
    distances, indices = index.search(query_vec, k)
    idxs = indices[0]
    results = []
    for i in idxs:
        if 0 <= i < len(metadata):
            results.append(metadata[i])
    return results


def keyword_search(metadata: np.ndarray, query: str, k: int = 3) -> List[Any]:
    """Fallback search without OpenAI embeddings (keyword overlap)."""
    query_lower = query.lower()
    words = [w for w in re.findall(r"\w+", query_lower) if len(w) > 2]

    scored = []
    for item in metadata:
        text = f"{item['question']} {item['answer']}".lower()
        score = sum(text.count(word) for word in words)
        if query_lower in item["question"].lower():
            score += 5
        scored.append((score, item))

    scored.sort(key=lambda pair: (-pair[0], pair[1]["question"]))
    results = [item for score, item in scored if score > 0][:k]
    if results:
        return results
    return [metadata[i] for i in range(min(k, len(metadata)))]


def answer_from_context(items: List[Any]) -> str:
    if not items:
        return (
            "Не нашёл информации в базе знаний. "
            "Пожалуйста, свяжитесь с поддержкой."
        )
    if len(items) == 1:
        return items[0]["answer"]
    return items[0]["answer"]


def to_context_dict(item: Any) -> dict:
    return {
        "question": item["question"],
        "answer": item["answer"],
        "source": item.get("source", "unknown"),
    }


def load_faq_data(path: str):
    """Загружает FAQ данные из JSON файла."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


