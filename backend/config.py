import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ✅ Store log files inside 'logs' folder
LOG_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOG_DIR, "file_monitor.log")

# ✅ Store database inside 'db' folder
DB_DIR = os.path.join(BASE_DIR, "db")
DB_PATH = os.path.join(DB_DIR, "file_integrity.db")

# Ensure directories exist
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DB_DIR, exist_ok=True)

# Directory to monitor
MONITOR_DIR = ""