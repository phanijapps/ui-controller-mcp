import os
import keyring
import json
from pathlib import Path
from cryptography.fernet import Fernet
from typing import Optional

class CredentialManager:
    """
    Manages secure storage of credentials using system keyring or encrypted file fallback.
    """
    SERVICE_NAME = "ui-controller-mcp"
    
    def __init__(self):
        self._key_file = Path.home() / ".ui_controller_mcp_key"
        self._data_file = Path.home() / ".ui_controller_mcp_data"
        self._ensure_key()

    def _ensure_key(self):
        """Ensure encryption key exists for fallback storage."""
        if not self._key_file.exists():
            key = Fernet.generate_key()
            self._key_file.write_bytes(key)
            self._key_file.chmod(0o600)  # Read/write only for user

    def _get_cipher(self) -> Fernet:
        key = self._key_file.read_bytes()
        return Fernet(key)

    def set_credential(self, username: str, password: str) -> bool:
        """Store a credential securely."""
        try:
            # Try system keyring first
            keyring.set_password(self.SERVICE_NAME, username, password)
            return True
        except Exception:
            # Fallback to encrypted file
            return self._save_encrypted(username, password)

    def get_credential(self, username: str) -> Optional[str]:
        """Retrieve a credential."""
        try:
            # Try system keyring first
            password = keyring.get_password(self.SERVICE_NAME, username)
            if password:
                return password
        except Exception:
            pass
            
        # Fallback to encrypted file
        return self._load_encrypted(username)

    def _save_encrypted(self, username: str, password: str) -> bool:
        try:
            data = {}
            if self._data_file.exists():
                try:
                    encrypted_data = self._data_file.read_bytes()
                    decrypted_json = self._get_cipher().decrypt(encrypted_data).decode()
                    data = json.loads(decrypted_json)
                except Exception:
                    pass # Overwrite if corrupted

            data[username] = password
            
            encrypted_data = self._get_cipher().encrypt(json.dumps(data).encode())
            self._data_file.write_bytes(encrypted_data)
            self._data_file.chmod(0o600)
            return True
        except Exception as e:
            print(f"Error saving encrypted credential: {e}")
            return False

    def _load_encrypted(self, username: str) -> Optional[str]:
        if not self._data_file.exists():
            return None
            
        try:
            encrypted_data = self._data_file.read_bytes()
            decrypted_json = self._get_cipher().decrypt(encrypted_data).decode()
            data = json.loads(decrypted_json)
            return data.get(username)
        except Exception as e:
            print(f"Error loading encrypted credential: {e}")
            return None
