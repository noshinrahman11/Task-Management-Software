from flask import Flask, render_template, url_for, redirect, request
from flask_login import login_required
from __init__ import create_app
from database import init_db, db_sessions

app = create_app()

with app.app_context():
    init_db()

@app.route('/')
@login_required
def index():
    return render_template("index.html")

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        ## add function to check if user credentials are valid
        return render_template('login.html')
    if request.method == 'GET':
        return render_template('login.html')

@app.errorhandler(401)
def unauthorized(e):
    return render_template("login.html")
    
@app.errorhandler(404)
def not_found(e):
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='localhost', port=5000, debug=True)

    #make api call in js