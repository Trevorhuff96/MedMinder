"""
Reusable UI components for MedMinder pages.
"""

import json
import os
from pathlib import Path
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from auth import get_doctors_by_speciality, get_specialities
from prescription import get_prescriptions_for_patient
from styles import get_chatbot_component_css


def _get_secret_value(key: str, default: str = "") -> str:
    """Read a Streamlit secret only when a secrets.toml file exists."""
    secrets_paths = [
        Path.home() / ".streamlit" / "secrets.toml",
        Path.cwd() / ".streamlit" / "secrets.toml",
    ]

    if not any(path.exists() for path in secrets_paths):
        return default

    try:
        return st.secrets.get(key, default)
    except Exception:
        return default


def _build_prescription_summary(patient_email: str) -> str:
    """Build a short medication summary HTML for chatbot responses."""
    prescriptions = get_prescriptions_for_patient(patient_email)
    if not prescriptions:
        return "I could not find any prescriptions for you yet."

    medicines = prescriptions[0].get("medicines", [])
    summary_lines = []
    for med in medicines:
        med_name = escape(str(med.get("name") or "").strip())
        if not med_name:
            continue
        dosage = escape(str(med.get("dosage") or "-").strip())
        frequency = escape(str(med.get("frequency") or "-").strip())
        summary_lines.append(
            f"<strong>{med_name}</strong>: Dosage {dosage}, Frequency {frequency}"
        )

    if not summary_lines:
        return "I found your prescription, but medicine details are not available."

    return "Here is your latest prescription summary:<br>" + "<br>".join(summary_lines)


def _build_symptom_speciality_map():
    """Return symptom keywords used to suggest a speciality."""
    return {
        "Cardiologist": [
            "chest pain",
            "heart",
            "palpitation",
            "palpitations",
            "blood pressure",
            "hypertension",
            "shortness of breath",
            "breathless",
        ],
        "Dentist": [
            "tooth",
            "teeth",
            "gum",
            "gums",
            "jaw pain",
            "cavity",
            "toothache",
            "oral",
        ],
        "Neurologist": [
            "headache",
            "migraine",
            "seizure",
            "dizziness",
            "numbness",
            "tingling",
            "memory",
            "nerve",
            "brain",
        ],
        "Pediatrician": [
            "child",
            "kid",
            "baby",
            "infant",
            "toddler",
            "newborn",
            "son",
            "daughter",
        ],
        "General Practitioner": [
            "fever",
            "cold",
            "cough",
            "flu",
            "infection",
            "pain",
            "fatigue",
            "sore throat",
            "body ache",
        ],
    }


