import importlib

# ==============================================================================
# TEST SUITE: DYNAMIC ENVIRONMENT VARIABLES & FALLBACKS
# ==============================================================================

def test_model_name_default_fallback(monkeypatch):
    """Ensures that the application defaults to the standard model
    when no custom GEMINI_MODEL environment variable is configured.
    """
    import app  # Load module context
    
    # Arrange - Purge target environment variables from current process memory
    monkeypatch.delenv("GEMINI_MODEL", raising=False)
    
    # Act - Reload application module to force initialization cycle
    importlib.reload(app)
    
    # Assert - Verify application falls back to the specified default model
    assert app.MODEL_NAME == "gemini-2.5-flash"


def test_model_name_custom_value(monkeypatch):
    """Ensures the application dynamically overrides the target model
    when configured via custom system environment variables.
    """
    import app  # Load module context
    
    # Arrange - Simulate custom runtime environment configuration
    monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
    
    # Act - Reload application to register updated environmental states
    importlib.reload(app)
    
    # Assert - Verify system correctly binds the configured model parameter
    assert app.MODEL_NAME == "gemini-2.5-pro"
    