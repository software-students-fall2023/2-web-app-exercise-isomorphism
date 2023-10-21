import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, session, abort, url_for, make_response, flash
from functools import wraps
import datetime

app = Flask(__name__)

client = pymongo.MongoClient('mongodb://admin:secret@localhost:27017')
db = client["Isomorphism"]  
app.config['SECRET_KEY'] = 'supersecretkey'

#log-in check
def login_required(user_types=None):
    if user_types is None:
        user_types = ['donor', 'charity']
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'username' not in session:
                flash('Please login to access this page.')
                return redirect(url_for('display_login'))
            elif session.get('user_type') not in user_types:
                flash('You do not have permission to access this page.')
                return redirect(url_for('index_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/register')
def register_page():
    return render_template('register.html')

@app.route('/donor_home')
@login_required(['donor'])
def donor_home_page():
    return render_template('donor_home.html')

@app.route('/charity_home')
@login_required(['charity'])
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
                session['user_type'] = 'donor'
                session['username'] = username
                return redirect(url_for('donor_home_page'))
            else:
                return render_template('index.html', error = "Incorrect password.")
        else:
            return render_template('index.html', error = "Usernname Not Found.")
    elif user_type == "charity":
        charity = db.charities.find_one({"username": username})
        if charity:
            if charity["password"] == password:
                session['user_type'] = 'charity'
                session['username'] = username
                return redirect(url_for('charity_home_page'))
            else:
                return render_template('index.html', error = "Incorrect password.")
        else:
            return render_template('index.html', error = "Usernname Not Found.")
        
@app.route('/add_donation', methods=['POST'])
@login_required(['donor'])
def add_donation():
    donation_name = request.form['donation_name']
    donation_type = request.form['donation_type']
    recipient_age = request.form['recipient_age']
    db.donations.insert_one({
        "donor_username": session['username'],
        "name": donation_name,
        "type": donation_type,
        "recipient_age": recipient_age
    })
    flash('Donation added successfully!')  # Send a success message
    return redirect(url_for('donor_home_page'))

@app.route('/donor_view_donations')
@login_required(['donor'])
def donor_view_donations():
    donations = db.donations.find({"donor_username": session['username']})
    return render_template('donor_view_donations.html', donations = donations)

@app.route('/edit_donation/<donation_id>', methods=['GET'])
@login_required(['donor'])
def display_edit_donation(donation_id):
    donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    if donation:
        return render_template('edit_donation.html', donation=donation)
    else:
        flash('Donation not found!')
        return redirect(url_for('donor_view_donations'))

@app.route('/edit_donation/<donation_id>', methods=['POST'])
@login_required(['donor'])
def edit_donation(donation_id):
    updated_name = request.form['donation_name']
    updated_type = request.form['donation_type']
    updated_age = request.form['recipient_age']
    db.donations.update_one(
        {"_id": ObjectId(donation_id)},
        {"$set": {
            "name": updated_name,
            "type": updated_type,
            "recipient_age": updated_age
        }}
    )
    flash('Donation updated successfully!')
    return redirect(url_for('donor_view_donations'))

@app.route('/delete_donation/<donation_id>', methods=['GET'])
@login_required(user_types=['donor'])  # Ensure only donors can access this route
def delete_donation(donation_id):
    donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    if donation and donation["donor_username"] == session['username']:
        db.donations.delete_one({"_id": ObjectId(donation_id)})
        flash('Donation deleted successfully!')
    else:
        flash('Donation not found or you do not have permission to delete it!')
    return redirect(url_for('donor_view_donations'))
    
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index_page'))

if __name__ == "__main__":
    app.run(debug=True)