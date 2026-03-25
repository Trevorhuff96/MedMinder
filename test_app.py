import glob
import os
from datetime import datetime, timedelta

import pytest

import auth
import appointments
import pages
import prescription
from pages import DOB_MAX_DATE, validate_signup_fields


@pytest.fixture
def isolated_auth_db(tmp_path, monkeypatch):
    """Point auth module to a temporary SQLite database for unit tests."""
    test_db = tmp_path / "test_medminder.db"
    monkeypatch.setattr(auth, "DB_FILE", str(test_db))
    auth.init_db()
    return test_db


@pytest.fixture
def isolated_app_db(tmp_path, monkeypatch):
    """Point auth and appointments modules to a shared temporary database."""
    test_db = tmp_path / "test_medminder_appointments.db"
    monkeypatch.setattr(auth, "DB_FILE", str(test_db))
    monkeypatch.setattr(appointments, "DB_FILE", str(test_db))
    monkeypatch.setattr(prescription, "DB_FILE", str(test_db))
    auth.init_db()
    appointments.init_appointments_db()
    prescription.init_db()
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
            "off_day": "Friday",
        },
    )

    assert success is True

    profile = auth.get_user_profile("smith@example.com")
    assert profile is not None
    assert profile["role"] == "Doctor"
    assert profile["speciality"] == "Dentist"
    assert profile["office_hours"] == "9:00 AM to 6:00 PM"
    assert profile["off_day"] == "Friday"


def test_update_doctor_profile_can_change_office_hours_and_off_day(isolated_auth_db):
    auth.create_user(
        "Dr. Update",
        "update@example.com",
        "secret123",
        "Doctor",
        {
            "dob": "1980-10-11",
            "gender": "Male",
            "phone": "555-333-4444",
            "address": "99 Clinic Ave",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
            "off_day": "Friday",
        },
    )

    success, message = auth.update_user_profile(
        "update@example.com",
        address="101 Clinic Ave",
        office_hours="8:00 AM to 5:00 PM",
        off_day="Monday",
    )

    assert success is True
    assert message == "Profile updated successfully!"

    profile = auth.get_user_profile("update@example.com")
    assert profile is not None
    assert profile["address"] == "101 Clinic Ave"
    assert profile["office_hours"] == "8:00 AM to 5:00 PM"
    assert profile["off_day"] == "Monday"


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


def test_dashboard_assistant_returns_past_patient_appointments(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_past_appointments_for_patient",
        lambda _email: [
            {
                "date": "2026-01-10",
                "time": "09:00",
                "doctor_name": "Alex Carter",
                "speciality": "Dentist",
            }
        ],
    )
    monkeypatch.setattr(pages, "get_appointments_for_patient", lambda _email: [])

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Show my past appointments",
        {},
    )

    assert "You have 1 past appointment(s)." in reply
    assert "2026-01-10 at 09:00" in reply
    assert "Dr. Alex Carter" in reply
    assert recommended == []


def test_dashboard_assistant_schedule_appointment_uses_booking_intent():
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "I want to schedule appointment",
        {},
    )

    assert "recommend doctors first" in reply
    assert recommended == []


def test_dashboard_assistant_lists_prescriptions_for_patient(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_prescriptions_for_patient",
        lambda _email: [
            {
                "diagnosis": "Seasonal allergies",
                "doctor_name": "Taylor Nguyen",
                "created_at": "2026-02-01T10:30:00",
                "medicines": [{"name": "Cetirizine"}, {"name": "Fluticasone"}],
            }
        ],
    )

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Can you show my prescriptions?",
        {},
    )

    assert "I found 1 prescription on file." in reply
    assert "2026-02-01" in reply
    assert "Seasonal allergies" in reply
    assert "Cetirizine, Fluticasone" in reply
    assert recommended == []


def test_dashboard_assistant_summarizes_multiple_prescriptions_for_patient(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_prescriptions_for_patient",
        lambda _email: [
            {
                "diagnosis": "Migraine",
                "doctor_name": "Taylor Nguyen",
                "follow_up_days": 14,
                "created_at": "2026-03-10T09:00:00",
                "medicines": [{"name": "Sumatriptan"}],
            },
            {
                "diagnosis": "Sinusitis",
                "doctor_name": "Alex Carter",
                "follow_up_days": 7,
                "created_at": "2026-02-01T10:30:00",
                "medicines": [{"name": "Amoxicillin"}, {"name": "Cetirizine"}],
            },
        ],
    )

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Can you show my prescriptions?",
        {},
    )

    assert "I found 2 prescriptions on file" in reply
    assert "Most recent: 2026-03-10 for Migraine (Dr. Taylor Nguyen)" in reply
    assert "Doctors on record: Dr. Taylor Nguyen, Dr. Alex Carter" in reply
    assert "Diagnoses on record: Migraine, Sinusitis" in reply
    assert "Medicines mentioned: Sumatriptan, Amoxicillin, Cetirizine" in reply
    assert recommended == []


