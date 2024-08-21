import sqlite3

def get_all_available_items():
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    available_items = cursor.fetchall()
    conn.close()
    return available_items

def add_item(item_name, item_description):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO items (item_name, item_description) VALUES (?, ?)
            """,
            (item_name, item_description)
    )
    conn.commit()
    conn.close()

