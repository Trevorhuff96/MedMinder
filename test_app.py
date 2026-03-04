import glob
import os
from datetime import timedelta

import pytest

import auth
from pages import DOB_MAX_DATE, validate_signup_fields


@pytest.fixture
def isolated_auth_db(tmp_path, monkeypatch):
    """Point auth module to a temporary SQLite database for unit tests."""
    test_db = tmp_path / "test_medminder.db"
    monkeypatch.setattr(auth, "DB_FILE", str(test_db))
    auth.init_db()
    return test_db


def test_valid_email():
    assert auth.is_valid_email("test@example.com")


def test_invalid_email_missing_at():
    assert not auth.is_valid_email("testexample.com")


def test_invalid_email_missing_domain():
    assert not auth.is_valid_email("test@")


def test_invalid_email_missing_dot():
    assert not auth.is_valid_email("test@example")


def test_create_patient_user_persists_profile(isolated_auth_db):
    success, message = auth.create_user(
        "Jane Patient",
        "jane@example.com",
        "secret123",
        "Patient",
        {
            "dob": "1995-05-01",
            "gender": "Female",
            "phone": "555-111-2222",
            "address": "1 Main St",
        },
    )

    assert success is True
    assert message == "Account created successfully!"

    profile = auth.get_user_profile("jane@example.com")
    assert profile is not None
    assert profile["name"] == "Jane Patient"
    assert profile["role"] == "Patient"
    assert profile["phone"] == "555-111-2222"


def test_create_doctor_user_persists_speciality(isolated_auth_db):
    success, _ = auth.create_user(
        "Dr. Smith",
        "smith@example.com",
        "secret123",
        "Doctor",
        {
            "dob": "1980-10-11",
            "gender": "Male",
            "phone": "555-333-4444",
            "address": "99 Clinic Ave",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )

    assert success is True

    profile = auth.get_user_profile("smith@example.com")
    assert profile is not None
    assert profile["role"] == "Doctor"
    assert profile["speciality"] == "Dentist"
    assert profile["office_hours"] == "9:00 AM to 6:00 PM"


def test_create_user_rejects_invalid_email(isolated_auth_db):
    success, message = auth.create_user(
        "Bad Email",
        "bad-email",
        "secret123",
        "Patient",
        {"dob": "2000-01-01", "gender": "Other", "phone": "555", "address": "Nowhere"},
    )

    assert success is False
    assert message == "Invalid email format!"


def test_create_user_rejects_duplicate_email(isolated_auth_db):
    first_success, _ = auth.create_user(
        "First User",
        "dupe@example.com",
        "secret123",
        "Patient",
        {"dob": "2000-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    second_success, second_message = auth.create_user(
        "Second User",
        "dupe@example.com",
        "secret123",
        "Patient",
        {"dob": "2001-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )

    assert first_success is True
    assert second_success is False
    assert second_message == "An account with this email already exists!"


def test_authenticate_user_returns_name_and_role(isolated_auth_db):
    auth.create_user(
        "John Patient",
        "john@example.com",
        "secret123",
        "Patient",
        {"dob": "1999-09-09", "gender": "Male", "phone": "555", "address": "Addr"},
    )

    success, result = auth.authenticate_user("john@example.com", "secret123")

    assert success is True
    assert result == {"name": "John Patient", "role": "Patient"}


def test_authenticate_user_rejects_wrong_password(isolated_auth_db):
    auth.create_user(
        "John Patient",
        "john@example.com",
        "secret123",
        "Patient",
        {"dob": "1999-09-09", "gender": "Male", "phone": "555", "address": "Addr"},
    )

    success, result = auth.authenticate_user("john@example.com", "wrongpass")

    assert success is False
    assert result == "Incorrect password!"


def test_authenticate_user_rejects_unknown_email(isolated_auth_db):
    success, result = auth.authenticate_user("missing@example.com", "secret123")

    assert success is False
    assert result == "No account found with this email!"


def test_hash_password_and_verify_password():
    hashed_password = auth.hash_password("secret123")

    assert hashed_password != "secret123"
    assert auth.verify_password("secret123", hashed_password) is True
    assert auth.verify_password("wrongpass", hashed_password) is False


def test_get_specialities_returns_seeded_values(isolated_auth_db):
    specialities = auth.get_specialities()

    assert "Dentist" in specialities
    assert "Neurologist" in specialities


def test_validate_signup_fields_rejects_future_dob_for_patient():
    errors = validate_signup_fields(
        "Jane",
        "Patient",
        DOB_MAX_DATE + timedelta(days=1),
        "1 Main St",
        "Boston",
        "Massachusetts",
        "02110",
        "United States",
        "555-111-2222",
        "jane@example.com",
        "secret123",
    )

    assert errors["dob"] == "Date of Birth must be between 100 years ago and today."


def test_validate_signup_fields_rejects_future_dob_for_doctor():
    errors = validate_signup_fields(
        "John",
        "Doctor",
        DOB_MAX_DATE + timedelta(days=10),
        "99 Clinic Ave",
        "Boston",
        "Massachusetts",
        "02110",
        "United States",
        "555-333-4444",
        "doctor@example.com",
        "secret123",
        speciality="Dentist",
    )

    assert errors["dob"] == "Date of Birth must be between 100 years ago and today."


REQUIRED_DOCS = [
    "Design Decisions.docx",
    "Prompts.docx",
    "Requirements with Trust Gates.docx",
    "System Proposal - MedMinder.pdf",
]


def test_docs_folder_exists():
    assert os.path.isdir("docs"), "docs folder is missing!"


def test_required_docs_exist_in_docs():
    for doc in REQUIRED_DOCS:
        path = os.path.join("docs", doc)
        assert os.path.exists(path), f"{doc} is missing from docs folder!"


def test_no_docs_outside_docs_folder():
    all_docx = glob.glob("**/*.docx", recursive=True)
    all_pdf = glob.glob("**/*.pdf", recursive=True)

    for file in all_docx + all_pdf:
        normalized = file.replace("\\", "/")
        assert normalized.startswith("docs/"), f"{file} is outside the docs folder!"