def test_build_patient_treatment_summary_collects_patient_overview():
    prescriptions = [
        {
            "diagnosis": "Migraine",
            "doctor_name": "Taylor Nguyen",
            "follow_up_days": 14,
            "created_at": "2026-03-10T09:00:00",
            "medicines": [{"name": "Sumatriptan"}],
        },
        {
            "diagnosis": "Sinusitis",
            "doctor_name": "Alex Carter",
            "follow_up_days": 7,
            "created_at": "2026-02-01T10:30:00",
            "medicines": [{"name": "Amoxicillin"}, {"name": "Cetirizine"}],
        },
    ]
    care_team = [
        {"name": "Taylor Nguyen", "email": "taylor@example.com", "speciality": "Neurologist"},
        {"name": "Alex Carter", "email": "alex@example.com", "speciality": "General Practitioner"},
    ]

    summary = pages._build_patient_treatment_summary(prescriptions, care_team)

    assert summary["total_prescriptions"] == 2
    assert summary["total_diagnoses"] == 2
    assert summary["total_doctors"] == 2
    assert summary["latest_date"] == "2026-03-10"
    assert summary["latest_diagnosis"] == "Migraine"
    assert summary["latest_doctor"] == "Taylor Nguyen"
    assert summary["diagnoses"] == ["Migraine", "Sinusitis"]
    assert summary["medicines"] == ["Sumatriptan", "Amoxicillin", "Cetirizine"]
    assert summary["care_team_doctors"] == [
        "Dr. Taylor Nguyen • Neurologist",
        "Dr. Alex Carter • General Practitioner",
    ]
    assert summary["date_range"] == "2026-02-01 to 2026-03-10"


def test_dashboard_assistant_prescription_request_for_doctor():
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "show my prescriptions",
        {},
    )

    assert "which patient" in reply
    assert recommended == []


def test_dashboard_assistant_shows_specific_patient_prescription_summary_for_doctor(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_patients_for_doctor",
        lambda _email: [{"name": "Jamie Patient", "email": "jamie@example.com"}],
    )
    monkeypatch.setattr(
        pages,
        "get_prescriptions_for_doctor_patient",
        lambda _doctor_email, _patient_email: [
            {
                "diagnosis": "Migraine",
                "follow_up_days": 14,
                "created_at": "2026-03-10T09:00:00",
                "medicines": [{"name": "Sumatriptan"}],
            },
            {
                "diagnosis": "Sinusitis",
                "follow_up_days": 7,
                "created_at": "2026-02-01T11:15:00",
                "medicines": [{"name": "Amoxicillin"}, {"name": "Cetirizine"}],
            },
        ],
    )

    state = {}
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "Show me Jamie Patient's prescriptions",
        state,
    )

    assert "I found 2 prescriptions for Jamie Patient" in reply
    assert "Most recent: 2026-03-10 for Migraine" in reply
    assert "Diagnoses on record: Migraine, Sinusitis" in reply
    assert "Medicines mentioned: Sumatriptan, Amoxicillin, Cetirizine" in reply
    assert recommended == []
    assert state["last_prescription_patient"]["name"] == "Jamie Patient"
    assert len(state["last_prescriptions"]) == 2


def test_dashboard_assistant_answers_prescription_followup_for_doctor_patient_context():
    state = {
        "last_prescription_patient": {"name": "Jamie Patient", "email": "jamie@example.com"},
        "last_prescriptions": [
            {
                "diagnosis": "Migraine",
                "medicines": [
                    {"name": "Sumatriptan", "frequency": "Once daily", "days": 5},
                    {"name": "Ibuprofen", "frequency": "Twice daily", "days": 7},
                ],
            }
        ],
    }

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "What is the frequency for those medicines?",
        state,
    )

    assert "For Jamie Patient:" in reply
    assert "Sumatriptan: Once daily" in reply
    assert "Ibuprofen: Twice daily" in reply
    assert recommended == []


def test_dashboard_assistant_does_not_recommend_doctors_for_doctor_accounts():
    state = {
        "last_speciality": "Cardiologist",
        "last_recommended_doctors": [{"name": "Old Suggestion", "email": "old@example.com"}],
    }

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "I have chest pain and fever",
        state,
    )

    assert "only shown for patient accounts" in reply
    assert recommended == []
    assert state["last_speciality"] == ""
    assert state["last_recommended_doctors"] == []


