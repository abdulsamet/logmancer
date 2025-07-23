from logmancer.conf import get_bool, get_int, get_list


def test_default_values_used():
    assert get_int("CLEANUP_AFTER_DAYS") == 30
    assert get_bool("ENABLE_MIDDLEWARE") is True


def test_custom_list(monkeypatch):
    monkeypatch.setattr(
        "logmancer.conf.settings",
        type(
            "MockSettings",
            (),
            {
                "LOGMANCER_SIGNAL_EXCLUDE_MODELS": ["custom.AppModel"],
                "LOGMANCER_NOT_LIST": 1234,
                "CLEANUP_AFTER_DAYS": "45",
            },
        ),
    )

    assert "custom.AppModel" in get_list("SIGNAL_EXCLUDE_MODELS")
    assert get_list("NOT_LIST") == []
    assert get_int("CLEANUP_AFTER_DAYS") == 30
