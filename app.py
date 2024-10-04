import csv
from flask import Flask, render_template, request, send_file, session, redirect, url_for
from os import path
import os
from ddl import initialise_database
from dml import get_all_items, add_item, add_user, get_ipaddress, count_characters, check_upper, check_lower, check_number, check_special, validate_email, get_password_by_username, get_user_id_by_username, add_checkout, get_all_checked_out_items, update_item_availability, get_item_name_by_item_id, get_timestamp, check_in_item, get_items_by_category
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import time

if not path.exists("checkout_system.db"):
    initialise_database()

app = Flask(__name__, template_folder="templates")
app.secret_key = os.environ.get("SECRET_KEY", "default_fallback_key")

@app.route("/", methods=['GET'])
def index():
    errors = {"err": None}
    return render_template('index.html', errors=errors)

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    errors = {"err": None}
    db_password = get_password_by_username(username)
    user_id = get_user_id_by_username(username)[0]
    checked_out_items = get_all_checked_out_items(user_id)
    if db_password and check_password_hash(db_password[0], password):
        session["username"] = username  # Set session variable
        return render_template("account.html", username=username, checked_out_items=checked_out_items) 
    else:
        errors["err"] = "Invalid username or password."
        return render_template("index.html", errors=errors)

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session.clear()  # Clear the session data, meaning this removes what is stored as "username" in the session object
    return redirect(url_for("index"))

@app.route("/view_account_page", methods=["GET"])
def view_account_page():
    user_id = get_user_id_by_username(session["username"])[0]
    checked_out_items = get_all_checked_out_items(user_id)
    if "username" in session:
        username = session["username"]
        return render_template("account.html", username=username, checked_out_items=checked_out_items)
    else:
        return redirect(url_for("index")) 

# When user is new to web application, can create an account. Stores username, password, email (contact), ipaddress. 
@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    ipaddress = get_ipaddress()  
    password_length = count_characters(password)
    
    has_upper= check_upper(password)
    has_lower = check_lower(password)
    has_number = check_number(password)
    has_special = check_special(password)
    
    has_valid_email = validate_email(email)

    # Create errors dictionary to contain a value for a specific error, "key": value pairs. 
    errors = {"password": None, "email": None}

    if password_length < 8 or password_length > 15 or not has_upper or not has_lower or not has_number or not has_special:
        errors["password"] = "Password must be between 8 and 15 characters, one upper case letter, one lower case letter, one number, and one special character from #, $, %, &, ?, @."
    
    if not has_valid_email:
        errors["email"] = "Invalid email address."

    print(errors)
    if all(value is None for value in errors.values()):
        add_user(username, password, email, ipaddress)
        return index()
    else:
        return render_template("create_account.html", errors=errors)

@app.route("/view_create_account_page", methods=["GET"])
def view_create_account_page():
    return render_template("create_account.html", errors=None)

@app.route("/view_items_page", methods=["GET"])
def view_items_page():
    success_note = {
            "checkout": None
    }
    selected_category = request.args.get('category', 'All Items')
    items = get_items_by_category(selected_category)
    if "checkout_success" in session:
        success_note["checkout"] = session.pop("checkout_success")
    if "username" in session:
        username = session["username"]
        return render_template("catalog.html", items=items, username=username, selected_category=selected_category, success_note=success_note)
    else:
        return index()

@app.route("/view_register_items_page", methods=["GET"])
def view_register_items_page():
    if "username" in session:
        username = session["username"]
        errors = {"manual_item_error": None, "csv_error": None}
        success_note = {"add": None}
        return render_template('register.html', errors=errors, success_note=success_note)
    else:
        return redirect(url_for("index"))

@app.route("/add_item_manually", methods=["GET", "POST"])
def add_item_manually():
    errors = {
            "manual_item_error": None,
            "csv_error": None
    }
    success_note = {
            "add": None
    }
    item_name = request.form['item_name']
    item_description = request.form['item_description']
    item_category = request.form['item_category']
    if not item_name or not item_description or not item_category:
        errors["manual_item_error"] = "Item name, item description, and item category required."
        return render_template('register.html', errors=errors, success_note=success_note)
    success_note["add"] = "Item added successfully."
    add_item(item_name, item_description, item_availability="Available", item_category=item_category)
    return render_template('register.html', errors=errors, success_note=success_note)

# For downloading csv file when user accesses URL /download_template, server listens for GET HTTP requests. 
@app.route("/download_template", methods=["GET"])
def download_template():
    csv_file = "items.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['item_name', 'item_description', 'item_category'])
    return send_file(csv_file)

#For uploading populated csv, should start at index 1 skipping first row. 
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
        errors = {
                "manual_item_error": None,
                "csv_error": None
                }
        if "file" not in request.files:
            errors["csv_error"] = "No file part."
            return render_template("register.html", errors=errors)
        file = request.files["file"]
        if file.filename == '':
            errors["csv_error"] = "No selected file."
            return render_template("register.html", errors=errors)
        if file and file.filename.endswith(".csv"):
            file_data = file.stream.read().decode().splitlines()
            rows = csv.reader(file_data)
            # Effectively skipping the first row which is a header for the table
            next(rows)
            for row in rows:
                if len(row) < 3:
                    continue
                item_name = row[0]
                item_description = row[1]
                item_category = row[2]
                add_item(item_name, item_description, item_availability="Available", item_category=item_category)
            return view_items_page()    
        return view_register_item_page()

@app.route("/checkout_item", methods=["POST"])
def checkout_item():
    selected_category = request.args.get('category', 'All Items')
    items = get_items_by_category(selected_category)
    if "username" not in session:
        return index()
    username = session["username"]
    user_id = get_user_id_by_username(session["username"])[0]
    item_id = int(request.form["item_id"])
    item_name_tuple = get_item_name_by_item_id(item_id)
    item_name = item_name_tuple[0]
    checkout_date = get_timestamp()
    return_date = datetime.now() + timedelta(days=7)
    return_date = return_date.replace(hour=0, minute=0, microsecond=0) # Set to midnight
    return_date_str = return_date.strftime('%Y-%m-%d %H:%M:%S')
    update_item_availability(item_id, return_date_str)
    add_checkout(user_id, item_id, item_name, checkout_date, return_date_str)
    session["checkout_success"] = "Item checked out successfully."
    return redirect(url_for("view_items_page", category=selected_category))

@app.route("/checkin_item", methods=["POST"])
def checkin_item():
    if "username" not in session:
        return index()
    user_id = get_user_id_by_username(session["username"])[0]
    item_ids = request.form.getlist("item_ids")
    if item_ids:
        for item_id in item_ids:
            check_in_item(user_id, item_id)
    return view_account_page()


if __name__ == '__main__':
    app.run(debug=True)
