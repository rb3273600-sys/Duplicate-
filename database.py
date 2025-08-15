import sqlite3
import hashlib
import datetime

DB_NAME = "app_data.db"

def get_db_connection():
    """Creates a database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """Hashes the password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initializes the database and creates tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER NOT NULL DEFAULT 0,
        profile_image_path TEXT
    )
    """)

    # Create activity_log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TEXT NOT NULL,
        action TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE SET NULL
    )
    """)

    conn.commit()
    conn.close()

def add_user(username, password, is_admin=False):
    """Adds a new user to the database. Returns True on success, False on failure."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            (username, hash_password(password), 1 if is_admin else 0)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Username already exists
        conn.close()
        return False
    conn.close()
    return True

def get_user(username):
    """Retrieves a user by their username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_all_users():
    """Retrieves all users from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_admin FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def get_user_by_id(user_id):
    """Retrieves a user by their ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, is_admin FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_user(user_id, username, password=None, is_admin=None):
    """Updates a user's details in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    if password:
        cursor.execute(
            "UPDATE users SET username = ?, password_hash = ?, is_admin = ? WHERE id = ?",
            (username, hash_password(password), is_admin, user_id)
        )
    else:
        cursor.execute(
            "UPDATE users SET username = ?, is_admin = ? WHERE id = ?",
            (username, is_admin, user_id)
        )
    conn.commit()
    conn.close()

def delete_user(user_id):
    """Deletes a user from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

def update_profile_picture_path(user_id, path):
    """Updates the profile picture path for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile_image_path = ? WHERE id = ?", (path, user_id))
    conn.commit()
    conn.close()

def create_initial_admin():
    """Creates the initial admin user if they don't exist."""
    if not get_user("Rampratap"):
        add_user("Rampratap", "Ram@2001!!", is_admin=True)

def get_all_logs():
    """Retrieves all activity logs, joining with usernames."""
    conn = get_db_connection()
    cursor = conn.cursor()
    # LEFT JOIN to include logs from deleted users (whose username will be NULL)
    cursor.execute("""
        SELECT
            al.id,
            al.timestamp,
            u.username,
            al.action
        FROM activity_log al
        LEFT JOIN users u ON al.user_id = u.id
        ORDER BY al.timestamp DESC
    """)
    logs = cursor.fetchall()
    conn.close()
    return logs

def log_activity(user_id, action):
    """Logs a user's activity."""
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO activity_log (user_id, timestamp, action) VALUES (?, ?, ?)",
        (user_id, timestamp, action)
    )
    conn.commit()
    conn.close()
