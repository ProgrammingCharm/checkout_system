import sqlite3

def initialise_database():
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items(
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT,
                item_description TEXT
            )
            """
    )
    conn.commit()
    cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users(
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT,
                user_contact TEXT, 
                user_ipaddress TEXT,
                user_macaddress TEXT
            )
            """
    )
    conn.commit()
    conn.close()
    
