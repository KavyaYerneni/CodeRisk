from coderisk.data.repo_filter import RepoFilter


def test_allow_and_deny() -> None:
    f = RepoFilter(allow={"acme/a", "acme/b"}, deny={"acme/b"})
    assert f.apply(["acme/a", "acme/b", "other/x"]) == ["acme/a"]


def test_prefix() -> None:
    f = RepoFilter(allow_prefixes=("demo/",))
    assert f.accepts("demo/payments")
    assert not f.accepts("prod/payments")
