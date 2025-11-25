import pytest
from unittest.mock import patch, MagicMock
from ui_controller_mcp.utils.security import CredentialManager

@pytest.fixture
def mock_keyring():
    with patch("ui_controller_mcp.utils.security.keyring") as mock:
        store = {}
        def set_pw(service, user, pw):
            store[f"{service}:{user}"] = pw
        def get_pw(service, user):
            return store.get(f"{service}:{user}")
        
        mock.set_password.side_effect = set_pw
        mock.get_password.side_effect = get_pw
        yield mock

def test_credential_manager_keyring(mock_keyring):
    manager = CredentialManager()
    
    # Test setting credential
    assert manager.set_credential("test_user", "secret123")
    
    # Test retrieving credential
    assert manager.get_credential("test_user") == "secret123"
    
    # Test non-existent credential
    assert manager.get_credential("unknown") is None

@patch("ui_controller_mcp.utils.security.keyring")
def test_credential_manager_fallback(mock_keyring, tmp_path):
    # Simulate keyring failure
    mock_keyring.set_password.side_effect = Exception("Keyring unavailable")
    mock_keyring.get_password.side_effect = Exception("Keyring unavailable")
    
    # Mock file paths to use temp dir
    with patch.object(CredentialManager, "__init__", lambda self: None):
        manager = CredentialManager()
        manager._key_file = tmp_path / ".key"
        manager._data_file = tmp_path / ".data"
        manager._ensure_key()
        
        # Test setting credential (should use fallback)
        assert manager.set_credential("fallback_user", "fallback_pass")
        
        # Test retrieving credential
        assert manager.get_credential("fallback_user") == "fallback_pass"
