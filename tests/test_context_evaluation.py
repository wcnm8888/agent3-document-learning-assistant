from __future__ import annotations

import json
from pathlib import Path

from eval.run_context_evaluation import (
    DEFAULT_CASES,
    REQUIRED_CATEGORIES,
    load_cases,
    main,
    run_evaluation,
    select_final_citation_ids,
)


def test_frozen_dataset_covers_all_required_context_scenarios() -> None:
    cases = load_cases()

    assert len(cases) == 10
    assert {case["category"] for case in cases} == REQUIRED_CATEGORIES
    assert len({case["case_id"] for case in cases}) == len(cases)
    assert all(case["expected"]["human_review"] is True for case in cases)


def test_offline_context_evaluation_passes_structural_gates() -> None:
    report = run_evaluation(load_cases())

    assert report["summary"] == {
        "schema_version": "ctx-001-step5-v1",
        "mode": "offline_read_only",
        "case_count": 10,
        "automatic_passed": 10,
        "automatic_failed": 0,
        "coverage_complete": True,
        "human_review_pending": 10,
        "external_services_called": False,
        "wrote_result_files": False,
    }
    assert all(item["automatic_verdict"] == "pass" for item in report["cases"])


def test_offline_context_evaluation_is_deterministic() -> None:
    cases = load_cases()

    assert run_evaluation(cases) == run_evaluation(cases)


def test_report_contains_diagnostics_but_not_context_bodies() -> None:
    report = run_evaluation(load_cases())
    serialized = json.dumps(report, ensure_ascii=False)

    assert "section_usage" in serialized
    assert "compression_events" in serialized
    assert "完整提示" not in serialized
    for item in report["cases"]:
        assert "system_prompt" not in item
        assert "user_prompt" not in item
        assert "answer" not in item
        assert all("content" not in hit for hit in item["retrieval_hits"])


def test_conflicts_and_injection_never_gain_evidence_or_citation_authority() -> None:
    report = run_evaluation(load_cases())
    sensitive = {
        item["category"]: item
        for item in report["cases"]
        if item["category"] in {"history_rag_conflict", "note_rag_conflict", "prompt_injection"}
    }

    assert sensitive.keys() == {
        "history_rag_conflict",
        "note_rag_conflict",
        "prompt_injection",
    }
    for item in sensitive.values():
        assert item["included_citation_ids"] == ["S1"]
        assert item["final_citation_ids"] == ["S1"]
        assert item["fact_source_verdict"] == "qdrant_evidence_only"


def test_no_retrieval_short_circuits_without_builder_prompt() -> None:
    report = run_evaluation(load_cases())
    no_results = [item for item in report["cases"] if item["status"] == "no_results"]

    assert len(no_results) == 2
    assert all(item["builder_invoked"] is False for item in no_results)
    assert all(item["section_usage"] == {} for item in no_results)
    assert all(item["final_citation_ids"] == [] for item in no_results)


def test_model_source_ids_are_strictly_whitelisted_with_evidence_fallback() -> None:
    assert select_final_citation_ids(["S2", "S1", "S1"], ["S1", "S3"]) == ("S1",)
    assert select_final_citation_ids(["S8", "S9"], ["S1"]) == ("S1",)
    assert select_final_citation_ids([], []) == ()


def test_cli_reads_custom_cases_and_only_prints_report(tmp_path: Path, capsys) -> None:
    custom_cases = tmp_path / "cases.jsonl"
    custom_cases.write_text(DEFAULT_CASES.read_text(encoding="utf-8"), encoding="utf-8")

    assert main(["--cases", str(custom_cases)]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["summary"]["mode"] == "offline_read_only"
    assert list(tmp_path.iterdir()) == [custom_cases]
