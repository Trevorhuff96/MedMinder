import glob
import os
from datetime import datetime, timedelta

import pytest

import auth
import appointments
import pages
import prescription
import ui_components
from pages import DOB_MAX_DATE, validate_signup_fields


class SessionStateStub(dict):
    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError as exc:
            raise AttributeError(item) from exc

    def __setattr__(self, key, value):
        self[key] = value


class DummyContext:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class StreamlitPageStub:
    def __init__(self, session_state=None, button_clicks=None, input_values=None, select_values=None, form_submit=False):
        self.session_state = session_state or SessionStateStub()
        self.button_clicks = button_clicks or {}
        self.input_values = input_values or {}
        self.select_values = select_values or {}
        self.form_submit = form_submit
        self.query_params = {}
        self.markdowns = []
        self.infos = []
        self.errors = []
        self.successes = []
        self.subheaders = []
        self.rerun_called = False

    def markdown(self, text, **kwargs):
        self.markdowns.append(text)

    def info(self, text, **kwargs):
        self.infos.append(text)

    def error(self, text, **kwargs):
        self.errors.append(text)

    def success(self, text, **kwargs):
        self.successes.append(text)

    def subheader(self, text, **kwargs):
        self.subheaders.append(text)

    def columns(self, spec, **kwargs):
        count = spec if isinstance(spec, int) else len(spec)
        return [DummyContext() for _ in range(count)]

    def tabs(self, labels):
        return [DummyContext() for _ in labels]

    def container(self, **kwargs):
        return DummyContext()

    def form(self, *args, **kwargs):
        return DummyContext()

    def button(self, label, key=None, **kwargs):
        return self.button_clicks.get(key or label, False)

    def selectbox(self, label, options, index=0, key=None, **kwargs):
        lookup_key = key or label
        if lookup_key in self.select_values:
            return self.select_values[lookup_key]
        if options:
            return options[index if index is not None else 0]
        return None

    def text_input(self, label, value="", key=None, **kwargs):
        return self.input_values.get(key or label, value)

    def text_area(self, label, value="", key=None, **kwargs):
        return self.input_values.get(key or label, value)

    def form_submit_button(self, label, **kwargs):
        return self.form_submit

    def checkbox(self, label, value=False, key=None, **kwargs):
        return self.input_values.get(key or label, value)

    def rerun(self):
        self.rerun_called = True


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


def test_get_secret_value_returns_default_when_no_secrets_file(monkeypatch):
    monkeypatch.setattr(ui_components.Path, "home", lambda: ui_components.Path("/tmp/nonexistent-home"))
    monkeypatch.setattr(ui_components.Path, "cwd", lambda: ui_components.Path("/tmp/nonexistent-cwd"))

    value = ui_components._get_secret_value("OLLAMA_MODEL", default="fallback-model")

    assert value == "fallback-model"


def test_get_secret_value_reads_streamlit_secret_when_file_exists(monkeypatch):
    original_exists = ui_components.Path.exists

    def fake_exists(path_obj):
        if str(path_obj).endswith("secrets.toml"):
            return True
        return original_exists(path_obj)

    monkeypatch.setattr(ui_components.Path, "exists", fake_exists)
    monkeypatch.setattr(ui_components.st, "secrets", {"OLLAMA_MODEL": "llama-test"})

    value = ui_components._get_secret_value("OLLAMA_MODEL", default="fallback-model")

    assert value == "llama-test"


def test_appointments_page_doctor_shows_empty_states(monkeypatch):
    st_stub = StreamlitPageStub(
        session_state=SessionStateStub({"user_role": "Doctor", "user_email": "doctor@example.com", "menu_open": False})
    )
    monkeypatch.setattr(pages, "st", st_stub)
    monkeypatch.setattr(pages, "load_custom_styles", lambda: None)
    monkeypatch.setattr(pages, "init_menu_state", lambda: None)
    monkeypatch.setattr(pages, "render_side_drawer", lambda: None)
    monkeypatch.setattr(pages, "get_appointments_for_doctor", lambda _email: [])
    monkeypatch.setattr(pages, "get_past_appointments_for_doctor", lambda _email, _days=None: [])

    pages.appointments_page()

    assert "No upcoming patient appointments." in st_stub.infos
    assert "No past appointments found in the all past filter." in st_stub.infos


