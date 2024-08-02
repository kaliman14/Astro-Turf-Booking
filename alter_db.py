import sqlite3

def alter_bookings_table():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Add new fields to the bookings table
    try:
        cursor.execute('ALTER TABLE bookings ADD COLUMN user_id TEXT')
        cursor.execute('ALTER TABLE bookings ADD COLUMN turf_id TEXT')
        cursor.execute('ALTER TABLE bookings ADD COLUMN start_time TEXT')
        cursor.execute('ALTER TABLE bookings ADD COLUMN end_time TEXT')
    except sqlite3.OperationalError as e:
        print(f"Error: {e}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    alter_bookings_table()
