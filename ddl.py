import sqlite3

def initialise_database():
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items(
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                item_description TEXT,
                item_availability TEXT
            )
            """
    )
    conn.commit()
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_password TEXT,
                user_contact TEXT, 
                user_ipaddress TEXT
            )
            """
    )
    conn.commit()
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS checkouts(
                checkout_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                item_id INTEGER,
                item_name TEXT,
                checkout_date TEXT,
                return_date TEXT,
                FOREIGN KEY(user_id) REFERENCES users(user_id),
                FOREIGN KEY(item_id) REFERENCES items(item_id)
            )
            """
    )
    conn.commit()
    conn.close()
    
