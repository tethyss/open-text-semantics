# 开放文本语义理解与分析系统

一个面向开放文本的语义分析原型，提供文本分析、关键词提取、情感判断和批量主题发现接口，并附带一个轻量网页演示页。

## 快速运行

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

打开 http://127.0.0.1:8000 。API 文档位于 `/docs`。

## 接口

- `POST /api/analyze`：单文本语言识别、情感倾向、关键词
- `POST /api/topics`：多文本高频语义主题原型
- `GET /health`：健康检查

## 后续扩展

可将 `analyze()` 和 `/api/topics` 中的规则/统计实现替换为 Hugging Face Transformers、Sentence-BERT、BERTopic 或自训练模型；同时补充向量数据库、异步任务队列、用户鉴权和评测集。
