"""
Streamlit web interface for Kyungdong University RAG Chatbot
"""

import os
import sys
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import streamlit as st

try:
    from gtts import gTTS
except Exception:  # pragma: no cover
    gTTS = None

try:
    from streamlit_mic_recorder import mic_recorder
except Exception:  # pragma: no cover
    mic_recorder = None

# Suppress warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib

# Configure Streamlit page
st.set_page_config(
    page_title="KDU Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.chatbot_rag import KyungdongRAGChatbot
from src.knowledge_base import get_official_source_pages, load_knowledge_base


APP_ROOT = Path(__file__).resolve().parent
CACHE_DIR = APP_ROOT / ".cache"
PROFILE_FILE = CACHE_DIR / "user_profiles.json"
ANALYTICS_FILE = CACHE_DIR / "analytics_events.json"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _default_profile() -> dict:
    return {
        "response_tone": "Friendly",
        "response_detail": "Balanced",
        "response_language": "English",
        "voice_input_enabled": False,
        "tts_enabled": False,
        "tool_use_enabled": True,
        "notes": "",
        "conversation_memory": [],
        "conversation_summary": "",
    }


def load_user_profile(username: str) -> dict:
    payload = _read_json(PROFILE_FILE, {"users": {}})
    profile = payload.get("users", {}).get(username, {})
    merged = _default_profile()
    merged.update(profile)
    return merged


def save_user_profile(username: str, profile: dict) -> None:
    payload = _read_json(PROFILE_FILE, {"users": {}})
    users = payload.setdefault("users", {})
    existing = users.get(username, {})
    merged = _default_profile()
    merged.update(existing)
    merged.update(profile)
    users[username] = merged
    _write_json(PROFILE_FILE, payload)


def record_analytics_event(event: dict) -> str:
    payload = _read_json(ANALYTICS_FILE, {"events": [], "feedback": {"up": 0, "down": 0}})
    event_id = f"evt-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
    event["event_id"] = event_id
    payload.setdefault("events", []).append(event)
    payload["events"] = payload["events"][-1000:]
    _write_json(ANALYTICS_FILE, payload)
    return event_id


def record_feedback(event_id: str, vote: str, reason: str = "", note: str = "") -> None:
    payload = _read_json(ANALYTICS_FILE, {"events": [], "feedback": {"up": 0, "down": 0}})
    feedback = payload.setdefault("feedback", {"up": 0, "down": 0})

    if vote == "up":
        feedback["up"] = int(feedback.get("up", 0)) + 1
    elif vote == "down":
        feedback["down"] = int(feedback.get("down", 0)) + 1

    for event in payload.get("events", []):
        if event.get("event_id") == event_id:
            event["feedback"] = vote
            if reason:
                event["feedback_reason"] = reason
            if note:
                event["feedback_note"] = note
            break

    _write_json(ANALYTICS_FILE, payload)


def get_analytics_snapshot() -> dict:
    payload = _read_json(ANALYTICS_FILE, {"events": [], "feedback": {"up": 0, "down": 0}})
    events = payload.get("events", [])
    total = len(events)
    unknown = sum(1 for e in events if e.get("unknown"))
    moderated = sum(1 for e in events if e.get("moderated"))
    avg_docs = (sum(int(e.get("retrieved_count", 0)) for e in events) / total) if total else 0.0
    topics = Counter(e.get("topic", "general") for e in events)
    tools = Counter(e.get("tool_action", "none") for e in events if e.get("tool_action") and e.get("tool_action") != "none")
    feedback_reasons = Counter(
        e.get("feedback_reason", "")
        for e in events
        if e.get("feedback") == "down" and e.get("feedback_reason")
    )
    feedback = payload.get("feedback", {"up": 0, "down": 0})
    up = int(feedback.get("up", 0))
    down = int(feedback.get("down", 0))
    quality = (up / max(up + down, 1)) * 100.0 if (up + down) else 0.0

    return {
        "total_queries": total,
        "unknown_rate": (unknown / total * 100.0) if total else 0.0,
        "moderation_rate": (moderated / total * 100.0) if total else 0.0,
        "avg_retrieved_docs": avg_docs,
        "top_topics": topics.most_common(5),
        "tools_used": tools.most_common(5),
        "feedback_up": up,
        "feedback_down": down,
        "quality_score": quality,
        "top_feedback_reasons": feedback_reasons.most_common(5),
    }


def build_developer_feedback_report() -> dict:
    """Build a compact developer-facing report payload."""
    payload = _read_json(ANALYTICS_FILE, {"events": [], "feedback": {"up": 0, "down": 0}})
    snapshot = get_analytics_snapshot()

    examples = []
    for event in payload.get("events", []):
        if event.get("feedback") == "down" or event.get("moderated") or event.get("unknown"):
            examples.append(
                {
                    "event_id": event.get("event_id", ""),
                    "timestamp": event.get("timestamp", ""),
                    "query": event.get("query", ""),
                    "topic": event.get("topic", ""),
                    "feedback": event.get("feedback", ""),
                    "feedback_reason": event.get("feedback_reason", ""),
                    "feedback_note": event.get("feedback_note", ""),
                    "unknown": bool(event.get("unknown")),
                    "moderated": bool(event.get("moderated")),
                    "tool_action": event.get("tool_action", "none"),
                }
            )

    return {
        "generated_at": datetime.utcnow().isoformat(),
        "metrics": snapshot,
        "sampled_events": examples[-100:],
    }


def synthesize_tts_audio(text: str, language: str) -> bytes:
    if not text or gTTS is None:
        return b""

    lang_code = "en"
    if language.lower().startswith("korean"):
        lang_code = "ko"

    try:
        from io import BytesIO

        fp = BytesIO()
        gTTS(text=text[:3000], lang=lang_code).write_to_fp(fp)
        return fp.getvalue()
    except Exception:
        return b""


def _safe_index(options: list[str], selected: str, default: int = 0) -> int:
    try:
        return options.index(selected)
    except ValueError:
        return default


def _extract_audio_bytes(audio_data) -> bytes:
    """Normalize recorder output into raw audio bytes."""
    if not audio_data:
        return b""

    if isinstance(audio_data, (bytes, bytearray, memoryview)):
        return bytes(audio_data)

    if isinstance(audio_data, dict):
        for key in ("bytes", "audio", "blob", "file", "data"):
            value = audio_data.get(key)
            if isinstance(value, (bytes, bytearray, memoryview)):
                return bytes(value)
            if hasattr(value, "read"):
                try:
                    return value.read()
                except Exception:
                    pass
        return b""

    if hasattr(audio_data, "read"):
        try:
            return audio_data.read()
        except Exception:
            return b""

    return b""


def detect_input_language(text: str) -> str:
    """Detect basic input language between Korean and English."""
    if re.search(r"[\uac00-\ud7a3]", text or ""):
        return "Korean"
    return "English"


def resolve_response_language(user_input: str, preferred: str) -> str:
    if preferred == "Auto":
        return detect_input_language(user_input)
    return preferred


def load_admin_password() -> str:
    """Load admin password from secrets or environment."""
    try:
        secret_value = str(st.secrets.get("ADMIN_PASSWORD", "")).strip()
        if secret_value:
            return secret_value
    except Exception:
        pass

    return str(os.getenv("ADMIN_PASSWORD", "")).strip()


def _is_placeholder(value: str) -> bool:
    if not value:
        return True
    normalized = value.strip().lower()
    return normalized in {"your_groq_api_key_here", "your_api_key_here", "your_actual_api_key_here", "changeme"}


def load_groq_api_key() -> str:
    """Resolve the Groq API key from env, .env, or the local secret files."""
    try:
        secret_value = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        if not _is_placeholder(secret_value):
            os.environ["GROQ_API_KEY"] = secret_value
            return secret_value
    except Exception:
        pass

    candidate_values = [
        os.getenv("GROQ_API_KEY", ""),
        os.getenv("GROQ_KEY", ""),
        os.getenv("GROQ_APIKEY", ""),
    ]
    for value in candidate_values:
        if not _is_placeholder(value):
            return value.strip()

    project_root = Path(__file__).resolve().parent
    dotenv_paths = [project_root / ".env", project_root / "app.py" / ".env"]
    for dotenv_path in dotenv_paths:
        if dotenv_path.exists():
            try:
                for line in dotenv_path.read_text(encoding="utf-8").splitlines():
                    if "=" in line and line.strip().startswith("GROQ_API_KEY"):
                        value = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if not _is_placeholder(value):
                            os.environ["GROQ_API_KEY"] = value
                            return value
            except Exception:
                pass

    secret_candidates = [
        project_root / ".streamlit" / "secrets.toml",
        project_root / "toml .streamlit" / "secrets.toml",
        project_root / "app.py" / ".streamlit" / "secrets.toml",
    ]
    for secret_path in secret_candidates:
        if not secret_path.exists():
            continue
        try:
            with open(secret_path, "rb") as fh:
                data = tomllib.load(fh)
            value = str(data.get("GROQ_API_KEY", "")).strip()
            if not _is_placeholder(value):
                return value
        except Exception:
            try:
                text = secret_path.read_text(encoding="utf-8")
                for line in text.splitlines():
                    if "GROQ_API_KEY" in line and "=" in line:
                        value = line.split("=", 1)[1].strip().strip('"').strip("'")
                        if not _is_placeholder(value):
                            return value
            except Exception:
                pass

    return ""


@st.cache_resource
def initialize_chatbot():
    """Initialize chatbot once"""
    groq_api_key = load_groq_api_key()

    if not groq_api_key:
        return None

    chatbot = KyungdongRAGChatbot(groq_api_key=groq_api_key)

    # Load and add documents to vector database
    if not st.session_state.get("documents_loaded", False):
        sync_knowledge_base(
            chatbot,
            force_refresh=False,
            status_message="📚 Loading official university website data..."
        )
            
    return chatbot


def sync_knowledge_base(chatbot, force_refresh: bool, status_message: str) -> None:
    """Fetch website content and refresh the chatbot knowledge base."""
    with st.spinner(status_message):
        documents = load_knowledge_base(force_refresh=force_refresh)
        chatbot.add_documents(documents)
        st.session_state.documents_loaded = True
        st.session_state.knowledge_document_count = len(documents)
        st.session_state.knowledge_synced_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_chatbot():
    """Get or initialize chatbot - ensures documents are always loaded"""
    if "chatbot" not in st.session_state or st.session_state.chatbot is None:
        chatbot = initialize_chatbot()
        if chatbot:
            st.session_state.chatbot = chatbot
            # Ensure documents are loaded
            if st.session_state.get("documents_loaded", False) == False:
                sync_knowledge_base(
                    chatbot,
                    force_refresh=False,
                    status_message="📚 Loading official university website data..."
                )
        return chatbot
    return st.session_state.chatbot


def display_sources(retrieved_docs) -> None:
    """Display retrieved sources with relevance scores"""
    if retrieved_docs:
        st.markdown("### 📚 Retrieved Sources")
        st.progress(min(len(retrieved_docs) / 3, 1.0), text=f"{len(retrieved_docs)} document(s) found")
        
        for i, doc in enumerate(retrieved_docs, 1):
            # Color code by relevance
            if doc.relevance_score >= 0.7:
                relevance_class = "relevance-high"
                score_label = "🔴 High"
            elif doc.relevance_score >= 0.5:
                relevance_class = "relevance-medium"
                score_label = "🟡 Medium"
            else:
                relevance_class = ""
                score_label = "🟢 Low"
            
            with st.expander(f"📄 Source {i}: {doc.source} - {score_label}", expanded=(i==1)):
                st.write(doc.content)
                if doc.url:
                    st.markdown(f"[Open official source page]({doc.url})")
                st.markdown(
                    f"<small>Category: {doc.category} | Relevance Score: {doc.relevance_score:.1%}</small>",
                    unsafe_allow_html=True
                )
    else:
        st.info("ℹ️ No related documents found - generating response from general knowledge")


def display_tool_payload(tool_action: str, payload: dict | None, event_id: str = "") -> None:
    """Render tool-action outputs in chat."""
    if not payload:
        return

    if tool_action == "web_search":
        results = payload.get("results", [])
        if results:
            st.markdown("### 🌐 Web Results")
            for idx, item in enumerate(results, 1):
                title = item.get("title", f"Result {idx}")
                snippet = item.get("snippet", "")
                url = item.get("url", "")
                st.markdown(f"**{idx}. {title}**")
                if snippet:
                    st.write(snippet)
                if url:
                    st.markdown(f"[Open link]({url})")

    elif tool_action == "calendar":
        st.markdown("### 📅 Calendar Draft")
        st.write(f"Title: {payload.get('title', 'Event')}")
        st.write(f"Start: {payload.get('start', '')}")
        st.write(f"End: {payload.get('end', '')}")
        st.download_button(
            "Download .ics file",
            data=payload.get("ics", ""),
            file_name="kdu_event.ics",
            mime="text/calendar",
            key=f"ics_download_{event_id or 'default'}",
        )

    elif tool_action == "email":
        st.markdown("### ✉️ Email Draft")
        to = payload.get("to", "")
        subject = payload.get("subject", "")
        body = payload.get("body", "")
        st.write(f"To: {to}")
        st.write(f"Subject: {subject}")
        st.text_area("Body", value=body, height=140, key=f"email_body_{event_id or 'default'}")

        mailto = f"mailto:{to}?subject={quote(subject)}&body={quote(body)}"
        st.markdown(f"[Open in mail app]({mailto})")


def _serialize_messages_for_export(messages: list[dict]) -> list[dict]:
    """Convert chat messages to JSON-safe payload."""
    serialized = []
    for message in messages:
        item = dict(message)
        if item.get("sources"):
            clean_sources = []
            for source in item.get("sources", []):
                if hasattr(source, "__dict__"):
                    clean_sources.append(dict(source.__dict__))
                elif isinstance(source, dict):
                    clean_sources.append(source)
            item["sources"] = clean_sources
        serialized.append(item)
    return serialized


def _messages_to_conversation_history(messages: list[dict], limit: int = 8) -> list[dict]:
    """Extract role/content pairs for session-scoped conversation memory."""
    history: list[dict] = []
    for message in messages:
        role = str(message.get("role", "")).strip().lower()
        content = str(message.get("content", "")).strip()
        if role in {"user", "assistant"} and content:
            history.append({"role": role, "content": content})
    return history[-limit:]


def _profile_conversation_memory(messages: list[dict], limit: int = 12) -> list[dict]:
    """Build a compact, persistent conversation memory for a user profile."""
    return _messages_to_conversation_history(messages, limit=limit)


def _build_conversation_summary(messages: list[dict], existing_summary: str = "") -> str:
    """Create a compact summary of user goals for longer-term memory."""
    user_messages = [
        str(message.get("content", "")).strip()
        for message in messages
        if message.get("role") == "user" and str(message.get("content", "")).strip()
    ][-12:]

    if not user_messages:
        return existing_summary

    joined = " ".join(user_messages).lower()

    interest_map = {
        "undergraduate admission": ["undergraduate", "bachelor", "freshman", "admission", "apply"],
        "graduate admission": ["graduate", "master", "phd", "postgraduate"],
        "international student support": ["international student", "visa", "foreign student"],
        "scholarships": ["scholarship", "financial aid", "funding"],
        "tuition and fees": ["tuition", "fees", "payment", "cost"],
        "housing and dormitory": ["housing", "dorm", "dormitory", "accommodation"],
        "program selection": ["program", "major", "course", "degree"],
        "deadlines and documents": ["deadline", "deadlines", "document", "documents", "requirement", "requirements"],
        "student services": ["student service", "support", "career", "counseling", "counselling"],
    }

    detected_interests = [
        label for label, keywords in interest_map.items() if any(keyword in joined for keyword in keywords)
    ]

    preference_clues = []
    if any("english" in message.lower() for message in user_messages):
        preference_clues.append("prefers English guidance")
    if any("korean" in message.lower() for message in user_messages):
        preference_clues.append("may want Korean guidance")
    if any(any(token in message.lower() for token in ["step by step", "steps", "explain simply"]) for message in user_messages):
        preference_clues.append("likes step-by-step explanations")
    if any(any(token in message.lower() for token in ["quick", "short answer", "brief"]) for message in user_messages):
        preference_clues.append("prefers concise answers")

    latest_goal = user_messages[-1]
    latest_goal = re.sub(r"\s+", " ", latest_goal).strip()
    if len(latest_goal) > 140:
        latest_goal = latest_goal[:137].rstrip() + "..."

    summary_parts = []
    if detected_interests:
        summary_parts.append("User interests: " + ", ".join(detected_interests[:4]))
    if preference_clues:
        summary_parts.append("Preferences: " + ", ".join(preference_clues[:3]))
    summary_parts.append(f"Latest goal: {latest_goal}")

    summary = "; ".join(summary_parts)
    return summary or existing_summary


def apply_app_styles() -> None:
    """Apply a cleaner, more chat-focused UI style."""
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #f5f7fb;
            --panel-bg: rgba(255, 255, 255, 0.88);
            --panel-border: rgba(15, 23, 42, 0.08);
            --text-main: #172033;
            --text-soft: #5b6474;
            --accent: #0f766e;
            --accent-soft: #d9f3ef;
            --assistant-bg: #ffffff;
            --user-bg: linear-gradient(135deg, #0f766e 0%, #155e75 100%);
            --shadow-soft: 0 20px 45px rgba(15, 23, 42, 0.08);
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.10), transparent 30%),
                radial-gradient(circle at top right, rgba(59, 130, 246, 0.08), transparent 25%),
                var(--app-bg);
            color: var(--text-main);
        }

        .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .chat-shell {
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 28px;
            box-shadow: var(--shadow-soft);
            padding: 1.4rem 1.4rem 0.5rem 1.4rem;
            backdrop-filter: blur(14px);
        }

        .hero-panel {
            background: linear-gradient(135deg, rgba(15, 118, 110, 0.14), rgba(255, 255, 255, 0.92));
            border: 1px solid rgba(15, 118, 110, 0.18);
            border-radius: 24px;
            padding: 1.35rem 1.5rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
        }

        .main-header {
            margin: 0;
            color: var(--text-main);
            font-size: 2.1rem;
            line-height: 1.1;
            letter-spacing: -0.03em;
        }

        .hero-subtitle {
            margin-top: 0.45rem;
            color: var(--text-soft);
            font-size: 1rem;
        }

        .hero-note {
            margin-top: 0.85rem;
            display: inline-block;
            color: var(--accent);
            background: var(--accent-soft);
            border-radius: 999px;
            padding: 0.38rem 0.75rem;
            font-size: 0.9rem;
            font-weight: 600;
        }

        div[data-testid="stChatMessage"] {
            margin-bottom: 1rem;
        }

        div[data-testid="stChatMessage"] > div {
            align-items: flex-start;
            gap: 0.85rem;
        }

        div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"],
        div[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
            border-radius: 16px;
            box-shadow: 0 8px 20px rgba(15, 23, 42, 0.10);
        }

        div[data-testid="stChatMessageContent"] {
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
            border: 1px solid rgba(15, 23, 42, 0.05);
            line-height: 1.65;
        }

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] {
            background: var(--user-bg);
            color: #ffffff;
            margin-left: auto;
            max-width: 82%;
        }

        div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) div[data-testid="stChatMessageContent"] {
            background: var(--assistant-bg);
            color: var(--text-main);
            max-width: 86%;
        }

        div[data-testid="stChatMessageContent"] p {
            margin-bottom: 0.65rem;
        }

        div[data-testid="stChatMessageContent"] p:last-child {
            margin-bottom: 0;
        }

        .chat-memory-strip {
            margin: 0 0 1rem 0;
            padding: 0.85rem 1rem;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(15, 23, 42, 0.08);
            color: var(--text-soft);
            font-size: 0.94rem;
        }

        .chat-memory-strip strong {
            color: var(--text-main);
        }

        div[data-testid="stChatInput"] {
            background: rgba(255, 255, 255, 0.90);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 22px;
            padding: 0.25rem 0.55rem;
            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.07);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(255,255,255,0.96), rgba(244,247,250,0.98));
            border-right: 1px solid rgba(15, 23, 42, 0.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _save_current_profile_state() -> None:
    """Persist current profile preferences and recent conversation memory."""
    profile_name = st.session_state.get("profile_name", "guest")
    save_user_profile(
        profile_name,
        {
            "response_tone": st.session_state.get("response_tone", "Friendly"),
            "response_detail": st.session_state.get("response_detail", "Balanced"),
            "response_language": st.session_state.get("response_language", "English"),
            "voice_input_enabled": st.session_state.get("voice_input_enabled", False),
            "tts_enabled": st.session_state.get("tts_enabled", False),
            "tool_use_enabled": st.session_state.get("tool_use_enabled", True),
            "notes": st.session_state.get("profile_notes", ""),
            "conversation_memory": _profile_conversation_memory(st.session_state.get("messages", []), limit=12),
            "conversation_summary": _build_conversation_summary(
                st.session_state.get("messages", []),
                existing_summary=st.session_state.get("conversation_summary", ""),
            ),
        },
    )


def main():
    apply_app_styles()

    # Header
    st.markdown(
        '''
        <div class="hero-panel">
            <h1 class="main-header">Kyungdong University Global Campus</h1>
            <div class="hero-subtitle">A conversational student assistant for admissions, scholarships, campus life, and support.</div>
            <div class="hero-note">Ask naturally. The assistant keeps recent context and profile goals in mind.</div>
        </div>
        <div class="chat-shell">
        ''',
        unsafe_allow_html=True,
    )
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ℹ️ About This Chatbot")
        st.markdown("""
        This is an AI-powered chatbot powered by:
        - **LLM:** Groq (Gemma 2 9B - FREE & fast!)
        - **Retrieval:** Official website text matching
        - **Interface:** Streamlit
        - **Knowledge Source:** Official KDU Global website
        
        Ask questions about:
        - 🎓 Admissions & Programs
        - 💰 Scholarships & Fees
        - 🏫 Campus Life
        - 👨‍🎓 Student Services
        """)
        
        st.markdown("---")

        st.markdown("### 👤 User Profile")
        username = st.text_input(
            "Profile Name",
            value=st.session_state.get("profile_name", "guest"),
            key="profile_name_input",
            help="Use the same profile name to keep long-term preferences.",
        ).strip() or "guest"

        if st.session_state.get("profile_name") != username:
            profile = load_user_profile(username)
            st.session_state.profile_name = username
            st.session_state.response_tone = profile["response_tone"]
            st.session_state.response_detail = profile["response_detail"]
            st.session_state.response_language = profile["response_language"]
            st.session_state.voice_input_enabled = profile["voice_input_enabled"]
            st.session_state.tts_enabled = profile["tts_enabled"]
            st.session_state.tool_use_enabled = profile["tool_use_enabled"]
            st.session_state.profile_notes = profile.get("notes", "")
            st.session_state.messages = profile.get("conversation_memory", [])
            st.session_state.conversation_summary = profile.get("conversation_summary", "")

        st.markdown("### 🧠 Chat Experience")
        st.session_state.response_tone = st.selectbox(
            "Tone",
            ["Friendly", "Professional", "Conversational"],
            index=_safe_index(["Friendly", "Professional", "Conversational"], st.session_state.get("response_tone", "Friendly"), default=0),
            key="response_tone_selector",
        )
        st.session_state.response_detail = st.selectbox(
            "Detail Level",
            ["Concise", "Balanced", "Detailed"],
            index=_safe_index(["Concise", "Balanced", "Detailed"], st.session_state.get("response_detail", "Balanced"), default=1),
            key="response_detail_selector",
        )
        st.session_state.response_language = st.selectbox(
            "Response Language",
            ["English", "Korean", "Auto"],
            index=_safe_index(["English", "Korean", "Auto"], st.session_state.get("response_language", "English"), default=0),
            key="response_language_selector",
        )

        st.session_state.voice_input_enabled = st.checkbox(
            "Enable Voice Input",
            value=st.session_state.get("voice_input_enabled", False),
            key="voice_input_toggle",
        )
        st.session_state.tts_enabled = st.checkbox(
            "Enable Text-to-Speech",
            value=st.session_state.get("tts_enabled", False),
            key="tts_toggle",
        )
        st.session_state.tool_use_enabled = st.checkbox(
            "Enable Tool Actions (Web/Calendar/Email)",
            value=st.session_state.get("tool_use_enabled", True),
            key="tool_toggle",
        )
        st.session_state.profile_notes = st.text_area(
            "Preference Notes",
            value=st.session_state.get("profile_notes", ""),
            height=80,
            key="profile_notes_editor",
            help="Saved long-term with this profile.",
        )

        if st.session_state.get("conversation_summary"):
            st.caption("Conversation memory summary")
            st.info(st.session_state.get("conversation_summary", ""))

        if st.button("💾 Save Profile", use_container_width=True):
            _save_current_profile_state()
            st.success("Profile saved")

        with st.expander("📊 Analytics Dashboard", expanded=False):
            snapshot = get_analytics_snapshot()
            st.metric("Total Queries", snapshot["total_queries"])
            st.metric("Unknown Rate", f"{snapshot['unknown_rate']:.1f}%")
            st.metric("Moderation Trigger Rate", f"{snapshot['moderation_rate']:.1f}%")
            st.metric("Conversation Quality", f"{snapshot['quality_score']:.1f}%")
            st.caption(f"Average retrieved docs per query: {snapshot['avg_retrieved_docs']:.2f}")

            st.markdown("**Top Topics**")
            if snapshot["top_topics"]:
                for topic, count in snapshot["top_topics"]:
                    st.write(f"- {topic}: {count}")
            else:
                st.write("- No data yet")

            st.markdown("**Tool Usage**")
            if snapshot["tools_used"]:
                for tool, count in snapshot["tools_used"]:
                    st.write(f"- {tool}: {count}")
            else:
                st.write("- No tool calls yet")

            st.markdown("**Top Negative Feedback Reasons**")
            if snapshot.get("top_feedback_reasons"):
                for reason, count in snapshot["top_feedback_reasons"]:
                    st.write(f"- {reason}: {count}")
            else:
                st.write("- No negative feedback reasons yet")

        with st.expander("🛡️ Admin Profile", expanded=False):
            admin_password = load_admin_password()
            if not admin_password:
                st.warning("Set ADMIN_PASSWORD in environment or secrets to enable admin login.")
            else:
                admin_user = st.text_input("Admin Username", value="admin", key="admin_user_input")
                admin_pass_input = st.text_input("Admin Password", type="password", key="admin_password_input")

                if st.button("Login as Admin", use_container_width=True):
                    is_valid = admin_user.strip().lower() == "admin" and admin_pass_input == admin_password
                    st.session_state.admin_authenticated = bool(is_valid)
                    if is_valid:
                        st.success("Admin login successful")
                    else:
                        st.error("Invalid admin credentials")

                if st.session_state.get("admin_authenticated", False):
                    st.success("Admin mode enabled")
                    report = build_developer_feedback_report()
                    st.download_button(
                        "Download Developer Feedback Report",
                        data=json.dumps(report, ensure_ascii=False, indent=2),
                        file_name="developer_feedback_report.json",
                        mime="application/json",
                        use_container_width=True,
                    )
                    if st.button("Logout Admin", use_container_width=True):
                        st.session_state.admin_authenticated = False
                        st.info("Admin logged out")

        st.markdown("---")
        
        st.markdown("### 🎯 Quick Topics")
        topics = {
            "📝 Admissions": "Tell me about the admissions process for international students",
            "💼 Programs": "What programs does Kyungdong offer?",
            "🎓 Scholarships": "What scholarships are available for international students?",
            "💵 Tuition": "How much does tuition cost per year?",
            "🏠 Campus": "Describe the campus facilities and housing",
            "🆘 Support": "What student services are available?",
        }
        
        for label, question in topics.items():
            if st.button(label, use_container_width=True, key=label):
                st.session_state.suggested_question = question
        
        st.markdown("---")
        
        if st.button("🔄 Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            if st.session_state.get("chatbot"):
                st.session_state.chatbot.set_conversation_history([])
                st.session_state.chatbot.clear_history()
            _save_current_profile_state()
            st.success("✅ Chat history cleared!")

        if st.button("📥 Export Chat (JSON)", use_container_width=True):
            export_payload = {
                "exported_at": datetime.now().isoformat(),
                "messages": _serialize_messages_for_export(st.session_state.get("messages", [])),
            }
            st.download_button(
                "Download chat_export.json",
                data=json.dumps(export_payload, ensure_ascii=False, indent=2),
                file_name="chat_export.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("---")

        with st.expander("🌐 Official Website Sources"):
            for page in get_official_source_pages():
                st.markdown(f"- [{page['title']}]({page['url']})")
    
    # Check for API key
    chatbot = get_chatbot()
    
    if not chatbot:
        st.warning("⚠️ **Setup Required: GROQ_API_KEY Missing**")
        
        with st.expander("📋 Click to see setup instructions", expanded=True):
            st.markdown("""
            ### How to set up your API key:
            
            1. **Get a free API key from Groq:**
               - Visit: https://console.groq.com
               - Sign up for a free account
               - Generate an API key
            
            2. **Add the API key to this project:**
               - Create/Edit file: `.streamlit/secrets.toml`
               - Add this line:
               ```
               GROQ_API_KEY = "your_actual_api_key_here"
               ```
            
            3. **Restart the app** (press R or restart Streamlit)
            
            ### Or set as environment variable:
            ```bash
            # Windows PowerShell:
            $env:GROQ_API_KEY = "your_api_key"
            
            # Windows Command Prompt:
            set GROQ_API_KEY=your_api_key
            
            # Linux/Mac:
            export GROQ_API_KEY="your_api_key"
            ```
            """)
        st.stop()
    
    st.session_state.chatbot = chatbot
    
    # Status indicator
    with st.sidebar:
        try:
            count = chatbot.ensure_collection_exists()
            if count > 0:
                st.success(f"✅ Knowledge Base: {count} documents loaded")
            else:
                st.warning("⚠️ Knowledge Base initializing...")

            if st.session_state.get("knowledge_synced_at"):
                st.caption(f"Last website sync: {st.session_state['knowledge_synced_at']}")

            if st.button("🌐 Refresh Official Website Data", use_container_width=True):
                sync_knowledge_base(
                    chatbot,
                    force_refresh=True,
                    status_message="🌐 Refreshing from official KDU Global website..."
                )
                st.success("✅ Official website data refreshed")
                st.rerun()
        except Exception as e:
            st.warning(f"⚠️ Collection error: {str(e)[:50]}")
    
    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "documents_loaded" not in st.session_state:
        st.session_state.documents_loaded = False
    if "conversation_summary" not in st.session_state:
        st.session_state.conversation_summary = load_user_profile(
            st.session_state.get("profile_name", "guest")
        ).get("conversation_summary", "")

    if st.session_state.get("conversation_summary"):
        st.markdown(
            f'<div class="chat-memory-strip"><strong>Remembered context:</strong> {st.session_state.get("conversation_summary", "")}</div>',
            unsafe_allow_html=True,
        )
    
    # Display conversation history
    messages = st.session_state.get("messages", [])
    assistant_indexes = [i for i, m in enumerate(messages) if m.get("role") == "assistant"]
    last_assistant_index = assistant_indexes[-1] if assistant_indexes else -1

    for msg_index, message in enumerate(messages):
        with st.chat_message(message["role"], avatar="👤" if message["role"] == "user" else "🤖"):
            st.markdown(message["content"])
            
            # Display sources for assistant messages
            if message["role"] == "assistant" and message.get("sources"):
                display_sources(message["sources"])

            if message["role"] == "assistant" and message.get("tool_action"):
                display_tool_payload(
                    message.get("tool_action", ""),
                    message.get("tool_payload", {}),
                    event_id=message.get("event_id", ""),
                )

            # Display follow-up buttons only for the latest assistant message
            if (
                message["role"] == "assistant"
                and "followups" in message
                and msg_index == last_assistant_index
            ):
                st.markdown("### 💬 Suggested Follow-up Questions")
                for follow_idx, suggestion in enumerate(message["followups"], 1):
                    if st.button(suggestion, key=f"followup_{msg_index}_{follow_idx}"):
                        st.session_state.suggested_question = suggestion
                        st.rerun()

            if message["role"] == "assistant" and msg_index == last_assistant_index:
                event_id = message.get("event_id", "")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("👍 Helpful", key=f"feedback_up_{msg_index}") and event_id:
                        record_feedback(event_id, "up")
                        st.success("Thanks for the feedback")
                with col2:
                    if st.button("👎 Needs improvement", key=f"feedback_down_{msg_index}") and event_id:
                        st.session_state.feedback_target_event_id = event_id
                        st.info("Please select a reason below")

                if event_id and st.session_state.get("feedback_target_event_id") == event_id:
                    reason = st.selectbox(
                        "What was wrong?",
                        [
                            "Wrong fact",
                            "Not clear",
                            "Too long or too short",
                            "Unsafe response",
                            "Missing tool action",
                            "Other",
                        ],
                        key=f"feedback_reason_{msg_index}",
                    )
                    note = st.text_area(
                        "Optional note",
                        key=f"feedback_note_{msg_index}",
                        height=70,
                    )
                    if st.button("Submit feedback details", key=f"feedback_submit_{msg_index}"):
                        record_feedback(event_id, "down", reason=reason, note=note.strip())
                        st.session_state.feedback_target_event_id = ""
                        st.success("Detailed feedback recorded")
    
    # Handle suggested question, voice input, or chat input
    user_input = None
    if "suggested_question" in st.session_state:
        user_input = st.session_state.suggested_question
        del st.session_state.suggested_question
    else:
        if st.session_state.get("voice_input_enabled", False):
            if mic_recorder is None:
                st.caption("Voice input dependency missing: install streamlit-mic-recorder")
            else:
                st.markdown("### 🎙️ Voice Input")
                st.caption("Tip: speak clearly, pause before and after speaking, and press Stop before sending.")
                audio_data = mic_recorder(
                    start_prompt="Start recording",
                    stop_prompt="Stop recording",
                    key="voice_recorder",
                    just_once=False,
                )
                voice_output = st.session_state.get("voice_recorder_output") or audio_data
                audio_bytes = _extract_audio_bytes(voice_output)
                if audio_bytes:
                    signature = f"{len(audio_bytes)}-{hash(audio_bytes[:64])}"
                    if signature != st.session_state.get("last_voice_signature"):
                        st.session_state.last_voice_signature = signature
                        selected_language = st.session_state.get("response_language", "English")
                        input_lang = "ko" if selected_language == "Korean" else None
                        transcribed = chatbot.transcribe_audio(audio_bytes, language=input_lang)
                        if transcribed:
                            user_input = transcribed
                            st.info(f"Transcribed: {transcribed}")
                        else:
                            st.warning("Voice was captured but transcription was empty. Try speaking a little louder or using English/Korean explicitly.")
                elif audio_data:
                    st.info("Recorder is ready. Click Stop after speaking to send audio for transcription.")

        if not user_input:
            user_input = st.chat_input(
                "Ask about admissions, programs, scholarships, campus life, or student services...",
                key="chat_input"
            )
    
    # Process user input
    if user_input:
        # Initialize messages list if needed
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Add user message to session
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        prior_history = _messages_to_conversation_history(st.session_state.messages[:-1], limit=8)
        chatbot.set_conversation_history(prior_history)
        
        moderation = chatbot.moderate_user_input(
            user_input,
            conversation_history=prior_history,
            conversation_summary=st.session_state.get("conversation_summary", ""),
        )
        topic = chatbot.infer_query_topic(user_input)

        # Generate response
        with st.chat_message("assistant", avatar="🤖"):
            retrieved_docs = []
            docs_used = []
            tool_action = "none"
            tool_payload = {}
            unknown = False
            moderated = False

            if not moderation.allowed:
                moderated = True
                response = moderation.reason
                if detect_input_language(user_input) == "Korean":
                    response = (
                        "안전 정책에 따라 해당 요청은 처리할 수 없습니다. "
                        "경동대학교 글로벌 캠퍼스 관련 질문으로 다시 요청해 주세요."
                    )
                st.warning("Request blocked by safety layer")
            else:
                tool_result = None
                if st.session_state.get("tool_use_enabled", True):
                    tool_result = chatbot.handle_tool_action(user_input)

                if tool_result and tool_result.handled:
                    tool_action = tool_result.action
                    tool_payload = tool_result.payload or {}
                    response = tool_result.response
                else:
                    with st.spinner("🔍 Searching knowledge base..."):
                        retrieved_docs = chatbot.retrieve_documents(user_input, top_k=3)

                    if len(retrieved_docs) > 0:
                        st.success(f"✓ Found {len(retrieved_docs)} relevant document(s)")
                    else:
                        st.warning("⚠️ No relevant documents found - generating general response")

                    with st.spinner("💭 Generating response..."):
                        resolved_language = resolve_response_language(
                            user_input,
                            st.session_state.get("response_language", "English"),
                        )
                        style_options = {
                            "tone": st.session_state.get("response_tone", "Friendly"),
                            "detail_level": st.session_state.get("response_detail", "Balanced"),
                            "response_language": resolved_language,
                            "profile_notes": st.session_state.get("profile_notes", ""),
                            "conversation_summary": st.session_state.get("conversation_summary", ""),
                        }
                        response, docs_used = chatbot.generate_response(
                            user_input,
                            retrieved_docs,
                            style_options=style_options,
                            conversation_history=prior_history,
                        )

                unknown = "i don't know based on official data currently loaded" in response.lower()
            
            st.markdown(response)

            if tool_action != "none":
                display_tool_payload(tool_action, tool_payload)

            # Display sources
            if retrieved_docs:
                st.divider()
                display_sources(retrieved_docs)

            if st.session_state.get("tts_enabled", False):
                output_language = resolve_response_language(
                    user_input,
                    st.session_state.get("response_language", "English"),
                )
                tts_audio = synthesize_tts_audio(
                    response,
                    output_language,
                )
                if tts_audio:
                    st.audio(tts_audio, format="audio/mp3")

            event_id = record_analytics_event(
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "profile": st.session_state.get("profile_name", "guest"),
                    "query": user_input,
                    "topic": topic,
                    "response_language": resolve_response_language(
                        user_input,
                        st.session_state.get("response_language", "English"),
                    ),
                    "retrieved_count": len(retrieved_docs),
                    "unknown": unknown,
                    "moderated": moderated,
                    "tool_action": tool_action,
                }
            )

            # Store message with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": response,
                "sources": docs_used,
                "followups": chatbot.generate_follow_up_suggestions(user_input, docs_used, limit=3),
                "tool_action": tool_action,
                "tool_payload": tool_payload,
                "event_id": event_id,
            })
            chatbot.set_conversation_history(_messages_to_conversation_history(st.session_state.messages, limit=8))
            st.session_state.conversation_summary = _build_conversation_summary(
                st.session_state.messages,
                existing_summary=st.session_state.get("conversation_summary", ""),
            )
            _save_current_profile_state()

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()