def render_floating_chatbot(patient_name: str = "", patient_email: str = "", patient_role: str = "Patient") -> None:
    """Render a floating chatbot launcher and greeting panel."""
    chatbot_css = get_chatbot_component_css()
    safe_name = escape((patient_name or "").strip())
    greeting = f"Hi {safe_name} \U0001F44B" if safe_name else "Hi \U0001F44B"
    ollama_base_url = _get_secret_value("OLLAMA_BASE_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = _get_secret_value("OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    llm_system_prompt = (
        "You are MedMinder Assistant. Give concise, helpful, safe health support. "
        "Do not provide diagnosis. Encourage contacting a doctor for urgent symptoms."
    )
    prescription_summary = _build_prescription_summary(patient_email or "")
    prescription_summary_json = json.dumps(prescription_summary)
    speciality_options = get_specialities()
    speciality_options_json = json.dumps(speciality_options)
    doctors_by_speciality = {
        speciality: [
            {
                "name": escape(str(doctor.get("name") or "").strip()),
                "email": escape(str(doctor.get("email") or "").strip()),
                "speciality": escape(str(doctor.get("speciality") or "").strip()),
            }
            for doctor in get_doctors_by_speciality(speciality)
        ]
        for speciality in speciality_options
    }
    doctors_by_speciality_json = json.dumps(doctors_by_speciality)
    symptom_speciality_map = {
        speciality: keywords
        for speciality, keywords in _build_symptom_speciality_map().items()
        if speciality in speciality_options
    }
    symptom_speciality_map_json = json.dumps(symptom_speciality_map)
    ollama_base_url_json = json.dumps(ollama_base_url)
    ollama_model_json = json.dumps(ollama_model)
    llm_system_prompt_json = json.dumps(llm_system_prompt)
    patient_name_json = json.dumps(patient_name or "")
    patient_email_json = json.dumps(patient_email or "")
    patient_role_json = json.dumps(patient_role or "Patient")
    components.html(
        """
        <!doctype html>
        <html>
        <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <style>
        __MM_CHATBOT_COMPONENT_CSS__
        </style>
        </head>
        <body>
        <div class="mm-chatbot-wrap">
            <input type="checkbox" id="mm-chatbot-toggle" class="mm-chatbot-toggle" />
            <label class="mm-chatbot-btn" for="mm-chatbot-toggle" aria-label="Open chatbot">&#128172;</label>
            <div class="mm-chatbot-panel" role="dialog" aria-label="Chatbot window">
                <div class="mm-chatbot-header">MedMinder Assistant</div>
                <div class="mm-chatbot-body">
                    <div class="mm-chatbot-thread">
                        <p class="mm-chatbot-message">__MM_CHATBOT_GREETING__</p>
                        <p class="mm-chatbot-message">What can I help you with today?</p>
                        <div class="mm-chatbot-options">
                            <button
                                class="mm-chatbot-option"
                                type="button"
                                onclick="handleBookAppointment(this);"
                            >
                                Book Appointment
                            </button>
                            <button
                                class="mm-chatbot-option"
                                type="button"
                                onclick="appendUserMessage(this, 'See Prescription'); appendBotMessage(this, rxSummary, true);"
                            >
                                See Prescription
                            </button>
                        </div>
                    </div>
                    <form class="mm-chatbot-composer" onsubmit="return false;">
                        <input
                            class="mm-chatbot-input"
                            type="text"
                            placeholder="Type your message..."
                            onkeydown="if (event.key === 'Enter') { event.preventDefault(); this.nextElementSibling.click(); }"
                        />
                        <button
                            class="mm-chatbot-send"
                            type="button"
                            onclick="handleSendMessage(this);"
                        >
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <script>
        const rxSummary = __MM_RX_SUMMARY_JSON__;
        const specialityOptions = __MM_SPECIALITY_OPTIONS_JSON__;
        const doctorsBySpeciality = __MM_DOCTORS_BY_SPECIALITY_JSON__;
        const symptomSpecialityMap = __MM_SYMPTOM_SPECIALITY_MAP_JSON__;
        const ollamaBaseUrl = __MM_OLLAMA_BASE_URL_JSON__;
        const ollamaModel = __MM_OLLAMA_MODEL_JSON__;
        const llmSystemPrompt = __MM_LLM_SYSTEM_PROMPT_JSON__;
        const currentUserName = __MM_USER_NAME_JSON__;
        const currentUserEmail = __MM_USER_EMAIL_JSON__;
        const currentUserRole = __MM_USER_ROLE_JSON__;
        const conversation = [];
        let awaitingSymptomInput = false;

        function appendMessage(target, text, isUser, asHtml, storeInConversation = true) {
            const body = target.closest('.mm-chatbot-body');
            if (!body) return;
            const thread = body.querySelector('.mm-chatbot-thread');
            if (!thread) return;
            const bubble = document.createElement('p');
            bubble.className = isUser ? 'mm-chatbot-message user' : 'mm-chatbot-message';
            if (asHtml) {
                bubble.innerHTML = text;
            } else {
                bubble.textContent = text;
            }
            thread.appendChild(bubble);
            thread.scrollTop = thread.scrollHeight;
            if (storeInConversation) {
                conversation.push({
                    role: isUser ? 'user' : 'assistant',
                    content: text,
                });
            }
        }

        function appendUserMessage(target, text) {
            appendMessage(target, text, true, false);
        }

        function appendBotMessage(target, text, asHtml, storeInConversation = true) {
            appendMessage(target, text, false, !!asHtml, storeInConversation);
        }

        function navigateToAppointment(doctorEmail) {
            const parentWin = window.parent;
            if (!parentWin || !parentWin.location || !parentWin.history) return;
            const params = new URLSearchParams(parentWin.location.search || "");
            params.set("doctor_email", doctorEmail || "");
            params.set("logged_in", "1");
            if (currentUserName) params.set("user_name", currentUserName);
            if (currentUserEmail) params.set("user_email", currentUserEmail);
            if (currentUserRole) params.set("user_role", currentUserRole);
            parentWin.location.href = `/?${params.toString()}`;
        }

        function appendDoctorButtons(target, doctors) {
            const body = target.closest('.mm-chatbot-body');
            if (!body) return;
            const thread = body.querySelector('.mm-chatbot-thread');
            if (!thread || !Array.isArray(doctors) || doctors.length === 0) return;

            const topDoctors = doctors.slice(0, 5);

            const optionsWrap = document.createElement('div');
            optionsWrap.className = 'mm-chatbot-options';

            topDoctors.forEach((doctor) => {
                const doctorBtn = document.createElement('button');
                doctorBtn.type = 'button';
                doctorBtn.className = 'mm-chatbot-option';
                doctorBtn.textContent = doctor.name;
                doctorBtn.addEventListener('click', () => navigateToAppointment(doctor.email));
                optionsWrap.appendChild(doctorBtn);
            });

            thread.appendChild(optionsWrap);
            thread.scrollTop = thread.scrollHeight;
        }

        function appendTypingIndicator(target) {
            const body = target.closest('.mm-chatbot-body');
            if (!body) return null;
            const thread = body.querySelector('.mm-chatbot-thread');
            if (!thread) return null;
            const bubble = document.createElement('p');
            bubble.className = 'mm-chatbot-message';
            bubble.textContent = '...';
            thread.appendChild(bubble);
            thread.scrollTop = thread.scrollHeight;
            return bubble;
        }

        async function generateLlmReply(userText) {
            if (!ollamaBaseUrl || !ollamaModel) {
                return "I can help once LLM is configured. Please set OLLAMA_BASE_URL and OLLAMA_MODEL.";
            }

            const recentConversation = conversation.slice(-8);
            const messages = [
                { role: 'system', content: llmSystemPrompt },
                ...recentConversation,
                { role: 'user', content: userText },
            ];

            const response = await fetch(`${ollamaBaseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: ollamaModel,
                    messages,
                    stream: false,
                    options: {
                        temperature: 0.3,
                    },
                }),
            });

            if (!response.ok) {
                return "I couldn't generate a response right now. Ensure Ollama is running and the model is pulled.";
            }

            const data = await response.json();
            return data?.message?.content?.trim() || "I couldn't generate a response right now.";
        }

        async function handleUserInput(target, userText) {
            appendUserMessage(target, userText);
            if (awaitingSymptomInput) {
                awaitingSymptomInput = false;
                await suggestSpecialityFromSymptoms(target, userText);
                return;
            }
            const typingBubble = appendTypingIndicator(target);
            try {
                const llmReply = await generateLlmReply(userText);
                if (typingBubble) typingBubble.remove();
                appendBotMessage(target, llmReply, false);
            } catch (error) {
                if (typingBubble) typingBubble.remove();
                appendBotMessage(target, "I couldn't generate a response right now. Please try again.", false);
            }
        }

        async function handleSendMessage(target) {
            const body = target.closest('.mm-chatbot-body');
            if (!body) return;
            const input = body.querySelector('.mm-chatbot-input');
            if (!input) return;
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            await handleUserInput(target, text);
        }

        function findSuggestedSpeciality(symptomsText) {
            const normalizedText = (symptomsText || '').toLowerCase();
            let bestMatch = '';
            let bestScore = 0;

            Object.entries(symptomSpecialityMap).forEach(([speciality, keywords]) => {
                let score = 0;
                keywords.forEach((keyword) => {
                    if (normalizedText.includes(keyword.toLowerCase())) {
                        score += keyword.includes(' ') ? 2 : 1;
                    }
                });
                if (score > bestScore) {
                    bestScore = score;
                    bestMatch = speciality;
                }
            });

            if (bestMatch && bestScore >= 2) {
                return { speciality: bestMatch, confident: true };
            }

            if (specialityOptions.includes('General Practitioner')) {
                return { speciality: 'General Practitioner', confident: false };
            }

            return { speciality: specialityOptions[0] || 'a doctor', confident: false };
        }

        async function suggestSpecialityWithLlm(symptomsText) {
            if (!ollamaBaseUrl || !ollamaModel || !Array.isArray(specialityOptions) || specialityOptions.length === 0) {
                return null;
            }

            const response = await fetch(`${ollamaBaseUrl}/api/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: ollamaModel,
                    messages: [
                        {
                            role: 'system',
                            content: 'You route patient symptoms to one best doctor speciality. Reply with exactly one speciality from the allowed list.',
                        },
                        {
                            role: 'user',
                            content: `Allowed specialities: ${specialityOptions.join(', ')}\nSymptoms: ${symptomsText}\nReply with only one speciality name from the allowed list.`,
                        },
                    ],
                    stream: false,
                    options: {
                        temperature: 0.1,
                    },
                }),
            });

            if (!response.ok) {
                return null;
            }

            const data = await response.json();
            const reply = (data?.message?.content || '').trim().toLowerCase();
            return specialityOptions.find((speciality) => {
                const normalized = speciality.toLowerCase();
                return reply === normalized || reply.includes(normalized);
            }) || null;
        }

        async function suggestSpecialityFromSymptoms(target, symptomsText) {
            const matchResult = findSuggestedSpeciality(symptomsText);
            let speciality = matchResult.speciality;

            if (!matchResult.confident) {
                try {
                    const llmSpeciality = await suggestSpecialityWithLlm(symptomsText);
                    if (llmSpeciality) {
                        speciality = llmSpeciality;
                    }
                } catch (error) {
                    // Keep deterministic fallback if LLM routing fails.
                }
            }

            const matchedDoctors = Array.isArray(doctorsBySpeciality[speciality])
                ? doctorsBySpeciality[speciality]
                : [];
            const fallbackDoctors = Object.values(doctorsBySpeciality)
                .flat()
                .filter((doctor) => doctor && doctor.email);
            let replyHtml = `Based on the symptoms you shared, I suggest booking an appointment with a <strong>${speciality}</strong>.`;
            const doctorsToShow = matchedDoctors.length > 0 ? matchedDoctors : fallbackDoctors;

            if (matchedDoctors.length > 0) {
                replyHtml += `<br><br>Available doctors:`;
            } else if (fallbackDoctors.length > 0) {
                replyHtml += `<br><br>I could not find a perfect speciality match, but these doctors are available now:`;
            } else {
                replyHtml += `<br><br>No doctors are currently available in that speciality.`;
            }

            appendBotMessage(
                target,
                replyHtml,
                true,
            );
            if (doctorsToShow.length > 0) {
                appendDoctorButtons(target, doctorsToShow);
            }
        }

        function handleBookAppointment(target) {
            appendUserMessage(target, 'Book Appointment');
            awaitingSymptomInput = true;
            appendBotMessage(target, 'What specific symptoms are you experiencing?', false);
        }

        (function () {
            const frame = window.frameElement;
            if (frame) {
                frame.style.position = "fixed";
                frame.style.right = "0";
                frame.style.bottom = "0";
                frame.style.width = "390px";
                frame.style.height = "520px";
                frame.style.border = "0";
                frame.style.background = "transparent";
                frame.style.zIndex = "2147483000";
                frame.style.overflow = "visible";
            }
        })();
        </script>
        </body>
        </html>
        """
        .replace("__MM_CHATBOT_COMPONENT_CSS__", chatbot_css)
        .replace("__MM_CHATBOT_GREETING__", greeting)
        .replace("__MM_RX_SUMMARY_JSON__", prescription_summary_json)
        .replace("__MM_SPECIALITY_OPTIONS_JSON__", speciality_options_json)
        .replace("__MM_DOCTORS_BY_SPECIALITY_JSON__", doctors_by_speciality_json)
        .replace("__MM_SYMPTOM_SPECIALITY_MAP_JSON__", symptom_speciality_map_json)
        .replace("__MM_OLLAMA_BASE_URL_JSON__", ollama_base_url_json)
        .replace("__MM_OLLAMA_MODEL_JSON__", ollama_model_json)
        .replace("__MM_LLM_SYSTEM_PROMPT_JSON__", llm_system_prompt_json)
        .replace("__MM_USER_NAME_JSON__", patient_name_json)
        .replace("__MM_USER_EMAIL_JSON__", patient_email_json)
        .replace("__MM_USER_ROLE_JSON__", patient_role_json),
        height=520,
        scrolling=False,
    )



