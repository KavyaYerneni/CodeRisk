from coderisk.data.demo_dataset import generate_demo_records, records_to_frame
from coderisk.features.feature_pipeline import build_feature_frame, fit_transform_features


def test_feature_pipeline_fit_on_train_only() -> None:
    df = records_to_frame(generate_demo_records(40, seed=3))
    train = df.iloc[:30]
    test = df.iloc[30:]
    x_train, (x_test,), names, pipe = fit_transform_features(train, test)
    assert x_train.shape[0] == 30
    assert x_test.shape[0] == 10
    assert x_train.shape[1] == len(names)
    assert hasattr(pipe, "transform")
    frame = build_feature_frame(train)
    assert not frame.isna().all().any()
