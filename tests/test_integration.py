from unittest.mock import patch
import pytest

# Apontam o patch diretamente para a criação de chats dentro da biblioteca da Google
@patch("google.genai.chats.Chats.create")
def test_gemini_api_error_handling(mock_chats_create):
    # Arrange - Força o método create a lançar o erro de conexão
    mock_chats_create.side_effect = Exception("Erro de conexão com o servidor do Google")
    
    # Act & Assert - Testa se chamando a criação do chat o erro é disparado
    with pytest.raises(Exception) as exc_info:
        from google import genai
        client = genai.Client()
        client.chats.create(model="gemini-2.5-flash", history=[])
        
    assert "Erro de conexão" in str(exc_info.value)
    