import streamlit as st
import ollama
import json
import uuid
from pathlib import Path
from datetime import datetime

# ==================================================
# 1. CONFIGURATION
# ==================================================
st.set_page_config(
    page_title="Yash AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

TEXT_MODEL = "llama3.2"  # Text chat model; install with: ollama pull llama3.2
VISION_MODEL = "llava"  # Image understanding model; install with: ollama pull llava
BASE_DIR = Path(__file__).parent
HISTORY_FILE = BASE_DIR / "chat_history.json"
IMAGE_FILE = BASE_DIR / "yash_ai.png"
UPLOAD_DIR = BASE_DIR / "uploaded_images"
UPLOAD_DIR.mkdir(exist_ok=True)


# ==================================================
# 2. CHAT HISTORY
# ==================================================
def load_history():
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def save_history():
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(
                st.session_state.all_chats,
                f,
                ensure_ascii=False,
                indent=2
            )
    except OSError as error:
        st.error(f"Could not save history: {error}")


def start_new_chat():
    st.session_state.chat_id = None
    st.session_state.messages = []


def save_current_chat():
    chat_id = st.session_state.chat_id
    if not chat_id:
        return

    messages = st.session_state.messages.copy()
    first_question = next(
        (m["content"] for m in messages if m["role"] == "user"),
        "New conversation"
    )

    st.session_state.all_chats[chat_id] = {
        "title": first_question[:35],
        "messages": messages,
        "updated": datetime.now().isoformat()
    }
    save_history()


# ==================================================
# 3. SESSION STATE
# ==================================================
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_history()

if "chat_id" not in st.session_state:
    st.session_state.chat_id = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# ==================================================
# 4. CUSTOM CSS - PURPLE THEME
# ==================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --background: #0b0d1b;
    --panel: #171a30;
    --border: #393e68;
    --purple: #a995ff;
}

/* Main application background */
.stApp,
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        135deg,
        #0b0d1b 0%,
        #17132f 55%,
        #241746 100%
    ) !important;
    color: #ffffff !important;
    font-family: 'Inter', sans-serif;
}

/* Main content and bottom areas */
[data-testid="stMain"],
[data-testid="stMainBlockContainer"],
[data-testid="stBottom"],
[data-testid="stBottom"] > div,
[data-testid="stBottom"] > div > div,
.main,
.main .block-container {
    background: transparent !important;
    background-color: transparent !important;
}

/* Cover the full bottom section in purple */
[data-testid="stBottom"] {
    background: #17132f !important;
    background-color: #17132f !important;
}

[data-testid="stBottom"]::before {
    background: #17132f !important;
    background-color: #17132f !important;
}

/* Header */
[data-testid="stHeader"] {
    background: transparent !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0e1022 !important;
    border-right: 1px solid #303558;
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

.brand {
    color: #ffffff;
    font-size: 28px;
    font-weight: 800;
}

.brand span {
    color: #a995ff;
}

.tagline {
    color: #b1b5d8;
    font-size: 12px;
    margin: 4px 0 25px;
}

.side-heading {
    color: #929acb;
    font-size: 11px;
    letter-spacing: 2px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 12px;
}

.model-card {
    background: #171a31;
    border: 1px solid #35395f;
    border-radius: 15px;
    padding: 15px;
    color: #ffffff;
    font-size: 12px;
    line-height: 2;
}

.dot {
    display: inline-block;
    height: 9px;
    width: 9px;
    border-radius: 50%;
    background: #35e3a1;
    margin-right: 7px;
}

/* Buttons */
div.stButton > button {
    width: 100%;
    min-height: 43px;
    color: #ffffff !important;
    background: #191c35 !important;
    border: 1px solid #393e68 !important;
    border-radius: 12px !important;
    transition: 0.2s;
}

div.stButton > button:hover {
    background: #29254e !important;
    border-color: #a08aff !important;
}

/* Workspace header */
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    background: #171a31;
    border: 1px solid #393e68;
    border-radius: 16px;
    padding: 15px 22px;
    margin-bottom: 25px;
}

.topbar-title {
    font-size: 16px;
    font-weight: 700;
    color: #ffffff;
}

.topbar-sub {
    color: #b1b5d8;
    font-size: 12px;
    margin-top: 4px;
}

