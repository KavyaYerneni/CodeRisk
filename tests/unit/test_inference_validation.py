import pytest

from coderisk.inference.validation import DiffTooLargeError, validate_predict_request
from coderisk.schemas import PredictRequest


def test_validate_ok() -> None:
    req = PredictRequest(diff_text="diff --git a/a b/a\n+x")
    assert validate_predict_request(req).diff_text.startswith("diff")


def test_validate_too_large() -> None:
    req = PredictRequest(diff_text="x" * 100)
    with pytest.raises(DiffTooLargeError):
        validate_predict_request(req, max_diff_chars=10)
