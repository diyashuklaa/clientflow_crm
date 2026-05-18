from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.activity import Activity
from models.customer import Customer
from datetime import datetime, date, timedelta

activity_bp = Blueprint('activities', __name__)

ACTIVITY_TYPES = ['Call', 'Meeting', 'Follow-up', 'Quote Shared', 'Email', 'Note', 'Customer Response']

@activity_bp.route('/activities')
@login_required
def list_activities():
    today = date.today()
    next_week = today + timedelta(days=7)

    if current_user.role == 'sales_staff':
        customer_ids = [c.id for c in Customer.query.filter_by(assigned_to=current_user.id).all()]
        base_query = Activity.query.filter(Activity.customer_id.in_(customer_ids))
    else:
        base_query = Activity.query

    due_today = base_query.filter(
        db.func.date(Activity.next_followup) == today
    ).all()

    overdue = base_query.filter(
        Activity.next_followup < datetime.combine(today, datetime.min.time()),
        Activity.next_followup != None
    ).all()

    upcoming = base_query.filter(
        db.func.date(Activity.next_followup) > today,
        db.func.date(Activity.next_followup) <= next_week
    ).all()

    return render_template('followups.html',
        due_today=due_today,
        overdue=overdue,
        upcoming=upcoming,
        today=today
    )


@activity_bp.route('/customers/<int:customer_id>/activities/add', methods=['POST'])
@login_required
def add_activity(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    
    next_followup_str = request.form.get('next_followup')
    next_followup = None
    if next_followup_str:
        try:
            next_followup = datetime.strptime(next_followup_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            try:
                next_followup = datetime.strptime(next_followup_str, '%Y-%m-%d')
            except ValueError:
                pass

    activity = Activity(
        customer_id=customer_id,
        created_by=current_user.id,
        activity_type=request.form.get('activity_type'),
        note=request.form.get('note'),
        outcome=request.form.get('outcome'),
        next_followup=next_followup
    )
    db.session.add(activity)
    
    # Update customer updated_at
    customer.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash('Activity logged successfully!', 'success')
    return redirect(url_for('customers.customer_detail', customer_id=customer_id))


@activity_bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
@login_required
def delete_activity(activity_id):
    activity = Activity.query.get_or_404(activity_id)
    customer_id = activity.customer_id
    if current_user.role not in ['admin', 'manager'] and activity.created_by != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customers.customer_detail', customer_id=customer_id))
    db.session.delete(activity)
    db.session.commit()
    flash('Activity deleted.', 'success')
    return redirect(url_for('customers.customer_detail', customer_id=customer_id))
