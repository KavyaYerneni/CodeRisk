from coderisk.data.git_parser import is_merge_commit_message, parse_unified_diff


def test_parse_unified_diff() -> None:
    diff = (
        "diff --git a/src/a.py b/src/a.py\n"
        "--- a/src/a.py\n+++ b/src/a.py\n"
        "@@ -1,2 +1,3 @@\n"
        " keep\n-old\n+new\n+extra\n"
    )
    stats = parse_unified_diff(diff)
    assert stats.files_changed == 1
    assert stats.lines_added == 2
    assert stats.lines_deleted == 1
    assert stats.hunks == 1
    assert stats.paths == ["src/a.py"]


def test_merge_message() -> None:
    assert is_merge_commit_message("Merge branch 'main'")
    assert not is_merge_commit_message("fix: null check")
