import datetime

from logmancer.utils import make_json_safe, mask_sensitive_data


def test_mask_sensitive_data():
    data = {"username": "admin", "password": "123456", "nested": {"token": "abc"}}

    result = mask_sensitive_data(data)
    assert result["password"] == "****"
    assert result["nested"]["token"] == "****"


def test_make_json_safe_handles_datetime():
    now = datetime.datetime.now()
    data = {"created": now}
    result = make_json_safe(data)

    assert isinstance(result["created"], str)
    assert "T" in result["created"]


def test_make_json_safe_handles_decimal():
    from decimal import Decimal

    data = {"price": Decimal("19.99")}
    result = make_json_safe(data)

    assert isinstance(result["price"], float)
    assert result["price"] == 19.99


def test_make_json_safe_handles_uuid():
    import uuid

    data = {"id": uuid.uuid4()}
    result = make_json_safe(data)

    assert isinstance(result["id"], str)
    assert len(result["id"]) == 36  # UUID string length


def test_make_json_safe_handles_invalid_data():
    data = {"invalid": set([1, 2, 3])}  # Set is not JSON serializable
    result = make_json_safe(data)

    assert result == {"invalid": "{1, 2, 3}"}  # Fallback to string representation
