from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user
from models import db
from models.customer import Customer
from models.user import User
from models.activity import Activity
from datetime import datetime
import csv
import io

customer_bp = Blueprint('customers', __name__)

STATUSES = ['Interested', 'Contacted', 'Proposal Sent', 'Negotiation', 'Won', 'Lost']
LEAD_SOURCES = ['Website', 'Referral', 'Social Media', 'Cold Call', 'Email Campaign', 'Trade Show', 'Other']

@customer_bp.route('/customers')
@login_required
def list_customers():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    source_filter = request.args.get('source', '')

    query = Customer.query
    if current_user.role == 'sales_staff':
        query = query.filter_by(assigned_to=current_user.id)
    
    if search:
        query = query.filter(
            (Customer.name.ilike(f'%{search}%')) |
            (Customer.email.ilike(f'%{search}%')) |
            (Customer.phone.ilike(f'%{search}%'))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if source_filter:
        query = query.filter_by(lead_source=source_filter)

    customers = query.order_by(Customer.created_at.desc()).all()
    staff = User.query.filter(User.role.in_(['sales_staff', 'manager'])).all()
    
    return render_template('customers.html',
        customers=customers,
        statuses=STATUSES,
        lead_sources=LEAD_SOURCES,
        staff=staff,
        search=search,
        status_filter=status_filter,
        source_filter=source_filter
    )


@customer_bp.route('/customers/add', methods=['GET', 'POST'])
@login_required
def add_customer():
    staff = User.query.filter(User.role.in_(['sales_staff', 'manager'])).all()
    
    if request.method == 'POST':
        customer = Customer(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            requirement=request.form.get('requirement'),
            lead_source=request.form.get('lead_source'),
            status=request.form.get('status', 'Interested'),
            assigned_to=request.form.get('assigned_to') or current_user.id,
            deal_value=float(request.form.get('deal_value') or 0)
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers.customer_detail', customer_id=customer.id))
    
    return render_template('add_customer.html', statuses=STATUSES, lead_sources=LEAD_SOURCES, staff=staff)


@customer_bp.route('/customers/<int:customer_id>')
@login_required
def customer_detail(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if current_user.role == 'sales_staff' and customer.assigned_to != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customers.list_customers'))
    
    activities = Activity.query.filter_by(customer_id=customer_id).order_by(Activity.created_at.desc()).all()
    staff = User.query.filter(User.role.in_(['sales_staff', 'manager'])).all()
    return render_template('customer_detail.html',
        customer=customer,
        activities=activities,
        statuses=STATUSES,
        lead_sources=LEAD_SOURCES,
        staff=staff
    )


@customer_bp.route('/customers/<int:customer_id>/edit', methods=['POST'])
@login_required
def edit_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    if current_user.role == 'sales_staff' and customer.assigned_to != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('customers.list_customers'))
    
    customer.name = request.form.get('name')
    customer.email = request.form.get('email')
    customer.phone = request.form.get('phone')
    customer.address = request.form.get('address')
    customer.requirement = request.form.get('requirement')
    customer.lead_source = request.form.get('lead_source')
    customer.status = request.form.get('status')
    customer.deal_value = float(request.form.get('deal_value') or 0)
    if current_user.role in ['admin', 'manager']:
        customer.assigned_to = request.form.get('assigned_to') or customer.assigned_to
    customer.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Customer updated successfully!', 'success')
    return redirect(url_for('customers.customer_detail', customer_id=customer_id))


@customer_bp.route('/customers/<int:customer_id>/delete', methods=['POST'])
@login_required
def delete_customer(customer_id):
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied.', 'danger')
        return redirect(url_for('customers.list_customers'))
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    flash('Customer deleted.', 'success')
    return redirect(url_for('customers.list_customers'))


@customer_bp.route('/customers/export')
@login_required
def export_customers():
    if current_user.role not in ['admin', 'manager']:
        flash('Access denied.', 'danger')
        return redirect(url_for('customers.list_customers'))
    
    customers = Customer.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Name', 'Email', 'Phone', 'Address', 'Requirement',
                     'Lead Source', 'Status', 'Deal Value', 'Assigned To', 'Created At'])
    
    for c in customers:
        assigned = User.query.get(c.assigned_to)
        writer.writerow([
            c.id, c.name, c.email, c.phone, c.address, c.requirement,
            c.lead_source, c.status, c.deal_value,
            assigned.name if assigned else 'Unassigned',
            c.created_at.strftime('%Y-%m-%d %H:%M') if c.created_at else ''
        ])
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment;filename=customers.csv'}
    )