def test_appointments_page_patient_stops_when_no_doctors(monkeypatch):
    st_stub = StreamlitPageStub(
        session_state=SessionStateStub(
            {"user_role": "Patient", "user_email": "patient@example.com", "user_name": "Pat", "menu_open": False}
        )
    )
    monkeypatch.setattr(pages, "st", st_stub)
    monkeypatch.setattr(pages, "load_custom_styles", lambda: None)
    monkeypatch.setattr(pages, "init_menu_state", lambda: None)
    monkeypatch.setattr(pages, "render_side_drawer", lambda: None)
    monkeypatch.setattr(pages, "get_appointments_for_patient", lambda _email: [])
    monkeypatch.setattr(pages, "get_past_appointments_for_patient", lambda _email, _days=None: [])
    monkeypatch.setattr(pages, "get_all_doctors", lambda: [])
    monkeypatch.setattr(pages, "render_floating_chatbot", lambda *_args, **_kwargs: None)

    pages.appointments_page()

    assert "You have no upcoming appointments." in st_stub.infos
    assert "No past appointments found in the all past filter." in st_stub.infos
    assert "No doctors are available for booking yet." in st_stub.infos


def test_doctor_dashboard_page_shows_empty_sections(monkeypatch):
    st_stub = StreamlitPageStub(
        session_state=SessionStateStub(
            {"user_email": "doctor@example.com", "user_name": "Taylor", "user_role": "Doctor", "menu_open": False}
        )
    )
    monkeypatch.setattr(pages, "st", st_stub)
    monkeypatch.setattr(pages, "load_custom_styles", lambda: None)
    monkeypatch.setattr(pages, "init_menu_state", lambda: None)
    monkeypatch.setattr(pages, "render_side_drawer", lambda: None)
    monkeypatch.setattr(pages, "get_patient_count_for_doctor", lambda _email: 0)
    monkeypatch.setattr(pages, "get_appointments_for_doctor", lambda _email: [])
    monkeypatch.setattr(pages, "get_patients_for_doctor", lambda _email: [])
    monkeypatch.setattr(pages, "render_dashboard_assistant_tab", lambda *_args, **_kwargs: None)

    pages.doctor_dashboard_page()

    assert "No patients found. Patients will appear here once you create a prescription for them." in st_stub.infos
    assert "No appointments today." in st_stub.infos
    assert "No patients linked to you yet." in st_stub.infos