def test_dashboard_assistant_answers_prescription_frequency_from_context():
    state = {
        "last_prescriptions": [
            {
                "diagnosis": "Seasonal allergies",
                "medicines": [
                    {"name": "Cetirizine", "frequency": "Once daily", "days": 10},
                    {"name": "Fluticasone", "frequency": "Twice daily", "days": 14},
                ],
            }
        ]
    }

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "What is the frequency for those?",
        state,
    )

    assert "frequency" in reply.lower()
    assert "Cetirizine: Once daily" in reply
    assert "Fluticasone: Twice daily" in reply
    assert recommended == []


def test_dashboard_assistant_answers_prescription_days_from_context():
    state = {
        "last_prescriptions": [
            {
                "diagnosis": "Infection",
                "medicines": [
                    {"name": "Amoxicillin", "frequency": "Twice daily", "days": 7},
                ],
            }
        ]
    }

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "How many days do I need to take it?",
        state,
    )

    assert "how many days" in reply.lower()
    assert "Amoxicillin: 7 day(s)" in reply
    assert recommended == []


def test_upcoming_appointments_exclude_same_day_past_time(isolated_app_db):
    patient_email = "patient-time@example.com"
    doctor_email = "doctor-time@example.com"

    auth.create_user(
        "Time Patient",
        patient_email,
        "secret123",
        "Patient",
        {"dob": "1990-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    auth.create_user(
        "Time Doctor",
        doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )

    now = datetime.now().replace(second=0, microsecond=0)
    past_today = now - timedelta(minutes=90)
    future_today = now + timedelta(minutes=90)

    appointments.save_appointment(patient_email, doctor_email, past_today.isoformat())
    appointments.save_appointment(patient_email, doctor_email, future_today.isoformat())

    upcoming = appointments.get_appointments_for_patient(patient_email)
    past = appointments.get_past_appointments_for_patient(patient_email)

    past_key = (past_today.strftime("%Y-%m-%d"), past_today.strftime("%H:%M"))
    future_key = (future_today.strftime("%Y-%m-%d"), future_today.strftime("%H:%M"))

    upcoming_keys = {(item["date"], item["time"]) for item in upcoming}
    past_keys = {(item["date"], item["time"]) for item in past}

    assert future_key in upcoming_keys
    assert past_key not in upcoming_keys
    assert past_key in past_keys


def test_dashboard_assistant_cancel_intent_populates_cancellable_appointments(monkeypatch):
    upcoming = [
        {
            "appointment_id": 101,
            "date": "2026-03-20",
            "time": "09:30",
            "doctor_name": "Alex Carter",
        }
    ]
    monkeypatch.setattr(pages, "get_appointments_for_patient", lambda _email: upcoming)

    state = {}
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Please cancel my appointment",
        state,
    )

    assert "Select an appointment below" in reply
    assert state.get("pending_cancellable_appointments") == upcoming
    assert recommended == []


def test_dashboard_assistant_cancel_intent_for_doctor_is_rejected():
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "cancel appointment",
        {},
    )

    assert "Only patients can cancel" in reply
    assert recommended == []


def test_dashboard_assistant_cancel_upcoming_appointment_prefers_cancel_flow(monkeypatch):
    upcoming = [
        {
            "appointment_id": 202,
            "date": "2026-03-21",
            "time": "14:00",
            "doctor_name": "Casey Morgan",
        }
    ]
    monkeypatch.setattr(pages, "get_appointments_for_patient", lambda _email: upcoming)

    state = {}
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "cancel my upcoming appointment",
        state,
    )

    assert "Select an appointment below" in reply
    assert state.get("pending_cancellable_appointments") == upcoming
    assert recommended == []


def test_doctor_can_cancel_own_upcoming_appointment(isolated_app_db):
    patient_email = "patient-cancel@example.com"
    doctor_email = "doctor-cancel@example.com"

    auth.create_user(
        "Cancel Patient",
        patient_email,
        "secret123",
        "Patient",
        {"dob": "1990-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    auth.create_user(
        "Cancel Doctor",
        doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )

    future_time = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0)
    success, _message, appointment_id = appointments.save_appointment(
        patient_email,
        doctor_email,
        future_time.isoformat(),
    )

    assert success is True
    cancel_success, cancel_message = appointments.cancel_appointment(appointment_id, doctor_email)

    assert cancel_success is True
    assert cancel_message == "Appointment cancelled successfully"
    assert appointments.get_appointments_for_doctor(doctor_email) == []
    assert appointments.get_appointments_for_patient(patient_email) == []


