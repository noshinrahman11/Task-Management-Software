from flask import Flask, render_template, url_for, redirect, request, flash, session
# from flaskwebgui import FlaskUI
from TaskManagement.__init__ import create_app
from TaskManagement.database import init_db, db_sessions
from flask_session import Session
from datetime import datetime
from TaskManagement.email_notif import check_task_deadlines
import time
import threading
from TaskManagement.routes import register_routes
import os

app = create_app()
with app.app_context():
    init_db()
    register_routes(app)


# @app.errorhandler(401)
# def unauthorized(e):
#     print("401 error")
#     return render_template("404.html")
    
# @app.errorhandler(404)
# def not_found(e):
#     print("404 error")
#     return redirect(url_for('auth.login'))

if __name__ == "__main__":
    # app.run(host='localhost', port=5000, debug=True)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
    
    # def run_flask():
    #     print ("Starting Flask app...")
    #     FlaskUI(app=app,
    #         server="flask",
    #         width=800,
    #         height=600,
    #         ).run()
    #     flask_thread = threading.Thread(target=run_flask, name="Thread-f", daemon=True)  # Start the thread
    #     flask_thread.start()
    
    def run_deadline_checker():
        print ("Starting background thread for checking deadlines...")
        with app.app_context():
            while True:
                check_task_deadlines()  # Run the function
                print("Checking task deadlines...")
                time.sleep(3600)  # Wait for 1 hour before checking again
        
    deadline_thread = threading.Thread(target=run_deadline_checker, name="Thread-d", daemon=True)  # Start the thread
    deadline_thread.start()
    print("Background thread started!")

    print ("Starting Flask app...")
    # app.run(host='0.0.0.0', port=80, debug=True)
    # FlaskUI(app=app,
    #         server="flask",
    #         width=800,
    #         height=600,
    #         ).run()
    


# @app.route('/')
# def index():
#     return render_template("index.html")

# @app.route('/login', methods = ['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['identifier']
#         password_hash = request.form['password']
#         # Check if user exists and password is correct, if so, hash password and login user
#         user = User.query.filter((User.username == username) | (User.email == username)).first()
#         if user and user.check_password(password_hash): 
#             login_user(user)
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Invalid username or password', category='error')

#     return render_template('login.html')

# @app.route('/verification_code', methods=['GET', 'POST'])
# def verification_code():
#     if request.method == 'POST':
#         email = request.form['email']
#         user = User.query.filter_by(email=email).first()
#         if user:
#             # Creates a random 6-digit verification code 
#             verification_code = random.randint(100000, 999999) 
#             session['reset_email'] = email
#             session['verification_code'] = str(verification_code) # Store the verification code in the session so it can be accessed later
#             print(f"Password reset verification code: {verification_code}")
#             # Send email with verification code
#             send_password_reset_notification(user, email, verification_code)
#             flash('Password reset verification code has been sent to your email.', category='info')
#             return redirect(url_for('verify_code'))
#         else:
#             flash('Email not found.', category='error')
#             return redirect(url_for('login'))

#     return redirect(url_for('login'))

# @app.route('/verify_code', methods=['GET', 'POST'])
# def verify_code():
#     if request.method == 'POST':
#         print("Verifying code...")
#         user_code = str(request.form.get('verification_code')).strip()
#         actual_code = str(session.get('verification_code')).strip()
#         email = session.get('reset_email')
#         print(f"User code: {user_code}, Actual code: {actual_code}, Email: {email}")

#         # Check if the session has expired or if the email is not found
#         if not actual_code or not email:
#             flash('Session expired. Please try again.', 'error')
#             return redirect(url_for('login'))

#         # Check if the verification code matches the one sent to the email, redirect to reset password page if it does
#         if user_code == actual_code:
#             print(f"Given verification code matches the actual code: {actual_code}")
#             session.pop('verification_code', None) # Clear the verification code from the session
#             return redirect(url_for('reset_password', email=email))
#         else:
#             flash('Invalid verification code.', 'error')
#             return redirect(url_for('verify_code'))

#     return render_template('verification-code.html')  


# @app.route('/reset_password/<email>', methods=['GET', 'POST'])
# def reset_password(email):
#     if request.method == 'POST':
#         print(f"Resetting password for email: {email}")
#         password_hash = request.form['password']
#         confirmPassword = request.form['confirmPassword']
#         user = User.query.filter_by(email=email).first()
#         if user:
#             if password_hash != confirmPassword:
#                 flash('Passwords do not match.', category='error')
#                 return redirect(url_for('reset_password', email=email))
#             elif user.check_password(password_hash):
#                 flash('New password cannot be the same as the old password.', category='error')
#                 return redirect(url_for('reset_password', email=email))
#             elif not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password_hash):
#                 flash('Password must contain at least one number, one uppercase letter, and one special character.', category='error')
#                 return redirect(url_for('reset_password', email=email))
#             else:
#                 user.set_password(password_hash)
#                 db_sessions.commit()
#                 flash('Password reset successfully!', category='success')
#                 return redirect(url_for('login'))
#         else:
#             flash('User not found.', category='error')
#     return render_template('reset-password.html', email=email)


# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password_hash = request.form['password']
#         FirstName = request.form['FirstName']
#         LastName = request.form['LastName']
#         BirthDate = datetime.strptime(request.form['BirthDate'], "%Y-%m-%d") 
#         Role = request.form['Role']

#         # Check if username or email already exists
#         user = User.query.filter((User.username == username) | (User.email == email)).first()
#         # Checks for valid username, email, and password
#         if user:
#             flash('Username or email already exists', category='error')
#             return redirect(url_for('register'))
#         elif not re.match(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W)', password_hash):
#             flash('Password must contain at least one number, one uppercase letter, and one special character.', category='error')
#             return redirect(url_for('register'))
#         else:
#             new_user = User(username=username, password=password_hash, email=email, FirstName=FirstName, LastName=LastName, BirthDate=BirthDate, Role=Role)
#             # new_user.set_password(password_hash)
#             db_sessions.add(new_user)
#             db_sessions.commit()
#             login_user(new_user)  # Log in the new user automatically
#             flash('Registration successful! Welcome!', category='success')
#             # Send email for new sign-in
#             send_registration_notification(new_user, new_user.email)
#             print('Registration email sent')
            
#             return redirect(url_for('dashboard'))  # Redirect to dashboard after signup
#     return render_template('register.html')



# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     flash('You have been logged out successfully!', category='info')
#     return redirect(url_for('index'))

# @app.route("/reports")
# @login_required
# def reports():
#     chart_html = generate_progress_pie_chart(current_user.id)
#     return render_template("reports.html", chart_html=chart_html)


# @app.route('/sync_calendar/<int:task_id>', methods=['POST'])
# @login_required
# def add_task_to_calendar_route(task_id):
#     task = Task.query.get(task_id)
#     if task:
#         add_task_to_calendar(task.name, task.description, task.dueDate)
#         flash('Task added to Google Calendar successfully!', category='success')
#     else:
#         flash('Task not found!', category='error')
#     return redirect(url_for('dashboard'))

# @app.route('/admin', methods=['GET', 'POST'])
# @login_required
# def admin():

#     # Show all users in the database
#     users = User.query.all()
    
#     return render_template('admin.html', users=users)

# @app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
# def edit_user(user_id):
#     user = User.query.get(user_id)
#     if request.method == 'POST':
#         previous_role = user.Role
#         user.Role = request.form['Role']

#         db_sessions.commit()

#         print(f"User Role updated to from {previous_role} to {user.Role} successfully.")
#         flash('User updated successfully!', category='success')

#         # Send email notification if role is changed
#         if user and user.email:
#             if user.Role != previous_role:
#                 send_role_notification(user, previous_role, user.email) 

#         return redirect(url_for('admin'))
    

# @app.route('/dashboard', methods=['GET', 'POST'])
# @login_required
# def dashboard():
#     if request.method == 'POST':
#         # Add new event to user's event list
#         taskName = request.form['taskName']
#         description = request.form['description']
#         startDate = datetime.strptime(request.form['startDate'], "%Y-%m-%dT%H:%M")
#         dueDate = datetime.strptime(request.form['dueDate'], "%Y-%m-%dT%H:%M")
#         category = request.form['category']
#         status = request.form['status']
#         priority = request.form['priority']
#         assignedTo_username = request.form['assignedTo']  # This is a user ID, not username
#         assignedBy = current_user.username  # Task assigned by current user
#         # assignedTo_username = request.form['assignedTo']  # This is a username

#         print(f"Received task: {taskName}, {description}, {startDate}, {dueDate}, {category}, {status}, {priority}, {assignedTo_username}, {assignedBy}")
#         # print(f"Received task: {taskName}, {description}, {startDate}, {dueDate}, {category}, {status}, {priority}, {assignedTo_username}")

#         assigned_user = User.query.get(request.form['assignedTo'])  # Fetch by user ID
#         if not assigned_user:
#             flash('Assigned user not found!', category='danger')
#             return redirect(url_for('dashboard'))

#         new_task = Task(name=taskName, description=description, startDate=startDate, dueDate=dueDate, category=category, status=status, priority=priority, assignedTo=assignedTo_username, assignedBy=assignedBy)
#         # new_task = Task(name=taskName, description=description, startDate=startDate, dueDate=dueDate, category=category, status=status, priority=priority, assignedTo=assignedTo_username)
        
#         db_sessions.add(new_task)
#         db_sessions.commit()
#         print("Task added successfully to the database.")
        
#         # Link the task to the assigned user in `user_tasks`
#         user_task_entry = UserTask(user_id=assigned_user.id, task_id=new_task.id)
#         db_sessions.add(user_task_entry)
#         db_sessions.commit()
#         print("Task linked to user successfully.")

#         flash('Task added successfully!', category='success')

#         # Send email notification
#         assigned_user = User.query.get(assigned_user.id)  # Fetch user details
#         if assigned_user and assigned_user.email:
#             send_task_notification(new_task, assigned_user.email) 

#         return redirect(url_for('dashboard'))