def test_patient_dashboard_page_shows_cancel_banner_and_empty_summary(monkeypatch):
    st_stub = StreamlitPageStub(
        session_state=SessionStateStub(
            {"user_email": "patient@example.com", "user_name": "Jamie", "user_role": "Patient", "menu_open": False}
        )
    )
    monkeypatch.setattr(pages, "st", st_stub)
    monkeypatch.setattr(pages, "load_custom_styles", lambda: None)
    monkeypatch.setattr(pages, "init_menu_state", lambda: None)
    monkeypatch.setattr(pages, "render_side_drawer", lambda: None)
    monkeypatch.setattr(
        pages,
        "get_cancelled_appointments_for_patient",
        lambda _email: [{"doctor_name": "Alex Carter", "date": "2026-03-10", "time": "09:30"}],
    )
    monkeypatch.setattr(pages, "get_prescriptions_for_patient", lambda _email: [])
    monkeypatch.setattr(pages, "get_appointments_for_patient", lambda _email: [])
    monkeypatch.setattr(pages, "get_care_team_for_patient", lambda _email: [])
    monkeypatch.setattr(pages, "render_dashboard_assistant_tab", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(pages, "render_floating_chatbot", lambda *_args, **_kwargs: None)

    pages.patient_dashboard_page()

    assert any("Appointment cancelled:" in item for item in st_stub.markdowns)
    assert "Your treatment summary will appear here once you receive prescriptions or add doctors to your care team." in st_stub.infos
    assert "No prescriptions found yet." in st_stub.infos
    assert "No prescriptions found. Your medication schedule will appear here once you receive prescriptions." in st_stub.infos
    assert "No doctors in your care team yet. Book an appointment or receive a prescription to add a doctor to your team!" in st_stub.infos


def test_profile_edit_page_doctor_updates_professional_fields(monkeypatch):
    st_stub = StreamlitPageStub(
        session_state=SessionStateStub(
            {
                "user_email": "doctor@example.com",
                "user_role": "Doctor",
                "user_name": "Taylor",
                "profile_edit_mode": True,
                "menu_open": False,
            }
        ),
        input_values={
            "Full Name": "Dr. Taylor Updated",
            "Email": "doctor@example.com",
            "Address": "101 Clinic Ave",
        },
        select_values={"Office Hours": "8:00 AM to 5:00 PM", "Off Day": "Monday"},
        form_submit=True,
    )
    monkeypatch.setattr(pages, "st", st_stub)
    monkeypatch.setattr(pages, "load_custom_styles", lambda: None)
    monkeypatch.setattr(pages, "init_menu_state", lambda: None)
    monkeypatch.setattr(pages, "render_side_drawer", lambda: None)
    monkeypatch.setattr(pages, "render_floating_chatbot", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(
        pages,
        "get_user_profile",
        lambda _email: {
            "name": "Dr. Taylor",
            "email": "doctor@example.com",
            "role": "Doctor",
            "dob": "1980-01-01",
            "gender": "Other",
            "phone": "555",
            "address": "99 Clinic Ave",
            "speciality": "Dentist",
            "office_hours": "9:00 AM to 6:00 PM",
            "off_day": "Friday",
        },
    )
    update_calls = {}

    def fake_update(email, **kwargs):
        update_calls["email"] = email
        update_calls["kwargs"] = kwargs
        return True, "Profile updated successfully!"

    monkeypatch.setattr(pages, "update_user_profile", fake_update)

    pages.profile_edit_page()

    assert update_calls["email"] == "doctor@example.com"
    assert update_calls["kwargs"]["address"] == "101 Clinic Ave"
    assert update_calls["kwargs"]["office_hours"] == "8:00 AM to 5:00 PM"
    assert update_calls["kwargs"]["off_day"] == "Monday"
    assert st_stub.session_state["profile_edit_mode"] is False
    assert st_stub.session_state["user_name"] == "Dr. Taylor Updated"
    assert st_stub.rerun_called is True


def test_render_floating_chatbot_builds_component_html(monkeypatch):
    captured = {}

    monkeypatch.setattr(ui_components, "get_chatbot_component_css", lambda: ".mm-chatbot-wrap { color: red; }")
    monkeypatch.setattr(ui_components, "_get_secret_value", lambda key, default="": default)
    monkeypatch.setattr(
        ui_components,
        "_build_prescription_summary",
        lambda _email: "Here is your latest prescription summary:<br><strong>Amoxicillin</strong>",
    )
    monkeypatch.setattr(ui_components, "get_specialities", lambda: ["Dentist", "Neurologist"])
    monkeypatch.setattr(
        ui_components,
        "get_doctors_by_speciality",
        lambda speciality: (
            [{"name": "Taylor Nguyen", "email": "taylor@example.com", "speciality": speciality}]
            if speciality == "Dentist"
            else []
        ),
    )

    def fake_html(html, height=None, scrolling=None):
        captured["html"] = html
        captured["height"] = height
        captured["scrolling"] = scrolling

    monkeypatch.setattr(ui_components.components, "html", fake_html)

    ui_components.render_floating_chatbot(
        patient_name="Jamie",
        patient_email="jamie@example.com",
        patient_role="Patient",
    )

    html = captured["html"]
    assert "Hi Jamie" in html
    assert "Here is your latest prescription summary" in html
    assert "Taylor Nguyen" in html
    assert "taylor@example.com" in html
    assert "jamie@example.com" in html
    assert "Dentist" in html
    assert captured["height"] == 520
    assert captured["scrolling"] is False


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


def test_assistant_state_key_sanitizes_role_and_email():
    key = pages._assistant_state_key("Doctor", "doc.test@example.com")

    assert key == "dashboard_assistant_state_doctor_doc_test_at_example_com"


def test_compact_assistant_context_trims_messages_and_builds_summary():
    state = {
        "messages": [
            {"role": "user", "content": f"User message {idx} " + ("x" * 140)}
            if idx % 2 == 0
            else {"role": "assistant", "content": f"Assistant message {idx}"}
            for idx in range(18)
        ],
        "summary": "Earlier summary",
    }

    pages._compact_assistant_context(state, max_messages=10, max_summary_chars=500)

    assert len(state["messages"]) == 10
    assert len(state["summary"]) <= 500
    assert "User:" in state["summary"]
    assert "Assistant:" in state["summary"]
    assert "..." in state["summary"]


def test_infer_speciality_from_text_prefers_direct_match():
    result = pages._infer_speciality_from_text(
        "I think I need a Neurologist because of recurring dizziness.",
        ["Cardiologist", "Neurologist", "Dentist"],
    )

    assert result == "Neurologist"


def test_infer_speciality_from_text_falls_back_to_general_practitioner():
    result = pages._infer_speciality_from_text(
        "I feel tired and have a cough.",
        ["Dentist", "General Practitioner"],
    )

    assert result == "General Practitioner"


def test_build_prescription_summary_returns_empty_message(monkeypatch):
    monkeypatch.setattr(ui_components, "get_prescriptions_for_patient", lambda _email: [])

    summary = ui_components._build_prescription_summary("patient@example.com")

    assert summary == "I could not find any prescriptions for you yet."


def test_build_prescription_summary_formats_latest_medicines(monkeypatch):
    monkeypatch.setattr(
        ui_components,
        "get_prescriptions_for_patient",
        lambda _email: [
            {
                "medicines": [
                    {"name": "Amoxicillin", "dosage": "500 mg", "frequency": "Twice daily"},
                    {"name": "Cetirizine", "dosage": "10 mg", "frequency": "Once daily"},
                ]
            }
        ],
    )

    summary = ui_components._build_prescription_summary("patient@example.com")

    assert "Here is your latest prescription summary:" in summary
    assert "<strong>Amoxicillin</strong>: Dosage 500 mg, Frequency Twice daily" in summary
    assert "<strong>Cetirizine</strong>: Dosage 10 mg, Frequency Once daily" in summary


def test_build_symptom_speciality_map_contains_expected_keywords():
    symptom_map = ui_components._build_symptom_speciality_map()

    assert "Cardiologist" in symptom_map
    assert "chest pain" in symptom_map["Cardiologist"]
    assert "Dentist" in symptom_map
    assert "toothache" in symptom_map["Dentist"]


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


def test_dashboard_assistant_uses_ai_summary_for_patient_appointments(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_appointments_for_patient",
        lambda _email: [
            {
                "date": "2026-03-20",
                "time": "09:30",
                "doctor_name": "Alex Carter",
                "speciality": "Dentist",
            }
        ],
    )
    monkeypatch.setattr(pages, "get_past_appointments_for_patient", lambda _email: [])
    monkeypatch.setattr(
        pages,
        "_generate_dashboard_ai_summary",
        lambda summary_type, user_role, records, **kwargs: "AI summary: 1 upcoming appointment with Dr. Alex Carter.",
    )

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Show my upcoming appointments",
        {},
    )

    assert reply == "AI summary: 1 upcoming appointment with Dr. Alex Carter."
    assert recommended == []


def test_build_patient_appointment_summary_combines_upcoming_and_past(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_appointments_for_patient",
        lambda _email: [
            {"date": "2026-04-01", "time": "09:00", "doctor_name": "Alex Carter", "speciality": "Dentist"}
        ],
    )
    monkeypatch.setattr(
        pages,
        "get_past_appointments_for_patient",
        lambda _email: [
            {"date": "2026-03-01", "time": "10:00", "doctor_name": "Taylor Nguyen", "speciality": "Neurologist"}
        ],
    )

    reply = pages._build_patient_appointment_summary("patient@example.com")

    assert "You have 1 upcoming appointment(s)." in reply
    assert "2026-04-01 at 09:00 with Dr. Alex Carter (Dentist)" in reply
    assert "You also have 1 past appointment(s) in your history." in reply


def test_build_doctor_appointment_summary_upcoming_includes_today_count(monkeypatch):
    today_str = datetime.now().strftime("%Y-%m-%d")
    monkeypatch.setattr(
        pages,
        "get_appointments_for_doctor",
        lambda _email: [
            {"date": today_str, "time": "09:00", "patient_name": "Jamie Patient"},
            {"date": "2026-12-01", "time": "14:00", "patient_name": "Robin Patient"},
        ],
    )

    reply = pages._build_doctor_appointment_summary("doctor@example.com", focus="upcoming")

    assert "You have 2 upcoming appointment(s)." in reply
    assert "Today's appointments: 1." in reply
    assert f"- {today_str} at 09:00 with Jamie Patient" in reply


def test_get_appointment_query_focus_detects_past_and_upcoming():
    assert pages._get_appointment_query_focus("Show my past appointments") == "past"
    assert pages._get_appointment_query_focus("Do I have any future appointments?") == "upcoming"
    assert pages._get_appointment_query_focus("Tell me about my schedule") == "all"
    assert pages._get_appointment_query_focus("hello there") == "none"


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


def test_dashboard_assistant_uses_ai_summary_for_patient_prescriptions(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_prescriptions_for_patient",
        lambda _email: [
            {
                "diagnosis": "Seasonal allergies",
                "doctor_name": "Taylor Nguyen",
                "created_at": "2026-02-01T10:30:00",
                "medicines": [{"name": "Cetirizine"}],
            }
        ],
    )
    monkeypatch.setattr(
        pages,
        "_generate_dashboard_ai_summary",
        lambda summary_type, user_role, records, **kwargs: "AI summary: latest prescription highlights.",
    )

    state = {}
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Can you show my prescriptions?",
        state,
    )

    assert reply == "AI summary: latest prescription highlights."
    assert recommended == []
    assert len(state["last_prescriptions"]) == 1


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


