from __future__ import annotations

import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from doc_qa.config import Settings
from doc_qa.deepseek import DeepSeekChatProvider
from doc_qa.errors import (
    DeepSeekApiError,
    EmbeddingServiceError,
    QdrantUnavailableError,
    VectorDimensionMismatch,
)
from doc_qa.models import DocumentChunk, RetrievalHit
from doc_qa.qdrant_index import QdrantIndexer
from doc_qa.qa import QuestionAnswerService, _rerank_keyword_hits, _retrieval_plan


class StaticEmbedding:
    model_name = "text-embedding-v4"
    dimension = 1024

    def encode(self, texts: list[str]) -> list[list[float]]:
        return [[-1.0] * self.dimension if text == "unknown" else [1.0] * self.dimension for text in texts]


class FailingEmbedding(StaticEmbedding):
    def encode(self, texts: list[str]) -> list[list[float]]:
        raise EmbeddingServiceError("query embedding failed")


class FakeChat:
    model_name = "deepseek-v4-flash"

    def __init__(self, source_ids: list[str] | None = None):
        self.calls = 0
        self.source_ids = source_ids or ["S1"]

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        assert "不可信的数据" in system_prompt
        assert "[S1]" in user_prompt
        return json.dumps({"answer": "文档支持这个结论。", "source_ids": self.source_ids}, ensure_ascii=False)


class FailingChat(FakeChat):
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        self.calls += 1
        raise DeepSeekApiError("DeepSeek API 调用失败（http_status=503）")


def _settings(tmp_path: Path, threshold: float = 0.45) -> Settings:
    return Settings(
        embedding_model="text-embedding-v4",
        embedding_dimension=1024,
        qdrant_local_path=tmp_path / "qdrant",
        collection_prefix="qa",
        retrieval_top_k=5,
        retrieval_score_threshold=threshold,
        retrieval_context_max_chars=4000,
    )


def _seed(tmp_path: Path) -> tuple[Settings, QdrantIndexer, str]:
    settings = _settings(tmp_path)
    indexer = QdrantIndexer(
        settings.collection_name,
        settings.embedding_dimension,
        local_path=settings.qdrant_local_path,
    )
    indexer.ensure_collection()
    doc1 = "a" * 64
    doc2 = "b" * 64
    chunks = [
        DocumentChunk(doc1, "Happy-LLM-0727.pdf", "chunk-1", "文档一内容", 1, 1, "第一章", "doc1.pdf"),
        DocumentChunk(doc2, "other.pdf", "chunk-2", "文档二内容", 2, 2, "第二章", "doc2.pdf"),
    ]
    indexer.upsert(chunks, [[1.0] * 1024, [1.0] * 1024])
    return settings, indexer, doc1


def test_qdrant_search_returns_source_metadata_and_filters_document(tmp_path: Path):
    settings, indexer, doc1 = _seed(tmp_path)
    hits = indexer.search([1.0] * 1024, limit=5, document_id=doc1, score_threshold=0.45)
    assert len(hits) == 1
    assert hits[0].payload["document_id"] == doc1
    assert hits[0].payload["source_locator"] == "Happy-LLM-0727.pdf#page=1&chunk=chunk-1"
    indexer.close()


def test_markdown_citation_keeps_line_locator_without_fake_pages():
    hit = RetrievalHit(
        point_id="chunk-md",
        score=0.88,
        payload={
            "document_id": "doc-md",
            "document_name": "notes.md",
            "chunk_id": "chunk-md",
            "section": "第一章",
            "page_start": None,
            "page_end": None,
            "source_locator": "notes.md#section=%E7%AC%AC%E4%B8%80%E7%AB%A0&paragraph=1&lines=3-5&chunk=chunk-md",
            "content": "Markdown 内容",
        },
    )
    citation = QuestionAnswerService._citation(hit, 1)
    assert citation.page_start is None
    assert citation.page_end is None
    assert "lines=3-5" in citation.source_locator
def test_qa_returns_citation_bound_to_retrieved_chunk(tmp_path: Path):
    settings, indexer, doc1 = _seed(tmp_path)
    chat = FakeChat(["S1"])
    service = QuestionAnswerService(
        settings,
        query_embedding=StaticEmbedding(),
        chat=chat,
        indexer=indexer,
    )
    response = service.ask("known", document_id=doc1)
    assert response.status == "answered"
    assert response.citations[0].citation_id == "S1"
    assert response.citations[0].document_id == doc1
    assert "[S1]" in response.answer
    assert chat.calls == 1
    indexer.close()


def test_no_results_does_not_call_deepseek(tmp_path: Path):
    settings, indexer, _ = _seed(tmp_path)
    chat = FakeChat()
    service = QuestionAnswerService(settings, query_embedding=StaticEmbedding(), chat=chat, indexer=indexer)
    response = service.ask("unknown")
    assert response.status == "no_results"
    assert response.citations == []
    assert chat.calls == 0
    indexer.close()


def test_query_embedding_failure_is_propagated(tmp_path: Path):
    settings, indexer, _ = _seed(tmp_path)
    with pytest.raises(EmbeddingServiceError, match="query embedding failed"):
        QuestionAnswerService(
            settings,
            query_embedding=FailingEmbedding(),
            chat=FakeChat(),
            indexer=indexer,
        ).ask("known")
    indexer.close()


def test_query_vector_dimension_mismatch_is_rejected(tmp_path: Path):
    settings, indexer, _ = _seed(tmp_path)
    with pytest.raises(VectorDimensionMismatch):
        indexer.search([1.0], limit=1)
    indexer.close()


