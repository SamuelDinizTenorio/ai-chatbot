from app import prepare_gemini_history

def test_prepare_gemini_history_format():
    # 1. Arrage - Dados simulados do Streamlit
    mock_messages = [
        {"role": "user", "content": "Olá, tudo bem?"},
        {"role": "model", "content": "Olá! Como posso ajudar hoje?"}
    ]
    
    # 2. Act - Executa a função do seu app.py
    resultado = prepare_gemini_history(mock_messages)
    
    # 3. Assert
    assert len(resultado) == 2
    assert resultado[0].role == "user"
    assert resultado[1].role == "model"
    assert resultado[0].parts[0].text == "Olá, tudo bem?"
    assert resultado[1].parts[0].text == "Olá! Como posso ajudar hoje?"
