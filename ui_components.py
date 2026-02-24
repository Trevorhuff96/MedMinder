"""
Reusable UI components for MedMinder pages.
"""

import streamlit as st


def render_floating_chatbot() -> None:
    """Render a floating chatbot launcher and greeting panel."""
    st.markdown(
        """
        <style>
        .mm-chatbot-wrap {
            position: fixed;
            right: 24px;
            bottom: 24px;
            z-index: 1000;
            font-family: 'Inter', 'Arial', sans-serif;
        }

        .mm-chatbot-toggle {
            display: none;
        }

        .mm-chatbot-btn {
            width: 60px;
            height: 60px;
            border-radius: 999px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.65rem;
            cursor: pointer;
            background: linear-gradient(140deg, #00bfa5 0%, #1a237e 100%);
            color: #ffffff;
            box-shadow: 0 12px 28px rgba(8, 29, 83, 0.35);
            border: 2px solid rgba(255, 255, 255, 0.3);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .mm-chatbot-btn:hover {
            transform: translateY(-2px) scale(1.02);
            box-shadow: 0 16px 32px rgba(8, 29, 83, 0.4);
        }

        .mm-chatbot-panel {
            position: absolute;
            right: 0;
            bottom: 78px;
            width: min(340px, calc(100vw - 32px));
            border-radius: 16px;
            overflow: hidden;
            background: #ffffff;
            border: 1px solid rgba(26, 35, 126, 0.18);
            box-shadow: 0 20px 46px rgba(8, 29, 83, 0.35);
            opacity: 0;
            transform: translateY(8px) scale(0.98);
            pointer-events: none;
            transition: opacity 0.18s ease, transform 0.18s ease;
        }

        .mm-chatbot-toggle:checked ~ .mm-chatbot-panel {
            opacity: 1;
            transform: translateY(0) scale(1);
            pointer-events: auto;
        }

        .mm-chatbot-header {
            padding: 0.8rem 0.95rem;
            color: #ffffff;
            font-weight: 700;
            background: linear-gradient(135deg, #1a237e 0%, #0d47a1 100%);
            font-size: 0.92rem;
            letter-spacing: 0.02em;
        }

        .mm-chatbot-body {
            padding: 0.9rem;
            background: #f5f8ff;
        }

        .mm-chatbot-message {
            margin: 0;
            width: fit-content;
            max-width: 100%;
            color: #0f1b55;
            background: #eaf0ff;
            border: 1px solid #d5e2ff;
            border-radius: 12px 12px 12px 2px;
            padding: 0.55rem 0.7rem;
            font-size: 0.9rem;
            line-height: 1.35;
        }

        .mm-chatbot-message.user {
            margin-left: auto;
            border-radius: 12px 12px 2px 12px;
            background: #d9f8f3;
            border-color: #bdeee6;
            color: #06463d;
        }

        .mm-chatbot-thread {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            margin-bottom: 0.8rem;
            max-height: 180px;
            overflow-y: auto;
            padding-right: 0.2rem;
        }

        .mm-chatbot-composer {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding-top: 0.2rem;
        }

        .mm-chatbot-input {
            flex: 1;
            border: 1px solid #cfdcff;
            background: #ffffff;
            color: #1a237e;
            border-radius: 999px;
            padding: 0.5rem 0.8rem;
            font-size: 0.86rem;
            outline: none;
        }

        .mm-chatbot-input:focus {
            border-color: #00bfa5;
            box-shadow: 0 0 0 2px rgba(0, 191, 165, 0.18);
        }

        .mm-chatbot-send {
            border: none;
            border-radius: 999px;
            background: linear-gradient(140deg, #00bfa5 0%, #1a237e 100%);
            color: #ffffff;
            font-weight: 700;
            font-size: 0.78rem;
            padding: 0.48rem 0.78rem;
            cursor: pointer;
            white-space: nowrap;
        }

        @media (max-width: 640px) {
            .mm-chatbot-wrap {
                right: 14px;
                bottom: 14px;
            }

            .mm-chatbot-btn {
                width: 56px;
                height: 56px;
            }

            .mm-chatbot-panel {
                bottom: 72px;
                width: min(320px, calc(100vw - 24px));
            }
        }
        </style>

        <div class="mm-chatbot-wrap">
            <input type="checkbox" id="mm-chatbot-toggle" class="mm-chatbot-toggle" />
            <label class="mm-chatbot-btn" for="mm-chatbot-toggle" aria-label="Open chatbot">💬</label>
            <div class="mm-chatbot-panel" role="dialog" aria-label="Chatbot window">
                <div class="mm-chatbot-header">MedMinder Assistant</div>
                <div class="mm-chatbot-body">
                    <div class="mm-chatbot-thread">
                        <p class="mm-chatbot-message">Hi 👋</p>
                        <p class="mm-chatbot-message user">I need help with my reminders.</p>
                        <p class="mm-chatbot-message">Sure. Type below and press Send.</p>
                    </div>
                    <form class="mm-chatbot-composer" onsubmit="return false;">
                        <input class="mm-chatbot-input" type="text" placeholder="Type your message..." />
                        <button class="mm-chatbot-send" type="submit">Send</button>
                    </form>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
