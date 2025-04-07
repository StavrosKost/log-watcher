# 🛡️ Log Watcher – Hourly Log Backup & Tampering Detection

This script automates **hourly log backups** and performs **hash-based validation** to detect potential log tampering or deletion due to attacks. If anomalies are found, it immediately sends you an email alert with the suspicious logs attached.

---

## 🚀 Features

- ⏱️ Backs up logs every hour
- 📁 Organized backup folder structure
- 🧩 Detects missing or altered log entries
- 🔐 Validates log integrity using SHA-256 hashes
- 📧 Sends instant email alerts for suspicious activity

---

## 📂 Log Files Monitored

By default:
- `/var/log/syslog`
- `/var/log/auth.log`
- `/var/ossec/logs/alerts/alerts.json` (Wazuh alerts)

Feel free to customize this list in the script.

---

## 🧠 How It Works

1. Every hour, the script backs up selected log files to `/opt/log_backups/`.
2. It calculates a **SHA-256 hash** of each original log file.
3. On the next run, it compares current logs to previous hashes and backups.
4. If **log entries are missing** or **hashes mismatch**, it sends an alert email with the affected logs.

---

## ✉️ Email Configuration

Set your email and SMTP credentials inside the script:

```python
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

##🛠️ Cron Setup
To run the script every hour:

Edit
crontab -e
Add this line:

bash
Copy
Edit
0 * * * * /usr/bin/python3 /path/to/log_watcher.py
