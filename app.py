from pymongo import MongoClient
from flask import Flask, render_template, request, redirect, url_for, session
import random
import datetime
from bson.objectid import ObjectId

app = Flask(__name__)

client = MongoClient('mongodb://admin:secret@localhost:27017')
db = client["Isomorphism"] 
app.secret_key = "supersecretkey"

# mogo db infos
new_db = client['flask_web']

# collections
user = new_db['user']
donation = new_db['donation']
web_infos = new_db['web_infos']


# home page
@app.route('/')
def index_page():
    result = web_infos.find_one({})

    old_text = "The public welfare donation website is committed to providing a transparent and efficient platform for all sectors of society to promote charitable and public welfare activities. We believe that everyone has the ability to change the world, whether through donations, volunteer services, or other forms of support.Our mission is to gather love and bring hope to those in need. We support various public welfare projects, including education, medical assistance, environmental protection, and other fields, striving to make society better。"

    if result:

        txt_content = result.get("text")
        if txt_content:
            return render_template('index.html', txt_content=txt_content)
        else:
            return render_template('index.html', txt_content=old_text)
    else:
        return render_template('index.html', txt_content=old_text)


# register
@app.route('/register', methods=['POST', "GET"])
def register_page():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']

        if username and password:
            user_id = str(''.join(map(str, [random.randint(0, 9) for _ in range(20)])))
            data = {
                "username": username,
                "password": password,
                "name": name,
                "user_id": user_id,

            }
            user.insert_one(data)
            session['user_id'] = user_id

            return render_template('register.html', code=1)
        else:
            return render_template('register.html', code=2)


# log-in
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_info = user.find_one({'username': username})

        if user_info:
            if user_info['password'] == password:
                return redirect('/user_donation')
            else:
                return render_template('login.html', code=1)

        else:
            return render_template('login.html', code=1)


# donation
@app.route('/user_donation', methods=['POST', "GET"])
def donor_home_page():
    if request.method == 'GET':
        if not session.get('user_id'):
            return redirect('/login')

        return render_template('user_donation.html')
    if request.method == 'POST':
        money = request.form['money']
        world = request.form['world']
        user_id = session['user_id']

        if money is None or world is None or user_id is None or money == '' or world == '' or user_id == '':
            return render_template('user_donation.html', code='0')
        else:

            now_time = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))

            data = {
                "money": money,
                "world": world,
                "now_time": now_time,
                "user_id": user_id,

            }
            donation.insert_one(data)

            return render_template('user_donation.html', code='1')


# manage donation
@app.route('/user_cancels_donation', methods=['GET', 'POST'])
def user_cancels_donation_page():
    if request.method == 'GET':
        if not session.get('user_id'):
            return redirect('/login')
        user_donation_infos = donation.find()
        user_donation_infos = list(user_donation_infos)
        user_id = str(session.get('user_id'))

        to_jinjia_user_donation_infos = []
        for i in user_donation_infos:
            if i['user_id'] == user_id:
                to_jinjia_user_donation_infos.append(
                    {'money': i['money'], 'world': i['world'], 'now_time': i['now_time'], '_id': i['_id']})

        return render_template('user_cancels_donation.html',
                               to_jinjia_user_donation_infos=to_jinjia_user_donation_infos)
    if request.method == 'POST':
        donation_id = request.form['donation_id']
        donation_id = ObjectId(donation_id)
        result = donation.delete_one({'_id': donation_id})
        if result.deleted_count > 0:
            print("Successfully deleted")
            user_donation_infos = donation.find()
            user_donation_infos = list(user_donation_infos)
            user_id = str(session.get('user_id'))

            to_jinjia_user_donation_infos = []
            for i in user_donation_infos:
                if i['user_id'] == user_id:
                    to_jinjia_user_donation_infos.append(
                        {'money': i['money'], 'world': i['world'], 'now_time': i['now_time'], '_id': i['_id']})

            return render_template('user_cancels_donation.html',
                                   to_jinjia_user_donation_infos=to_jinjia_user_donation_infos, code='1')


        else:
            print("Failure reporting error")


# public donations
@app.route('/user_public_donations')
def user_public_donations_page():
    user_donation_infos = donation.find()
    user_donation_infos = list(user_donation_infos)
    to_jinjia_user_donation_infos = []
    for i in user_donation_infos:
        to_jinjia_user_donation_infos.append(
            {'money': i['money'], 'world': i['world'], 'now_time': i['now_time'], '_id': i['_id']})

    return render_template('user_public_donations.html', to_jinjia_user_donation_infos=to_jinjia_user_donation_infos)


# admin logon
@app.route('/admin_login', methods=['POST', "GET"])
def admin_login_page():
    if request.method == 'GET':
        return render_template('admin_login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin':
            session['admin_id'] = 'admin_id'
            return redirect('/admin')
        else:
            return render_template('admin_login.html', code=1)


@app.route('/admin', methods=["POST", "GET"])
def admin_page():
    if request.method == 'GET':
        if not session.get('admin_id'):
            return redirect('/admin_login')
        print()

        result = web_infos.find_one({})

        txt_content = "The public welfare donation website is committed to providing a transparent and efficient platform for all sectors of society to promote charitable and public welfare activities. We believe that everyone has the ability to change the world, whether through donations, volunteer services, or other forms of support.Our mission is to gather love and bring hope to those in need. We support various public welfare projects, including education, medical assistance, environmental protection, and other fields, striving to make society better。"

        if result:
            txt_content = result.get("text")

        return render_template('admin.html', txt_content=txt_content)

    if request.method == 'POST':
        text = request.form['infos']
        existing_data = web_infos.find_one({})
        if existing_data:
            web_infos.update_one({}, {"$set": {"text": text}})
        else:
            data = {
                "text": text,
            }
            web_infos.insert_one(data)

        return redirect('/admin')


if __name__ == "__main__":
    app.run(debug=True)