.pill {
    background: #29254f;
    border: 1px solid #51468a;
    color: #ffffff;
    border-radius: 30px;
    padding: 8px 13px;
    font-size: 11px;
    white-space: nowrap;
}

/* Welcome section */
.hero {
    padding: 50px 8px 35px;
}

.hero h1 {
    font-size: clamp(30px, 4vw, 50px);
    font-weight: 800;
    letter-spacing: -2px;
    color: #ffffff !important;
    margin-bottom: 12px;
}

.hero h1 span {
    background: linear-gradient(90deg, #b6a3ff, #f0a6f4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero p {
    color: #e0def5 !important;
    font-size: 15px;
    line-height: 1.9;
}

/* Chat messages */
[data-testid="stChatMessage"] {
    background: rgba(23, 26, 48, 0.92) !important;
    border: 1px solid #393e68 !important;
    border-radius: 16px !important;
    padding: 14px !important;
    margin-bottom: 12px !important;
}

[data-testid="stChatMessage"] *,
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] strong,
[data-testid="stChatMessage"] em {
    color: #ffffff !important;
}

[data-testid="stChatMessage"] pre {
    background: #0b0d1b !important;
    border: 1px solid #393e68 !important;
    border-radius: 10px !important;
    padding: 14px !important;
}

[data-testid="stChatMessage"] code {
    color: #e5dcff !important;
}

/* Chat input - stays inside the main content layout */
[data-testid="stChatInput"] {
    position: relative !important;
    left: auto !important;
    right: auto !important;
    bottom: auto !important;
    transform: none !important;

    width: 100% !important;
    max-width: 850px !important;
    box-sizing: border-box !important;

    margin: 20px auto 12px auto !important;
    padding: 8px 12px !important;

    background: #211b3e !important;
    background-color: #211b3e !important;
    border: 1px solid #a995ff !important;
    border-radius: 20px !important;

    box-shadow: 0 5px 22px rgba(0, 0, 0, 0.25) !important;
    z-index: 1 !important;
}

/* Inner input wrapper */
[data-testid="stChatInput"] > div {
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
}

/* Text entered into input */
[data-testid="stChatInput"] textarea,
[data-testid="stChatInput"] textarea:focus {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
    caret-color: #c4b5fd !important;
    background: transparent !important;
    border: none !important;
    outline: none !important;
    box-shadow: none !important;
    padding: 12px 10px !important;
    line-height: 1.5 !important;
}

/* Placeholder */
[data-testid="stChatInput"] textarea::placeholder {
    color: #c4b5fd !important;
    -webkit-text-fill-color: #c4b5fd !important;
    opacity: 1 !important;
}
/* Hide Enter-to-submit hint */
[data-testid="InputInstructions"] {
    display: none !important;
}
/* Send button */
[data-testid="stChatInput"] button {
    background: #39305f !important;
    color: #ffffff !important;
    border: 1px solid #6553a7 !important;
    border-radius: 12px !important;
}

[data-testid="stChatInput"] button:hover {
    background: #55418c !important;
}

/* Custom composer */
.attachment-area {
    max-width: 850px;
    margin: 20px auto 12px auto;
}
.attachment-area [data-testid="stTextInput"] input {
    min-height: 48px;
    color: #ffffff !important;
    background: #211b3e !important;
    border: 1px solid #a995ff !important;
    border-radius: 18px !important;
}
.attachment-area [data-testid="stTextInput"] input::placeholder {
    color: #c4b5fd !important;
}
.attachment-area [data-testid="stPopover"] button {
    min-height: 48px;
    width: 48px;
    border-radius: 50% !important;
    color: #ffffff !important;
    background: #39305f !important;
    border: 1px solid #a995ff !important;
    font-size: 23px !important;
}
.attachment-area div.stButton > button {
    min-height: 48px;
    border-radius: 16px !important;
    color: #ffffff !important;
    background: #6d4aff !important;
    border: 1px solid #a995ff !important;
}

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #ffffff;
}

/* Hide Streamlit footer and menu */
#MainMenu,
footer {
    visibility: hidden;
}

