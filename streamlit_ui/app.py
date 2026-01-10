"""
Streamlit UI for UOV AI Assistant.

A chat interface for the Faculty of Technological Studies chatbot.
"""

import streamlit as st
import requests
from uuid import uuid4, UUID
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="UOV AI Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with brand colors
st.markdown("""
<style>
    /* Force light mode */
    [data-testid="stAppViewContainer"] {
        background-color: #ffffff;
    }
    
    /* Main theme colors */
    :root {
        --primary-color: #6a0047;
        --secondary-color: #ffffff;
        --background-color: #f5f5f5;
        --text-color: #333333;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #6a0047 0%, #8b0059 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9);
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
    }
    
    /* Chat message styling */
    .user-message {
        background-color: #e8e8e8;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #6a0047;
    }
    
    .assistant-message {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #6a0047;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Citation styling */
    .citation {
        background-color: #f9f9f9;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        font-size: 0.9rem;
        border-left: 3px solid #6a0047;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #6a0047;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #8b0059;
        box-shadow: 0 4px 8px rgba(106, 0, 71, 0.3);
    }
    
    /* Simple feedback buttons - no background */
    .feedback-btn {
        background: none !important;
        border: none !important;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0.25rem 0.5rem;
        transition: transform 0.2s;
    }
    
    .feedback-btn:hover {
        transform: scale(1.2);
    }
    
    /* Input box styling - enhanced */
    .stChatInputContainer {
        border: 2px solid #6a0047 !important;
        border-radius: 25px !important;
        padding: 0.5rem !important;
        box-shadow: 0 4px 12px rgba(106, 0, 71, 0.15) !important;
        background: white !important;
    }
    
    .stChatInput > div > div > input {
        border: none !important;
        border-radius: 20px !important;
        padding: 0.75rem 1rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInput > div > div > input:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    
    /* Quick questions styling */
    .quick-question-btn {
        background-color: #f0f0f0;
        border: 1px solid #6a0047;
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
        font-size: 0.9rem;
    }
    
    .quick-question-btn:hover {
        background-color: #6a0047;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# API configuration
API_BASE_URL = "https://thasvithu-uov-assistant-backend.hf.space/"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_available" not in st.session_state:
    st.session_state.api_available = None


# Helper functions
def check_api_health():
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def send_message(question: str):
    """Send a message to the chatbot API."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat",
            json={
                "session_id": st.session_state.session_id,
                "question": question
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to connect to API: {e}")
        return None


def submit_feedback(message_id: str, rating: str, comment: str = ""):
    """Submit feedback for a message."""
    try:
        response = requests.post(
            f"{API_BASE_URL}/feedback",
            json={
                "session_id": st.session_state.session_id,
                "message_id": message_id,
                "rating": rating,
                "comment": comment
            },
            timeout=10
        )
        return response.status_code == 200
    except:
        return False


# Header
st.markdown("""
<div class="main-header">
    <h1>🎓 UOV AI Assistant</h1>
    <p>Faculty of Technological Studies - University of Vavuniya</p>
</div>
""", unsafe_allow_html=True)

# Quick questions (show only if no messages yet)
if len(st.session_state.messages) == 0:
    st.markdown("### ❓ Quick Questions")
    st.markdown("Click a question to get started:")
    
    quick_questions = [
        "What is the vision of the faculty?",
        "Who is the dean?",
        "What programs are offered?",
        "When was the faculty established?"
    ]
    
    cols = st.columns(2)
    for i, q in enumerate(quick_questions):
        with cols[i % 2]:
            if st.button(q, key=f"quick_{i}", use_container_width=True):
                st.session_state.quick_question = q
                st.rerun()
    
    st.markdown("---")

# Sidebar
with st.sidebar:
    st.markdown("### 📚 About")
    st.markdown("""
    This AI assistant helps answer questions about the Faculty of Technological Studies 
    at the University of Vavuniya.
    
    **Features:**
    - 💬 Natural language Q&A
    - 📖 Source citations
    - 🌐 Multilingual support
    - 👍 Feedback system
    """)
    
    st.markdown("---")
    
    # Session info
    st.markdown("### 💬 Session Info")
    st.caption(f"Session ID: `{st.session_state.session_id[:8]}...`")
    st.caption(f"Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 New Session"):
        st.session_state.session_id = str(uuid4())
        st.session_state.messages = []
        st.rerun()

# Main chat area
st.markdown("### 💬 Chat")

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="user-message">
            <strong>You:</strong><br>
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {msg["content"]}
        </div>
        """, unsafe_allow_html=True)
        
        # Feedback buttons (simple, no background)
        if msg.get("message_id"):
            col1, col2, col3 = st.columns([1, 1, 8])
            with col1:
                if st.button("👍", key=f"up_{msg['message_id']}", help="Helpful"):
                    if submit_feedback(msg["message_id"], "up"):
                        st.toast("Thanks for your feedback!", icon="✅")
            with col2:
                if st.button("👎", key=f"down_{msg['message_id']}", help="Not helpful"):
                    if submit_feedback(msg["message_id"], "down"):
                        st.toast("Thanks for your feedback!", icon="✅")

# Chat input
st.markdown("---")

# Character limit configuration
MAX_CHARS = 1000

# Handle quick question
if "quick_question" in st.session_state:
    user_input = st.session_state.quick_question
    del st.session_state.quick_question
else:
    user_input = st.chat_input("Ask a question about the Faculty of Technological Studies...")

# Validate input length
if user_input:
    input_length = len(user_input)
    
    # Check character limit
    if input_length > MAX_CHARS:
        st.error(f"Your question has {input_length} characters. Please shorten it to {MAX_CHARS} characters or less (~150-200 words).")
        st.stop()
    
    # Check API availability
    if not check_api_health():
        st.error("⚠️ API is not available. Please start the backend server.")
        st.stop()
    
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Show loading
    with st.spinner("🤔 Thinking..."):
        # Get response
        response = send_message(user_input)
        
        if response:
            # Add assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": response["answer"],
                "citations": response.get("citations", []),
                "message_id": response.get("message_id")
            })
    
    # Rerun to display new messages
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9rem;">
    <p>University of Vavuniya - Faculty of Technological Studies</p>
    <p>Powered by RAG Technology | Built with ❤️ using Streamlit</p>
</div>
""", unsafe_allow_html=True)
