import logging
from app import SessionFilter

def test_session_filter_outside_streamlit():
    # Arrange - Cria um registro de log falso e o filtro
    filtro = SessionFilter()
    log_record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="", lineno=0, msg="Mensagem de teste", args=(), exc_info=None
    )
    
    # Act - Executa o filtro sobre o registro
    filtro.filter(log_record)
    
    # Assert - Fora do Streamlit (no ambiente de teste), ele deve injetar "N/A"
    assert hasattr(log_record, "session_id")
    assert log_record.session_id == "LOCAL"
    