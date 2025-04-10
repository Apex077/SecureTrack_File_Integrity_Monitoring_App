import sqlite3
from config import DB_PATH

def setup_database():
    """Ensure the database and 'files' table exist before use."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Ensure the "files" table exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            hash TEXT NOT NULL
        )
    """)
    
    conn.commit()
    conn.close()

def store_file_hash(file_path, file_hash):
    """Save or update a file hash in the database."""
    setup_database()  # Ensure DB is initialized
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO files (path, hash) VALUES (?, ?)", (file_path, file_hash))
    conn.commit()
    conn.close()

def get_stored_hash(file_path):
    """Retrieve the stored hash of a file."""
    setup_database()  # Ensure DB is initialized
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT hash FROM files WHERE path=?", (file_path,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

if __name__ == "__main__":
    setup_database()  # Ensure DB is initialized on script run
    print("✅ Database setup complete.")
