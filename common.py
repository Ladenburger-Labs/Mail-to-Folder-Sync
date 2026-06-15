"""Shared helpers: config loading and a cross-platform credential provider.

Credentials never live in config or in the process environment. They are
read from the OS-native secret store via the `keyring` library:
  - macOS  -> Keychain
  - Windows -> Credential Locker
  - Linux  -> Secret Service (if you ever run there)

The CredentialProvider abstraction keeps the storage mechanism behind an
interface, so the scripts depend on the interface, not on any OS.
"""
import os
from abc import ABC, abstractmethod

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
KEYRING_SERVICE = "mailflow-privateemail"


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class CredentialProvider(ABC):
    """Interface for retrieving a password for a given account."""

    @abstractmethod
    def get_password(self, account: str) -> str:
        ...


class KeyringCredentialProvider(CredentialProvider):
    """Backed by the OS-native secret store (keyring lib)."""

    def __init__(self, service: str = KEYRING_SERVICE):
        self._service = service

    def get_password(self, account: str) -> str:
        import keyring
        pwd = keyring.get_password(self._service, account)
        if not pwd:
            raise SystemExit(
                f"No stored credential for '{account}'. "
                f"Run: python setup_credentials.py"
            )
        return pwd


class EnvCredentialProvider(CredentialProvider):
    """Backed by an environment variable. Useful for containers/CI."""

    def __init__(self, var: str = "MAILFLOW_PASSWORD"):
        self._var = var

    def get_password(self, account: str) -> str:
        pwd = os.environ.get(self._var)
        if not pwd:
            raise SystemExit(f"Environment variable {self._var} is not set.")
        return pwd


def default_provider() -> CredentialProvider:
    """Pick a provider. Env var wins if present (containers), else keyring."""
    if os.environ.get("MAILFLOW_PASSWORD"):
        return EnvCredentialProvider()
    return KeyringCredentialProvider()
