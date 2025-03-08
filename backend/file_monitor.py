import sqlite3
import time
import hashlib
import os
import logging
from watchdog.observers import Observer  # ✅ Fix for Windows
from watchdog.events import FileSystemEventHandler
from database import store_file_hash, get_stored_hash
from config import DB_PATH, LOG_FILE

# ✅ Setup logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# ✅ Global variables to control monitoring
is_monitoring = False
observer = None
current_directory = None  # ✅ Track selected directory

def calculate_file_hash(file_path, retries=3, delay = 1.0):
    """Generate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    for attempt in range(retries):
        try:
            with open(file_path, "rb") as file:
                while chunk := file.read(4096):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except PermissionError:
            if attempt < retries - 1:
                logging.warning(f"Permission denied for {file_path}. Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                logging.error(f"Failed to read {file_path} after {retries} attempts due to permission issues.")
                return None

class FileMonitorHandler(FileSystemEventHandler):
    """Handles file events (created, modified, deleted, moved/renamed)."""

    def on_created(self, event):
        """Handles new file creation."""
        if event.is_directory:
            return
        file_path = event.src_path
        file_hash = calculate_file_hash(file_path)

        if file_hash:
            store_file_hash(file_path, file_hash)
            logging.info(f"ADDED: {file_path} has been created.")

    def on_modified(self, event):
        """Handles file modifications."""
        if event.is_directory:
            return
        file_path = event.src_path
        current_hash = calculate_file_hash(file_path)
        stored_hash = get_stored_hash(file_path)

        if stored_hash is None:
            # ✅ New file detected, store it
            store_file_hash(file_path, current_hash)
            logging.info(f"ADDED: {file_path} detected and stored.")
        elif stored_hash != current_hash:
            # ✅ Existing file modified
            logging.warning(f"MODIFIED: {file_path} has been changed!")
            store_file_hash(file_path, current_hash)

    def on_deleted(self, event):
        """Handles file deletions."""
        if event.is_directory:
            return
        file_path = event.src_path
        try:
            # Check if the file exists in the database before attempting deletion
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM files WHERE path=?", (file_path,))
            result = cursor.fetchone()

            if result:
                cursor.execute("DELETE FROM files WHERE path=?", (file_path,))
                conn.commit()
                logging.error(f"DELETED: {file_path} has been removed.")
            else:
                logging.warning(f"DELETED (not tracked): {file_path} was removed but not found in DB.")

        except sqlite3.Error as e:
            logging.error(f"Database error on deletion: {e}")
        finally:
            conn.close()

    def on_moved(self, event):
        """Handles file renaming or moving."""
        if event.is_directory:
            return
        old_path = event.src_path
        new_path = event.dest_path
        logging.info(f"RENAMED: {old_path} -> {new_path}")

        # Update database with new file path
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT hash FROM files WHERE path=?", (old_path,))
        result = cursor.fetchone()

        if result:
            file_hash = result[0]
            cursor.execute("DELETE FROM files WHERE path=?", (old_path,))
            cursor.execute("INSERT OR REPLACE INTO files (path, hash) VALUES (?, ?)", (new_path, file_hash))
            conn.commit()

        conn.close()

def start_monitoring(directory):
    """Start monitoring the selected directory."""
    global is_monitoring, observer, current_directory
    
    # ✅ Ensure the directory exists before monitoring
    if not os.path.exists(directory):
        logging.error(f"Directory not found: {directory}")
        return
    
    if is_monitoring:
        logging.info("Monitoring is already running.")
        return

    is_monitoring = True
    current_directory = directory  # ✅ Store selected directory
    event_handler = FileMonitorHandler()
    observer = Observer()  # ✅ Fix for Windows
    observer.schedule(event_handler, directory, recursive=True)
    observer.start()
    
    logging.info(f"Monitoring started on: {directory}")

    try:
        while is_monitoring:
            time.sleep(10)
    except KeyboardInterrupt:
        stop_monitoring()

def stop_monitoring():
    """Stop monitoring the directory."""
    global is_monitoring, observer, current_directory
    if not is_monitoring:
        logging.info("Monitoring is not running.")
        return

    is_monitoring = False
    current_directory = None
    if observer:
        observer.stop()
        observer.join()
        logging.info(f"Monitoring stopped for: {current_directory}")
