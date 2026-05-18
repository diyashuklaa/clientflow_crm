from models.customer import Customer
from datetime import datetime, timedelta

def segment_customers():
    """
    Segments:
    - High Value: deal_value > 50000
    - Frequent Buyers: status = Won
    - New Customers: created within last 30 days
    - Inactive: no activity in 60+ days and not won/lost
    """
    now = datetime.utcnow()
    thirty_days_ago = now - timedelta(days=30)
    sixty_days_ago = now - timedelta(days=60)

    high_value = Customer.query.filter(Customer.deal_value >= 50000).all()
    frequent_buyers = Customer.query.filter_by(status='Won').all()
    new_customers = Customer.query.filter(Customer.created_at >= thirty_days_ago).all()
    inactive = Customer.query.filter(
        Customer.updated_at <= sixty_days_ago,
        Customer.status.notin_(['Won', 'Lost'])
    ).all()

    def to_dict(customers):
        return [{'id': c.id, 'name': c.name, 'status': c.status, 'deal_value': c.deal_value} for c in customers]

    return {
        'high_value': to_dict(high_value),
        'frequent_buyers': to_dict(frequent_buyers),
        'new_customers': to_dict(new_customers),
        'inactive': to_dict(inactive)
    }
