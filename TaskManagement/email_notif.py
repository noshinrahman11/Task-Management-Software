from flask_mail import Message
from flask import current_app
from TaskManagement.__init__ import mail
from datetime import datetime, timedelta
from TaskManagement.models import Task, User

# Admin password = "@dminPassword1"
# User# password = P@ssword#

# email = 'taskmanagementsystemcs264@gmail.com'
# password = taskGroup7


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

    You have been assigned a new task.

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

def send_registration_notification(user, recipient_email):
    subject = f"Welcome to Task Management System!"
    body = f"""
    Hi {user.FirstName}! 
    
    Thanks for registering for Task Management System!
    
    See your registration info below. 

    Username: {user.username}
    Email: {user.email}
    Role: {user.Role}

    Sincerely,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def send_password_reset_notification(user, recipient_email, password_reset_code):
    subject = f"Password Reset Request"
    body = f"""
    Hello {user.FirstName},

    A password reset request has been made for the following account:

    To reset your password, please enter the following code: {password_reset_code}

    If you did not request this, please ignore this email.

    Sincerely,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def send_password_reset_success_notification(user, recipient_email):
    subject = f"Password Reset Successful"
    body = f"""
    Hello {user.FirstName},

    Your password has been successfully reset.

    If you did not initiate this change, please contact support immediately.

    Sincerely,
    Task Management System
    """
    send_email(subject, [recipient_email], body)

def send_calendar_sync_notification(user, task):
    subject = f"Task Synced to Calendar"
    body = f"""
    Hello {user.FirstName},

    The following task has been synced to your Google Calendar:

    Task: {task.name}
    Description: {task.description}
    Due Date: {task.dueDate.strftime('%Y-%m-%d %H:%M')}

    Regards,
    Task Management System
    """
    send_email(subject, [user.email], body)  # Send email notification

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