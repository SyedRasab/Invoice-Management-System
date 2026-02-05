"""
Payment Management Module
Handles payment processing, status updates, and validation
"""
import json
from datetime import datetime
from models import PaymentTransaction, Invoice, AuditLog
from database import get_session


# Payment methods
PAYMENT_METHODS = ['Cash', 'Bank Transfer', 'Cheque', 'Mobile Wallet']

# Invoice statuses
INVOICE_STATUSES = ['Draft', 'Unpaid', 'Partially Paid', 'Paid', 'Cancelled']


def add_payment(invoice_id, amount, payment_method, notes=None, created_by='System'):
    """
    Add a payment to an existing invoice
    
    Args:
        invoice_id: ID of the invoice
        amount: Payment amount
        payment_method: Method of payment
        notes: Optional payment notes
        created_by: User who created the payment
    
    Returns:
        (success, message, payment_data)
    """
    session = get_session()
    
    try:
        # Get invoice
        invoice = session.query(Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return False, "Invoice not found", None
        
        # Validate invoice status
        if invoice.status == 'Cancelled':
            return False, "Cannot add payment to cancelled invoice", None
        
        if invoice.status == 'Paid':
            return False, "Invoice is already fully paid", None
        
        # Validate payment amount
        if amount <= 0:
            return False, "Payment amount must be greater than 0", None
        
        if amount > invoice.remaining_balance:
            return False, f"Payment amount (${amount:,.2f}) exceeds remaining balance (${invoice.remaining_balance:,.2f})", None
        
        # Validate payment method
        if payment_method not in PAYMENT_METHODS:
            return False, f"Invalid payment method. Must be one of: {', '.join(PAYMENT_METHODS)}", None
        
        # Create payment transaction
        payment = PaymentTransaction(
            invoice_id=invoice_id,
            customer_id=invoice.customer_id,
            amount=amount,
            payment_method=payment_method,
            notes=notes,
            created_by=created_by
        )
        session.add(payment)
        session.flush()  # Generate ID for audit log
        
        # Update invoice balance and status
        invoice.remaining_balance -= amount
        invoice.status = calculate_invoice_status(invoice)
        
        # Create audit log
        log_payment(session, created_by, 'payment_added', invoice, payment)
        
        session.commit()
        
        return True, "Payment added successfully", payment.to_dict()
        
    except Exception as e:
        session.rollback()
        return False, f"Error adding payment: {str(e)}", None
    finally:
        session.close()


def get_payment_history(invoice_id):
    """
    Get all payments for an invoice
    
    Args:
        invoice_id: ID of the invoice
    
    Returns:
        List of payment dictionaries
    """
    session = get_session()
    
    try:
        payments = session.query(PaymentTransaction).filter_by(invoice_id=invoice_id).order_by(PaymentTransaction.payment_date.desc()).all()
        return [payment.to_dict() for payment in payments]
    finally:
        session.close()


def calculate_invoice_status(invoice):
    """
    Calculate invoice status based on payments
    
    Args:
        invoice: Invoice object
    
    Returns:
        Status string
    """
    if invoice.status == 'Cancelled':
        return 'Cancelled'
    
    if invoice.status == 'Draft':
        return 'Draft'
    
    if invoice.remaining_balance <= 0:
        return 'Paid'
    elif invoice.remaining_balance < invoice.total_amount:
        return 'Partially Paid'
    else:
        return 'Unpaid'


def update_invoice_status(invoice_id, new_status, user='System'):
    """
    Update invoice status manually
    
    Args:
        invoice_id: ID of the invoice
        new_status: New status
        user: User making the change
    
    Returns:
        (success, message)
    """
    session = get_session()
    
    try:
        invoice = session.query(Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return False, "Invoice not found"
        
        if new_status not in INVOICE_STATUSES:
            return False, f"Invalid status. Must be one of: {', '.join(INVOICE_STATUSES)}"
        
        old_status = invoice.status
        invoice.status = new_status
        
        # Log the change
        log_entry = AuditLog(
            user=user,
            action='status_changed',
            entity_type='invoice',
            entity_id=invoice_id,
            details=json.dumps({'old_status': old_status, 'new_status': new_status})
        )
        session.add(log_entry)
        
        session.commit()
        return True, f"Invoice status updated to {new_status}"
        
    except Exception as e:
        session.rollback()
        return False, f"Error updating status: {str(e)}"
    finally:
        session.close()


def delete_payment(payment_id, user='System'):
    """
    Delete a payment (admin only)
    
    Args:
        payment_id: ID of the payment to delete
        user: User deleting the payment
    
    Returns:
        (success, message)
    """
    session = get_session()
    
    try:
        payment = session.query(PaymentTransaction).filter_by(id=payment_id).first()
        if not payment:
            return False, "Payment not found"
        
        invoice = payment.invoice
        
        # Restore balance
        invoice.remaining_balance += payment.amount
        
        # Log deletion
        log_entry = AuditLog(
            user=user,
            action='payment_deleted',
            entity_type='payment',
            entity_id=payment_id,
            details=json.dumps({
                'invoice_id': invoice.id,
                'amount': payment.amount,
                'payment_method': payment.payment_method
            })
        )
        session.add(log_entry)
        
        # Delete payment
        session.delete(payment)
        
        # Recalculate status
        invoice.status = calculate_invoice_status(invoice)
        
        session.commit()
        return True, "Payment deleted successfully"
        
    except Exception as e:
        session.rollback()
        return False, f"Error deleting payment: {str(e)}"
    finally:
        session.close()


def log_payment(session, user, action, invoice, payment):
    """
    Create audit log entry for payment action
    
    Args:
        session: Database session
        user: User performing action
        action: Action type
        invoice: Invoice object
        payment: Payment object
    """
    details = {
        'invoice_number': invoice.invoice_number,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
        'new_balance': invoice.remaining_balance,
        'new_status': invoice.status
    }
    
    log_entry = AuditLog(
        user=user,
        action=action,
        entity_type='payment',
        entity_id=payment.id,
        details=json.dumps(details)
    )
    session.add(log_entry)


def get_customer_outstanding(customer_id):
    """
    Get total outstanding balance for a customer
    
    Args:
        customer_id: ID of the customer
    
    Returns:
        Total outstanding amount
    """
    session = get_session()
    
    try:
        invoices = session.query(Invoice).filter_by(customer_id=customer_id).filter(Invoice.status != 'Cancelled').all()
        total = sum(inv.remaining_balance for inv in invoices)
        return total
    finally:
        session.close()


def validate_payment(invoice_id, amount):
    """
    Validate if a payment can be made
    
    Args:
        invoice_id: ID of the invoice
        amount: Payment amount
    
    Returns:
        (is_valid, message)
    """
    session = get_session()
    
    try:
        invoice = session.query(Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return False, "Invoice not found"
        
        if invoice.status == 'Cancelled':
            return False, "Cannot add payment to cancelled invoice"
        
        if invoice.status == 'Paid':
            return False, "Invoice is already fully paid"
        
        if amount <= 0:
            return False, "Payment amount must be greater than 0"
        
        if amount > invoice.remaining_balance:
            return False, f"Payment amount exceeds remaining balance of ${invoice.remaining_balance:,.2f}"
        
        return True, "Payment is valid"
        
    finally:
        session.close()
