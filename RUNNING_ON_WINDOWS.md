# Running Script 1 continuously on Windows

The Python code is identical across OSes. Only the "keep it running at
login" mechanism differs. On Windows, use Task Scheduler.

## Create the scheduled task (GUI)

- Open Task Scheduler -> Create Task (not "Basic Task").
- General tab:
  - Name: mailflow
  - Select "Run only when user is logged on" (keyring's Credential Locker
    is per-user, so the task must run as you).
- Triggers tab -> New:
  - Begin the task: "At log on", your user.
- Actions tab -> New:
  - Action: Start a program
  - Program/script: full path to your venv python, e.g.
    `C:\Users\you\mailflow\.venv\Scripts\pythonw.exe`
    (use `pythonw.exe`, not `python.exe`, to avoid a console window)
  - Add arguments: `script1_save_attachments.py`
  - Start in: `C:\Users\you\mailflow`
- Settings tab:
  - Enable "If the task fails, restart every 1 minute" (mirrors launchd
    KeepAlive — recovers a dropped IDLE connection).
  - "If the running task does not end when requested, force it to stop."

## Create the same task (PowerShell)

```powershell
$py   = "C:\Users\you\mailflow\.venv\Scripts\pythonw.exe"
$dir  = "C:\Users\you\mailflow"
$act  = New-ScheduledTaskAction -Execute $py `
          -Argument "script1_save_attachments.py" -WorkingDirectory $dir
$trg  = New-ScheduledTaskTrigger -AtLogOn
$set  = New-ScheduledTaskSettingsSet -RestartCount 999 `
          -RestartInterval (New-TimeSpan -Minutes 1)
Register-ScheduledTask -TaskName "mailflow" -Action $act `
          -Trigger $trg -Settings $set -RunLevel Limited
```

## Manage

- Start now:   `Start-ScheduledTask -TaskName mailflow`
- Stop:        `Stop-ScheduledTask  -TaskName mailflow`
- Remove:      `Unregister-ScheduledTask -TaskName mailflow -Confirm:$false`

Logs: redirect output yourself if you want a file, e.g. wrap the call in a
`.bat` that appends to `mailflow.log`, since Task Scheduler does not capture
stdout the way the launchd plist does.
