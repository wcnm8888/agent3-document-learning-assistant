from __future__ import annotations

import math
import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import replace
from datetime import datetime, timezone
from typing import Any

from .config import ContextConfig
from .models import Citation, ContextBuildResult, ContextPacket, estimate_tokens


SECTION_ORDER = {
    "policy": 0,
    "task": 1,
    "rag_evidence": 2,
    "conversation": 3,
    "note": 4,
    "output_contract": 5,
}


class ContextBuildError(ValueError):
    """上下文无法在既定事实和预算约束内安全构建。"""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ContextBuilder:
    """无 I/O、可重放的 Gather-Select-Structure-Compress 流水线。"""

    def __init__(
        self,
        config: ContextConfig | None = None,
        *,
        now_provider: Callable[[], datetime] | None = None,
    ):
        self.config = config or ContextConfig()
        self._now_provider = now_provider or _utc_now

    def build(
        self,
        *,
        question: str,
        rag_citations: Sequence[Citation],
        conversation_history: Sequence[object],
        notes: Sequence[object],
        system_policies: str,
        output_contract: str,
        document_id: str | None,
        task_context: str | None = None,
        reference_turn_id: str | None = None,
        reference_hint_chars: int = 0,
    ) -> ContextBuildResult:
        question = self._required_text(question, "question")
        normalized_task_context = (
            self._required_text(task_context, "task_context")
            if task_context is not None
            else question
        )
        if not isinstance(reference_hint_chars, int) or isinstance(reference_hint_chars, bool):
            raise ContextBuildError("reference_hint_chars 必须是整数")
        if reference_hint_chars < 0:
            raise ContextBuildError("reference_hint_chars 不能为负数")
        system_policies = self._required_text(system_policies, "system_policies")
        output_contract = self._required_text(output_contract, "output_contract")
        normalized_document_id = document_id.strip() if document_id else None
        now = self._now()

        packets, dropped_ids, drop_reasons = self._gather(
            question=question,
            task_context=normalized_task_context,
            rag_citations=rag_citations,
            conversation_history=conversation_history,
            notes=notes,
            system_policies=system_policies,
            output_contract=output_contract,
            now=now,
        )
        selected, selection_dropped, selection_reasons, compression_events = self._select(
            packets,
            question=question,
            document_id=normalized_document_id,
            now=now,
        )
        self._merge_diagnostics(
            dropped_ids,
            drop_reasons,
            selection_dropped,
            selection_reasons,
        )

        selected, budget_dropped, budget_reasons, budget_events = self._compress(
            selected,
            now=now,
        )
        self._merge_diagnostics(
            dropped_ids,
            drop_reasons,
            budget_dropped,
            budget_reasons,
        )
        compression_events.extend(budget_events)

        rendered = self._structure(selected)
        if self._over_budget(rendered[3], rendered[4]):
            raise ContextBuildError("上下文预算压缩后仍然超限")

        ordered = self._ordered(selected)
        included_citation_ids = tuple(
            str(packet.metadata["citation_id"])
            for packet in ordered
            if packet.evidence_eligible
        )
        return ContextBuildResult(
            system_prompt=rendered[0],
            user_prompt=rendered[1],
            selected_packet_ids=tuple(packet.packet_id for packet in ordered),
            dropped_packet_ids=tuple(dropped_ids),
            included_citation_ids=included_citation_ids,
            section_usage=rendered[2],
            total_estimated_tokens=rendered[3],
            total_chars=rendered[4],
            compression_events=tuple(compression_events),
            drop_reasons=drop_reasons,
            over_budget=False,
            reference_resolution_used=task_context is not None,
            reference_turn_id=reference_turn_id,
            reference_hint_chars=reference_hint_chars,
        )

    def _gather(
        self,
        *,
        question: str,
        task_context: str,
        rag_citations: Sequence[Citation],
        conversation_history: Sequence[object],
        notes: Sequence[object],
        system_policies: str,
        output_contract: str,
        now: datetime,
    ) -> tuple[list[ContextPacket], list[str], dict[str, str]]:
        packets = [
            ContextPacket(
                packet_id="policy:system",
                kind="policy",
                content=system_policies,
                timestamp=now,
                relevance_score=1.0,
                stable_order=0,
            ),
            ContextPacket(
                packet_id="task:current",
                kind="task",
                content=task_context,
                timestamp=now,
                relevance_score=1.0,
                stable_order=1,
            ),
        ]
        dropped_ids: list[str] = []
        drop_reasons: dict[str, str] = {}
        stable_order = 2

        for citation in rag_citations:
            packet = self._citation_packet(citation, now=now, stable_order=stable_order)
            packets.append(packet)
            stable_order += 1

        for index, turn in enumerate(conversation_history, start=1):
            packet_id = f"conversation:{self._value(turn, 'turn_id') or index}"
            question_text = str(self._value(turn, "question") or "").strip()
            answer_text = str(self._value(turn, "answer") or "").strip()
            if not question_text and not answer_text:
                self._drop(dropped_ids, drop_reasons, packet_id, "empty_content")
                continue
            content = f"第{index}轮\n用户：{question_text}\n助手：{answer_text}"
            timestamp = self._timestamp(
                self._value(turn, "timestamp") or self._value(turn, "created_at"),
                fallback=now,
            )
            packets.append(
                ContextPacket(
                    packet_id=packet_id,
                    kind="conversation",
                    content=content,
                    timestamp=timestamp,
                    relevance_score=max(0.60, self._relevance(content, question)),
                    stable_order=stable_order,
                    metadata={
                        "turn_index": index,
                        "dedupe_content": f"{question_text}\n{answer_text}",
                    },
                )
            )
            stable_order += 1

        for index, note in enumerate(notes, start=1):
            note_id = str(self._value(note, "note_id") or index).strip()
            packet_id = f"note:{note_id}"
            content_text = str(self._value(note, "content") or "").strip()
            if not content_text:
                self._drop(dropped_ids, drop_reasons, packet_id, "empty_content")
                continue
            timestamp = self._timestamp(
                self._value(note, "updated_at") or self._value(note, "created_at"),
                fallback=now,
            )
            note_document_id = self._value(note, "document_id")
            content = f"[{note_id}] {content_text}"
            metadata: dict[str, object] = {"note_id": note_id}
            metadata["dedupe_content"] = content_text
            if note_document_id:
                metadata["document_id"] = str(note_document_id)
            turn_id = self._value(note, "turn_id")
            if turn_id:
                metadata["turn_id"] = str(turn_id)
            source_locator = self._value(note, "source_locator")
            if source_locator:
                metadata["source_locator"] = str(source_locator)
            packets.append(
                ContextPacket(
                    packet_id=packet_id,
                    kind="note",
                    content=content,
                    timestamp=timestamp,
                    relevance_score=max(0.30, self._relevance(content, question)),
                    stable_order=stable_order,
                    metadata=metadata,
                )
            )
            stable_order += 1

        packets.append(
            ContextPacket(
                packet_id="output:contract",
                kind="output_contract",
                content=output_contract,
                timestamp=now,
                relevance_score=1.0,
                stable_order=stable_order,
            )
        )
        return packets, dropped_ids, drop_reasons

    def _select(
        self,
        packets: Sequence[ContextPacket],
        *,
        question: str,
        document_id: str | None,
        now: datetime,
    ) -> tuple[list[ContextPacket], list[str], dict[str, str], list[str]]:
        selected = [packet for packet in packets if packet.pinned]
        dropped_ids: list[str] = []
        drop_reasons: dict[str, str] = {}
        compression_events: list[str] = []
        seen_non_evidence: set[tuple[str, str]] = set()
        had_rag_evidence = any(packet.kind == "rag_evidence" for packet in packets)
        evidence: list[ContextPacket] = []
        conversation: list[ContextPacket] = []
        notes: list[ContextPacket] = []

        for packet in packets:
            if packet.pinned:
                continue
            packet_document_id = str(packet.metadata.get("document_id") or "").strip() or None
            if document_id and packet_document_id and packet_document_id != document_id:
                self._drop(dropped_ids, drop_reasons, packet.packet_id, "scope_mismatch")
                continue
            if packet.kind in {"conversation", "note"}:
                duplicate_key = (
                    packet.kind,
                    self._normalize(str(packet.metadata.get("dedupe_content") or packet.content)),
                )
                if duplicate_key in seen_non_evidence:
                    self._drop(dropped_ids, drop_reasons, packet.packet_id, "duplicate")
                    continue
                seen_non_evidence.add(duplicate_key)
                if packet.relevance_score < self.config.min_relevance:
                    self._drop(dropped_ids, drop_reasons, packet.packet_id, "low_relevance")
                    continue
            if packet.kind == "rag_evidence":
                evidence.append(packet)
            elif packet.kind == "conversation":
                conversation.append(packet)
            elif packet.kind == "note":
                notes.append(packet)

        if had_rag_evidence and not evidence:
            raise ContextBuildError("当前文档范围没有可用 Evidence")

        pinned_reserve = math.ceil(
            self.config.max_input_chars * self.config.pinned_reserve_ratio
        )
        non_pinned_remaining = max(0, self.config.max_input_chars - pinned_reserve)
        selected_evidence, group_dropped, group_reasons, events = self._select_group(
            evidence,
            max_chars=min(self.config.evidence_max_chars, non_pinned_remaining),
            limit=None,
            now=now,
            preserve_input_order=True,
        )
        self._merge_diagnostics(dropped_ids, drop_reasons, group_dropped, group_reasons)
        compression_events.extend(events)
        if evidence and not selected_evidence:
            raise ContextBuildError("上下文预算不足以保留最小 Evidence")
        selected.extend(selected_evidence)
        non_pinned_remaining = max(
            0,
            non_pinned_remaining - self._group_chars(selected_evidence, evidence=True),
        )

        selected_history, group_dropped, group_reasons, events = self._select_group(
            conversation,
            max_chars=min(self.config.history_max_chars, non_pinned_remaining),
            limit=self.config.history_turn_limit,
            now=now,
        )
        self._merge_diagnostics(dropped_ids, drop_reasons, group_dropped, group_reasons)
        compression_events.extend(events)
        selected.extend(selected_history)
        non_pinned_remaining = max(
            0,
            non_pinned_remaining - self._group_chars(selected_history),
        )

        selected_notes, group_dropped, group_reasons, events = self._select_group(
            notes,
            max_chars=min(self.config.notes_max_chars, non_pinned_remaining),
            limit=self.config.note_limit,
            now=now,
        )
        self._merge_diagnostics(dropped_ids, drop_reasons, group_dropped, group_reasons)
        compression_events.extend(events)
        selected.extend(selected_notes)
        return self._ordered(selected), dropped_ids, drop_reasons, compression_events

    @staticmethod
    def _group_chars(packets: Sequence[ContextPacket], *, evidence: bool = False) -> int:
        if not packets:
            return 0
        separator = 7 if evidence else 2
        return sum(packet.char_count for packet in packets) + separator * (len(packets) - 1)

    def _select_group(
        self,
        packets: Sequence[ContextPacket],
        *,
        max_chars: int,
        limit: int | None,
        now: datetime,
        preserve_input_order: bool = False,
    ) -> tuple[list[ContextPacket], list[str], dict[str, str], list[str]]:
        if preserve_input_order:
            ranked = list(packets)
        else:
            ranked = sorted(
                packets,
                key=lambda packet: (
                    -self._combined_score(packet, now),
                    -packet.timestamp.timestamp(),
                    packet.stable_order,
                    packet.packet_id,
                ),
            )
        if limit is not None:
            overflow = ranked[limit:]
            ranked = ranked[:limit]
        else:
            overflow = []

        selected: list[ContextPacket] = []
        dropped_ids: list[str] = []
        drop_reasons: dict[str, str] = {}
        events: list[str] = []
        for packet in overflow:
            self._drop(dropped_ids, drop_reasons, packet.packet_id, "item_limit")

        remaining = max_chars
        for packet in ranked:
            separator = 0 if not selected else (7 if packet.kind == "rag_evidence" else 2)
            available = remaining - separator
            if available <= 0:
                self._drop(dropped_ids, drop_reasons, packet.packet_id, "section_budget")
                continue
            if packet.char_count <= available:
                selected.append(packet)
                remaining -= packet.char_count + separator
                continue
            truncated = (
                self._truncate_packet(packet, available)
                if self.config.enable_compression
                else None
            )
            if truncated is None:
                self._drop(dropped_ids, drop_reasons, packet.packet_id, "section_budget")
                continue
            selected.append(truncated)
            remaining -= truncated.char_count + separator
            events.append(
                f"truncate:{packet.packet_id}:section_budget:"
                f"{packet.char_count}->{truncated.char_count}"
            )

        ordered = sorted(selected, key=lambda packet: packet.stable_order)
        return ordered, dropped_ids, drop_reasons, events

    def _structure(
        self, packets: Sequence[ContextPacket]
    ) -> tuple[str, str, dict[str, dict[str, int]], int, int]:
        groups: dict[str, list[ContextPacket]] = {kind: [] for kind in SECTION_ORDER}
        for packet in self._ordered(packets):
            groups[packet.kind].append(packet)

        policy_body = "\n\n".join(packet.content for packet in groups["policy"])
        task_body = "\n\n".join(packet.content for packet in groups["task"])
        evidence_body = "\n\n---\n\n".join(
            packet.content for packet in groups["rag_evidence"]
        ) or "（本轮没有可用的 Qdrant 检索证据）"
        conversation_content = "\n\n".join(
            packet.content for packet in groups["conversation"]
        ) or "（无历史对话）"
        conversation_body = (
            "以下内容可用于解析当前问题中的代词、省略信息和对话对象，但不是事实证据；"
            "用于指代消解的对话对象属于用户意图，不具备事实或引用资格；"
            "关于该对象的最终文档事实仍必须由 Evidence 支持。\n"
            + conversation_content
        )
        notes_content = "\n\n".join(packet.content for packet in groups["note"]) or "（无相关笔记）"
        notes_body = "以下内容仅用于理解学习背景，不是事实证据。\n" + notes_content
        output_body = "\n\n".join(packet.content for packet in groups["output_contract"])

        sections = {
            "policies": f"[Role & Policies]\n{policy_body}",
            "task": f"[Task]\n{task_body}",
            "evidence": f"[Evidence: Qdrant Retrieval Only]\n{evidence_body}",
            "conversation": f"[Conversation Context: Non-evidence]\n{conversation_body}",
            "notes": f"[Notes: Non-evidence]\n{notes_body}",
            "output": f"[Output Contract]\n{output_body}",
        }
        system_prompt = sections["policies"]
        user_prompt = "\n\n".join(
            sections[name] for name in ("task", "evidence", "conversation", "notes", "output")
        )
        complete_prompt = f"{system_prompt}\n\n{user_prompt}"
        packet_counts = {
            "policies": len(groups["policy"]),
            "task": len(groups["task"]),
            "evidence": len(groups["rag_evidence"]),
            "conversation": len(groups["conversation"]),
            "notes": len(groups["note"]),
            "output": len(groups["output_contract"]),
        }
        usage = {
            name: {
                "chars": len(section),
                "estimated_tokens": estimate_tokens(section),
                "packets": packet_counts[name],
            }
            for name, section in sections.items()
        }
        return (
            system_prompt,
            user_prompt,
            usage,
            estimate_tokens(complete_prompt),
            len(complete_prompt),
        )

    def _compress(
        self,
        packets: Sequence[ContextPacket],
        *,
        now: datetime,
    ) -> tuple[list[ContextPacket], list[str], dict[str, str], list[str]]:
        selected = list(packets)
        new_dropped: list[str] = []
        new_reasons: dict[str, str] = {}
        events: list[str] = []
        rendered = self._structure(selected)
        if not self._over_budget(rendered[3], rendered[4]):
            return selected, new_dropped, new_reasons, events
        if not self.config.enable_compression:
            raise ContextBuildError("上下文超过预算且压缩已禁用")

        for kind in ("conversation", "note"):
            while self._over_budget(rendered[3], rendered[4]):
                candidates = [packet for packet in selected if packet.kind == kind]
                if not candidates:
                    break
                victim = min(
                    candidates,
                    key=lambda packet: (
                        self._combined_score(packet, now),
                        packet.timestamp.timestamp(),
                        -packet.stable_order,
                    ),
                )
                selected.remove(victim)
                self._drop(new_dropped, new_reasons, victim.packet_id, "total_budget")
                events.append(f"drop:{victim.packet_id}:total_budget")
                rendered = self._structure(selected)

        while self._over_budget(rendered[3], rendered[4]):
            evidence = [packet for packet in selected if packet.kind == "rag_evidence"]
            if len(evidence) <= 1:
                break
            victim = max(evidence, key=lambda packet: packet.stable_order)
            selected.remove(victim)
            self._drop(new_dropped, new_reasons, victim.packet_id, "total_budget")
            events.append(f"drop:{victim.packet_id}:total_budget")
            rendered = self._structure(selected)

        attempts = 0
        while self._over_budget(rendered[3], rendered[4]):
            attempts += 1
            if attempts > 64:
                raise ContextBuildError("上下文预算压缩未能稳定收敛")
            evidence = [packet for packet in selected if packet.kind == "rag_evidence"]
            if not evidence:
                raise ContextBuildError("固定上下文分区超过预算")
            packet = evidence[-1]
            char_excess = max(0, rendered[4] - self.config.max_input_chars)
            token_excess = max(0, rendered[3] - self.config.max_input_tokens)
            reduction = max(1, char_excess, token_excess)
            target_chars = packet.char_count - reduction
            truncated = self._truncate_packet(packet, target_chars)
            if truncated is None or truncated.char_count >= packet.char_count:
                raise ContextBuildError("上下文预算不足以保留最小 Evidence")
            selected[selected.index(packet)] = truncated
            events.append(
                f"truncate:{packet.packet_id}:total_budget:"
                f"{packet.char_count}->{truncated.char_count}"
            )
            rendered = self._structure(selected)

        return self._ordered(selected), new_dropped, new_reasons, events

    def _truncate_packet(
        self, packet: ContextPacket, max_chars: int
    ) -> ContextPacket | None:
        marker = self.config.truncation_marker
        if packet.char_count <= max_chars:
            return packet
        if max_chars <= len(marker):
            return None

        if packet.kind == "rag_evidence":
            header = str(packet.metadata.get("header") or "")
            body = str(packet.metadata.get("body") or "")
            minimum_body = min(len(body), self.config.min_evidence_chars)
            fixed_chars = len(header) + 1 + len(marker)
            if max_chars < fixed_chars + minimum_body:
                return None
            body_limit = max_chars - fixed_chars
            shortened = self._truncate_text(body, body_limit)
            content = f"{header}\n{shortened}{marker}"
        else:
            text_limit = max_chars - len(marker)
            if text_limit <= 0:
                return None
            shortened = self._truncate_text(packet.content, text_limit)
            if not shortened:
                return None
            content = f"{shortened}{marker}"

        return replace(packet, content=content)

    @staticmethod
    def _truncate_text(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        candidate = text[:max_chars].rstrip()
        if not candidate:
            return ""
        search_start = max(0, int(len(candidate) * 0.75))
        boundary = max(candidate.rfind(char, search_start) for char in "\n。！？；;，, ")
        if boundary > 0:
            candidate = candidate[: boundary + 1].rstrip()
        return candidate

    def _citation_packet(
        self, citation: Citation, *, now: datetime, stable_order: int
    ) -> ContextPacket:
        if not isinstance(citation, Citation):
            raise ContextBuildError("rag_citations 必须包含 Citation")
        location = (
            f"页码={citation.page_start}-{citation.page_end}"
            if citation.page_start is not None
            else f"定位={citation.source_locator}"
        )
        header = (
            f"[{citation.citation_id}] 文档={citation.document_name}; "
            f"章节={citation.section}; {location}; 来源定位={citation.source_locator}"
        )
        body = citation.content.strip()
        if not body:
            raise ContextBuildError(f"Citation 内容为空: {citation.citation_id}")
        return ContextPacket(
            packet_id=f"rag:{citation.citation_id}",
            kind="rag_evidence",
            content=f"{header}\n{body}",
            timestamp=now,
            relevance_score=max(0.0, min(1.0, float(citation.score))),
            stable_order=stable_order,
            metadata={
                "citation_id": citation.citation_id,
                "document_id": citation.document_id,
                "chunk_id": citation.chunk_id,
                "source_locator": citation.source_locator,
                "header": header,
                "body": body,
            },
        )

    def _combined_score(self, packet: ContextPacket, now: datetime) -> float:
        return (
            self.config.relevance_weight * packet.relevance_score
            + self.config.recency_weight * self._recency(packet.timestamp, now)
        )

    @staticmethod
    def _recency(timestamp: datetime, now: datetime) -> float:
        age_hours = max(0.0, (now - timestamp).total_seconds() / 3600)
        return max(0.1, min(1.0, math.exp(-0.1 * age_hours / 24)))

    @staticmethod
    def _relevance(content: str, question: str) -> float:
        content_units = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", content.lower()))
        question_units = set(re.findall(r"[A-Za-z0-9_]+|[\u4e00-\u9fff]", question.lower()))
        if not question_units:
            return 0.0
        return len(content_units & question_units) / len(question_units)

    @staticmethod
    def _normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().lower()

    @staticmethod
    def _value(item: object, key: str) -> Any:
        if isinstance(item, Mapping):
            return item.get(key)
        return getattr(item, key, None)

    @staticmethod
    def _timestamp(value: object, *, fallback: datetime) -> datetime:
        if value is None:
            return fallback
        if isinstance(value, datetime):
            parsed = value
        elif isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError as exc:
                raise ContextBuildError(f"上下文时间戳非法: {value}") from exc
        else:
            raise ContextBuildError("上下文时间戳必须是 datetime 或 ISO 字符串")
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed

    def _now(self) -> datetime:
        now = self._now_provider()
        if not isinstance(now, datetime):
            raise ContextBuildError("now_provider 必须返回 datetime")
        if now.tzinfo is None or now.utcoffset() is None:
            raise ContextBuildError("now_provider 必须返回带时区的 datetime")
        return now

    @staticmethod
    def _required_text(value: str, name: str) -> str:
        normalized = value.strip() if isinstance(value, str) else ""
        if not normalized:
            raise ContextBuildError(f"{name} 不能为空")
        return normalized

    @staticmethod
    def _ordered(packets: Sequence[ContextPacket]) -> list[ContextPacket]:
        return sorted(
            packets,
            key=lambda packet: (
                SECTION_ORDER[packet.kind],
                packet.stable_order,
                packet.packet_id,
            ),
        )

    def _over_budget(self, total_tokens: int, total_chars: int) -> bool:
        return (
            total_tokens > self.config.max_input_tokens
            or total_chars > self.config.max_input_chars
        )

    @staticmethod
    def _drop(
        dropped_ids: list[str],
        drop_reasons: dict[str, str],
        packet_id: str,
        reason: str,
    ) -> None:
        if packet_id not in drop_reasons:
            dropped_ids.append(packet_id)
            drop_reasons[packet_id] = reason

    @staticmethod
    def _merge_diagnostics(
        dropped_ids: list[str],
        drop_reasons: dict[str, str],
        new_ids: Sequence[str],
        new_reasons: Mapping[str, str],
    ) -> None:
        for packet_id in new_ids:
            if packet_id not in drop_reasons:
                dropped_ids.append(packet_id)
                drop_reasons[packet_id] = new_reasons[packet_id]
