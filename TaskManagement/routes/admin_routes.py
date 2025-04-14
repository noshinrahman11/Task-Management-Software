from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from TaskManagement.models import User
from TaskManagement.database import db_sessions
from TaskManagement.email_notif import send_role_notification

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/admin/admin', methods=['GET', 'POST'])
@login_required
def admin():

    # Show all users in the database
    users = User.query.all()
    
    return render_template('admin.html', users=users)

@admin_bp.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    user = User.query.get(user_id)
    if request.method == 'POST':
        previous_role = user.Role
        user.Role = request.form['Role']

        db_sessions.commit()

        print(f"User Role updated to from {previous_role} to {user.Role} successfully.")
        flash('User updated successfully!', category='success')

        # Send email notification if role is changed
        if user and user.email:
            if user.Role != previous_role:
                send_role_notification(user, previous_role, user.email) 

        return redirect(url_for('admin.admin'))