def test_dashboard_assistant_falls_back_when_ai_summary_missing_for_patient_prescriptions(monkeypatch):
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
    monkeypatch.setattr(pages, "_generate_dashboard_ai_summary", lambda *args, **kwargs: "")

    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Patient",
        "patient@example.com",
        "Can you show my prescriptions?",
        {},
    )

    assert "I found 1 prescription on file." in reply
    assert "Cetirizine, Fluticasone" in reply
    assert recommended == []


def test_build_ai_summary_payload_for_doctor_prescriptions_limits_and_sanitizes_records():
    payload = pages._build_ai_summary_payload(
        "prescriptions",
        "Doctor",
        [
            {
                "created_at": "2026-03-10T09:00:00",
                "diagnosis": "Migraine",
                "doctor_name": "Taylor Nguyen",
                "follow_up_days": 14,
                "medicines": [
                    {"name": "Sumatriptan", "dosage": "50 mg", "frequency": "Once daily", "days": 5, "timing": "Morning"},
                    {"name": "", "dosage": "ignored"},
                    "invalid",
                ],
            }
        ],
        patient_name="Jamie Patient",
    )

    assert payload["summary_type"] == "prescriptions"
    assert payload["user_role"] == "Doctor"
    assert payload["patient_name"] == "Jamie Patient"
    assert payload["record_count"] == 1
    assert payload["records"][0]["diagnosis"] == "Migraine"
    assert payload["records"][0]["medicines"] == [
        {
            "name": "Sumatriptan",
            "dosage": "50 mg",
            "frequency": "Once daily",
            "days": 5,
            "timing": "Morning",
        }
    ]


