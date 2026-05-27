from unittest.mock import patch
import pytest

# Aponta o patch diretamente para a criação de chats dentro da biblioteca da Google
@patch("google.genai.chats.Chats.create")
def test_gemini_api_error_handling(mock_chats_create):
    # Arrange - Força o método create a lançar o erro de conexão
    mock_chats_create.side_effect = Exception("Erro de conexão com o servidor do Google")
    
    # Act & Assert - Passa uma api_key fictícia para a biblioteca não travar no início
    with pytest.raises(Exception) as exc_info:
        from google import genai
        # Passando a chave fake aqui, ele ignora a falta de .env e vai direto para o método mockado
        client = genai.Client(api_key="fake_key_for_testing")
        client.chats.create(model="gemini-2.5-flash", history=[])
        
    assert "Erro de conexão" in str(exc_info.value)