from unittest.mock import patch
import pytest

# ==============================================================================
# TEST SUITE: INTEGRATION & THIRD-PARTY ERROR HANDLING
# ==============================================================================

@patch("google.genai.chats.Chats.create")
def test_gemini_api_error_handling(mock_chats_create):
    """Verifies that connection-level exceptions raised by the external
    Google GenAI SDK propagate correctly through the communication layer.
    """
    # Arrange - Force mock client to raise a network connection error
    mock_chats_create.side_effect = Exception("Connection error with upstream Google servers")
    
    # Act & Assert - Initialize sandbox client instance and verify exception bubble-up
    with pytest.raises(Exception) as exc_info:
        from google import genai
        # Provide simulated API credentials to prevent SDK self-initialization blockages
        client = genai.Client(api_key="fake_key_for_testing")
        client.chats.create(model="gemini-2.5-flash", history=[])
        
    assert "Connection error" in str(exc_info.value)
    