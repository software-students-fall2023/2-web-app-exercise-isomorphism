from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import pymongo

app = Flask(__name__)

try:
    connection = pymongo.MongoClient('mongodb://admin:secret@localhost:27017')
    connection.server_info()
except pymongo.errors.ServerSelectionTimeoutError as err:
    print("Could not connect to MongoDB:", err)
    connection = None
db = connection["Isomorphism"] if connection else None

@app.route('/register', methods=['POST'])
def register():
    if not db: 
        return "Error: Database connection failed!", 500
    user_type = request.form['userType']
    username = request.form['username']
    password = request.form['password']
    if user_type == "donor":
        db.donors.insert_one({"username": username, "password": password})
    elif user_type == "charity":
        db.charities.insert_one({"username": username, "password": password})
    return "Registration successful!"

if __name__ == "__main__":
    app.run()