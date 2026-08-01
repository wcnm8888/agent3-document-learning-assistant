from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace

from .config import Settings
from .backup import backup_sqlite
from .deepseek import DeepSeekChatProvider
from .embedding import DashScopeEmbeddingProvider
from .errors import DocumentIngestionError
from .ingestion import DocumentIngestionService
from .health import run_health_check
from .learning import LearningService
from .memory_store import SQLiteMemoryStore
from .qdrant_index import QdrantIndexer
from .qa import QuestionAnswerService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="文档学习助手 CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    index = sub.add_parser("index", help="解析并索引一个 PDF 或 Markdown")
    index.add_argument("document_path", help="PDF 或 Markdown 文件路径")
    ask = sub.add_parser("ask", help="检索文档并生成带来源的回答")
    ask.add_argument("question", help="用户问题")
    ask.add_argument("--document-id", default=None, help="可选的 document_id 过滤")
    ask.add_argument("--top-k", type=int, default=None, help="可选的检索数量")
    ask.add_argument("--score-threshold", type=float, default=None, help="可选的最低相似度")
    session_create = sub.add_parser("session-create", help="创建学习会话")
    session_create.add_argument("--session-id", default=None, help="可选的固定会话 ID")
    ask_session = sub.add_parser("ask-session", help="在学习会话中提问并持久化问答")
    ask_session.add_argument("session_id")
    ask_session.add_argument("question")
    ask_session.add_argument("--document-id", default=None)
    ask_session.add_argument("--top-k", type=int, default=None)
    ask_session.add_argument("--score-threshold", type=float, default=None)
    note_create = sub.add_parser("note-create", help="创建学习笔记")
    note_create.add_argument("session_id")
    note_create.add_argument("content")
    note_create.add_argument("--turn-id", default=None)
    note_create.add_argument("--document-id", default=None)
    note_create.add_argument("--source-locator", default=None)
    note_update = sub.add_parser("note-update", help="更新学习笔记")
    note_update.add_argument("note_id")
    note_update.add_argument("content")
    notes = sub.add_parser("notes", help="查询学习笔记")
    notes.add_argument("--session-id", default=None)
    history = sub.add_parser("history", help="查询会话问答历史")
    history.add_argument("session_id")
    stats = sub.add_parser("stats", help="生成学习统计")
    stats.add_argument("--start-date", default=None)
    stats.add_argument("--end-date", default=None)
    report = sub.add_parser("report", help="生成确定性的学习报告")
    report.add_argument("--start-date", default=None)
    report.add_argument("--end-date", default=None)
    health = sub.add_parser("health", help="检查配置、Qdrant collection 和 SQLite 状态")
    backup = sub.add_parser("backup-sqlite", help="创建并校验 SQLite 一致性备份")
    backup.add_argument("destination", help="备份文件路径")
    backup.add_argument("--source", default=None, help="可选的 SQLite 源文件路径")
    backup.add_argument("--overwrite", action="store_true", help="允许覆盖已有备份文件")
    return parser


def _build_embedding(settings: Settings) -> DashScopeEmbeddingProvider:
    return DashScopeEmbeddingProvider(
        model_name=settings.embedding_model,
        expected_dimension=settings.embedding_dimension,
        api_key=settings.embedding_api_key,
        base_url=settings.embedding_base_url,
        batch_size=settings.embedding_batch_size,
        max_retries=settings.embedding_max_retries,
        retry_backoff_seconds=settings.embedding_retry_backoff_seconds,
    )


