import time
from src.config.settings import SettingsManager

def test_get_settings():
    """Verifies that default settings and values from mock env are correctly loaded."""
    assert SettingsManager.get_pet_name() == "TestCat"
    assert SettingsManager.get_pet_color() == "#112233"
    assert SettingsManager.get_master_name() == "Master"

def test_set_settings(mock_env_file):
    """Verifies that settings updates are instant in-memory and eventually written to disk."""
    SettingsManager.set("PET_NAME", "Whiskers")
    assert SettingsManager.get_pet_name() == "Whiskers"
    
    # Allow background saving thread to complete disk write
    time.sleep(0.1)
    
    content = mock_env_file.read_text(encoding="utf-8")
    assert "PET_NAME" in content
    assert "Whiskers" in content
