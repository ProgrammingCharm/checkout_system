import csv
from flask import Flask, render_template, request, send_file
from os import path
from ddl import initialise_database
from dml import get_all_items, add_item, add_user, get_ipaddress, count_characters, check_upper, check_lower, check_number, check_special, validate_email, get_password_by_username

if not path.exists("checkout_system.db"):
    initialise_database()

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    errors = []
    db_password = get_password_by_username(username)
    if db_password and db_password[0] == password:
        return render_template("account.html", username=username, password=password)
    else:
        errors.append("Invalid username or password.")
        return render_template("index.html", errors=errors)

@app.route("/view_account_page", methods=["GET"])
def view_account_page():
    return render_template("account.html")

# When user is new to web application, can create an account. Stores username, password, email (contact), ipaddress. 
@app.route("/create_account", methods=["POST"])
def create_account():
    username = request.form["username"]
    password = request.form["password"]
    email = request.form["email"]
    ipaddress = get_ipaddress() 
    username_length = count_characters(username) 
    password_length = count_characters(password)
    
    has_upper= check_upper(password)
    has_lower = check_lower(password)
    has_number = check_number(password)
    has_special = check_special(password)
    
    has_valid_email = validate_email(email)

    # Create errors list to be passed to render_template for on-page viewing.
    errors = []

    if (username_length < 8 or username_length > 15) and (password_length < 8 or password_length > 15):
        errors.append("Username and password must be between 8 and 15 characters.")
    if username_length < 8 or username_length > 15:
        errors.append("Username must be between 8 and 15 characters.")
    if password_length < 8 or password_length > 15:
        errors.append("Password must be between 8 and 15 characters.")
    if not has_upper or not has_lower or not has_number or not has_special:
        errors.append("Password must contain at least one uppercase letter, one lowercase letter, one number, and one special character from #, $, %, &, ?, @.")
    if not has_valid_email:
        errors.append("Email must be valid coming from one of the common email providers such as gmail.com, icloud.com, outlook.com, hotmail.com, aol.com, yahoo.com, or mail.com.")
    
    if errors:
        return render_template("create_account.html", errors=errors)

    add_user(username, password, email, ipaddress)
    return index()

@app.route("/view_create_account_page", methods=["GET"])
def view_create_account_page():
    return render_template("create_account.html")

@app.route("/view_items_page", methods=["GET"])
def view_items_page():
    return render_template('catalog.html', items=get_all_items())

@app.route("/view_register_items_page", methods=["GET"])
def view_register_items_page():
    return render_template('register.html')

@app.route("/add_item_manually", methods=["GET", "POST"])
def add_item_manually():
    item_name = request.form['item_name']
    item_description = request.form['item_description']
    add_item(item_name, item_description, item_availability="Available")
    return render_template('register.html')

# For downloading csv file when user accesses URL /download_template, server listens for GET HTTP requests. 
@app.route("/download_template", methods=["GET"])
def download_template():
    csv_file = "items.csv"
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['item_name', 'item_description'])
    return send_file(csv_file)

#For uploading populated csv, should start at index 1 skipping first row. 
@app.route("/upload_csv", methods=["POST"])
def upload_csv():
        if "file" not in request.files:
            return "No file part in form.", 400
        file = request.files["file"]
        if file.filename == '':
            return "No selected file.", 400
        if file and file.filename.endswith(".csv"):
            file_data = file.stream.read().decode().splitlines()
            rows = csv.reader(file_data)
            # Effectively skipping the first row which is a header for the table
            next(rows)
            for row in rows:
                if len(row) < 2:
                    continue
                item_name = row[0]
                item_description = row[1]
                add_item(item_name, item_description, item_availability="Available")
            return view_items_page()    
            #return "Items added successfully.", 200
        #return "Invalid file format.", 400
        return view_register_item_page()
        
if __name__ == '__main__':
    app.run(debug=True)