def _build_qa_service(settings: Settings, args: argparse.Namespace) -> tuple[QuestionAnswerService, QdrantIndexer]:
    if args.top_k is not None:
        settings = replace(settings, retrieval_top_k=args.top_k)
    if args.score_threshold is not None:
        settings = replace(settings, retrieval_score_threshold=args.score_threshold)
    embedding = _build_embedding(settings)
    indexer = QdrantIndexer(
        settings.collection_name,
        settings.embedding_dimension,
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        local_path=settings.qdrant_local_path,
        timeout=settings.qdrant_timeout,
    )
    try:
        chat = DeepSeekChatProvider(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            model_name=settings.deepseek_model,
            thinking=settings.deepseek_thinking,
            trust_env=settings.deepseek_trust_env,
            max_retries=settings.deepseek_max_retries,
            retry_backoff_seconds=settings.deepseek_retry_backoff_seconds,
        )
        return QuestionAnswerService(settings, query_embedding=embedding, chat=chat, indexer=indexer), indexer
    except Exception:
        indexer.close()
        raise


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        settings = Settings.from_env()
        if args.command == "health":
            result = run_health_check(settings)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0 if result["status"] == "ok" else 1
        if args.command == "backup-sqlite":
            result = backup_sqlite(
                args.source or settings.sqlite_path,
                args.destination,
                overwrite=args.overwrite,
            )
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        if args.command == "index":
            embedding = _build_embedding(settings)
            store = SQLiteMemoryStore(settings.sqlite_path)
            service = None
            try:
                from .document_catalog import DocumentCatalogService

                service = DocumentIngestionService(
                    settings,
                    embedding=embedding,
                    catalog=DocumentCatalogService(store),
                )
                report = service.index_document(args.document_path)
                print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
                return 0
            finally:
                if service is not None:
                    service.close()
                store.close()
        if args.command == "ask":
            service, indexer = _build_qa_service(settings, args)
            try:
                response = service.ask(args.question, document_id=args.document_id)
                print(json.dumps(response.as_dict(), ensure_ascii=False, indent=2))
                return 0
            finally:
                indexer.close()
        if args.command == "session-create":
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                session = store.create_session(args.session_id)
            print(json.dumps(session.__dict__, ensure_ascii=False, indent=2))
            return 0
        if args.command == "ask-session":
            service, indexer = _build_qa_service(settings, args)
            store = SQLiteMemoryStore(settings.sqlite_path)
            learning = LearningService(settings, qa_service=service, store=store)
            try:
                response = learning.ask(args.session_id, args.question, document_id=args.document_id)
                print(json.dumps(response.as_dict(), ensure_ascii=False, indent=2))
                return 0
            finally:
                learning.close()
                indexer.close()
        if args.command == "note-create":
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                note = store.create_note(
                    session_id=args.session_id,
                    content=args.content,
                    turn_id=args.turn_id,
                    document_id=args.document_id,
                    source_locator=args.source_locator,
                )
            print(json.dumps(note.__dict__, ensure_ascii=False, indent=2))
            return 0
        if args.command == "note-update":
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                note = store.update_note(args.note_id, args.content)
            print(json.dumps(note.__dict__, ensure_ascii=False, indent=2))
            return 0
        if args.command == "notes":
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                notes = [note.__dict__ for note in store.list_notes(args.session_id)]
            print(json.dumps(notes, ensure_ascii=False, indent=2))
            return 0
        if args.command == "history":
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                turns = []
                for turn in store.list_turns(args.session_id):
                    turns.append(
                        {
                            "turn_id": turn.turn_id,
                            "session_id": turn.session_id,
                            "turn_index": turn.turn_index,
                            "question": turn.question,
                            "answer": turn.answer,
                            "status": turn.status,
                            "model": turn.model,
                            "created_at": turn.created_at,
                            "citations": [citation.as_dict() for citation in turn.citations],
                        }
                    )
            print(json.dumps(turns, ensure_ascii=False, indent=2))
            return 0
        if args.command in {"stats", "report"}:
            with SQLiteMemoryStore(settings.sqlite_path) as store:
                if args.command == "stats":
                    result = store.stats(args.start_date, args.end_date).as_dict()
                else:
                    result = store.report(args.start_date, args.end_date)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        return 2
    except DocumentIngestionError as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
