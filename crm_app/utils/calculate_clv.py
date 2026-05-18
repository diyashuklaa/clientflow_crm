from models.customer import Customer
from models.activity import Activity
from models import db

def calculate_clv(customer_id=None):
    """
    CLV = Avg Deal Value × Number of Won Deals
    Returns dict of customer_id -> CLV or single CLV value
    """
    if customer_id:
        customer = Customer.query.get(customer_id)
        if not customer:
            return 0
        deal_value = customer.deal_value or 0
        # Count won activities (repeat orders)
        won_count = Customer.query.filter_by(id=customer_id, status='Won').count()
        return round(deal_value * max(won_count, 1), 2)
    
    # Calculate for all customers
    customers = Customer.query.all()
    clv_data = {}
    for c in customers:
        deal_value = c.deal_value or 0
        clv_data[c.id] = round(deal_value, 2)
    return clv_data


def get_total_clv():
    """Sum of all won customer deal values"""
    won_customers = Customer.query.filter_by(status='Won').all()
    return round(sum(c.deal_value or 0 for c in won_customers), 2)


def get_avg_deal_value():
    customers = Customer.query.filter(Customer.deal_value > 0).all()
    if not customers:
        return 0
    return round(sum(c.deal_value for c in customers) / len(customers), 2)
