import pandas as pd

from coderisk.data.demo_dataset import generate_demo_records, records_to_frame
from coderisk.data.splits import make_splits


def _demo() -> pd.DataFrame:
    return records_to_frame(generate_demo_records(120, seed=42))


def test_no_commit_overlap_random() -> None:
    train, val, test, meta = make_splits(_demo(), strategy="random_stratified", seed=0)
    ids = set(train.commit_sha) | set(val.commit_sha) | set(test.commit_sha)
    assert len(ids) == len(train) + len(val) + len(test)
    assert meta.strategy == "random_stratified"


def test_time_split_ordered() -> None:
    train, val, test, _ = make_splits(_demo(), strategy="time")
    assert train["timestamp"].max() <= val["timestamp"].min()
    assert val["timestamp"].max() <= test["timestamp"].min()


def test_repository_holdout() -> None:
    train, val, test, _ = make_splits(_demo(), strategy="repository", seed=1)
    assert set(test["repository"]).isdisjoint(set(train["repository"]))


def test_repository_time() -> None:
    train, val, test, meta = make_splits(_demo(), strategy="repository_time", seed=2)
    assert set(test["repository"]).isdisjoint(set(train["repository"]))
    assert meta.class_balance["train"]["n"] > 0
