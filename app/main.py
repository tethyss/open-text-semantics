"""开放文本语义理解平台的 API 入口与基线推理服务。"""
from collections import Counter
from datetime import datetime, timezone
import re
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Open Text Intelligence Platform", version="1.0.0", docs_url="/api/docs")
STOPWORDS = {"the", "and", "is", "are", "of", "to", "in", "a", "an", "的", "了", "和", "是", "在", "我", "有"}
POSITIVE = {"好", "优秀", "喜欢", "满意", "good", "great", "excellent", "love"}
NEGATIVE = {"差", "糟糕", "讨厌", "失望", "bad", "poor", "hate", "terrible"}

class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10000)
    request_id: str | None = None

class BatchRequest(BaseModel):
    texts: list[str] = Field(min_length=1, max_length=1000)

class TopicRequest(BaseModel):
    texts: list[str] = Field(min_length=2, max_length=10000)
    n_topics: int = Field(default=5, ge=1, le=20)

def tokenize(text: str) -> list[str]:
    parts = re.findall(r"[\u4e00-\u9fff]|[A-Za-z][A-Za-z0-9_-]+", text.lower())
    return [p for p in parts if p not in STOPWORDS and len(p.strip()) > 1]

def analyze_text(text: str) -> dict:
    words = tokenize(text)
    counts = Counter(words)
    score = sum(counts[w] for w in POSITIVE) - sum(counts[w] for w in NEGATIVE)
    sentiment = "positive" if score > 0 else "negative" if score < 0 else "neutral"
    return {"language": "zh" if re.search(r"[\u4e00-\u9fff]", text) else "en", "sentiment": {"label": sentiment, "score": score}, "keywords": [{"term": w, "weight": n} for w, n in counts.most_common(10)], "statistics": {"characters": len(text), "tokens": len(words)}, "entities": []}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "semantic-understanding", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/ready")
def ready():
    return {"status": "ready", "model_registry": "baseline", "dependencies": {"storage": "not_required"}}

@app.post("/api/v1/semantic/analyze")
def semantic_analyze(req: TextRequest):
    return {"request_id": req.request_id or str(uuid4()), "result": analyze_text(req.text)}

@app.post("/api/v1/semantic/batch")
def semantic_batch(req: BatchRequest):
    return {"request_id": str(uuid4()), "count": len(req.texts), "results": [analyze_text(t) for t in req.texts]}

@app.post("/api/v1/discovery/topics")
def discover_topics(req: TopicRequest):
    ranked = Counter(w for text in req.texts for w in tokenize(text))
    words = [w for w, _ in ranked.most_common(req.n_topics * 5)]
    topics = [{"topic_id": f"topic-{i + 1:03d}", "keywords": words[i * 5:(i + 1) * 5], "document_count": sum(1 for text in req.texts if any(w in tokenize(text) for w in words[i * 5:(i + 1) * 5]))} for i in range(req.n_topics)]
    return {"request_id": str(uuid4()), "document_count": len(req.texts), "topics": topics}
