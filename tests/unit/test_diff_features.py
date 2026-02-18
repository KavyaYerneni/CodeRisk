from coderisk.features.diff_features import extract_diff_features


def test_extract_diff_features_basic() -> None:
    diff = (
        "diff --git a/src/a.py b/src/a.py\n"
        "--- a/src/a.py\n+++ b/src/a.py\n"
        "@@ -1 +1,2 @@\n-old\n+new\n+extra\n"
        "diff --git a/tests/test_a.py b/tests/test_a.py\n"
        "--- a/tests/test_a.py\n+++ b/tests/test_a.py\n"
        "@@ -1 +1 @@\n-x\n+y\n"
    )
    feats = extract_diff_features(diff)
    assert feats["feat_lines_added"] == 3.0
    assert feats["feat_lines_deleted"] == 2.0
    assert feats["feat_test_file_count"] >= 1.0
    assert feats["feat_ext_py"] == 2.0
