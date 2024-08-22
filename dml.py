import sqlite3

def get_all_items():
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()
    return items

def add_item(item_name, item_description, item_availability):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO items (item_name, item_description, item_availability) VALUES (?, ?, ?)
            """,
            (item_name, item_description, item_availability)
    )
    conn.commit()
    conn.close()

