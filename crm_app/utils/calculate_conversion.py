from models.customer import Customer
from models.user import User

def get_conversion_rate():
    """Conversion Rate = (Total Won / Total Leads) * 100"""
    total = Customer.query.count()
    won = Customer.query.filter_by(status='Won').count()
    if total == 0:
        return 0
    return round((won / total) * 100, 2)


def get_funnel_data():
    """Returns count per pipeline stage"""
    stages = ['Interested', 'Contacted', 'Proposal Sent', 'Negotiation', 'Won', 'Lost']
    data = {}
    for stage in stages:
        data[stage] = Customer.query.filter_by(status=stage).count()
    return data


def get_staff_performance():
    """Returns performance metrics per staff member"""
    staff = User.query.filter(User.role.in_(['sales_staff', 'manager'])).all()
    performance = []
    for user in staff:
        total_leads = Customer.query.filter_by(assigned_to=user.id).count()
        won_leads = Customer.query.filter_by(assigned_to=user.id, status='Won').count()
        conversion = round((won_leads / total_leads * 100), 2) if total_leads > 0 else 0
        total_revenue = sum(
            c.deal_value or 0
            for c in Customer.query.filter_by(assigned_to=user.id, status='Won').all()
        )
        performance.append({
            'name': user.name,
            'email': user.email,
            'total_leads': total_leads,
            'won_leads': won_leads,
            'conversion': conversion,
            'total_revenue': round(total_revenue, 2)
        })
    return performance
