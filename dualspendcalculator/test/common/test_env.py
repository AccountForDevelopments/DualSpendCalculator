import pytest

from common.env import env_bool, env_str


@pytest.mark.parametrize(
    "value,default,expected",
    [
        (None, False, False),
        (None, True, True),
        ("true", False, True),
        ("TRUE", False, True),
        ("1", False, True),
        ("yes", False, True),
        ("on", False, True),
        ("false", True, False),
        ("0", True, False),
    ],
)
def test__env_bool(value, default, expected):
    assert env_bool(value, default) is expected


@pytest.mark.parametrize(
    "value,default,expected",
    [
        (None, "fallback", "fallback"),
        ("", "fallback", ""),
        ("prod-key", "fallback", "prod-key"),
    ],
)
def test__env_str(value, default, expected):
    assert env_str(value, default) == expected