def test_license_retrieval_plan_expands_terms_without_changing_normal_queries():
    query, threshold, terms = _retrieval_plan("Happy-LLM PDF 的授权信息是什么？", 0.45)
    assert "开源协议" in query
    assert "知识共享" in query
    assert threshold == 0.25
    assert "非商业性使用" in terms

    normal_query, normal_threshold, normal_terms = _retrieval_plan("Transformer 的核心内容是什么？", 0.45)
    assert normal_query == "Transformer 的核心内容是什么？"
    assert normal_threshold == 0.45
    assert normal_terms == ()


def test_license_hits_are_reranked_by_matched_terms():
    unrelated = RetrievalHit(
        point_id="unrelated",
        score=0.80,
        payload={"content": "这是普通技术内容"},
    )
    license_hit = RetrievalHit(
        point_id="license",
        score=0.30,
        payload={"content": "开源协议：知识共享署名-非商业性使用-相同方式共享 4.0 国际许可协议"},
    )
    ranked = _rerank_keyword_hits([unrelated, license_hit], ("开源协议", "知识共享", "非商业性使用"))
    assert [hit.point_id for hit in ranked] == ["license", "unrelated"]


def test_qdrant_unavailable_is_reported_for_retrieval():
    indexer = QdrantIndexer("missing", 1024, url="http://127.0.0.1:1", timeout=1)
    settings = Settings(embedding_model="text-embedding-v4", embedding_dimension=1024)
    service = QuestionAnswerService(settings, query_embedding=StaticEmbedding(), chat=FakeChat(), indexer=indexer)
    with pytest.raises(QdrantUnavailableError):
        service.ask("known")


def test_deepseek_failure_is_not_replaced_by_fabricated_answer(tmp_path: Path):
    settings, indexer, doc1 = _seed(tmp_path)
    service = QuestionAnswerService(
        settings,
        query_embedding=StaticEmbedding(),
        chat=FailingChat(),
        indexer=indexer,
    )
    with pytest.raises(DeepSeekApiError, match="http_status=503"):
        service.ask("known", document_id=doc1)
    indexer.close()


def test_deepseek_provider_preserves_http_status(monkeypatch):
    class Unauthorized(Exception):
        status_code = 401

    class Completions:
        def create(self, **kwargs):
            raise Unauthorized("invalid key")

    class Chat:
        completions = Completions()

    class FakeClient:
        chat = Chat()

        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    provider = DeepSeekChatProvider(api_key="test-key", max_retries=0)
    with pytest.raises(DeepSeekApiError, match="http_status=401"):
        provider.generate("system", "user")


def test_deepseek_provider_does_not_inherit_environment_proxy_by_default(monkeypatch):
    captured = {}

    class FakeHttpClient:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    class FakeClient:
        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr("httpx.Client", FakeHttpClient)
    monkeypatch.setattr("openai.OpenAI", FakeClient)
    DeepSeekChatProvider(api_key="test-key")
    assert captured == {"trust_env": False}


def test_deepseek_provider_retries_empty_response_then_succeeds(monkeypatch):
    class Completions:
        def __init__(self):
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            content = "" if self.calls == 1 else '{"answer":"ok","source_ids":[]}'
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    completions = Completions()

    class Chat:
        pass

    chat = Chat()
    chat.completions = completions

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = chat

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    provider = DeepSeekChatProvider(
        api_key="test-key",
        max_retries=1,
        retry_backoff_seconds=0,
    )
    assert provider.generate("system", "user") == '{"answer":"ok","source_ids":[]}'
    assert completions.calls == 2


def test_deepseek_provider_disables_thinking_by_default(monkeypatch):
    captured = {}

    class Completions:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason="stop",
                        message=SimpleNamespace(content='{"answer":"ok","source_ids":[]}'),
                    )
                ]
            )

    class Chat:
        completions = Completions()

    class FakeClient:
        chat = Chat()

        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    provider = DeepSeekChatProvider(api_key="test-key", max_retries=0)
    provider.generate("system", "user")
    assert captured["extra_body"] == {"thinking": {"type": "disabled"}}
    assert captured["response_format"] == {"type": "json_object"}


def test_deepseek_provider_reports_truncated_empty_response(monkeypatch):
    class Completions:
        def create(self, **kwargs):
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        finish_reason="length",
                        message=SimpleNamespace(content="", reasoning_content="partial reasoning"),
                    )
                ]
            )

    class Chat:
        completions = Completions()

    class FakeClient:
        chat = Chat()

        def __init__(self, **kwargs):
            pass

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    provider = DeepSeekChatProvider(api_key="test-key", max_retries=0)
    with pytest.raises(DeepSeekApiError, match=r"finish_reason=length.*reasoning_length=17"):
        provider.generate("system", "user")


def test_deepseek_provider_exhausts_empty_response_retries(monkeypatch):
    class Completions:
        def __init__(self):
            self.calls = 0

        def create(self, **kwargs):
            self.calls += 1
            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=""))]
            )

    completions = Completions()

    class Chat:
        pass

    chat = Chat()
    chat.completions = completions

    class FakeClient:
        def __init__(self, **kwargs):
            self.chat = chat

    monkeypatch.setattr("openai.OpenAI", FakeClient)
    provider = DeepSeekChatProvider(
        api_key="test-key",
        max_retries=2,
        retry_backoff_seconds=0,
    )
    with pytest.raises(DeepSeekApiError, match="empty content"):
        provider.generate("system", "user")
    assert completions.calls == 3
