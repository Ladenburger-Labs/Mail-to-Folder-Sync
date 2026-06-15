# mailflow

A collection of small scripts to automate email ↔ filesystem interactions. 

## Basic Idea
Connect to mail server directly (IMAP/SMTP), instead of going through local mail clients (e.g. Outlook, Mail, Thunderbird, etc).

## What each script does

- Script 1 — `script1_save_attachments.py`: watches an IMAP folder, saves
  attachments from new mail to disk, then moves the message to a `done`
  subfolder so it is never processed twice. Event-driven via IMAP IDLE.
- Script 2 — `script2_prepare_draft.py`: takes a file from a configured source
  folder, builds an email (recipient/subject depend on which folder key you
  pass), and saves it as a Drafts message for you to review and send.

## Setup

- Install Python 3.10+ and create a venv:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install imap-tools pyyaml`
- Store your password in the Keychain (run once):
  - `chmod +x setup_keychain.sh && ./setup_keychain.sh`
- Edit `config.yaml`:
  - set `imap.user` / `smtp.user` to your address
  - set the folder names and absolute paths (use real `/Users/you/...` paths)

A note on credentials: PrivateEmail supports app-specific passwords in its
webmail settings. Prefer one of those over your main account password.

## Usage

- Script 1, process backlog once and exit:
  - `python script1_save_attachments.py --once`
- Script 1, run continuously (event-driven):
  - `python script1_save_attachments.py`
- Script 2, newest file in the `invoices` folder key:
  - `python script2_prepare_draft.py invoices`
- Script 2, a specific file:
  - `python script2_prepare_draft.py reports march.pdf`

## Event-driven at login (Script 1)

- Edit the paths in `com.you.mailflow.plist`
- `cp com.you.mailflow.plist ~/Library/LaunchAgents/`
- `launchctl load ~/Library/LaunchAgents/com.you.mailflow.plist`

## Design notes

- IMAP-first, not Thunderbird-file-first: avoids Mbox locking/corruption and
  gives true push (IDLE) instead of polling.
- Idempotency by moving handled mail to a `done` folder — visible, robust across
  reconnects and reruns, no hidden state file to corrupt.
- Drafts via IMAP `APPEND` — you always review before anything sends. No
  automated sending path exists in this code by design.
- Boundaries kept separate (`common.py` for config/creds, IMAP access isolated
  inside each script) so the IMAP layer can be swapped or mocked later.

## Possible next steps

- Per-folder save rules / subfolder routing in Script 1.
- Multiple watch folders (one IDLE connection each, or one agent per folder).
- A sidecar `.yaml` next to a file in Script 2 to override recipient/subject
  per-file instead of per-folder.
