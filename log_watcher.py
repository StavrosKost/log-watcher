import os
import hashlib
import smtplib
from datetime import datetime
from email.message import EmailMessage
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

# === CONFIGURATION ===
LOG_SOURCES = {
    "syslog": "/var/log/syslog",
    "authlog": "/var/log/auth.log",
    "wazuh": "/var/ossec/logs/alerts/alerts.json"  # Adjust if different
}
BACKUP_ROOT = "/opt/log_backups"
MISSING_ROOT = os.path.join(BACKUP_ROOT, "missing")
EMAIL_TO = "you@example.com"
EMAIL_FROM= os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))

# === FUNCTIONS ===

def hash_line(line):
    return hashlib.sha256(line.encode()).hexdigest()

def send_email(subject, body, attachment_path):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = EMAIL_TO
    msg.set_content(body)

    with open(attachment_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='text', subtype='plain', filename=os.path.basename(attachment_path))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_FROM, EMAIL_PASSWORD)
        smtp.send_message(msg)

def backup_log(log_name, log_path):
    log_dir = os.path.join(BACKUP_ROOT, log_name)
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(log_dir, f"{log_name}_{timestamp}.log")

    try:
        with open(log_path, 'r') as src, open(backup_path, 'w') as dst:
            dst.writelines(src.readlines())
        return backup_path
    except Exception as e:
        print(f"Failed to back up {log_name}: {e}")
        return None

def detect_missing(log_name, new_backup_path):
    log_dir = os.path.join(BACKUP_ROOT, log_name)
    backups = sorted([f for f in os.listdir(log_dir) if f.startswith(log_name)])
    if len(backups) < 2:
        return []

    previous_backup = os.path.join(log_dir, backups[-2])
    
    with open(previous_backup, 'r') as f1, open(new_backup_path, 'r') as f2:
        old_hashes = set(hash_line(line) for line in f1)
        new_lines = f2.readlines()
        new_hashes = set(hash_line(line) for line in new_lines)

    missing_lines = [line for line in new_lines if hash_line(line) not in old_hashes]

    if missing_lines:
        os.makedirs(MISSING_ROOT, exist_ok=True)
        missing_path = os.path.join(MISSING_ROOT, f"missing_{log_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        with open(missing_path, 'w') as f:
            f.writelines(missing_lines)
        return missing_path
    return None

# === MAIN ===

def main():
    for name, path in LOG_SOURCES.items():
        new_backup = backup_log(name, path)
        if new_backup:
            missing_file = detect_missing(name, new_backup)
            if missing_file:
                subject = f"🚨 {name.upper()} - Missing Logs Detected!"
                body = f"Missing or altered log entries detected in '{name}'. Attached are the suspicious entries."
                send_email(subject, body, missing_file)

if __name__ == "__main__":
    main()
