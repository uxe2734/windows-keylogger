# Keylogger for Windows

ℹ A keylogger written in Python, which runs when OS turns on, and send report to PHP host and takes customized commands from server.

⚠ Please note, this repo is for educational purposes only. No contributors, major or minor, are to fault for any actions done by this program.

## Usage
1️⃣ First install requirements.txt
```bash
pip install -r requirements.txt
```
2️⃣ You can make customize commands in `main.py` for `command.php` before turning `main.py` into `.exe` file. After your customization, turn main.py into main.exe using this command:
```bash
pyinstaller --onefile --noconsole main.py
```
3️⃣ You need a PHP host, and a domain to send POST requests to `echo.php`. This file takes report from `main.exe` file and saves it inside `messages.json`.

## What happens on Target OS?

🔸 When Target user , runs the `main.exe` , program automatically creates itself in Startup folder , so whenever Windows turns on , program runs! Every 30min program sends a report from
what buttons (including Mouse, ALT,CTRL,SHIFT and Capital and Small characters) + Clipboard content have pressed or written. and PHP host saves report with report time , and Target IP Address
inside `messages.json`. You can write "CHANGE" inside `command.php` so `main.exe` changes Target's wallpaper into `bg.jpg`.
