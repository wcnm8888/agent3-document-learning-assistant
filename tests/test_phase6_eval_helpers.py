from __future__ import annotations

from eval.run_embedding_comparison import grade_item, page_hint, refusal_like


def test_page_hint_supports_single_and_ranges() -> None:
    assert page_hint("第 2 页") == [2]
    assert page_hint("第2-3页") == [2, 3]
    assert page_hint("没有页码") is None


def test_refusal_detection_accepts_explicit_missing_evidence() -> None:
    assert refusal_like("文档中没有提到该配置，当前片段不足以回答。")
    assert not refusal_like("根据文档，系统使用了某个模型。")


def test_no_answer_question_is_not_marked_correct_when_model_invents_fact() -> None:
    question = {
        "id": "q014",
        "question": "文档是否说明了某个模型？",
        "question_type": "无答案",
        "expected_answer_points": [],
        "source_hint": "",
    }
    invented = {
        "status": "answered",
        "answer": "文档说明使用了某个模型。",
        "citations": [{"page_start": 1, "page_end": 1, "content": "无关片段"}],
    }
    refusal = {
        "status": "answered",
        "answer": "文档中没有提到该模型，无法回答。",
        "citations": [{"page_start": 1, "page_end": 1, "content": "无关片段"}],
    }
    assert grade_item(question, invented)["answer_correct_auto"] is False
    assert grade_item(question, refusal)["answer_correct_auto"] is True
