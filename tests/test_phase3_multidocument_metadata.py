from __future__ import annotations

from pathlib import Path

from doc_qa.chunker import PageAwareChunker
from doc_qa.config import Settings
from doc_qa.document_parser import DocumentParser
from doc_qa.qdrant_index import QdrantIndexer


def test_existing_point_payload_can_be_enriched_without_replacing_vector(tmp_path: Path) -> None:
    source = Path("data/reference/Happy-LLM-0727.pdf")
    document = DocumentParser().parse(source)
    chunks = PageAwareChunker().chunk_document(document)[:1]
    settings = Settings(
        embedding_model="text-embedding-v4",
        embedding_dimension=1024,
        qdrant_local_path=tmp_path / "qdrant",
        collection_prefix="metadata",
    )
    indexer = QdrantIndexer(settings.collection_name, 1024, local_path=settings.qdrant_local_path)
    indexer.ensure_collection()
    from qdrant_client.models import PointStruct

    indexer.client.upsert(
        collection_name=settings.collection_name,
        points=[
            PointStruct(
                id=indexer._point_id(chunks[0].chunk_id),
                vector=[0.1] * 1024,
                payload={"document_id": chunks[0].document_id, "chunk_id": chunks[0].chunk_id},
            )
        ],
        wait=True,
    )
    before_vector = indexer.client.retrieve(
        collection_name=settings.collection_name,
        ids=[indexer._point_id(chunks[0].chunk_id)],
        with_vectors=True,
    )[0].vector

    repaired = indexer.ensure_metadata(chunks)

    assert repaired == 1
    assert indexer.verify_metadata({chunks[0].chunk_id}) is True
    point = indexer.client.retrieve(
        collection_name=settings.collection_name,
        ids=[indexer._point_id(chunks[0].chunk_id)],
        with_vectors=True,
    )[0]
    assert point.vector == before_vector
    indexer.close()