#     # Get all tasks assigned to the current user
#     user_tasks = (
#         db_sessions.query(Task)
#         .join(UserTask, Task.id == UserTask.task_id)
#         .filter(UserTask.user_id == current_user.id)
#         .all()
#     )
#     # Get all users for dropdown
#     users = User.query.all()

    

#     # Filtering Tasks
#     filters = {
#         "status": request.args.getlist("status"),  # Get selected statuses
#         "priority": request.args.getlist("priority"),
#         "category": request.args.getlist("category"),
#         "assigned_by": request.args.getlist("assignedBy"),
#     }

#     filter_query = (
#         db_sessions.query(Task)
#         .join(UserTask, Task.id == UserTask.task_id)
#         .filter(UserTask.user_id == current_user.id)
#     )

#     # Apply filters only if options are selected
#     if filters["status"]:
#         filter_query = filter_query.filter(Task.status.in_(filters["status"]))
#         print(f"Filtering by status: {filters['status']}")
#     if filters["priority"]:
#         filter_query = filter_query.filter(Task.priority.in_(filters["priority"]))
#         print(f"Filtering by priority: {filters['priority']}")
#     if filters["category"]:
#         filter_query = filter_query.filter(Task.category.in_(filters["category"]))
#         print(f"Filtering by category: {filters['category']}")
#     if filters["assigned_by"]:
#         filter_query = filter_query.filter(Task.assignedBy.in_(filters["assigned_by"]))
#         print(f"Filtering by assigned by: {filters['assigned_by']}")
        

#     user_tasks = filter_query.all()

#     assigned_by_users = (
#         db_sessions.query(User)
#         .join(Task, User.username == Task.assignedBy)  # Join on username
#         .join(UserTask, Task.id == UserTask.task_id)
#         .filter(UserTask.user_id == current_user.id)
#         .distinct()
#         .all()
#     )
#     print("Assigned By Users:", [user.username for user in assigned_by_users])

#     users = User.query.all()  # Get all users for dropdown

#     # Generate the pie chart for the current user
#     generate_progress_pie_chart(current_user.id)

#     return render_template('dashboard.html', tasks=user_tasks, user=current_user, users=users, assigned_by_users=assigned_by_users, filters=filters)

# @app.route('/edit_task/<int:task_id>', methods=['GET', 'POST'])
# @login_required
# def edit_task(task_id):
#     task = Task.query.get(task_id)

#     if request.method == 'POST':
#         task.name = request.form['taskName']
#         task.description = request.form['description']
#         task.startDate = datetime.strptime(request.form['startDate'], "%Y-%m-%dT%H:%M")
#         task.dueDate = datetime.strptime(request.form['dueDate'], "%Y-%m-%dT%H:%M")
#         task.category = request.form['category']
#         task.status = request.form['status']
#         task.priority = request.form['priority']

#         assigned_user_id = request.form['assignedTo']
#         assigned_user = User.query.get(assigned_user_id)
#         print(f"Assigned user ID: {assigned_user_id}, Found user: {assigned_user.id}")

#         # if the task is not being reassigned, then keep the same assignedBy, otherwise, the current user will be the new assigner(assignedBy)
#         if task.assignedTo != assigned_user.id:
#             task.assignedBy = current_user.username  # Update assignedBy to current user
#             print(f"Task assignedBy updated to {task.assignedBy}")
#         else:
#             task.assignedBy = task.assignedBy # Keep the same assignedBy

#         if assigned_user:
#             task.assignedTo = assigned_user.id  # Store new user ID
#         print(f"Task assigned to {task.assignedTo}")

#         # Link the task to the assigned user in `user_tasks`
#         UserTask.query.filter_by(task_id=task.id).delete()  # Remove existing link
#         db_sessions.commit()  # Save changes before adding new link
#         user_task_entry = UserTask(user_id=assigned_user.id, task_id=task.id)
#         db_sessions.add(user_task_entry)
#         db_sessions.commit()  # Save changes
#         print("Assigned to updated successfully.")
#         flash('Task updated successfully!', category='success')
#         return redirect(url_for('dashboard'))

#     user_tasks = (
#         db_sessions.query(Task)
#         .join(UserTask, Task.id == UserTask.task_id)
#         .filter(UserTask.user_id == current_user.id)
#         .all()
#     )

#     users = User.query.all()  # Get all users for dropdown
#     return redirect(url_for('dashboard'), task=task, users=users, user_tasks=user_tasks)
#     # return render_template('eddit_task.html', task=task, users=users)


# @app.route('/delete_task/<int:task_id>', methods=['POST'])
# @login_required
# def delete_task(task_id):
#     task = Task.query.get(task_id)
#     print(f"Found task: {task.name}")

#     # Remove task-user relationship
#     UserTask.query.filter_by(task_id=task.id).delete()
#     print("Removed task-user relationship.")

#     # Remove the task itself
#     db_sessions.delete(task)
#     db_sessions.commit()
#     print("Task deleted from database.")

#     flash('Task deleted successfully!', category='success')
#     return redirect(url_for('dashboard'))