def test_find_doctor_patient_match_uses_unique_token_match(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_patients_for_doctor",
        lambda _email: [
            {"name": "Jamie Carter", "email": "jamie@example.com"},
            {"name": "Robin Mills", "email": "robin@example.com"},
        ],
    )

    match = pages._find_doctor_patient_match("doctor@example.com", "Can you review Robin's prescription?")

    assert match == {"name": "Robin Mills", "email": "robin@example.com"}


def test_find_doctor_patient_match_returns_none_for_ambiguous_tokens(monkeypatch):
    monkeypatch.setattr(
        pages,
        "get_patients_for_doctor",
        lambda _email: [
            {"name": "Jamie Carter", "email": "jamie@example.com"},
            {"name": "Jamie Morgan", "email": "jamie2@example.com"},
        ],
    )

    match = pages._find_doctor_patient_match("doctor@example.com", "Show Jamie's prescriptions")

    assert match is None


def test_build_doctor_patient_prescription_summary_for_single_prescription():
    summary = pages._build_doctor_patient_prescription_summary(
        "Jamie Patient",
        [
            {
                "diagnosis": "Migraine",
                "follow_up_days": 14,
                "created_at": "2026-03-10T09:00:00",
                "medicines": [{"name": "Sumatriptan"}, {"name": "Ibuprofen"}],
            }
        ],
    )

    assert "I found 1 prescription for Jamie Patient." in summary
    assert "2026-03-10: Migraine" in summary
    assert "Medicines: Sumatriptan, Ibuprofen" in summary
    assert "Follow-up: 14 day(s)" in summary


