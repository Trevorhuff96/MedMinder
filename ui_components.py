"""
Reusable UI components for MedMinder pages.
"""

import json
import os
from html import escape

import streamlit as st
import streamlit.components.v1 as components
from auth import get_specialities
from prescription import get_prescriptions_for_patient
from styles import get_chatbot_component_css


def _get_secret_value(key: str, default: str = "") -> str:
    """Safely read a Streamlit secret without requiring secrets.toml to exist."""
    try:
        return st.secrets[key]
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


def render_floating_chatbot(patient_name: str = "", patient_email: str = "") -> None:
    """Render a floating chatbot launcher and greeting panel."""
    chatbot_css = get_chatbot_component_css()
    safe_name = escape((patient_name or "").strip())
    greeting = f"Hi {safe_name} 👋" if safe_name else "Hi 👋"
    ollama_base_url = _get_secret_value("OLLAMA_BASE_URL") or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = _get_secret_value("OLLAMA_MODEL") or os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    llm_system_prompt = (
        "You are MedMinder Assistant. Give concise, helpful, safe health support. "
        "Do not provide diagnosis. Encourage contacting a doctor for urgent symptoms."
    )
    prescription_summary = _build_prescription_summary(patient_email or "")
    prescription_summary_json = json.dumps(prescription_summary)
    speciality_options_json = json.dumps(get_specialities())
    ollama_base_url_json = json.dumps(ollama_base_url)
    ollama_model_json = json.dumps(ollama_model)
    llm_system_prompt_json = json.dumps(llm_system_prompt)
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
        const ollamaBaseUrl = __MM_OLLAMA_BASE_URL_JSON__;
        const ollamaModel = __MM_OLLAMA_MODEL_JSON__;
        const llmSystemPrompt = __MM_LLM_SYSTEM_PROMPT_JSON__;
        const conversation = [];

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
                optionBtn.onclick = async function () {
                    await handleUserInput(optionBtn, speciality);
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
        .replace("__MM_SPECIALITY_OPTIONS_JSON__", speciality_options_json)
        .replace("__MM_OLLAMA_BASE_URL_JSON__", ollama_base_url_json)
        .replace("__MM_OLLAMA_MODEL_JSON__", ollama_model_json)
        .replace("__MM_LLM_SYSTEM_PROMPT_JSON__", llm_system_prompt_json),
        height=520,
        scrolling=False,
    )
