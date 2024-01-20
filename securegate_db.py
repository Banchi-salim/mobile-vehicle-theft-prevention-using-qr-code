import sqlite3

def setup_database():
    conn = sqlite3.connect("securegate.db")
    cursor = conn.cursor()

    # Create vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            plate_number TEXT NOT NULL UNIQUE
        )
    """)

    # Create personnel table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personnel (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            user_id TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            security_status BOOLEAN NOT NULL
        )
    """)

    # Create stolen_vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stolen_vehicles (
            id INTEGER PRIMARY KEY,
            vehicle_make TEXT NOT NULL,
            vehicle_model TEXT NOT NULL,
            plate_number TEXT NOT NULL UNIQUE,
            reported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create notifications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()