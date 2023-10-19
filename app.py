import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, abort, url_for, make_response
import datetime

app = Flask(__name__)

client = pymongo.MongoClient('mongodb://admin:secret@localhost:27017')
db = client["Isomorphism"]  
app.secret_key = "supersecretkey"

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/donor_home')
def donor_home_page():
    return render_template('donor_home.html')

@app.route('/charity_home')
def charity_home_page():
    return render_template('charity_home.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type']
    if user_type == "donor":
        db.donors.insert_one({"username": username, "password": password})
    elif user_type == "charity":
        db.charities.insert_one({"username": username, "password": password})
    return render_template('success.html')

@app.route('/login', methods=['GET'])
def display_login():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['login-username']
    password = request.form['login-password']
    user_type = request.form['login-user_type']
    if user_type == "donor":
        donor = db.donors.find_one({"username": username})
        if donor:
            if donor["password"] == password:
                return redirect(url_for('donor_home_page'))
            else:
                return render_template('index.html', error = "Incorrect password.")
        else:
            return render_template('index.html', error = "Usernname Not Found.")
    elif user_type == "charity":
        charity = db.charities.find_one({"username": username})
        if charity:
            if charity["password"] == password:
                return redirect(url_for('charity_home_page'))
            else:
                return render_template('index.html', error = "Incorrect password.")
        else:
            return render_template('index.html', error = "Usernname Not Found.")
    


if __name__ == "__main__":
    app.run(debug=True)