from database import get_session
from models import Invoice, PaymentTransaction
from sqlalchemy import func
from datetime import datetime

def get_monthly_revenue(year):
    """Get revenue by month for a given year"""
    session = get_session()
    try:
        # This is a simplified version. Real version would group by month.
        # For SQLite, date manipulation in SQL is tricky, better to fetch and process or use specific func.
        invoices = session.query(Invoice).filter(func.strftime('%Y', Invoice.date) == str(year)).all()
        
        revenue = {}
        for inv in invoices:
            month = inv.date.strftime('%B')
            if month not in revenue:
                revenue[month] = 0
            revenue[month] += (inv.total_amount - inv.remaining_balance)
            
        return revenue
    finally:
        session.close()

def get_payment_summary():
    """Get updated summary of payments"""
    session = get_session()
    try:
        total_paid = session.query(func.sum(PaymentTransaction.amount)).scalar() or 0
        total_invoiced = session.query(func.sum(Invoice.total_amount)).scalar() or 0
        
        return {
            'total_invoices': total_invoiced,
            'total_paid': total_paid,
            'outstanding': total_invoiced - total_paid
        }
    finally:
        session.close()
