from coderisk.data.dataset_builder import build_demo_frame, save_processed_dataset


def test_build_and_save(tmp_path) -> None:  # noqa: ANN001
    df = build_demo_frame(50, seed=1)
    report = save_processed_dataset(df, tmp_path)
    assert report["n_rows"] == 50
    assert (tmp_path / "dataset.csv").exists()
