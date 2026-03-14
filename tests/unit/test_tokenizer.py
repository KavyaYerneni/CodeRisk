from coderisk.models.tokenizer import build_codebert_text


def test_build_codebert_text_contains_sections() -> None:
    text = build_codebert_text(
        {
            "diff_text": "diff --git a/a.py b/a.py\n+hello",
            "files_changed": 2,
            "lines_added": 3,
            "lines_deleted": 1,
            "author": "alice",
        }
    )
    assert "DIFF:" in text
    assert "[SEP]" in text
    assert "AUTHOR: alice" in text
