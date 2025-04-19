from flask import Blueprint, render_template, url_for, redirect, request, flash, session
from flask_login import login_required, current_user
from TaskManagement.models import User, Task, UserTask
from datetime import datetime
from TaskManagement.email_notif import send_calendar_sync_notification
from TaskManagement.reports import generate_progress_pie_chart
from TaskManagement.calendar_sync import add_task_to_calendar, generate_auth_url, fetch_and_store_token, is_user_google_authed
from TaskManagement.database import db_sessions

features_bp = Blueprint('features', __name__)

@features_bp.route("/features/reports")
@login_required
def reports():
    chart_html = generate_progress_pie_chart(current_user.id)
    return render_template("reports.html", chart_html=chart_html)


@features_bp.route('/features/sync_calendar/<int:task_id>', methods=['POST'])
@login_required
def add_task_to_calendar_route(task_id):
    task = Task.query.get(task_id)
    if task:
        if not is_user_google_authed(current_user):
            flash("Please connect your Google Calendar first.", "warning")
            # return redirect(url_for('features.connect_google_calendar'))
            return redirect(url_for('task.dashboard'))

        add_task_to_calendar(task, task.name, task.description, task.dueDate)
        flash('Task added to Google Calendar successfully!', category='success')
    else:
        flash('Task not found!', category='error')
    return redirect(url_for('task.dashboard'))

@features_bp.route('/features/sync_to_calendar', methods=['POST'])
def sync_to_calendar():
    # Get task details from the form or database
    task_id = request.form['task_id']
    task_title = request.form['title']
    task_description = request.form['description']
    task_due_date = request.form['due_date']  # Format: YYYY-MM-DDTHH:MM:SS
    
    # Fetch the task from the database
    task = Task.query.get(task_id)
    if not task:
        flash("Task not found!", "danger")
        return redirect(url_for('task.dashboard'))

    # Convert due_date to a datetime object
    task_due_date = datetime.fromisoformat(task_due_date)

    # Add task to Google Calendar
    try:
        if not is_user_google_authed(current_user):
            flash("Please connect your Google Calendar first.", "warning")
            # return redirect(url_for('features.connect_google_calendar'))
            return redirect(url_for('task.dashboard'))
        add_task_to_calendar(task, task_title, task_description, task_due_date)
        send_calendar_sync_notification(current_user, task)  # Send email notification

        # Increment isSynced 
        task.isSynced += 1
        db_sessions.commit()

        flash('Task successfully synced to Google Calendar!', 'success')
    except Exception as e:
        flash(f'Error syncing task to Google Calendar: {e}', 'danger')

    # Redirect to the task list or another page
    return redirect(url_for('task.dashboard'))

@features_bp.route('/features/connect-google-calendar')
@login_required
def connect_google_calendar():
    auth_url = generate_auth_url()
    return redirect(auth_url)

@features_bp.route('/authorize-redirect')
@login_required
def oauth2callback():
    code = request.args.get('code')
    state = session.get('oauth_state')

    if not code or not state:
        flash('Authorization failed. Missing code or state.', 'danger')
        return redirect(url_for('task.dashboard'))

    try:
        fetch_and_store_token(code, state, current_user)
        flash('Google Calendar connected successfully!', 'success')
    except Exception as e:
        flash(f'Authorization error: {e}', 'danger')

    return redirect(url_for('task.dashboard'))


@features_bp.route('/create_task', methods=['POST'])
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

    return redirect(url_for('task.dashboard'))
