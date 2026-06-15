#!/usr/bin/env python3
"""Script 2 — prepare an email draft from a file.

Picks a file from a configured source folder, attaches it to a new
message addressed per that folder's config, and APPENDs it to the IMAP
Drafts folder. The draft appears in Thunderbird on next sync for you to
review and send manually. Nothing is ever sent automatically.

Usage:
    python script2_prepare_draft.py <folder_key>            # newest file in folder
    python script2_prepare_draft.py <folder_key> <filename> # a specific file

Dependency: imap-tools  (pip install imap-tools)
"""
import argparse
import mimetypes
import os
import sys
from email.message import EmailMessage
from email.utils import formatdate

from imap_tools import MailBox

from common import load_config, get_password


def pick_file(source_dir: str, filename: str | None) -> str:
    if filename:
        path = os.path.join(source_dir, filename)
        if not os.path.isfile(path):
            sys.exit(f"File not found: {path}")
        return path
    files = [os.path.join(source_dir, f) for f in os.listdir(source_dir)]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        sys.exit(f"No files in {source_dir}")
    return max(files, key=os.path.getmtime)  # newest


def build_message(sender, recipient, subject, body, file_path) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg.set_content(body)

    ctype, _ = mimetypes.guess_type(file_path)
    maintype, subtype = (ctype or "application/octet-stream").split("/", 1)
    with open(file_path, "rb") as fh:
        msg.add_attachment(fh.read(), maintype=maintype, subtype=subtype,
                           filename=os.path.basename(file_path))
    return msg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("folder_key", help="key under script2.folders in config")
    parser.add_argument("filename", nargs="?", help="specific file (optional)")
    args = parser.parse_args()

    cfg = load_config()
    folders = cfg["script2"]["folders"]
    if args.folder_key not in folders:
        sys.exit(f"Unknown folder key '{args.folder_key}'. "
                 f"Known: {', '.join(folders)}")

    fc = folders[args.folder_key]
    file_path = pick_file(fc["source_dir"], args.filename)
    print(f"Using file: {file_path}")

    sender = cfg["imap"]["user"]
    msg = build_message(sender, fc["recipient"], fc["subject"],
                        fc.get("body", ""), file_path)

    host = cfg["imap"]["host"]
    pwd = get_password(sender)
    drafts = cfg["script2"]["drafts_folder"]

    with MailBox(host).login(sender, pwd) as mailbox:
        mailbox.append(msg.as_bytes(), drafts)

    print(f"Draft created in '{drafts}' → to: {fc['recipient']}, "
          f"subject: {fc['subject']!r}")
    print("Open Thunderbird to review and send.")


if __name__ == "__main__":
    main()
