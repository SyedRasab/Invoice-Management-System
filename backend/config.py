"""
Configuration settings for Invoice Management System
"""
import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'invoice_system.db')

# Data storage
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
CUSTOMERS_DIR = os.path.join(DATA_DIR, 'customers')

# Company Information (for invoices)
COMPANY_INFO = {
    'name': 'Silver Trading Co.',
    'address': '123 Business Street, City, Country',
    'phone': '+1 234 567 8900',
    'email': 'info@silvertrading.com',
    'website': 'www.silvertrading.com'
}

# Piece Size Options (in kg)
PIECE_SIZES = {
    '10 Tola': 0.1165,  # 10 Tola = 116.5 grams = 0.1165 kg
    '500 g': 0.5,
    '1 kg': 1.0
}

# Billing Modes
BILLING_MODES = ['Ready', 'Mazduri']

# Payment Methods
PAYMENT_METHODS = ['Cash', 'Bank Transfer', 'Cheque', 'Mobile Wallet']

# Invoice Statuses
INVOICE_STATUSES = ['Draft', 'Unpaid', 'Partially Paid', 'Paid', 'Cancelled']

# Flask settings
# Flask settings
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = False
HOST = '0.0.0.0'
PORT = 5000

# Create necessary directories
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CUSTOMERS_DIR, exist_ok=True)
