from models.customer import Customer
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

def get_monthly_revenue_data():
    """Get past 6 months of revenue from Won customers"""
    now = datetime.utcnow()
    monthly = defaultdict(float)

    for i in range(6):
        month_date = now - timedelta(days=30 * i)
        key = month_date.strftime('%Y-%m')
        monthly[key] = 0.0

    won_customers = Customer.query.filter_by(status='Won').all()
    for c in won_customers:
        if c.updated_at:
            key = c.updated_at.strftime('%Y-%m')
            monthly[key] += (c.deal_value or 0)

    sorted_monthly = dict(sorted(monthly.items()))
    return sorted_monthly


def simple_moving_average_forecast(data, window=3):
    """Simple moving average forecast"""
    values = list(data.values())
    if len(values) < window:
        return round(sum(values) / max(len(values), 1), 2)
    return round(sum(values[-window:]) / window, 2)


def get_forecast():
    """Returns forecast for next month"""
    monthly_data = get_monthly_revenue_data()
    
    if not monthly_data:
        return {
            'next_month': get_next_month_label(),
            'predicted_revenue': 0,
            'predicted_sales': 0,
            'conversion_probability': 0,
            'monthly_labels': [],
            'monthly_values': []
        }

    predicted_revenue = simple_moving_average_forecast(monthly_data, window=3)

    # Count monthly deals
    monthly_counts = defaultdict(int)
    won_customers = Customer.query.filter_by(status='Won').all()
    for c in won_customers:
        if c.updated_at:
            key = c.updated_at.strftime('%Y-%m')
            monthly_counts[key] += 1

    total_leads = Customer.query.count()
    total_won = Customer.query.filter_by(status='Won').count()
    conversion_prob = round((total_won / total_leads * 100), 1) if total_leads > 0 else 0

    count_values = [monthly_counts.get(k, 0) for k in monthly_data.keys()]
    window = min(3, len(count_values))
    predicted_sales = round(sum(count_values[-window:]) / max(window, 1)) if count_values else 0

    return {
        'next_month': get_next_month_label(),
        'predicted_revenue': predicted_revenue,
        'predicted_sales': predicted_sales,
        'conversion_probability': conversion_prob,
        'monthly_labels': list(monthly_data.keys()),
        'monthly_values': list(monthly_data.values())
    }


def get_next_month_label():
    now = datetime.utcnow()
    if now.month == 12:
        return f"{now.year + 1}-01"
    return f"{now.year}-{now.month + 1:02d}"
