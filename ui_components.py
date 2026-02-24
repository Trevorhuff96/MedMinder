"""
Reusable UI components for MedMinder pages.
"""

import streamlit as st
import streamlit.components.v1 as components
from styles import get_chatbot_component_css


def render_floating_chatbot() -> None:
    """Render a floating chatbot launcher and greeting panel."""
    chatbot_css = get_chatbot_component_css()
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
                        <p class="mm-chatbot-message">Hi 👋</p>
                        <p class="mm-chatbot-message user">I need help with my reminders.</p>
                        <p class="mm-chatbot-message">Sure. Type below and press Send.</p>
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
                            onclick="const body=this.closest('.mm-chatbot-body'); const input=body.querySelector('.mm-chatbot-input'); const thread=body.querySelector('.mm-chatbot-thread'); const text=input.value.trim(); if (text) { const bubble=document.createElement('p'); bubble.className='mm-chatbot-message user'; bubble.textContent=text; thread.appendChild(bubble); input.value=''; thread.scrollTop=thread.scrollHeight; }"
                        >
                            Send
                        </button>
                    </form>
                </div>
            </div>
        </div>

        <script>
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
        """.replace("__MM_CHATBOT_COMPONENT_CSS__", chatbot_css),
        height=520,
        scrolling=False,
    )
