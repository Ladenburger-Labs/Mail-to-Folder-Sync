#!/usr/bin/env python3
"""Script 1 — save attachments from incoming mail.

Watches an IMAP folder on PrivateEmail. For each unprocessed message it
saves the allowed attachments to disk, then MOVES the message into the
processed folder so it is never handled twice.

Run modes:
    python script1_save_attachments.py          # event-driven (IMAP IDLE)
    python script1_save_attachments.py --once    # process current backlog, exit

Dependency: imap-tools  (pip install imap-tools)
"""
import argparse
import os
import sys

from imap_tools import MailBox, AND

from common import load_config, default_provider


def _safe_name(folder: str, name: str) -> str:
    """Avoid collisions and path traversal in attachment filenames."""
    base = os.path.basename(name or "unnamed")
    target = os.path.join(folder, base)
    stem, ext = os.path.splitext(base)
    i = 1
    while os.path.exists(target):
        target = os.path.join(folder, f"{stem}_{i}{ext}")
        i += 1
    return target


def process_message(msg, cfg) -> int:
    """Save allowed attachments from one message. Returns count saved."""
    allowed = [e.lower() for e in cfg["script1"].get("allowed_extensions") or []]
    save_dir = cfg["script1"]["save_dir"]
    os.makedirs(save_dir, exist_ok=True)

    saved = 0
    for att in msg.attachments:
        ext = os.path.splitext(att.filename or "")[1].lstrip(".").lower()
        if allowed and ext not in allowed:
            continue
        path = _safe_name(save_dir, att.filename)
        with open(path, "wb") as fh:
            fh.write(att.payload)
        print(f"  saved: {path}")
        saved += 1
    return saved


def handle_backlog(mailbox, cfg) -> None:
    """Process every message currently in the watch folder."""
    processed = cfg["script1"]["processed_folder"]
    # Fetch all; we decide what to do per message, then move it out.
    for msg in mailbox.fetch(AND(all=True), mark_seen=False):
        print(f"message: {msg.subject!r} from {msg.from_}")
        process_message(msg, cfg)
        mailbox.move(msg.uid, processed)
        print(f"  moved to {processed}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true",
                        help="process current backlog and exit")
    args = parser.parse_args()

    cfg = load_config()
    host = cfg["imap"]["host"]
    user = cfg["imap"]["user"]
    pwd = default_provider().get_password(user)
    watch = cfg["script1"]["watch_folder"]

    with MailBox(host).login(user, pwd, initial_folder=watch) as mailbox:
        # Always clear whatever is already sitting in the folder first.
        handle_backlog(mailbox, cfg)

        if args.once:
            return

        print(f"Idling on '{watch}' — waiting for new mail (Ctrl-C to stop)…")
        while True:
            # IDLE blocks until the server reports activity (or 5-min timeout).
            responses = mailbox.idle.wait(timeout=300)
            if responses:
                print("new activity detected")
                handle_backlog(mailbox, cfg)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
