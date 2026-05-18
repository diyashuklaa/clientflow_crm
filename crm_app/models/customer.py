from models import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    requirement = db.Column(db.Text)
    lead_source = db.Column(db.String(50))  # Website, Referral, Social, Cold Call, etc.
    status = db.Column(db.String(30), default='Interested')  # Interested, Contacted, Proposal Sent, Negotiation, Won, Lost
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    deal_value = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    activities = db.relationship('Activity', backref='customer', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Customer {self.name}>'
