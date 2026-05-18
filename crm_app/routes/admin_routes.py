from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.customer import Customer
from utils.auth_middleware import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    users = User.query.all()
    return render_template('admin_users.html', users=users)


@admin_bp.route('/admin/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    role = request.form.get('role', 'sales_staff')

    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin.manage_users'))

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash(f'User {name} created successfully!', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/users/<int:user_id>/edit', methods=['POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.name = request.form.get('name')
    user.email = request.form.get('email')
    user.role = request.form.get('role')
    user.is_active = request.form.get('is_active') == 'on'
    
    new_password = request.form.get('password')
    if new_password:
        user.set_password(new_password)
    
    db.session.commit()
    flash('User updated successfully!', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash("You can't delete yourself.", 'danger')
        return redirect(url_for('admin.manage_users'))
    user = User.query.get_or_404(user_id)
    # Unassign customers
    Customer.query.filter_by(assigned_to=user_id).update({'assigned_to': None})
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'success')
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/admin/assign', methods=['POST'])
@login_required
@admin_required
def assign_lead():
    customer_id = request.form.get('customer_id')
    user_id = request.form.get('user_id')
    customer = Customer.query.get_or_404(customer_id)
    customer.assigned_to = user_id
    db.session.commit()
    flash('Lead assigned successfully!', 'success')
    return redirect(url_for('customers.customer_detail', customer_id=customer_id))
