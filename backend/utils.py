"""
Utility functions for Invoice Management System
"""
import os
import json
from datetime import datetime
import config


def generate_invoice_number():
    """Generate unique invoice number based on timestamp"""
    return f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def calculate_num_pieces(silver_weight, piece_size):
    """
    Calculate number of pieces based on total weight and piece size
    
    Args:
        silver_weight: Total silver weight in kg
        piece_size: Piece size name (e.g., "10 Tola", "500 g", "1 kg")
    
    Returns:
        Number of pieces (float)
    """
    piece_weight = config.PIECE_SIZES.get(piece_size, 1.0)
    return round(silver_weight / piece_weight, 2)


def calculate_total_amount(billing_mode, silver_weight, num_pieces, rate):
    """
    Calculate total amount based on billing mode
    
    Args:
        billing_mode: "Ready" or "Mazduri"
        silver_weight: Total silver weight in kg
        num_pieces: Number of pieces
        rate: Rate per kg (Ready mode) or per piece (Mazduri mode)
    
    Returns:
        Total amount (float)
    """
    if billing_mode == 'Ready':
        return round(silver_weight * rate, 2)
    elif billing_mode == 'Mazduri':
        return round(num_pieces * rate, 2)
    return 0.0


def calculate_remaining_balance(total_amount, advance_payment):
    """Calculate remaining balance after advance payment"""
    return round(total_amount - advance_payment, 2)


def create_customer_folder(customer_id):
    """
    Create folder structure for a customer
    
    Structure:
    /data/customers/{customer_id}/
        - invoices/
        - payments/
        - profile.json
    """
    customer_dir = os.path.join(config.CUSTOMERS_DIR, str(customer_id))
    invoices_dir = os.path.join(customer_dir, 'invoices')
    payments_dir = os.path.join(customer_dir, 'payments')
    
    os.makedirs(invoices_dir, exist_ok=True)
    os.makedirs(payments_dir, exist_ok=True)
    
    return customer_dir


def save_customer_profile(customer_id, customer_data):
    """Save customer profile as JSON"""
    customer_dir = create_customer_folder(customer_id)
    profile_path = os.path.join(customer_dir, 'profile.json')
    
    with open(profile_path, 'w') as f:
        json.dump(customer_data, f, indent=2)
    
    return profile_path


def get_invoice_pdf_path(customer_id, invoice_number):
    """Get the file path for saving invoice PDF"""
    customer_dir = create_customer_folder(customer_id)
    invoices_dir = os.path.join(customer_dir, 'invoices')
    return os.path.join(invoices_dir, f"{invoice_number}.pdf")


def validate_invoice_data(data):
    """
    Validate invoice creation data
    
    Returns:
        (is_valid, error_message)
    """
    required_fields = ['customer_name', 'contact', 'silver_weight', 'piece_size', 'billing_mode', 'rate']
    
    for field in required_fields:
        if field not in data or data[field] == '':
            return False, f"Missing required field: {field}"
    
    # Validate numeric fields
    try:
        silver_weight = float(data['silver_weight'])
        if silver_weight <= 0:
            return False, "Silver weight must be greater than 0"
    except ValueError:
        return False, "Invalid silver weight"
    
    try:
        rate = float(data['rate'])
        if rate <= 0:
            return False, "Rate must be greater than 0"
    except ValueError:
        return False, "Invalid rate"
    
    # Validate piece size
    if data['piece_size'] not in config.PIECE_SIZES:
        return False, "Invalid piece size"
    
    # Validate billing mode
    if data['billing_mode'] not in config.BILLING_MODES:
        return False, "Invalid billing mode"
    
    # Validate advance payment if provided
    if 'advance_payment' in data and data['advance_payment']:
        try:
            advance = float(data['advance_payment'])
            if advance < 0:
                return False, "Advance payment cannot be negative"
        except ValueError:
            return False, "Invalid advance payment"
    
    return True, None
