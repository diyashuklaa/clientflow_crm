from flask import Flask, render_template, redirect, url_for
from flask_login import login_required, current_user
from config import Config
from models import db, login_manager
from models.user import User
from models.customer import Customer
from models.activity import Activity
from datetime import datetime, date, timedelta

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from routes.auth_routes import auth_bp
    from routes.customer_routes import customer_bp
    from routes.activity_routes import activity_bp
    from routes.analytics_routes import analytics_bp
    from routes.admin_routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(activity_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    @login_required
    def index():
        return redirect(url_for('dashboard'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        today = date.today()
        next_week = today + timedelta(days=7)

        if current_user.role == 'sales_staff':
            total_customers = Customer.query.filter_by(assigned_to=current_user.id).count()
            won = Customer.query.filter_by(assigned_to=current_user.id, status='Won').count()
            active = Customer.query.filter(
                Customer.assigned_to == current_user.id,
                Customer.status.notin_(['Won', 'Lost'])
            ).count()
            customer_ids = [c.id for c in Customer.query.filter_by(assigned_to=current_user.id).all()]
            if customer_ids:
                base_q = Activity.query.filter(Activity.customer_id.in_(customer_ids))
            else:
                base_q = Activity.query.filter_by(id=-1)
        else:
            total_customers = Customer.query.count()
            won = Customer.query.filter_by(status='Won').count()
            active = Customer.query.filter(Customer.status.notin_(['Won', 'Lost'])).count()
            base_q = Activity.query
            customer_ids = []

        due_today = base_q.filter(
            db.func.date(Activity.next_followup) == today
        ).count()

        overdue = base_q.filter(
            Activity.next_followup < datetime.combine(today, datetime.min.time()),
            Activity.next_followup != None
        ).count()

        upcoming = base_q.filter(
            db.func.date(Activity.next_followup) > today,
            db.func.date(Activity.next_followup) <= next_week
        ).count()

        recent_customers = Customer.query
        if current_user.role == 'sales_staff':
            recent_customers = recent_customers.filter_by(assigned_to=current_user.id)
        recent_customers = recent_customers.order_by(Customer.created_at.desc()).limit(5).all()

        if current_user.role == 'sales_staff' and customer_ids:
            recent_activities = Activity.query.filter(
                Activity.customer_id.in_(customer_ids)
            ).order_by(Activity.created_at.desc()).limit(5).all()
        elif current_user.role != 'sales_staff':
            recent_activities = Activity.query.order_by(Activity.created_at.desc()).limit(5).all()
        else:
            recent_activities = []

        from utils.calculate_conversion import get_funnel_data
        funnel = get_funnel_data() if current_user.role != 'sales_staff' else {}
        now = datetime.utcnow()

        return render_template('dashboard.html',
            total_customers=total_customers,
            won=won,
            active=active,
            due_today=due_today,
            overdue=overdue,
            upcoming=upcoming,
            recent_customers=recent_customers,
            recent_activities=recent_activities,
            funnel=funnel,
            today=today,
            now=now
        )

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    if not User.query.filter_by(email='admin@clientflow.com').first():
        admin = User(name='Admin User', email='admin@clientflow.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)

        manager = User(name='Sales Manager', email='manager@clientflow.com', role='manager')
        manager.set_password('manager123')
        db.session.add(manager)

        staff = User(name='Sales Staff', email='staff@clientflow.com', role='sales_staff')
        staff.set_password('staff123')
        db.session.add(staff)
        db.session.commit()

        customers_data = [
            {'name': 'Rajesh Kumar',  'email': 'rajesh@example.com',  'phone': '9876543210', 'lead_source': 'Referral',      'status': 'Won',           'deal_value': 85000,  'assigned_to': staff.id},
            {'name': 'Priya Sharma',  'email': 'priya@example.com',   'phone': '9876543211', 'lead_source': 'Website',       'status': 'Negotiation',   'deal_value': 120000, 'assigned_to': staff.id},
            {'name': 'Amit Singh',    'email': 'amit@example.com',    'phone': '9876543212', 'lead_source': 'Cold Call',     'status': 'Proposal Sent', 'deal_value': 45000,  'assigned_to': manager.id},
            {'name': 'Sunita Patel',  'email': 'sunita@example.com',  'phone': '9876543213', 'lead_source': 'Social Media',  'status': 'Interested',    'deal_value': 30000,  'assigned_to': staff.id},
            {'name': 'Vikram Mehta',  'email': 'vikram@example.com',  'phone': '9876543214', 'lead_source': 'Website',       'status': 'Contacted',     'deal_value': 75000,  'assigned_to': manager.id},
            {'name': 'Neha Gupta',    'email': 'neha@example.com',    'phone': '9876543215', 'lead_source': 'Referral',      'status': 'Won',           'deal_value': 95000,  'assigned_to': manager.id},
            {'name': 'Arjun Verma',   'email': 'arjun@example.com',   'phone': '9876543216', 'lead_source': 'Email Campaign','status': 'Lost',          'deal_value': 20000,  'assigned_to': staff.id},
        ]
        for cd in customers_data:
            c = Customer(**cd)
            db.session.add(c)
        db.session.commit()

        from models.activity import Activity
        customers = Customer.query.all()
        for i, c in enumerate(customers[:4]):
            act = Activity(
                customer_id=c.id,
                created_by=staff.id,
                activity_type='Call',
                note=f'Initial discovery call with {c.name}. Discussed requirements.',
                outcome='Interested in moving forward.',
                next_followup=datetime.utcnow() + timedelta(days=i - 1)
            )
            db.session.add(act)
        db.session.commit()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
