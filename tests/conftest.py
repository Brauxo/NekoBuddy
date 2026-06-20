import pytest
import os
from pathlib import Path

@pytest.fixture(autouse=True)
def mock_env_file(tmp_path, monkeypatch):
    """Redirects SettingsManager env path to a temporary file for tests to isolate configurations."""
    temp_env = tmp_path / ".env"
    temp_env.write_text("PET_NAME=TestCat\nPET_COLOR=#112233\nMASTER_NAME=Master\n", encoding="utf-8")
    
    # Isolate from host machine environment variables
    monkeypatch.delenv("MASTER_NAME", raising=False)
    monkeypatch.delenv("PET_NAME", raising=False)
    monkeypatch.delenv("PET_COLOR", raising=False)
    monkeypatch.delenv("MASTER_COLOR", raising=False)
    monkeypatch.delenv("LITELLM_MODEL", raising=False)
    monkeypatch.delenv("PET_LANGUAGE", raising=False)

    import src.config.settings
    monkeypatch.setattr(src.config.settings, "ENV_PATH", temp_env)
    src.config.settings._pending_writes.clear()
    src.config.settings._flush_scheduled = False
    src.config.settings.SettingsManager.reload()
    
    yield temp_env

