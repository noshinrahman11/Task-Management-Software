from flask_mail import Message
from flask import current_app
from __init__ import mail

def send_email(subject, recipients, body, html=None):
    with current_app.app_context():
        msg = Message(subject, recipients=recipients, body=body, html=html)
        mail.send(msg)


def send_task_notification(task, recipient_email):
    subject = f"New Task Assigned: {task.name}"
    body = f"""
    Hello,

    You have been assigned a new task:

    Task: {task.name}
    Description: {task.description}
    Due Date: {task.dueDate.strftime('%Y-%m-%d %H:%M')}

    Please check your dashboard for more details.

    Regards,
    Task Management System
    """
    send_email(subject, [recipient_email], body)