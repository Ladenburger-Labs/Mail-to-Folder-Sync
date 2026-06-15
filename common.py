"""Shared helpers: load config, read credentials from macOS Keychain."""
import os
import subprocess
import sys

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")
KEYCHAIN_SERVICE = "mailflow-privateemail"


def load_config(path: str = CONFIG_PATH) -> dict:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get_password(account: str) -> str:
    """Read the password for `account` from the macOS login keychain.

    Stored once via setup_keychain.sh. We never keep the password in config
    or in the process environment.
    """
    try:
        result = subprocess.run(
            ["security", "find-generic-password",
             "-s", KEYCHAIN_SERVICE, "-a", account, "-w"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        sys.exit(
            f"No keychain entry for '{account}'. "
            f"Run ./setup_keychain.sh first."
        )
