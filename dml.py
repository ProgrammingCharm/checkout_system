import sqlite3
import time
from flask import request
from werkzeug.security import generate_password_hash

def get_all_items():
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items") # Changed to all items in general
    items = cursor.fetchall()
    conn.close()
    return items

def add_item(item_name, item_description, item_availability, item_category):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO items (item_name, item_description, item_availability, item_category) VALUES (?, ?, ?, ?)
            """,
            (item_name, item_description, item_availability, item_category)
    )
    conn.commit()
    conn.close()

def add_user(username, password, email, ipaddress):
    hashed_password = generate_password_hash(password)  # Using PBKDF2 with SHA256 for generating hash. 
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO users (user_name, user_password, user_contact, user_ipaddress) VALUES (?, ?, ?, ?)
            """, 
            (username, hashed_password, email, ipaddress)
    )
    conn.commit()
    conn.close()

def count_characters(s):
    # Checks usernames, passwords to ensure they are within range of length. 
    count = 0
    for char in s:
        count += 1
    return count

def get_ipaddress():
    # Accesses ip address from the request header being sent to server, stored in request object of flask
    return request.remote_addr

def check_upper(s):
    # Checks ASCII value betwee 65 and 90 to ensure password has an upper case letter.
    has_upper = False
    for char in s:
        if ord(char) >= 65 and ord(char) <= 90:
            has_upper = True
            break
    return has_upper

def check_lower(s):
    # Checks ASCII value betwee 97 and 122 to ensure password has at least one lower case.
    has_lower = False
    for char in s:
        if ord(char) >= 97 and ord(char) <= 122:
            has_lower =  True
            break
    return has_lower

def check_number(s):
    # Checks ASCII value using ord() built-in to ensure there is a number, or 48 to 57 digit.
    has_number = False
    for char in s:
        if ord(char) >= 48 and ord(char) <= 57:
            has_number = True
            break
    return has_number

def check_special(s):
    # Checks ASCII value for each character in password to see if #, $, %, &, ?, @ is included. 
    has_special = False
    for char in s:
        if (ord(char) >= 35 and ord(char) <= 38) or (ord(char) == 63, 64):
            has_special = True
            break
    return has_special

def validate_email(s):
    # Simplified email check for a signle character. If the email string contains "@", it is a valid email address. 
    for char in s:
        if char == "@":
            return True
    return False
    # Validates email by ensuring it belongs to one of the main email providers and includes and '@' symbol."
    #email_providers = {"gmail.com", "icloud.com", "outlook.com", "hotmail.com", "aol.com", "yahoo.com", "mail.com"}
    #at_symbol_present = False
    #for char in s:
    #    if char == "@":
    #        at_symbol_present = True
    #if at_symbol_present == False:
    #    return False
    #local_part, _, domain_part = s.partition("@")
    #char_count_local = count_characters(local_part)
    #char_count_domain = count_characters(domain_part)
    #if char_count_local == 0 or char_count_domain == 0:
    #    return False
    #if domain_part in email_providers:  # Check to see if the email domain is in the set of providers.
    #    return True


def get_password_by_username(username):
    # Used in validating password and username during login see /login in app.py
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT user_password FROM users
            WHERE user_name = ?
            """,
            (username,)
    )
    password = cursor.fetchone()
    conn.close()
    return password

def get_user_id_by_username(username):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT user_id FROM users WHERE user_name = ?
            """,
            (username,)
    )
    username_id = cursor.fetchone()
    conn.commit()
    conn.close()
    return username_id

def get_item_name_by_item_id(item_id):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT item_name FROM items WHERE item_id = ?
            """,
            (item_id,)
    )
    item_name = cursor.fetchone()
    conn.commit()
    conn.close()
    return item_name

def add_checkout(user_id, item_id, item_name, checkout_date, return_date):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            INSERT INTO checkouts (user_id, item_id, item_name, checkout_date, return_date) VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, item_id, item_name, checkout_date, return_date)
    )
    conn.commit()
    conn.close()

def get_all_checked_out_items(user_id):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            SELECT * FROM checkouts WHERE user_id = ?
            """,
            (user_id,)
    )
    checked_out_items = cursor.fetchall()
    conn.close()
    return checked_out_items

def update_item_availability(item_id):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            UPDATE items SET item_availability='Unavailable' WHERE item_id = ?
            """,
            (item_id,)
    )
    conn.commit()
    conn.close()

def get_timestamp():
    current_time = time.localtime()
    return time.strftime('%Y-%m-%d %H:%M:%S', current_time)

def check_in_item(user_id, item_id):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    cursor.execute(
            """
            DELETE FROM checkouts WHERE user_id = ? AND item_id = ?
            """,
            (user_id, item_id)
    )
    cursor.execute(
            """
            UPDATE items SET item_availability = "Available" WHERE item_id = ?
            """,
            (item_id,)
    )
    conn.commit()
    conn.close()

def get_items_by_category(category):
    conn = sqlite3.connect("checkout_system.db")
    cursor = conn.cursor()
    if category == "All Items":
        cursor.execute("SELECT * FROM items") # Retrieve all items, not specific
    else:
        cursor.execute("SELECT * FROM items WHERE item_category = ?", (category,))
    items = cursor.fetchall()
    conn.close()
    return items
