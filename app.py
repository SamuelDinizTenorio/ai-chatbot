import streamlit as st
from google import genai
import os
import time
from dotenv import load_dotenv
import logging
from typing import List, Dict

# Load environment variables required for execution
load_dotenv()

# ==============================================================================
# LOGGING AND TELEMETRY SYSTEM
# ==============================================================================

class SessionFilter(logging.Filter):
    """Custom log filter to inject the Streamlit session ID into log records.
    
    Enables isolated tracking of specific user interactions, maintaining session 
    boundary separation even when multiple clients access the chatbot concurrently.
    """
    def filter(self, record: logging.LogRecord) -> bool:
        # Official context retrieval utility from the Streamlit runtime
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        
        # Extract the unique Streamlit session identifier associated with the active connection context
        ctx = get_script_run_ctx()
        # Safe fallback evaluation: populate with the session ID only if context runtime is active
        record.session_id = ctx.session_id if (ctx and hasattr(ctx, 'session_id')) else "N/A"
        return True

@st.cache_resource
def setup_logging() -> logging.Logger:
    """Configures high-performance logging optimized for containerized environments (e.g., AWS ECS/Fargate)."""
    logger = logging.getLogger("ChatBot")
    logger.setLevel(logging.INFO)
    
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # Standardized logging format easily parsed by cloud analytics platforms (such as AWS CloudWatch Logs Insights)
    log_format = '%(asctime)s - [%(session_id)s] - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    
    # Redirect logs to standard output (stdout) for automated container runtime aggregation
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addFilter(SessionFilter())
    logger.addHandler(console_handler)
    
    return logger

# Initialize the global application logger
logger = setup_logging()

# ==============================================================================
# CORE COMPONENT INITIALIZATION
# ==============================================================================

try:
    # The SDK automatically establishes authentication via the GEMINI_API_KEY environment variable
    client = genai.Client()
except Exception as e:
    logger.critical(f"Critical failure during Gemini client initialization: {str(e)}")
    st.error("Internal configuration error. Please contact the administrator.")
    st.stop()

# Default model fallback definition if the GEMINI_MODEL environment variable is undefined
MODEL_NAME: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ==============================================================================
# DATA TRANSFORMATION AND SCHEMAS
# ==============================================================================

def prepare_gemini_history(messages: List[Dict[str, str]]) -> List[genai.types.Content]:
    """Serializes the Streamlit state history into the structured schemas expected by the Gemini SDK.
    
    The Gemini API strictly requires specialized Content and Part objects,
    maintaining an alternate turn-taking sequence between the 'user' and 'model' roles.

    Args:
        messages (List[Dict[str, str]]): List of raw message dicts formatted as 
            [{"role": "...", "content": "..."}].

    Returns:
        List[genai.types.Content]: List of validated Content schema payloads for the API.
    """
    gemini_history: List[genai.types.Content] = []
    for msg in messages:
        gemini_history.append(
            genai.types.Content(
                role=msg["role"],
                parts=[genai.types.Part.from_text(text=msg["content"])]
            )
        )
    return gemini_history

# ==============================================================================
# STREAMLIT USER INTERFACE & STATE ENGINE
# ==============================================================================

def main():
    # Render structural UI components
    st.title("🤖 AI Chatbot Assistant")
    st.caption("Developed with Google Gemini SDK and Streamlit")
    st.markdown("---")

    # Safe initialization of state persistence for user message history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Capture prompt payload from the user input interface
    user_input: str = st.chat_input()

    # Re-render persistent history elements to screen
    for message in st.session_state.messages:
        role_display = "assistant" if message["role"] == "model" else "user"
        st.chat_message(role_display).write(message["content"])

    # Evaluate incoming message payload
    if user_input:
        # Update UI layout and local session state with the current user prompt
        st.chat_message("user").write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        logger.info(f"Incoming message received. Local message history depth: {len(st.session_state.messages)} messages.")
        
        try:
            logger.info(f"Initiating remote API request (Target Model: {MODEL_NAME})")
            
            # Initiate high-resolution performance timer to measure end-to-end API inference latency
            start_time = time.time()
            
            # Extract historical runtime state (excluding current un-evaluated message)
            gemini_history = prepare_gemini_history(st.session_state.messages[:-1])
            
            chat = client.chats.create(
                model=MODEL_NAME, 
                history=gemini_history
            )
            
            response = chat.send_message(user_input)
            ai_response = response.text
            
            # Calculate round-trip latency metrics
            latency = time.time() - start_time
            
            # Extract system token usage metadata if exposed by the response schema
            token_info = ""
            if hasattr(response, 'usage_metadata') and response.usage_metadata:
                prompt_tokens = response.usage_metadata.prompt_token_count
                candidates_tokens = response.usage_metadata.candidates_token_count
                token_info = f" | Prompt Tokens: {prompt_tokens} | Output Tokens: {candidates_tokens}"
            
            # Output structured telemetry log mapping response latency, token limits, and consumption cost metrics
            logger.info(f"Response generated successfully | End-to-End Latency: {latency:.2f}s{token_info}")
            
            # Synchronize client state and UI container with the generated AI model output
            st.chat_message("assistant").write(ai_response)
            st.session_state.messages.append({"role": "model", "content": ai_response})
            
        except Exception as e:
            # Capture structural stack trace for execution failures during model evaluation
            logger.error(f"Communication failure with upstream GenAI service provider: {str(e)}", exc_info=True)
            st.error("We encountered an error processing your request. Please try again.")
        
if __name__ == "__main__":
    main()
    