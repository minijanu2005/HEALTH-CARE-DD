import pytest

from utils.validators import ValidationError, optional_email, parse_date, require_non_empty


def test_require_non_empty() -> None:
    assert require_non_empty("  abc ", "x") == "abc"


def test_require_non_empty_fails() -> None:
    with pytest.raises(ValidationError):
        require_non_empty("  ", "x")


def test_parse_date() -> None:
    assert str(parse_date("2020-01-02", "d")) == "2020-01-02"


def test_optional_email_invalid() -> None:
    with pytest.raises(ValidationError):
        optional_email("not-an-email")
