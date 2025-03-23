from flask import Flask, render_template, url_for, redirect, request, flash
from flask_login import login_required, login_user, logout_user, current_user
from flaskwebgui import FlaskUI
from __init__ import create_app
from models import User, Task, Project, UserTask, UserProject, ProjectTask 
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
def index():
    return render_template("index.html")

#do hashing in post section and login in get section
### Right now, the only user is username: admin, password: @dminPassword1, the hashed password is in db
### Pssswords are P@ssword#
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['identifier']
        password_hash = request.form['password']
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        if user and user.check_password(password_hash):
            login_user(user)
            return redirect(url_for('dashboard'))
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
        BirthDate = datetime.strptime(request.form['BirthDate'], "%Y-%m-%d") 
        Role = request.form['Role']

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
            new_user = User(username=username, password=password_hash, email=email, FirstName=FirstName, LastName=LastName, BirthDate=BirthDate, Role=Role)
            # new_user.set_password(password_hash)
            db_sessions.add(new_user)
            db_sessions.commit()
            login_user(new_user)  # Log in the new user automatically
            flash('Registration successful! Welcome!', category='success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard after signup
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully!', category='info')
    return redirect(url_for('index'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        # Add new event to user's event list
        taskName = request.form['taskName']
        description = request.form['description']
        startDate = datetime.strptime(request.form['startDate'], "%Y-%m-%dT%H:%M")
        dueDate = datetime.strptime(request.form['dueDate'], "%Y-%m-%dT%H:%M")
        category = request.form['category']
        status = request.form['status']
        priority = request.form['priority']
        assignedTo_username = request.form['assignedTo']  # This is a user ID, not username
        # assignedTo_username = request.form['assignedTo']  # This is a username

        print(f"Received task: {taskName}, {description}, {startDate}, {dueDate}, {category}, {status}, {priority}, {assignedTo_username}")

        assigned_user = User.query.get(request.form['assignedTo'])  # Fetch by user ID
        if not assigned_user:
            flash('Assigned user not found!', category='danger')
            return redirect(url_for('dashboard'))

        new_task = Task(name=taskName, description=description, startDate=startDate, dueDate=dueDate, category=category, status=status, priority=priority, assignedTo=assignedTo_username)
        
        db_sessions.add(new_task)
        db_sessions.commit()
        print("Task added successfully to the database.")
        
        # Link the task to the assigned user in `user_tasks`
        user_task_entry = UserTask(user_id=assigned_user.id, task_id=new_task.id)
        db_sessions.add(user_task_entry)
        db_sessions.commit()
        print("Task linked to user successfully.")

        flash('Task added successfully!', category='success')
        return redirect(url_for('dashboard'))
    
    user_tasks = (
        db_sessions.query(Task)
        .join(UserTask, Task.id == UserTask.task_id)
        .filter(UserTask.user_id == current_user.id)
        .all()
    )
    
    users = User.query.all()
    # Retrieve user's tasks from the database
    # user_tasks = current_user.tasks
    # return render_template('dashboard.html', tasks=user_tasks, user=current_user)

    # return render_template('dashboard.html', user=current_user)

    # user_tasks = Task.query.filter_by(assignedTo=current_user.username).all()
    return render_template('dashboard.html', tasks=user_tasks, user=current_user, users=users)

@app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get(task_id)

    if request.method == 'POST':
        task.name = request.form['taskName']
        task.description = request.form['description']
        task.startDate = datetime.strptime(request.form['startDate'], "%Y-%m-%dT%H:%M")
        task.dueDate = datetime.strptime(request.form['dueDate'], "%Y-%m-%dT%H:%M")
        task.category = request.form['category']
        task.status = request.form['status']
        task.priority = request.form['priority']

        assigned_user_id = request.form['assignedTo']
        assigned_user = User.query.get(assigned_user_id)

        if assigned_user:
            task.assignedTo = assigned_user.id  # Store new user ID

        db_sessions.commit()  # Save changes
        flash('Task updated successfully!', category='success')
        return redirect(url_for('dashboard'))

    users = User.query.all()  # Get all users for dropdown
    return render_template('edit_task.html', task=task, users=users)


@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get(task_id)
    print(f"Found task: {task.name}")

    # Remove task-user relationship
    UserTask.query.filter_by(task_id=task.id).delete()
    print("Removed task-user relationship.")

    # Remove the task itself
    db_sessions.delete(task)
    db_sessions.commit()
    print("Task deleted from database.")

    flash('Task deleted successfully!', category='success')
    return redirect(url_for('dashboard'))

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