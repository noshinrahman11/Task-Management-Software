from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, login_user, logout_user, current_user
from TaskManagement.models import User
from TaskManagement.database import db_sessions
from TaskManagement.email_notif import send_password_reset_notification, send_registration_notification, send_password_reset_success_notification
from datetime import datetime
import random
import re


auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/')
def index():
    return render_template("index.html")

@auth_bp.route('/auth/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['identifier']
        password_hash = request.form['password']
        # Check if user exists and password is correct, if so, hash password and login user
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password_hash): 
            login_user(user)
            return redirect(url_for('task.dashboard'))
        else:
            flash('Invalid username or password', category='error')

    return render_template('login.html')

@auth_bp.route('/auth/verification_code', methods=['GET', 'POST'])
def verification_code():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            # Creates a random 6-digit verification code 
            verification_code = random.randint(100000, 999999) 
            session['reset_email'] = email
            session['verification_code'] = str(verification_code) # Store the verification code in the session so it can be accessed later
            print(f"Password reset verification code: {verification_code}")
            # Send email with verification code
            send_password_reset_notification(user, email, verification_code)
            flash('Password reset verification code has been sent to your email.', category='info')
            return redirect(url_for('auth.verify_code'))
        else:
            flash('Email not found.', category='error')
            return redirect(url_for('auth.login'))

    return redirect(url_for('auth.login'))

@auth_bp.route('/auth/verify_code', methods=['GET', 'POST'])
def verify_code():
    if request.method == 'POST':
        print("Verifying code...")
        user_code = str(request.form.get('verification_code')).strip()
        actual_code = str(session.get('verification_code')).strip()
        email = session.get('reset_email')
        print(f"User code: {user_code}, Actual code: {actual_code}, Email: {email}")

        # Check if the session has expired or if the email is not found
        if not actual_code or not email:
            flash('Session expired. Please try again.', 'error')
            return redirect(url_for('auth.login'))

        # Check if the verification code matches the one sent to the email, redirect to reset password page if it does
        if user_code == actual_code:
            print(f"Given verification code matches the actual code: {actual_code}")
            session.pop('verification_code', None) # Clear the verification code from the session
            return redirect(url_for('auth.reset_password', email=email))
        else:
            flash('Invalid verification code.', 'error')
            return redirect(url_for('auth.verify_code'))

    return render_template('verification-code.html')  


@auth_bp.route('/auth/reset_password/<email>', methods=['GET', 'POST'])
def reset_password(email):
    if request.method == 'POST':
        print(f"Resetting password for email: {email}")
        password_hash = request.form['password']
        confirmPassword = request.form['confirmPassword']
        user = User.query.filter_by(email=email).first()
        if user:
            if password_hash != confirmPassword:
                flash('Passwords do not match.', category='error')
                return redirect(url_for('auth.reset_password', email=email))
            elif user.check_password(password_hash):
                flash('New password cannot be the same as the old password.', category='error')
                return redirect(url_for('auth.reset_password', email=email))
            elif not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password_hash):
                flash('Password must contain at least one number, one uppercase letter, and one special character.', category='error')
                return redirect(url_for('auth.reset_password', email=email))
            else:
                user.set_password(password_hash)
                db_sessions.commit()
                send_password_reset_success_notification(user, email) # Send email for password reset
                flash('Password reset successfully!', category='success')
                return redirect(url_for('auth.login'))
        else:
            flash('User not found.', category='error')
    return render_template('reset-password.html', email=email)


@auth_bp.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password_hash = request.form['password']
        FirstName = request.form['FirstName']
        LastName = request.form['LastName']
        BirthDate = datetime.strptime(request.form['BirthDate'], "%Y-%m-%d") 
        Role = request.form['Role']

        # Check if username or email already exists
        user = User.query.filter((User.username == username) | (User.email == email)).first()
        # Checks for valid username, email, and password
        if user:
            flash('Username or email already exists', category='error')
            return redirect(url_for('auth.register'))
        elif not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password_hash):
            flash('Password must contain at least one number, one uppercase letter, and one special character.', category='error')
            return redirect(url_for('auth.register'))
        else:
            new_user = User(username=username, password=password_hash, email=email, FirstName=FirstName, LastName=LastName, BirthDate=BirthDate, Role=Role)
            # new_user.set_password(password_hash)
            db_sessions.add(new_user)
            db_sessions.commit()
            login_user(new_user)  # Log in the new user automatically
            flash('Registration successful! Welcome!', category='success')
            # Send email for new sign-in
            send_registration_notification(new_user, new_user.email)
            print('Registration email sent')
            
            return redirect(url_for('task.dashboard'))  # Redirect to user's dashboard after signup
    return render_template('register.html')

@auth_bp.route('/auth/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully!', category='info')
    return redirect(url_for('auth.index'))
