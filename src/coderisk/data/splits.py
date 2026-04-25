"""Train/validation/test split strategies with leakage guards."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split

SplitStrategy = Literal["random_stratified", "time", "repository", "repository_time"]


@dataclass
class SplitResult:
    train_ids: list[str]
    val_ids: list[str]
    test_ids: list[str]
    strategy: str
    seed: int
    class_balance: dict[str, dict[str, float]]


def _ids(df: pd.DataFrame) -> pd.Series:
    return df["commit_sha"].astype(str)


def _balance(df: pd.DataFrame) -> dict[str, float]:
    n = len(df)
    pos = float((df["bug_introducing_label"] == 1).sum())
    return {"n": float(n), "positive_rate": (pos / n) if n else 0.0}


def _assert_no_id_overlap(train: pd.DataFrame, val: pd.DataFrame, test: pd.DataFrame) -> None:
    sets = [_ids(train), _ids(val), _ids(test)]
    all_ids = pd.concat(sets)
    if all_ids.duplicated().any():
        raise ValueError("Commit SHA appears in multiple splits")


def split_random_stratified(
    df: pd.DataFrame, *, test_size: float, val_size: float, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_val, test = train_test_split(
        df,
        test_size=test_size,
        random_state=seed,
        stratify=df["bug_introducing_label"],
    )
    relative_val = val_size / max(1e-9, (1.0 - test_size))
    train, val = train_test_split(
        train_val,
        test_size=relative_val,
        random_state=seed,
        stratify=train_val["bug_introducing_label"],
    )
    return train, val, test


def split_time(
    df: pd.DataFrame, *, test_size: float, val_size: float
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    ordered = df.sort_values("timestamp").reset_index(drop=True)
    n = len(ordered)
    n_test = max(1, int(round(n * test_size)))
    n_val = max(1, int(round(n * val_size)))
    n_train = n - n_test - n_val
    if n_train < 1:
        raise ValueError("Not enough rows for time split")
    train = ordered.iloc[:n_train]
    val = ordered.iloc[n_train : n_train + n_val]
    test = ordered.iloc[n_train + n_val :]
    return train, val, test


def split_repository(
    df: pd.DataFrame, *, test_size: float, val_size: float, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    groups = df["repository"].astype(str)
    gss = GroupShuffleSplit(n_splits=1, test_size=test_size, random_state=seed)
    train_val_idx, test_idx = next(gss.split(df, groups=groups))
    train_val = df.iloc[train_val_idx]
    test = df.iloc[test_idx]
    relative_val = val_size / max(1e-9, (1.0 - test_size))
    gss2 = GroupShuffleSplit(n_splits=1, test_size=relative_val, random_state=seed)
    tr_idx, va_idx = next(gss2.split(train_val, groups=train_val["repository"].astype(str)))
    return train_val.iloc[tr_idx], train_val.iloc[va_idx], test


def split_repository_time(
    df: pd.DataFrame, *, test_size: float, val_size: float, seed: int
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Group by repository, then apply time split within held-in repos for val.

    Test repos are fully held out; validation is the latest fraction within train repos.
    """
    repos = sorted(df["repository"].astype(str).unique())
    rng = np.random.default_rng(seed)
    rng.shuffle(repos)
    n_test_repos = max(1, int(round(len(repos) * test_size)))
    test_repos = set(repos[:n_test_repos])
    train_repos = [r for r in repos if r not in test_repos]
    test = df[df["repository"].isin(test_repos)]
    train_pool = df[df["repository"].isin(train_repos)].sort_values("timestamp")
    n_val = max(1, int(round(len(train_pool) * (val_size / max(1e-9, 1.0 - test_size)))))
    val = train_pool.iloc[len(train_pool) - n_val :]
    train = train_pool.iloc[: len(train_pool) - n_val]
    return train, val, test


def make_splits(
    df: pd.DataFrame,
    *,
    strategy: SplitStrategy = "repository_time",
    test_size: float = 0.2,
    val_size: float = 0.1,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, SplitResult]:
    if strategy == "random_stratified":
        train, val, test = split_random_stratified(df, test_size=test_size, val_size=val_size, seed=seed)
    elif strategy == "time":
        train, val, test = split_time(df, test_size=test_size, val_size=val_size)
    elif strategy == "repository":
        train, val, test = split_repository(df, test_size=test_size, val_size=val_size, seed=seed)
    elif strategy == "repository_time":
        train, val, test = split_repository_time(df, test_size=test_size, val_size=val_size, seed=seed)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    _assert_no_id_overlap(train, val, test)
    result = SplitResult(
        train_ids=_ids(train).tolist(),
        val_ids=_ids(val).tolist(),
        test_ids=_ids(test).tolist(),
        strategy=strategy,
        seed=seed,
        class_balance={
            "train": _balance(train),
            "val": _balance(val),
            "test": _balance(test),
        },
    )
    return train, val, test, result


def save_split_result(path: Path | str, result: SplitResult) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(result), indent=2) + "\n", encoding="utf-8")
