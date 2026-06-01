import logging
from app import SessionFilter

# ==============================================================================
# TEST SUITE: TELEMETRY & LOGGING ISOLATION
# ==============================================================================

def test_session_filter_outside_streamlit():
    """Validates telemetry log safety boundaries when execution occurs
    outside of an active Streamlit runtime session context (e.g., during tests).
    """
    # Arrange - Instantiate the custom logging filter and a mock log record
    filter_instance = SessionFilter()
    log_record = logging.LogRecord(
        name="test_logger", 
        level=logging.INFO, 
        pathname="", 
        lineno=0, 
        msg="Telemetry verification test message", 
        args=(), 
        exc_info=None
    )
    
    # Act - Apply filtering transformations on the simulated log entity
    filter_instance.filter(log_record)
    
    # Assert - Verify metadata injection defaults safely to "N/A" context
    assert hasattr(log_record, "session_id")
    assert log_record.session_id == "N/A"
    