/* Mobile adjustments */
@media (max-width: 700px) {
    .hero {
        padding-top: 20px;
    }

    .topbar {
        padding: 12px;
    }

    [data-testid="stChatInput"] {
        width: 100% !important;
        max-width: 100% !important;
        margin-top: 15px !important;
    }
}
</style>
""", unsafe_allow_html=True)


# ==================================================
# 5. SIDEBAR
# ==================================================
with st.sidebar:
    st.markdown(
        '<div class="brand">🤖 Yash <span>AI ✦</span></div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="tagline">Your Personal AI Assistant</div>',
        unsafe_allow_html=True
    )

    if st.button("🏠 Home", use_container_width=True):
        start_new_chat()
        st.rerun()

    if st.button("＋ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    

    st.markdown(
        '<div class="side-heading">CHAT HISTORY</div>',
        unsafe_allow_html=True
    )

    sorted_chats = sorted(
        st.session_state.all_chats.items(),
        key=lambda item: item[1].get("updated", ""),
        reverse=True
    )

    if not sorted_chats:
        st.caption("Your conversations will appear here.")

    for saved_id, chat in sorted_chats:
        title = chat.get("title", "New conversation")

        if st.button(
            "💬 " + title[:28],
            key="history_" + saved_id,
            use_container_width=True
        ):
            st.session_state.chat_id = saved_id
            st.session_state.messages = chat.get("messages", []).copy()
            st.rerun()

    st.markdown("---")
    st.caption("💜 Conversations saved locally")


# ==================================================
# 6. MAIN HEADER
# ==================================================
st.markdown("""
<div class="topbar">
    <div>
        <div class="topbar-title">✦ Your AI Workspace</div>
        <div class="topbar-sub">
            Ready to learn, build and explore today?
        </div>
    </div>
    <div class="pill">● Local AI</div>
