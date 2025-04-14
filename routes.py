from flask import Blueprint, request, redirect, url_for, flash
from datetime import datetime
from TaskManagement.calendar_sync import add_task_to_calendar

# Create a Blueprint
routes = Blueprint('routes', __name__)

@routes.route('/create_task', methods=['POST'])
def create_task():
    task_title = request.form['title']
    task_description = request.form['description']
    task_due_date = request.form['due_date']  # Format: YYYY-MM-DDTHH:MM:SS

    # Convert due_date to datetime object
    task_due_date = datetime.fromisoformat(task_due_date)

    # Add task to database (example logic)
    # db.session.add(Task(title=task_title, description=task_description, due_date=task_due_date))
    # db.session.commit()

    # Add task to Google Calendar
    try:
        add_task_to_calendar(task_title, task_description, task_due_date)
        flash('Task created and added to Google Calendar!', 'success')
    except Exception as e:
        flash(f'Error adding task to Google Calendar: {e}', 'danger')

    return redirect(url_for('auth.index'))

@routes.route('/sync_to_calendar', methods=['POST'])
def sync_to_calendar():
    # Get task details from the form or database
    task_title = request.form['title']
    task_description = request.form['description']
    task_due_date = request.form['due_date']  # Format: YYYY-MM-DDTHH:MM:SS

    # Convert due_date to a datetime object
    task_due_date = datetime.fromisoformat(task_due_date)

    # Add task to Google Calendar
    try:
        add_task_to_calendar(task_title, task_description, task_due_date)
        flash('Task successfully synced to Google Calendar!', 'success')
    except Exception as e:
        flash(f'Error syncing task to Google Calendar: {e}', 'danger')

    # Redirect to the task list or another page
    return redirect(url_for('auth.index'))