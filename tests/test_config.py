import os
import importlib
import app  # Importa o app.py

def test_model_name_default_fallback(monkeypatch):
    # Arrange - Garante que a variável do modelo está vazia na memória
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    
    # Act - Recarrega o módulo para testar a lógica de inicialização
    importlib.reload(app)
    
    # Assert - Deve assumir o valor padrão definido no código
    assert app.MODEL_NAME == "gemini-2.5-flash"

def test_model_name_custom_value(monkeypatch):
    # Arrange - Simula que o usuário mudou o modelo no arquivo .env para o Pro
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
    
    # Act
    importlib.reload(app)
    
    # Assert - Deve capturar o modelo do ambiente corretamente
    assert app.MODEL_NAME == "gemini-2.5-pro"
    