import pymongo
from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, session, abort, url_for, make_response, flash
from functools import wraps
import datetime

#start flask
app = Flask(__name__)

#connect to the database server and create a new database called Isomorphism
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
            if 'username' not in session: #if the user tries to access page without log-in
                flash('Please login to access this page.', "info")
                return redirect(url_for('display_login'))
            elif session.get('user_type') not in user_types: #if the user tries to access page that is not accessible for its user group.
                flash('You do not have permission to access this page.', "info")
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

#user registration
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    user_type = request.form['user_type'] #record the user group of the user (donor or charity)
    if user_type == "donor": #add the user's username and password into corresponding collections
        db.donors.insert_one({"username": username, "password": password})
    elif user_type == "charity":
        db.charities.insert_one({"username": username, "password": password})
    return render_template('success.html')

@app.route('/login', methods=['GET'])
def display_login():
    return render_template('index.html')

#user login
@app.route('/login', methods=['POST'])
def login():
    username = request.form['login-username']
    password = request.form['login-password']
    user_type = request.form['login-user_type']
    if user_type == "donor": #search the corresponding collections
        donor = db.donors.find_one({"username": username})
        if donor: #check if the username exists
            if donor["password"] == password: #check if the password matches
                session['user_type'] = 'donor' #update session
                session['username'] = username
                return redirect(url_for('donor_home_page'))
            else:
                flash("Incorrect password.", "error")
                return redirect(url_for('display_login'))
        else:
            flash("Username Not Found.", "error")
            return redirect(url_for('display_login'))
    elif user_type == "charity":
        charity = db.charities.find_one({"username": username})
        if charity: #same as donors
            if charity["password"] == password:
                session['user_type'] = 'charity'
                session['username'] = username
                return redirect(url_for('charity_home_page'))
            else:
                flash("Incorrect password.", "error")
                return redirect(url_for('display_login'))
        else:
            flash("Username Not Found.", "error")
            return redirect(url_for('display_login'))

#add donation (for donor)   
@app.route('/add_donation', methods=['POST'])
@login_required(['donor'])
def add_donation():
    donation_name = request.form['donation_name']
    donation_type = request.form['donation_type']
    recipient_age = request.form['recipient_age']
    db.donations.insert_one({ #add one donation object into database donations collection
        "donor_username": session['username'],
        "name": donation_name,
        "type": donation_type,
        "recipient_age": recipient_age
    })
    flash('Donation added successfully!') #inform the user that adding is successful
    return redirect(url_for('donor_home_page'))

#view all donations (for donor)
@app.route('/donor_view_donations')
@login_required(['donor'])
def donor_view_donations(): #search all donations that has the current session user's username
    donations = db.donations.find({"donor_username": session['username']})
    return render_template('donor_view_donations.html', donations = donations)

#double-check the object exists before we really edit the object in the database
@app.route('/edit_donation/<donation_id>', methods=['GET'])
@login_required(['donor'])
def display_edit_donation(donation_id):
    donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    if donation:
        return render_template('edit_donation.html', donation = donation)
    else:
        flash('Donation not found!')
        return redirect(url_for('donor_view_donations'))

#edit donation (for donor)
@app.route('/edit_donation/<donation_id>', methods=['POST'])
@login_required(['donor'])
def edit_donation(donation_id):
    updated_name = request.form['donation_name']
    updated_type = request.form['donation_type']
    updated_age = request.form['recipient_age']
    db.donations.update_one( #update the corresponding object
        {"_id": ObjectId(donation_id)},
        {"$set": {
            "name": updated_name,
            "type": updated_type,
            "recipient_age": updated_age
        }}
    )
    flash('Donation updated successfully!')
    return redirect(url_for('donor_view_donations'))

#delete a donation (for donor)
@app.route('/delete_donation/<donation_id>', methods=['GET'])
@login_required(user_types=['donor']) 
def delete_donation(donation_id):
    donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    if donation and donation["donor_username"] == session['username']: #double-check the user's username (i.e., someone is nor supposed to delete other's donation)
        db.donations.delete_one({"_id": ObjectId(donation_id)}) #delete the object in the database
        flash('Donation deleted successfully!')
    else:
        flash('Donation not found or you do not have permission to delete it!')
    return redirect(url_for('donor_view_donations'))

#view and search donations (for charity)
@app.route('/view_all_donations', methods=['GET', 'POST'])
@login_required(['charity'])
def view_all_donations():
    if request.method == 'POST':
        donor = request.form.get('donor')
        name = request.form.get('name')
        type = request.form.get('type')
        age = request.form.get('age')
        query = {}
        if donor:
            query['donor_username'] = {'$regex': donor, '$options': 'i'} #case insensitive
        if name:
            query['name'] = {'$regex': name, '$options': 'i'}
        if type:
            query['type'] = type
        if age:
            query['recipient_age'] = age
        session['search_query'] = query
        return redirect(url_for('view_all_donations'))
    all_donations = db.donations.find(session.get('search_query', {})) #search the donations collections with user-specified query.
    return render_template('view_all_donations.html', donations = all_donations)

#accept donation (for charity)
@app.route('/accept_donation/<donation_id>')
@login_required(['charity'])
def accept_donation(donation_id):
    donation = db.donations.find_one({"_id": ObjectId(donation_id)})
    if not donation: #double-check the donation exists before proceeding.
        flash('Donation not found!')
        return redirect(url_for('view_all_donations'))
    db.charity_donations.insert_one({ #add the donation to the charity_donations collection
        "charity_username": session['username'],
        "name": donation['name'],
        "type": donation['type'],
        "recipient_age": donation['recipient_age'],
        "donor_username": donation['donor_username']
    })
    db.donations.delete_one({"_id": ObjectId(donation_id)}) #delete the donation from donations collection
    flash('Donation accepted!')
    return redirect(url_for('view_all_donations'))

#view all accepted donations (for charity)
@app.route('/charity_accepted_donations')
@login_required(['charity'])
def charity_accepted_donations():
    accepted_donations = db.charity_donations.find({"charity_username": session['username']}) #display all donations accepted by current user
    return render_template('charity_accepted_donations.html', accepted_donations=accepted_donations)

#logout, clear the session, and return to home page
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index_page'))

if __name__ == "__main__":
    app.run(debug=True)