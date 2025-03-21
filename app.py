from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import login_required, login_user, logout_user
from flaskwebgui import FlaskUI
from __init__ import create_app
from models import User, Task, Project 
from database import init_db, db_sessions

app = create_app()

with app.app_context():
    init_db()

@app.route('/')
@login_required
def index():
    return render_template("index.html")

#do hashing in post section and login in get section
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['identifier']
        password = request.form['password']
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', category='error')
    return render_template('login.html')
    



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