"""
Reusable UI components for MedMinder pages.
"""

import json
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from auth import get_specialities
from prescription import get_prescriptions_for_patient
from styles import get_chatbot_component_css


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


def render_floating_chatbot(patient_name: str = "", patient_email: str = "") -> None:
    """Render a floating chatbot launcher and greeting panel."""
    chatbot_css = get_chatbot_component_css()
    safe_name = escape((patient_name or "").strip())
    greeting = f"Hi {safe_name} 👋" if safe_name else "Hi 👋"
    prescription_summary = _build_prescription_summary(patient_email or "")
    prescription_summary_json = json.dumps(prescription_summary)
    speciality_options_json = json.dumps(get_specialities())
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
            <label class="mm-chatbot-btn" for="mm-chatbot-toggle" aria-label="Open chatbot">💬</label>
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
                            onclick="const body=this.closest('.mm-chatbot-body'); const input=body.querySelector('.mm-chatbot-input'); const text=input.value.trim(); if (text) { appendUserMessage(this, text); input.value=''; }"
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

        function appendMessage(target, text, isUser, asHtml) {
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
        }

        function appendUserMessage(target, text) {
            appendMessage(target, text, true, false);
        }

        function appendBotMessage(target, text, asHtml) {
            appendMessage(target, text, false, !!asHtml);
        }

        function appendSpecialityOptions(target) {
            const body = target.closest('.mm-chatbot-body');
            if (!body) return;
            const thread = body.querySelector('.mm-chatbot-thread');
            if (!thread || !Array.isArray(specialityOptions) || specialityOptions.length === 0) return;
            const optionsWrap = document.createElement('div');
            optionsWrap.className = 'mm-chatbot-options';
            specialityOptions.forEach((speciality) => {
                const optionBtn = document.createElement('button');
                optionBtn.type = 'button';
                optionBtn.className = 'mm-chatbot-option';
                optionBtn.textContent = speciality;
                optionBtn.onclick = function () {
                    appendUserMessage(optionBtn, speciality);
                };
                optionsWrap.appendChild(optionBtn);
            });
            thread.appendChild(optionsWrap);
            thread.scrollTop = thread.scrollHeight;
        }

        function handleBookAppointment(target) {
            appendUserMessage(target, 'Book Appointment');
            appendBotMessage(target, 'What speciality are you looking for?', false);
            appendSpecialityOptions(target);
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
        .replace("__MM_SPECIALITY_OPTIONS_JSON__", speciality_options_json),
        height=520,
        scrolling=False,
    )