</div>
""", unsafe_allow_html=True)


# ==================================================
# 7. WELCOME SECTION AND IMAGE
# ==================================================
if not st.session_state.messages:
    left, right = st.columns([3, 2], vertical_alignment="center")

    with left:
        st.markdown("""
        <div class="hero">
            <h1>Hi, I'm <span>Yash AI ✦</span></h1>
            <p>
                Your personal AI assistant, here to help you<br>
                learn, code, and turn your ideas into reality.
            </p>
            <p>Ask me anything to get started 💜</p>
        </div>
        """, unsafe_allow_html=True)

    with right:
        if IMAGE_FILE.exists():
            st.image(str(IMAGE_FILE), width=300)
        else:
            st.markdown(
                "<div style='font-size:100px;text-align:center;'>🤖💜</div>",
                unsafe_allow_html=True
            )


# ==================================================
# 8. DISPLAY CHAT HISTORY
# ==================================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.markdown("**✦ Yash AI**")
        if message.get("image_paths"):
            for image_path in message["image_paths"]:
                if Path(image_path).exists():
                    st.image(image_path, width=260)
        st.markdown(message["content"])


# ==================================================
# ==================================================
# 9. CHAT INPUT, PHOTO ATTACHMENT, AND OLLAMA RESPONSE
# ==================================================
if "pending_images" not in st.session_state:
    st.session_state.pending_images = []

if "pending_response" not in st.session_state:
    st.session_state.pending_response = False

# Process a submitted message on the next rerun. This makes the user's
# message appear in the chat history before the "thinking" indicator starts.
if st.session_state.pending_response:
    st.session_state.pending_response = False

    with st.chat_message("assistant"):
        st.markdown("**✦ Yash AI**")
        try:
            with st.spinner("Yash AI is thinking... 💜"):
                ollama_messages = [{
                    "role": "system",
                    "content": (
                        "You are Yash AI, a helpful personal AI assistant. Answer the exact "
                        "question asked. If photos are attached, inspect them and answer "
                        "about their visible contents. Be accurate, clear, and use Markdown."
                    )
                }]

                for msg in st.session_state.messages:
                    item = {"role": msg["role"], "content": msg["content"]}
                    if msg.get("image_paths"):
                        item["images"] = msg["image_paths"]
                    ollama_messages.append(item)

                has_images = any(
                    msg.get("image_paths") for msg in st.session_state.messages
                )
                selected_model = VISION_MODEL if has_images else TEXT_MODEL

                # Check whether the required model is installed.
                installed_models = ollama.list()
                model_entries = (
                    installed_models.get("models", [])
                    if isinstance(installed_models, dict)
                    else getattr(installed_models, "models", [])
                )
                installed_names = set()
                for model_entry in model_entries:
                    if isinstance(model_entry, dict):
                        model_name = (
                            model_entry.get("name")
                            or model_entry.get("model", "")
                        )
                    else:
                        model_name = (
                            getattr(model_entry, "model", "")
                            or getattr(model_entry, "name", "")
                        )
                    if model_name:
                        installed_names.add(model_name.split(":")[0])

                if selected_model not in installed_names:
                    raise RuntimeError(
                        f"Required Ollama model '{selected_model}' is not installed. "
                        f"Run `ollama pull {selected_model}` in your terminal."
                    )

                response = ollama.chat(
                    model=selected_model,
                    messages=ollama_messages,
                    options={"num_predict": 512, "temperature": 0.7}
                )
                answer = response.message.content

            if not answer or not answer.strip():
                answer = "I couldn't generate an answer. Please try again."

            st.markdown(answer)
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer
            })
            save_current_chat()

        except Exception as error:
            st.error("Yash AI couldn't generate a response.")
            st.code(str(error))
            error_text = str(error).lower()
            if (
                "connect" in error_text
                or "refused" in error_text
                or "localhost:11434" in error_text
            ):
                st.info("Ollama is not running. Start Ollama, then try again.")
            elif (
                "not installed" in error_text
                or "pull" in error_text
                or "model" in error_text
            ):
                st.info(
                    "Install the required model in a terminal: "
                    "`ollama pull llama3.2` for text chat, or "
                    "`ollama pull llava` for image questions."
                )
            else:
                st.info(
                    "Check the error above. Confirm Ollama is running and "
                    "that the required model is installed."
                )

    # Refresh so the final answer is saved and displayed in the normal history.
    st.rerun()


# Attachment button stays outside the form; text input and send button are
# inside one form so pressing Enter submits the message.
st.markdown('<div class="attachment-area">', unsafe_allow_html=True)
attach_col, composer_col = st.columns([0.7, 6.85], vertical_alignment="bottom")

with attach_col:
    with st.popover("＋", help="Attach photos"):
        uploaded_files = st.file_uploader(
            "Choose photos",
            type=["png", "jpg", "jpeg", "webp"],
            accept_multiple_files=True,
            key="photo_uploader"
        )
        if uploaded_files:
            st.session_state.pending_images = uploaded_files

with composer_col:
    with st.form("chat_form", clear_on_submit=True, border=False):
        text_col, send_col = st.columns([6, 0.85], vertical_alignment="bottom")
        with text_col:
            user_prompt = st.text_input(
                "Message Yash AI...",
                key="chat_text_input",
                label_visibility="collapsed",
                placeholder="Message Yash AI..."
            )
        with send_col:
            send_clicked = st.form_submit_button(
                "➤",
                help="Send message",
                use_container_width=True
            )

st.markdown('</div>', unsafe_allow_html=True)

if st.session_state.pending_images:
    st.caption(f"📎 {len(st.session_state.pending_images)} photo(s) attached")
    preview_cols = st.columns(min(len(st.session_state.pending_images), 4))
    for i, uploaded in enumerate(st.session_state.pending_images):
        with preview_cols[i % len(preview_cols)]:
            st.image(uploaded, caption=uploaded.name, width=110)


if send_clicked and (user_prompt.strip() or st.session_state.pending_images):
    if st.session_state.chat_id is None:
        st.session_state.chat_id = str(uuid.uuid4())

    saved_image_paths = []
    for uploaded in st.session_state.pending_images:
        safe_name = f"{uuid.uuid4().hex}_{Path(uploaded.name).name}"
        saved_path = UPLOAD_DIR / safe_name
        saved_path.write_bytes(uploaded.getvalue())
        saved_image_paths.append(str(saved_path))

    display_text = user_prompt.strip() or "Please look at the attached photo(s)."
    st.session_state.messages.append({
        "role": "user",
        "content": display_text,
        "image_paths": saved_image_paths
    })
    save_current_chat()

    # Clear pending uploads and trigger a rerun. On that rerun, the user
    # message is rendered in history first, then the assistant starts thinking.
    st.session_state.pending_images = []
    st.session_state.pending_response = True
    st.rerun()
elif send_clicked:
    st.warning("Please type a message or attach a photo before sending.")
