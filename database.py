import sqlite3
from config import DB_NAME

def connect_db():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        phone TEXT,
        caregiver_email TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_name TEXT NOT NULL,
        dose TEXT NOT NULL,
        time TEXT NOT NULL,
        instruction TEXT,
        start_date TEXT,
        end_date TEXT,
        frequency TEXT DEFAULT 'Daily',
        stock INTEGER DEFAULT 0,
        notes TEXT,
        active INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        medicine_id INTEGER,
        medicine_name TEXT,
        dose TEXT,
        time TEXT,
        status TEXT,
        date TEXT,
        action_time TEXT,
        remarks TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(medicine_id) REFERENCES medicines(id)
    )
    """)

    migrate_columns(cur)
    conn.commit()
    conn.close()

def migrate_columns(cur):
    required = {
        "users": {
            "phone": "TEXT",
            "caregiver_email": "TEXT",
            "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
        },
        "medicines": {
            "start_date": "TEXT",
            "end_date": "TEXT",
            "frequency": "TEXT DEFAULT 'Daily'",
            "stock": "INTEGER DEFAULT 0",
            "notes": "TEXT",
            "active": "INTEGER DEFAULT 1",
            "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
        },
        "history": {
            "medicine_id": "INTEGER",
            "action_time": "TEXT",
            "remarks": "TEXT"
        }
    }

    for table, columns in required.items():
        cur.execute(f"PRAGMA table_info({table})")
        existing = {row[1] for row in cur.fetchall()}
        for column, datatype in columns.items():
            if column not in existing:
                cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {datatype}")

def get_user_email(user_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT caregiver_email FROM users WHERE id=?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row and row[0] else None
