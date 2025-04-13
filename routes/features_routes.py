from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import login_required, current_user
from models import User, Task, UserTask
from datetime import datetime
from email_notif import send_task_notification
from reports import generate_progress_pie_chart
from calendar_sync import add_task_to_calendar

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
        add_task_to_calendar(task.name, task.description, task.dueDate)
        flash('Task added to Google Calendar successfully!', category='success')
    else:
        flash('Task not found!', category='error')
    return redirect(url_for('task.dashboard'))