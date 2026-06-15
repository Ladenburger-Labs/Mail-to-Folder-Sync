#!/usr/bin/env bash
# Store the PrivateEmail password in the macOS login keychain once.
# Re-run to update it. The Python scripts read it via `security`.
set -euo pipefail

SERVICE="M2FS-privateemail"

read -rp "PrivateEmail address (e.g. you@yourdomain.com): " ACCOUNT
read -rsp "Password (app password recommended): " PASSWORD
echo

security add-generic-password \
  -s "$SERVICE" \
  -a "$ACCOUNT" \
  -w "$PASSWORD" \
  -U   # update if it already exists

echo "Stored credentials for $ACCOUNT under service '$SERVICE'."