def test_cancel_appointment_rejects_unrelated_user(isolated_app_db):
    patient_email = "patient-unauth@example.com"
    doctor_email = "doctor-unauth@example.com"
    other_email = "other@example.com"

    auth.create_user(
        "Unauth Patient",
        patient_email,
        "secret123",
        "Patient",
        {"dob": "1990-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    auth.create_user(
        "Unauth Doctor",
        doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )
    auth.create_user(
        "Other User",
        other_email,
        "secret123",
        "Patient",
        {"dob": "1992-01-01", "gender": "Other", "phone": "555", "address": "Addr 2"},
    )

    future_time = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0)
    success, _message, appointment_id = appointments.save_appointment(
        patient_email,
        doctor_email,
        future_time.isoformat(),
    )

    assert success is True
    cancel_success, cancel_message = appointments.cancel_appointment(appointment_id, other_email)

    assert cancel_success is False
    assert "not allowed" in cancel_message
    assert len(appointments.get_appointments_for_doctor(doctor_email)) == 1


def test_get_cancelled_appointments_for_patient_returns_latest_first(isolated_app_db):
    patient_email = "patient-banner@example.com"
    doctor_email = "doctor-banner@example.com"

    auth.create_user(
        "Banner Patient",
        patient_email,
        "secret123",
        "Patient",
        {"dob": "1990-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    auth.create_user(
        "Banner Doctor",
        doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )

    first_time = (datetime.now() + timedelta(days=1)).replace(second=0, microsecond=0)
    second_time = (datetime.now() + timedelta(days=2)).replace(second=0, microsecond=0)

    _, _, first_id = appointments.save_appointment(patient_email, doctor_email, first_time.isoformat())
    _, _, second_id = appointments.save_appointment(patient_email, doctor_email, second_time.isoformat())

    appointments.cancel_appointment(first_id, doctor_email)
    appointments.cancel_appointment(second_id, doctor_email)

    cancelled = appointments.get_cancelled_appointments_for_patient(patient_email)

    assert len(cancelled) == 2
    assert cancelled[0]["appointment_id"] == second_id
    assert cancelled[1]["appointment_id"] == first_id
    assert cancelled[0]["doctor_email"] == doctor_email


def test_get_prescriptions_for_doctor_patient_filters_by_doctor_and_patient(isolated_app_db):
    doctor_email = "doctor@example.com"
    other_doctor_email = "other-doctor@example.com"
    patient_email = "patient@example.com"
    other_patient_email = "other-patient@example.com"

    auth.create_user(
        "Dr. Taylor",
        doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )
    auth.create_user(
        "Dr. Morgan",
        other_doctor_email,
        "secret123",
        "Doctor",
        {
            "dob": "1981-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "Clinic 2",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
        },
    )
    auth.create_user(
        "Jamie Patient",
        patient_email,
        "secret123",
        "Patient",
        {"dob": "1990-01-01", "gender": "Other", "phone": "555", "address": "Addr"},
    )
    auth.create_user(
        "Robin Patient",
        other_patient_email,
        "secret123",
        "Patient",
        {"dob": "1991-01-01", "gender": "Other", "phone": "555", "address": "Addr 2"},
    )

    prescription.save_prescription(
        patient_name="Jamie Patient",
        doctor_email=doctor_email,
        diagnosis="Migraine",
        follow_up_days=14,
        general_notes="Hydrate and rest",
        medicines=[{"name": "Sumatriptan", "frequency": "Once daily", "days": 5}],
    )
    prescription.save_prescription(
        patient_name="Jamie Patient",
        doctor_email=other_doctor_email,
        diagnosis="Cold",
        follow_up_days=7,
        general_notes="Monitor symptoms",
        medicines=[{"name": "Cetirizine", "frequency": "Once daily", "days": 7}],
    )
    prescription.save_prescription(
        patient_name="Robin Patient",
        doctor_email=doctor_email,
        diagnosis="Sprain",
        follow_up_days=10,
        general_notes="Ice and elevate",
        medicines=[{"name": "Ibuprofen", "frequency": "Twice daily", "days": 5}],
    )

    results = prescription.get_prescriptions_for_doctor_patient(doctor_email, patient_email)

    assert len(results) == 1
    assert results[0]["diagnosis"] == "Migraine"
    assert results[0]["general_notes"] == "Hydrate and rest"
    assert results[0]["doctor_email"] == doctor_email
