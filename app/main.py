from collections import Counter
from pathlib import Path
import re

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Open Text Semantic Understanding API", version="0.1.0")

STOPWORDS = {"the", "and", "is", "are", "of", "to", "in", "a", "an", "的", "了", "和", "是", "在", "我", "有"}


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)


class TopicRequest(BaseModel):
    texts: list[str] = Field(min_length=2, max_length=100)
    n_topics: int = Field(default=3, ge=1, le=10)


def tokens(text: str) -> list[str]:
    parts = re.findall(r"[\u4e00-\u9fff]|[A-Za-z][A-Za-z0-9_-]+", text.lower())
    return [p for p in parts if p not in STOPWORDS and len(p.strip()) > 1]


def analyze(text: str) -> dict:
    words = tokens(text)
    counts = Counter(words)
    positive = {"好", "优秀", "喜欢", "满意", "good", "great", "excellent", "love"}
    negative = {"差", "糟糕", "讨厌", "失望", "bad", "poor", "hate", "terrible"}
    score = sum(counts[w] for w in positive) - sum(counts[w] for w in negative)
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"language": "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en", "sentiment": sentiment,
            "sentiment_score": score, "keywords": [w for w, _ in counts.most_common(10)],
            "token_count": len(words), "entities": []}


@app.get("/", response_class=HTMLResponse)
def home():
    return (Path(__file__).parent / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/api/analyze")
def api_analyze(req: TextRequest):
    return analyze(req.text)


@app.post("/api/topics")
def api_topics(req: TopicRequest):
    ranked = Counter(w for text in req.texts for w in tokens(text))
    words = [w for w, _ in ranked.most_common(req.n_topics * 5)]
    return {"topics": [{"id": i + 1, "keywords": words[i * 5:(i + 1) * 5]} for i in range(req.n_topics)]}
