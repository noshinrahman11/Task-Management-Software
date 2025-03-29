from flask_mail import Message
from flask import current_app
from __init__ import mail
from datetime import datetime, timedelta
from models import Task, User


# In powershell:
# $env:MAIL_USERNAME="taskmanagementsystemcs264@gmail.com"
# $env:MAIL_PASSWORD="aebn jexs dokr whwb"

# Christine: jdls kkaj zbne hzva
# Nandanie: valn itnl gbnt nxpt
# Drew: wmhq xojg qdjx biuj

def send_email(subject, recipients, body, html=None):
    with current_app.app_context():
        msg = Message(subject, recipients=recipients, body=body, html=html)
        mail.send(msg)


def send_task_notification(task, recipient_email):
    subject = f"New Task Assigned: {task.name}"
    body = f"""
    Hello,

    You have been assigned a new task

    Task: {task.name}
    Description: {task.description}
    Due Date: {task.dueDate.strftime('%Y-%m-%d %H:%M')}

    Please check your dashboard for more details.

    Regards,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def send_task_deadline_notification(recipient_email, task):
    subject = f"Deadline Approaching: {task.name} due soon"
    body = f"""
    Hello,

    The following task is due soon:

    Task: {task.name}
    Description: {task.description}
    Due Date: {task.dueDate.strftime('%Y-%m-%d %H:%M')}

    Please check your dashboard for more details.

    Regards,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def send_role_notification(user, previous_role, recipient_email):
    subject = f"User Role Updated: {user.FirstName}'s role is now {user.Role}"
    body = f"""
    Hello,

    Your role in the Task Management System has been updated.

    Previous Role: {previous_role}
    New Role: {user.Role}

    Your permissions have been updated accordingly.

    Sincerely,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def check_task_deadlines():
    """Check for tasks that are due in 24 hours and send email notifications."""
    print("Inside check_task_deadlines function...")
    with current_app.app_context():
        now = datetime.now()
        reminder_time = now + timedelta(hours=24)  # 24 hours from now

        print(f"Checking tasks at {now} for reminder at {reminder_time}")

        # Find tasks where due_date is exactly 24 hours from now
        tasks = Task.query.filter(Task.dueDate <= reminder_time, Task.dueDate > now).all()

        print(f"Found {len(tasks)} tasks due in 24 hours.")

        for task in tasks:
            assigned_user = User.query.get(task.assignedTo)

            if assigned_user:
                #FIX: Check if task is not completed, cancelled or on hold
                if task.status != "Completed" and task.status != "Cancelled" and task.status != "On Hold":
                    # send_task_deadline_notification(assigned_user.email, task.name, task.description, task.dueDate)
                    send_task_deadline_notification(assigned_user.email, task)

                    print(f"Sent deadline notification to {assigned_user.email} for task {task.name}.")

        print(f"Checked tasks at {now}.")