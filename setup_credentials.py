#!/usr/bin/env python3
"""Store the PrivateEmail password in the OS-native secret store.

Runs the same on macOS (Keychain) and Windows (Credential Locker) — the
keyring library picks the right backend automatically. Run once; re-run
to update. Nothing is written to disk in plaintext.

    python setup_credentials.py
"""
import getpass

import keyring

from common import KEYRING_SERVICE


def main():
    account = input("PrivateEmail address (e.g. you@yourdomain.com): ").strip()
    password = getpass.getpass("Password (app password recommended): ")
    keyring.set_password(KEYRING_SERVICE, account, password)
    print(f"Stored credentials for {account} "
          f"under service '{KEYRING_SERVICE}' using backend: "
          f"{keyring.get_keyring().__class__.__name__}")


if __name__ == "__main__":
    main()
