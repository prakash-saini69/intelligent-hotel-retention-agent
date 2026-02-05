import sqlite3
import os
from datetime import datetime, timedelta
import random

# Configuration
DB_PATH = "data/hotel_retention.db"

def create_connection():
    """Create a database connection to the SQLite database."""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        print(f"✅ Connected to SQLite: {DB_PATH}")
        return conn
    except sqlite3.Error as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def create_table(conn):
    """Create the bookings table."""
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bookings (
        booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT,
        room_type TEXT NOT NULL,
        booking_price REAL NOT NULL,
        booking_date TEXT NOT NULL,
        checkin_date TEXT NOT NULL,
        checkout_date TEXT NOT NULL,
        special_requests TEXT,
        total_stays INTEGER DEFAULT 1,
        previous_cancellations INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Confirmed'
    );
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("✅ Table 'bookings' created.")
    except sqlite3.Error as e:
        print(f"❌ Error creating table: {e}")

def generate_mock_data(conn):
    """Insert mock data for testing."""
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT count(*) FROM bookings")
    if cursor.fetchone()[0] > 0:
        print("ℹ️  Data already exists. Skipping insertion.")
        return

    # 1. John Doe (High Risk Example)
    # Booked long ago, high price, history of cancellations
    john_checkin = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d")
    
    bookings = [
        # (id, name, email, phone, room, price, book_date, checkin, checkout, requests, stays, cancels, status)
        (101, "John Doe", "john.doe@example.com", "555-0101", "Deluxe Suite", 850.00, "2023-12-01", john_checkin, "2024-03-15", "Late check-in", 2, 3, "Confirmed"),
        
        # 2. Alice Smith (Low Risk - Loyal)
        (102, "Alice Smith", "alice.smith@test.com", "555-0102", "Standard", 120.00, "2024-01-15", "2024-04-10", "2024-04-12", "Quiet room", 15, 0, "Confirmed"),
        
        # 3. Bob Jones (Medium Risk - New customer)
        (103, "Bob Jones", "bob.j@test.com", "555-0103", "Standard", 200.00, "2024-02-20", "2024-03-05", "2024-03-08", None, 1, 0, "Confirmed"),
        
        # 4. Sarah Connor (Cancelled before)
        (104, "Sarah Connor", "sarah.c@test.com", "555-0104", "Presidential", 1500.00, "2023-11-01", "2024-06-01", "2024-06-05", "No machines", 5, 1, "Confirmed"),
    ]

    sql = '''INSERT INTO bookings(customer_id, name, email, phone, room_type, booking_price, booking_date, checkin_date, checkout_date, special_requests, total_stays, previous_cancellations, status)
             VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'''
    
    cursor.executemany(sql, bookings)
    conn.commit()
    print(f"✅ Inserted {len(bookings)} mock bookings.")

def main():
    conn = create_connection()
    if conn:
        create_table(conn)
        generate_mock_data(conn)
        conn.close()
        print("🚀 Database setup complete!")

if __name__ == '__main__':
    main()