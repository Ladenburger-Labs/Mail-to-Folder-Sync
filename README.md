# Mail-to-Folder-Sync

A collection of small, cross-platform scripts to automate email <-> filesystem sync.

## What each script does

- Script 1 — `script1_save_attachments.py`: watches an IMAP folder, saves
  attachments from new mail to disk, then moves the message to a `done`
  subfolder so it is never processed twice. Event-driven via IMAP IDLE.
- Script 2 — `script2_prepare_draft.py`: takes a file from a configured source
  folder, builds an email (recipient/subject depend on which folder key you
  pass), and saves it as a Drafts message for you to review and send.

## Portability design

- All application logic is pure Python and OS-independent.
- The only OS-specific concerns are isolated behind boundaries:
  - Credentials go through a `CredentialProvider` interface in `common.py`.
    The default uses the `keyring` library, which selects the native store
    automatically (macOS Keychain, Windows Credential Locker).
  - "Keep running at login" is a per-OS supervisor, shipped as config rather
    than code: `com.you.mailflow.plist` (macOS launchd) and
    `RUNNING_ON_WINDOWS.md` (Windows Task Scheduler).
- A second provider (`EnvCredentialProvider`) reads `MAILFLOW_PASSWORD`, so the
  same code drops into a container later with no changes.

## Setup (macOS and Windows alike)

- Install Python 3.10+ and create a venv:
  - macOS:   `python3 -m venv .venv && source .venv/bin/activate`
  - Windows: `py -m venv .venv && .venv\Scripts\activate`
- Install dependencies:
  - `pip install -r requirements.txt`
- Store your password in the native secret store (run once):
  - `python setup_credentials.py`
- Edit `config.yaml`:
  - set `imap.user` / `smtp.user` to your address
  - set folder names and absolute paths (use paths native to your OS)

A note on credentials: PrivateEmail supports app-specific passwords in its
webmail settings. Prefer one of those over your main account password.

## Usage (same on both OSes)

- Script 1, process backlog once and exit:
  - `python script1_save_attachments.py --once`
- Script 1, run continuously (event-driven):
  - `python script1_save_attachments.py`
- Script 2, newest file in the `invoices` folder key:
  - `python script2_prepare_draft.py invoices`
- Script 2, a specific file:
  - `python script2_prepare_draft.py reports march.pdf`

## Event-driven at login (Script 1)

- macOS — edit the paths in `com.you.mailflow.plist`, then:
  - `cp com.you.mailflow.plist ~/Library/LaunchAgents/`
  - `launchctl load ~/Library/LaunchAgents/com.you.mailflow.plist`
- Windows — see `RUNNING_ON_WINDOWS.md` (Task Scheduler).

## Design notes

- IMAP-first, not Thunderbird-file-first: avoids Mbox locking/corruption and
  gives true push (IDLE) instead of polling.
- Idempotency by moving handled mail to a `done` folder — visible, robust across
  reconnects and reruns, no hidden state file to corrupt.
- Drafts via IMAP `APPEND` — you always review before anything sends. No
  automated sending path exists in this code by design.
- Boundaries kept separate so OS-specific bits and the IMAP layer can be swapped
  or mocked without touching the scripts.

## Possible next steps

- Per-folder save rules / subfolder routing in Script 1.
- Multiple watch folders (one supervisor entry per folder).
- A sidecar `.yaml` next to a file in Script 2 to override recipient/subject
  per-file instead of per-folder.
- Containerize using `EnvCredentialProvider` if this moves to a server.
