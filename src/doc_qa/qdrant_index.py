from __future__ import annotations

import uuid
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from .errors import MetadataIntegrityError, QdrantUnavailableError, VectorDimensionMismatch
from .models import DocumentChunk, RetrievalHit


REQUIRED_METADATA = {
    "document_id",
    "document_name",
    "chunk_id",
    "content",
    "page_start",
    "page_end",
    "section",
    "source_path",
    "format",
    "content_hash",
    "embedding_profile",
    "source_locator_scheme",
    "source_locator",
}


def _is_local_qdrant_url(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return host in {"localhost", "127.0.0.1", "::1"}


class QdrantIndexer:
    def __init__(
        self,
        collection_name: str,
        vector_dimension: int,
        *,
        url: str | None = None,
        api_key: str | None = None,
        local_path: str | Path | None = None,
        timeout: int = 10,
    ):
        try:
            from qdrant_client import QdrantClient
        except ImportError as exc:
            raise QdrantUnavailableError("未安装 qdrant-client") from exc
        self.collection_name = collection_name
        self.vector_dimension = vector_dimension
        self._local_path = Path(local_path) if local_path else None
        try:
            if url:
                client_kwargs = {
                    "url": url,
                    "api_key": api_key,
                    "timeout": timeout,
                }
                # 本地 Qdrant 不应被系统 SOCKS/HTTP 代理接管；否则
                # httpx 可能在客户端初始化阶段因代理依赖缺失而失败。
                if _is_local_qdrant_url(url):
                    client_kwargs["trust_env"] = False
                self.client = QdrantClient(**client_kwargs)
            else:
                if not self._local_path:
                    raise QdrantUnavailableError("未配置 QDRANT_URL 或 QDRANT_LOCAL_PATH")
                self._local_path.mkdir(parents=True, exist_ok=True)
                self.client = QdrantClient(path=str(self._local_path))
        except QdrantUnavailableError:
            raise
        except Exception as exc:
            raise QdrantUnavailableError("Qdrant 客户端初始化失败") from exc

    def ensure_collection(self) -> None:
        from qdrant_client.models import Distance, VectorParams

        try:
            exists = self.collection_name in {item.name for item in self.client.get_collections().collections}
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=self.vector_dimension, distance=Distance.COSINE),
                )
                return
            actual = self._collection_dimension()
            if actual != self.vector_dimension:
                raise VectorDimensionMismatch(
                    f"Qdrant collection {self.collection_name} 维度为 {actual}，期望 {self.vector_dimension}"
                )
        except VectorDimensionMismatch:
            raise
        except Exception as exc:
            raise QdrantUnavailableError("Qdrant collection 检查或创建失败") from exc

    def _collection_dimension(self) -> int:
        info = self.client.get_collection(self.collection_name)
        vectors = getattr(getattr(getattr(info, "config", None), "params", None), "vectors", None)
        size = getattr(vectors, "size", None)
        if size is None and isinstance(vectors, dict):
            size = vectors.get("size")
        if size is None:
            raise QdrantUnavailableError("无法读取 Qdrant collection 的向量维度")
        return int(size)

    def _point_id(self, chunk_id: str) -> str:
        return str(uuid.uuid5(uuid.NAMESPACE_URL, f"docqa:{chunk_id}"))

    def existing_chunk_ids(self, chunk_ids: Iterable[str]) -> set[str]:
        expected = set(chunk_ids)
        if not expected:
            return set()
        found: set[str] = set()
        offset = None
        try:
            while True:
                points, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                for point in points:
                    chunk_id = (point.payload or {}).get("chunk_id")
                    if chunk_id in expected:
                        found.add(chunk_id)
                if offset is None:
                    break
        except Exception as exc:
            raise QdrantUnavailableError("无法读取 Qdrant 现有分块") from exc
        return found

    def upsert(self, chunks: list[DocumentChunk], vectors: list[list[float]]) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("分块数量与向量数量不一致")
        for vector in vectors:
            if len(vector) != self.vector_dimension:
                raise VectorDimensionMismatch(
                    f"待写入向量维度为 {len(vector)}，期望 {self.vector_dimension}"
                )
        try:
            from qdrant_client.models import PointStruct

            points = []
            for chunk, vector in zip(chunks, vectors):
                payload = chunk.payload()
                if REQUIRED_METADATA - payload.keys():
                    raise MetadataIntegrityError(f"分块元数据缺失: {chunk.chunk_id}")
                points.append(PointStruct(id=self._point_id(chunk.chunk_id), vector=vector, payload=payload))
            self.client.upsert(collection_name=self.collection_name, points=points, wait=True)
        except (MetadataIntegrityError, VectorDimensionMismatch):
            raise
        except Exception as exc:
            raise QdrantUnavailableError("Qdrant upsert 失败") from exc

    def point_count(self) -> int:
        return self._count_with_filter(None)

    def document_point_count(self, document_id: str) -> int:
        if not document_id.strip():
            raise ValueError("document_id 不能为空")
        return self._count_with_filter(document_id)

    def delete_document_points(self, document_id: str) -> int:
        """按 document_id 精确删除 points，返回删除前数量。"""
        if not document_id.strip():
            raise ValueError("document_id 不能为空")
        before = self.document_point_count(document_id)
        if before == 0:
            return 0
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            self.client.delete(
                collection_name=self.collection_name,
                points_selector=Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
                ),
                wait=True,
            )
            after = self.document_point_count(document_id)
            if after != 0:
                raise QdrantUnavailableError(
                    f"Qdrant 文档 points 删除后仍剩余 {after}: {document_id}"
                )
            return before
        except QdrantUnavailableError:
            raise
        except Exception as exc:
            raise QdrantUnavailableError("Qdrant 文档 points 删除失败") from exc

    def _count_with_filter(self, document_id: str | None) -> int:
        try:
            query_filter = None
            if document_id:
                from qdrant_client.models import FieldCondition, Filter, MatchValue

                query_filter = Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
                )
            return int(
                self.client.count(
                    collection_name=self.collection_name,
                    count_filter=query_filter,
                    exact=True,
                ).count
            )
        except Exception as exc:
            raise QdrantUnavailableError("无法读取 Qdrant point 数量") from exc

    def collection_info(self) -> dict[str, object]:
        """读取 collection 状态，不创建、写入或迁移任何数据。"""
        try:
            names = {item.name for item in self.client.get_collections().collections}
            if self.collection_name not in names:
                raise QdrantUnavailableError(f"Qdrant collection 不存在: {self.collection_name}")
            info = self.client.get_collection(self.collection_name)
            status = getattr(info, "status", None)
            return {
                "collection": self.collection_name,
                "status": getattr(status, "value", status) or "unknown",
                "points_count": self.point_count(),
                "vector_dimension": self._collection_dimension(),
            }
        except QdrantUnavailableError:
            raise
        except Exception as exc:
            raise QdrantUnavailableError(
                f"无法读取 Qdrant collection 状态: {self.collection_name}"
            ) from exc

    def search(
        self,
        query_vector: list[float],
        *,
        limit: int = 5,
        document_id: str | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievalHit]:
        if len(query_vector) != self.vector_dimension:
            raise VectorDimensionMismatch(
                f"查询向量维度为 {len(query_vector)}，期望 {self.vector_dimension}"
            )
        if limit <= 0:
            raise ValueError("检索 limit 必须大于 0")
        try:
            from qdrant_client.models import FieldCondition, Filter, MatchValue

            query_filter = None
            if document_id:
                query_filter = Filter(
                    must=[FieldCondition(key="document_id", match=MatchValue(value=document_id))]
                )
            response = self.client.query_points(
                collection_name=self.collection_name,
                query=[float(value) for value in query_vector],
                query_filter=query_filter,
                limit=limit,
                score_threshold=score_threshold,
                with_payload=True,
                with_vectors=False,
            )
            hits: list[RetrievalHit] = []
            for point in response.points:
                payload = dict(point.payload or {})
                missing = REQUIRED_METADATA - payload.keys()
                if missing:
                    raise MetadataIntegrityError(
                        f"检索结果 {point.id} 缺少来源元数据: {sorted(missing)}"
                    )
                hits.append(RetrievalHit(point_id=str(point.id), score=float(point.score), payload=payload))
            return hits
        except (MetadataIntegrityError, VectorDimensionMismatch):
            raise
        except Exception as exc:
            raise QdrantUnavailableError("Qdrant 检索失败") from exc

    def verify_metadata(self, expected_chunk_ids: set[str]) -> bool:
        found: set[str] = set()
        offset = None
        try:
            while True:
                points, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                for point in points:
                    payload = point.payload or {}
                    if payload.get("chunk_id") in expected_chunk_ids:
                        if REQUIRED_METADATA - payload.keys():
                            return False
                        found.add(payload["chunk_id"])
                if offset is None:
                    break
        except Exception as exc:
            raise QdrantUnavailableError("无法验证 Qdrant 元数据") from exc
        return found == expected_chunk_ids

    def ensure_metadata(self, chunks: list[DocumentChunk]) -> int:
        """只补齐已有 point 的 payload，不重建向量、不改变 point ID。"""
        expected = {chunk.chunk_id: chunk for chunk in chunks}
        if not expected:
            return 0
        repaired = 0
        found: set[str] = set()
        try:
            offset = None
            while True:
                points, offset = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=256,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False,
                )
                for point in points:
                    payload = point.payload or {}
                    chunk_id = payload.get("chunk_id")
                    if chunk_id not in expected:
                        continue
                    found.add(str(chunk_id))
                    desired = expected[str(chunk_id)].payload()
                    missing = REQUIRED_METADATA - payload.keys()
                    if missing:
                        self.client.set_payload(
                            collection_name=self.collection_name,
                            payload={key: desired[key] for key in REQUIRED_METADATA},
                            points=[point.id],
                            wait=True,
                        )
                        repaired += 1
                if offset is None:
                    break
        except (MetadataIntegrityError, VectorDimensionMismatch):
            raise
        except Exception as exc:
            raise QdrantUnavailableError("无法补齐 Qdrant 来源元数据") from exc
        if found != set(expected):
            raise MetadataIntegrityError(
                f"Qdrant 缺少待验证分块: {sorted(set(expected) - found)}"
            )
        return repaired

    def close(self) -> None:
        close = getattr(self.client, "close", None)
        if close:
            close()
