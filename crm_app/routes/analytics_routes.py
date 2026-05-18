from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.calculate_clv import get_total_clv, get_avg_deal_value
from utils.calculate_conversion import get_conversion_rate, get_funnel_data, get_staff_performance
from utils.segmentation import segment_customers
from utils.forecasting import get_forecast
from models.customer import Customer

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    if current_user.role == 'sales_staff':
        # Limited analytics for staff
        my_customers = Customer.query.filter_by(assigned_to=current_user.id)
        total = my_customers.count()
        won = my_customers.filter_by(status='Won').count()
        conversion = round((won / total * 100), 2) if total > 0 else 0
        return render_template('analytics.html',
            limited=True,
            total=total,
            won=won,
            conversion=conversion
        )

    total_clv = get_total_clv()
    avg_deal = get_avg_deal_value()
    conversion_rate = get_conversion_rate()
    funnel_data = get_funnel_data()
    staff_performance = get_staff_performance()
    segments = segment_customers()
    forecast = get_forecast()

    total_customers = Customer.query.count()
    won_count = Customer.query.filter_by(status='Won').count()
    lost_count = Customer.query.filter_by(status='Lost').count()

    return render_template('analytics.html',
        limited=False,
        total_clv=total_clv,
        avg_deal=avg_deal,
        conversion_rate=conversion_rate,
        funnel_data=funnel_data,
        staff_performance=staff_performance,
        segments=segments,
        forecast=forecast,
        total_customers=total_customers,
        won_count=won_count,
        lost_count=lost_count
    )
