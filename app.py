import csv
from flask import Flask, render_template, request, send_file
from os import path
from ddl import initialise_database
from dml import get_all_items, add_item

if not path.exists("checkout_system.db"):
    initialise_database()

app = Flask(__name__, template_folder="templates")

@app.route("/", methods=['GET'])
def index():
    return render_template('index.html', items=get_all_items())

@app.route("/view_items_page", methods=["GET"])
def view_items_page():
    return render_template('index.html', items=get_all_items())

@app.route("/view_register_item_page", methods=["GET"])
def view_register_item_page():
    return render_template('register.html')

@app.route("/add_item_manually", methods=["GET", "POST"])
def add_item_manually():
    item_name = request.form['item_name']
    item_description = request.form['item_description']
    add_item(item_name, item_description, item_availability="Available")
    return render_template('register.html')

@app.route("/about_page", methods=["GET"])
def about_page():
    return render_template('about.html')

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



