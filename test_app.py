import pytest
from streamlit_app import is_valid_email

def test_valid_email():
    assert is_valid_email("test@example.com")

def test_invalid_email_missing_at():
    assert not is_valid_email("testexample.com")

def test_invalid_email_missing_domain():
    assert not is_valid_email("test@")

def test_invalid_email_missing_dot():
    assert not is_valid_email("test@example")

