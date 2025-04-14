from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from TaskManagement.models import User, Task, UserTask, Project, UserProject, ProjectTask 
from TaskManagement.database import init_db, db_sessions
from flask_session import Session
import re
from datetime import datetime
from TaskManagement.email_notif import send_task_notification, check_task_deadlines
from TaskManagement.reports import generate_progress_pie_chart

task_bp = Blueprint('task', __name__)


@task_bp.route('/task/dashboard', methods=['GET', 'POST'])
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
        assignedBy = current_user.username  # Task assigned by current user
        # assignedTo_username = request.form['assignedTo']  # This is a username

        print(f"Received task: {taskName}, {description}, {startDate}, {dueDate}, {category}, {status}, {priority}, {assignedTo_username}, {assignedBy}")
        # print(f"Received task: {taskName}, {description}, {startDate}, {dueDate}, {category}, {status}, {priority}, {assignedTo_username}")

        assigned_user = User.query.get(request.form['assignedTo'])  # Fetch by user ID
        if not assigned_user:
            flash('Assigned user not found!', category='danger')
            return redirect(url_for('task.dashboard'))

        new_task = Task(name=taskName, description=description, startDate=startDate, dueDate=dueDate, category=category, status=status, priority=priority, assignedTo=assignedTo_username, assignedBy=assignedBy)
        # new_task = Task(name=taskName, description=description, startDate=startDate, dueDate=dueDate, category=category, status=status, priority=priority, assignedTo=assignedTo_username)
        
        db_sessions.add(new_task)
        db_sessions.commit()
        print("Task added successfully to the database.")
        
        # Link the task to the assigned user in `user_tasks`
        user_task_entry = UserTask(user_id=assigned_user.id, task_id=new_task.id)
        db_sessions.add(user_task_entry)
        db_sessions.commit()
        print("Task linked to user successfully.")

        flash('Task added successfully!', category='success')

        # Send email notification
        assigned_user = User.query.get(assigned_user.id)  # Fetch user details
        if assigned_user and assigned_user.email:
            send_task_notification(new_task, assigned_user.email) 

        return redirect(url_for('task.dashboard'))

    # Get all tasks assigned to the current user
    user_tasks = (
        db_sessions.query(Task)
        .join(UserTask, Task.id == UserTask.task_id)
        .filter(UserTask.user_id == current_user.id)
        .all()
    )
    # Get all users for dropdown
    users = User.query.all()

    # Filtering Tasks
    filters = {
        "status": request.args.getlist("status"),  # Get selected statuses
        "priority": request.args.getlist("priority"),
        "category": request.args.getlist("category"),
        "assigned_by": request.args.getlist("assignedBy"),
    }

    filter_query = (
        db_sessions.query(Task)
        .join(UserTask, Task.id == UserTask.task_id)
        .filter(UserTask.user_id == current_user.id)
    )

    # Apply filters only if options are selected
    if filters["status"]:
        filter_query = filter_query.filter(Task.status.in_(filters["status"]))
        print(f"Filtering by status: {filters['status']}")
    if filters["priority"]:
        filter_query = filter_query.filter(Task.priority.in_(filters["priority"]))
        print(f"Filtering by priority: {filters['priority']}")
    if filters["category"]:
        filter_query = filter_query.filter(Task.category.in_(filters["category"]))
        print(f"Filtering by category: {filters['category']}")
    if filters["assigned_by"]:
        filter_query = filter_query.filter(Task.assignedBy.in_(filters["assigned_by"]))
        print(f"Filtering by assigned by: {filters['assigned_by']}")
        
    # Get filtered tasks
    user_tasks = filter_query.all()

    # Get users who assigned tasks to the current user for the dropdown
    assigned_by_users = (
        db_sessions.query(User)
        .join(Task, User.username == Task.assignedBy)  # Join on username
        .join(UserTask, Task.id == UserTask.task_id)
        .filter(UserTask.user_id == current_user.id)
        .distinct()
        .all()
    )
    print("Assigned By Users:", [user.username for user in assigned_by_users])

    users = User.query.all()  # Get all users for dropdown

    # Generate the pie chart for the current user
    generate_progress_pie_chart(current_user.id)

    return render_template('dashboard.html', tasks=user_tasks, user=current_user, users=users, assigned_by_users=assigned_by_users, filters=filters)

@task_bp.route('/task/edit_task/<int:task_id>', methods=['GET', 'POST'])
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
        print(f"Assigned user ID: {assigned_user_id}, Found user: {assigned_user.id}")

        # if the task is not being reassigned, then keep the same assignedBy, otherwise, the current user will be the new assigner(assignedBy)
        if task.assignedTo != assigned_user.id:
            task.assignedBy = current_user.username  # Update assignedBy to current user
            print(f"Task assignedBy updated to {task.assignedBy}")
        else:
            task.assignedBy = task.assignedBy # Keep the same assignedBy

        if assigned_user:
            task.assignedTo = assigned_user.id  # Store new user ID
        print(f"Task assigned to {task.assignedTo}")

        # Link the task to the assigned user in `user_tasks`
        UserTask.query.filter_by(task_id=task.id).delete()  # Remove existing link
        db_sessions.commit()  # Save changes before adding new link
        user_task_entry = UserTask(user_id=assigned_user.id, task_id=task.id)
        db_sessions.add(user_task_entry)
        db_sessions.commit()  # Save changes
        print("Assigned to updated successfully.")
        flash('Task updated successfully!', category='success')
        return redirect(url_for('task.dashboard'))

    user_tasks = (
        db_sessions.query(Task)
        .join(UserTask, Task.id == UserTask.task_id)
        .filter(UserTask.user_id == current_user.id)
        .all()
    )

    users = User.query.all()  # Get all users for dropdown
    return redirect(url_for('task.dashboard'), task=task, users=users, user_tasks=user_tasks)
    # return render_template('edit_task.html', task=task, users=users)


@task_bp.route('/task/delete_task/<int:task_id>', methods=['POST'])
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
    return redirect(url_for('task.dashboard'))
