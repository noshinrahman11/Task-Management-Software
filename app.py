from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import login_required, login_user, logout_user
from flaskwebgui import FlaskUI
from __init__ import create_app
from models import User, Task, Project 
from database import init_db, db_sessions
from flask_session import Session
import re
from datetime import datetime

### When manually entering user, use this to enter hashed password
# from werkzeug.security import generate_password_hash

# password = "@dminPassword1"
# hashed_password = generate_password_hash(password)
# print(hashed_password)

app = create_app()

with app.app_context():
    init_db()

@app.route('/')
@login_required
def index():
    return render_template("index.html")

#do hashing in post section and login in get section
### Right now, the only user is username: admin, password: @dminPassword1, the hashed password is in db
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['identifier']
        password_hash = request.form['password']
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password_hash):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', category='error')
    return render_template('login.html')
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_hash = request.form['password']
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        # BirthDate = request.form['BirthDate']
        BirthDate = datetime.strptime(request.form['BirthDate'], "%Y-%m-%d")

        # Check if username or email already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        # Checks for valid username, email, and password
        if user:
            flash('Username or email already exists', category='error')
            return redirect(url_for('register'))
        elif not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password_hash):
            flash('Password must contain at least one number, one uppercase letter, and one special character.', category='error')
            return redirect(url_for('register'))
        else:
            new_user = User(username=username, password=password_hash, email=email, FirstName=FirstName, LastName=LastName, BirthDate=BirthDate)
            # new_user.set_password(password_hash)
            db_sessions.add(new_user)
            db_sessions.commit()
            login_user(new_user)  # Log in the new user automatically
            flash('Registration successful! Welcome!', category='success')
            return redirect(url_for('index'))  # Redirect to the homepage after signup
    return render_template('register.html')


@app.errorhandler(401)
def unauthorized(e):
    return render_template("login.html")
    
@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('login'))

if __name__ == "__main__":
    # app.run(host='localhost', port=5000, debug=True)
    
    FlaskUI(app=app,
        server="flask",
        width=800,
        height=600,
        ).run()
    
    # make api call in js