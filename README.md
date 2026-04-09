# MedMinder

MedMinder is a Streamlit-based healthcare coordination prototype for two roles: `Patient` and `Doctor`. It combines account onboarding, role-based dashboards, prescription management, appointment scheduling, and a lightweight AI assistant intended to help users navigate the system without replacing clinical judgment.

This README consolidates the repository's development history into one place and explains four things clearly:

1. What the system does today
2. How AI was used in both the process and the product
3. What mechanisms currently enforce trust and safety
4. Which limitations still remain

## Project History

The repository history shows a steady progression from planning artifacts into an implemented prototype:

- `2026-01-15` to `2026-01-23`: the project began with the system proposal, AI-assisted requirements elicitation, and the first "trust gates" documents.
- `2026-02-02`: design-decision documents were added, including role-separated shell ideas and guardrail-oriented component planning.
- `2026-02-10` to `2026-02-21`: the Streamlit app, authentication flow, onboarding forms, and SQLite-backed role-specific data model were introduced.
- `2026-02-24` to `2026-02-25`: the UI expanded to include dashboards, prescriptions, profile editing, filtering, and the first chatbot interactions.
- `2026-02-26` to `2026-03-03`: LLM-backed chatbot behavior, doctor recommendations, medication reminders, doctor listing, appointment booking, and chatbot-to-appointment routing were added.
- `2026-03-04` to `2026-03-24`: unit tests, Playwright smoke tests, doctor patient-management views, past/upcoming appointment tabs, treatment summary views, and profile-edit improvements were added.
- `2026-03-30` to `2026-04-02`: password handling was improved, trust claims were documented, CI was updated, and doctors gained chatbot-supported appointment cancellation.

The result is not a finished production health platform. It is a working prototype that tries to make trust explicit while gradually adding AI-assisted features.

## Current System

### User roles

MedMinder supports two mutually exclusive roles:

- `Patient`
- `Doctor`

After sign-in, the app routes users to different dashboards and workflows based on the role stored in the `users` table.

### Core capabilities

Implemented capabilities in the current codebase include:

- Account creation and sign-in backed by SQLite
- Separate doctor and patient profile records
- Doctor speciality, office-hours, and off-day capture during onboarding
- Patient and doctor dashboards with role-specific views
- Prescription creation and retrieval
- Patient prescription filtering by diagnosis, medication, and doctor
- Appointment booking and cancellation
- Past and upcoming appointment history
- Care-team linking between patients and doctors after confirmed appointments
- Doctor patient-roster views restricted to linked patients
- Patient treatment summary cards built from prescriptions and care-team data
- Floating chatbot and dashboard assistant interactions for booking, cancellations, prescription summaries, appointment summaries, and doctor recommendations

### Main files

- [`streamlit_app.py`](/Users/achakr13/Documents/GitHub/MedMinder/streamlit_app.py): app entry point and route/session coordination
- [`pages.py`](/Users/achakr13/Documents/GitHub/MedMinder/pages.py): role-specific pages, dashboards, assistant logic, treatment summary UI
- [`auth.py`](/Users/achakr13/Documents/GitHub/MedMinder/auth.py): authentication, profile persistence, role-aware data access
- [`appointments.py`](/Users/achakr13/Documents/GitHub/MedMinder/appointments.py): appointment and care-team storage rules
- [`prescription.py`](/Users/achakr13/Documents/GitHub/MedMinder/prescription.py): prescription schema and retrieval helpers
- [`ui_components.py`](/Users/achakr13/Documents/GitHub/MedMinder/ui_components.py): floating chatbot UI and Ollama integration
- [`.github/workflows/basic_action.yml`](/Users/achakr13/Documents/GitHub/MedMinder/.github/workflows/basic_action.yml): CI for tests and docs-change notifications

## How AI Was Used

AI appears in this project in two distinct ways: during design, and inside the prototype itself.

### 1. AI-assisted design and requirements work

The `docs/` folder shows that AI was used early to help generate and refine:

- functional requirements
- trust-gate statements
- appointment-management user stories
- note-synthesis requirements
- design alternatives for role-separated UI architecture

This was useful for breadth and speed. It also influenced the language of the trust model, especially around:

- hallucination risk
- patient/doctor role separation
- doctor approval of AI-generated content
- data-binding to the correct patient and visit

At the same time, the repository history makes it clear that the code does not implement every AI-generated requirement. The docs were used as a planning aid, not as proof that a feature exists.

### 2. AI inside the running application

The current app uses AI in narrower, more controlled ways:

- The floating chatbot can call a local Ollama model through `OLLAMA_BASE_URL` and `OLLAMA_MODEL`.
- The chatbot uses a constrained system prompt that explicitly tells the model not to diagnose.
- Doctor recommendation starts with deterministic symptom-to-speciality keyword matching and only uses the LLM as a fallback.
- The dashboard assistant can generate Ollama-backed appointment and prescription summaries from structured records, with deterministic fallbacks when Ollama is unavailable.
- The patient treatment summary is labeled `AI-Generated`, but in code it is actually a deterministic aggregate built from stored prescriptions and care-team data.

This means the "AI" in MedMinder is currently a hybrid:

- true LLM use for conversational replies, speciality fallback, and dashboard summary rewriting
- non-LLM computed summaries for several trust-sensitive views

That hybrid approach reduces risk compared with letting the model invent medical state from scratch.

## How Trust Is Enforced

Trust in MedMinder is enforced mostly through application structure, database checks, and intentionally narrow AI scope.

### Role separation

Trust starts with role-based routing:

- users log in with a stored role
- the app sends them to either the doctor or patient experience
- the UI only exposes role-appropriate actions

This is not a full enterprise authorization layer, but it does prevent many accidental cross-role interactions at the app level.

### Patient-doctor access boundaries

The code enforces a few important data boundaries:

- Doctors see linked patients through the `care_team` relationship.
- A patient is linked to a doctor when an appointment is successfully created.
- If the last confirmed appointment between a patient and doctor is cancelled and the patient and doctor do not have any previous appointments together, the care-team link is removed.
- Doctor-specific prescription lookups are scoped to prescriptions that doctor wrote for the selected patient.

These rules are a direct attempt to satisfy the trust claim that doctors should not freely browse unrelated patient data.

### Appointment integrity

Appointment trust is backed by database checks rather than chatbot text alone:

- bookings are written through SQLite
- duplicate booking for the same patient, doctor, date, and time is rejected
- doctor-side booked-slot lookups are used to keep open-slot views accurate
- cancellation requires the requester to be either the patient or the doctor on the appointment
- the patient dashboard surfaces cancellation notices from persisted appointment status

This is one of the strongest trust areas in the current implementation because the chatbot ultimately routes to backend-backed scheduling state.

### Reduced AI authority

The assistant is intentionally not the source of truth for clinical state:

- the prompt tells the chatbot not to diagnose
- doctor recommendation can fall back to deterministic rules
- prescription answers are generated from stored medication data
- appointment-history answers are generated from stored appointment data
- treatment summary cards derive from saved prescriptions and care-team links

In other words, AI helps users navigate and summarize, but the trusted record remains the database.

### Transparency signals

A few trust-oriented transparency choices are already visible:

- treatment summaries are explicitly labeled `AI-Generated`
- chatbot guidance encourages contact with a doctor for urgent symptoms
- trust claims and limitations are documented in the repository
- tests exist for authentication, profile updates, appointments, and assistant-related helpers
- CI runs `pytest` on GitHub Actions

## What The System Can Credibly Claim Today

Based on the current code and the repository's trust-claims document, the strongest defensible claims are:

- Patients and doctors can sign up and log in.
- Patients can book and cancel appointments.
- Doctors can cancel appointments.
- Patients can view prescriptions associated with their account.
- Doctors can view patient rosters derived from care-team links.
- Patients can see a consolidated treatment-summary view assembled from multiple providers' prescription history and care-team records.
- The chatbot can help route users to booking flows, summarize appointments, summarize prescriptions, and suggest doctors by speciality.

## Where Limitations Remain

This is the most important section for trust. Several planned safeguards are not yet implemented, and some current controls are prototype-grade only.

### Security and identity limitations

- There is no forgot-password flow.
- There is no email verification.
- There is no multi-factor authentication.
- The app should not be described as HIPAA-compliant based on the current codebase alone.

### Audit and governance limitations

- The requirements mention audit logging for demographic changes, but the current code does not implement a real audit log table or audit trail.
- There is no approval workflow for AI-generated patient summaries by a doctor.
- There is no version history for generated summaries.
- There is no explicit source-note to summary traceability mechanism.

### AI and medical-safety limitations

- The chatbot still relies on a general-purpose LLM for open-ended replies, which means hallucination risk is reduced, not eliminated.
- The assistant prompt says "do not diagnose," but prompt-only controls are weaker than hard policy enforcement.
- The "AI-Generated" treatment summary is an aggregate overview, not a clinician-reviewed note synthesis pipeline.
- The note-synthesis requirements in the docs are broader than what is implemented in code.
- There is no confidence scoring, human approval gate, or medical contradiction checker.

### Scheduling limitations

- The system prevents double-booking for the same doctor/time slot, but a patient can still book the same time with different doctors.
- Booking confirmation is shown on-screen, but there is no external notification channel such as email or SMS.
- The chatbot helps users reach booking and cancellation flows, but it is not a fully autonomous scheduler with robust transaction handling.
- Doctor availability is simplified to office hours and off-day metadata rather than a full editable availability engine.

### Data-model and product limitations

- Health metrics mentioned in the requirements are not implemented as persistent, patient-specific stored records.
- Medication adherence on the patient dashboard is session-based and simplistic.
- The repository currently includes a local SQLite database file, which is fine for prototyping but not for multi-user deployment.
- Some trust requirements in the documents remain aspirational and should be read as target behavior, not current guarantees.

## Running The Project

### Requirements

- Python 3.11 recommended
- Streamlit
- SQLite
- Optional: Ollama for chatbot LLM responses
- Optional: Node.js for Playwright tests

### Install

```bash
pip install -r requirements.txt
```

For end-to-end tests:

```bash
npm install
```

### Start the app

```bash
streamlit run streamlit_app.py
```

### Optional LLM configuration

The floating chatbot can connect to Ollama if you provide:

- `OLLAMA_BASE_URL`
- `OLLAMA_MODEL`

If those are missing or the model is unavailable, LLM-backed chat behavior is limited and the UI falls back to safer deterministic behavior where available.

### Tests

Unit tests:

```bash
pytest
```

Playwright smoke tests:

```bash
npm test
```

## Final Assessment

MedMinder is best understood as a trust-aware healthcare prototype rather than a production-ready medical platform. Its strongest design choice is that the database, not the model, remains the authority for appointments, prescriptions, and most patient-facing summaries. Its biggest remaining gap is that several trust controls described in the planning documents, especially around security hardening, auditability, and clinician approval of AI output, are only partially implemented or not implemented yet.

That gap matters. The repository is valuable because it makes the trust problem visible, not because it has already solved it completely.
