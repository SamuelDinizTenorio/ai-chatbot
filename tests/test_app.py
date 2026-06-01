from app import prepare_gemini_history

# ==============================================================================
# TEST SUITE: DATA TRANSFORMATION & SCHEMA VALIDATION
# ==============================================================================

def test_prepare_gemini_history_format():
    """Validates that raw Streamlit message structures are correctly serialized
    into Google GenAI Content and Part schemas.
    """
    # 1. Arrange - Simulate persistent message logs from the user interface
    mock_messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "model", "content": "Hello! How can I assist you today?"}
    ]
    
    # 2. Act - Execute the serialization function defined in app.py
    result = prepare_gemini_history(mock_messages)
    
    # 3. Assert - Verify correct structural hierarchy and turn-taking roles
    assert len(result) == 2
    assert result[0].role == "user"
    assert result[1].role == "model"
    assert result[0].parts[0].text == "Hello, how are you?"
    assert result[1].parts[0].text == "Hello! How can I assist you today?"