def test_get_prescription_followup_focus_detects_route_and_follow_up():
    assert pages._get_prescription_followup_focus("What is the route for this medicine?") == "route"
    assert pages._get_prescription_followup_focus("When is my follow up?") == "follow_up"
    assert pages._get_prescription_followup_focus("tell me something else") == "none"


def test_build_prescription_followup_response_handles_missing_context():
    reply = pages._build_prescription_followup_response([], "frequency")

    assert "could not find any prescription context yet" in reply.lower()


def test_build_prescription_followup_response_returns_follow_up_timeline():
    reply = pages._build_prescription_followup_response(
        [{"follow_up_days": 21, "medicines": []}],
        "follow_up",
    )

    assert reply == "Your follow-up timeline is 21 day(s) based on the latest prescription."


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


def test_build_medication_schedule_supports_every_x_hours_pattern():
    schedule = pages.build_medication_schedule(
        [
            {
                "doctor_name": "Taylor Nguyen",
                "medicines": [
                    {
                        "name": "Antibiotic",
                        "dosage": "250 mg",
                        "frequency": "Every 6 hours",
                        "directions": "Take with water",
                    }
                ],
            }
        ]
    )

    assert "Antibiotic" == schedule["8 AM"][0]["name"]
    assert "Antibiotic" == schedule["2 PM"][0]["name"]
    assert "Antibiotic" == schedule["8 PM"][0]["name"]


def test_calculate_medication_adherence_uses_taken_doses(monkeypatch):
    monkeypatch.setattr(
        pages.st,
        "session_state",
        SessionStateStub({"medication_doses_taken": {"dose_1": True, "dose_2": False}}),
    )
    prescriptions = [
        {
            "doctor_name": "Taylor Nguyen",
            "medicines": [
                {"name": "A", "dosage": "5 mg", "frequency": "Once daily", "directions": ""},
                {"name": "B", "dosage": "10 mg", "frequency": "Once daily", "directions": ""},
            ],
        }
    ]

    adherence = pages.calculate_medication_adherence(prescriptions)

    assert adherence["taken"] == 1
    assert adherence["total"] == 2
    assert adherence["adherence_percent"] == 50
    assert adherence["trend"] == "-2%"


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

def test_dashboard_assistant_cancel_intent_for_doctor_lists_upcoming_appointments(monkeypatch):
    upcoming = [
        {
            "appointment_id": 303,
            "date": "2026-03-22",
            "time": "11:00",
            "patient_name": "Jordan Lee",
        }
    ]
    monkeypatch.setattr(pages, "get_appointments_for_doctor", lambda _email: upcoming)

    state = {}
    reply, recommended = pages._generate_dashboard_assistant_reply(
        "Doctor",
        "doctor@example.com",
        "cancel appointment",
        state,
    )

    assert "Select an appointment below" in reply
    assert state.get("pending_cancellable_appointments") == upcoming
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
