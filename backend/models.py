"""
Database models for Invoice Management System
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    """Customer model"""
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    contact = Column(String(50), nullable=False)
    created_date = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)  # Customer notes
    last_invoice_date = Column(DateTime, nullable=True)
    
    # Relationships
    invoices = relationship('Invoice', back_populates='customer', cascade='all, delete-orphan')
    payments = relationship('PaymentTransaction', back_populates='customer', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'contact': self.contact,
            'created_date': self.created_date.isoformat() if self.created_date else None,
            'notes': self.notes,
            'total_invoices': len(self.invoices) if self.invoices else 0,
            'total_outstanding': self.get_total_outstanding()
        }
    
    def get_total_outstanding(self):
        """Calculate total outstanding balance across all invoices"""
        if not self.invoices:
            return 0.0
        return sum(inv.remaining_balance for inv in self.invoices if inv.status != 'Cancelled')


class Invoice(Base):
    """Invoice model"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True)
    invoice_number = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    date = Column(DateTime, default=datetime.now)
    
    # Silver details
    silver_weight = Column(Float, nullable=False)  # in kg
    piece_size = Column(String(20), nullable=False)  # "10 Tola", "500 g", "1 kg"
    num_pieces = Column(Float, nullable=False)
    
    # Billing details
    billing_mode = Column(String(20), nullable=False)  # "Ready" or "Mazduri"
    rate = Column(Float, nullable=False)  # Rate per kg (Ready) or per piece (Mazduri)
    total_amount = Column(Float, nullable=False)
    
    # Payment details
    advance_payment = Column(Float, default=0.0)
    remaining_balance = Column(Float, nullable=False)
    
    # Status and metadata
    status = Column(String(20), default='Unpaid')  # Draft, Unpaid, Partially Paid, Paid, Cancelled
    notes = Column(Text, nullable=True)
    tax_amount = Column(Float, default=0.0)
    created_by = Column(String(100), nullable=True)
    
    # Relationships
    customer = relationship('Customer', back_populates='invoices')
    payments = relationship('PaymentTransaction', back_populates='invoice', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'customer_contact': self.customer.contact if self.customer else None,
            'date': self.date.isoformat() if self.date else None,
            'silver_weight': self.silver_weight,
            'piece_size': self.piece_size,
            'num_pieces': self.num_pieces,
            'billing_mode': self.billing_mode,
            'rate': self.rate,
            'total_amount': self.total_amount,
            'advance_payment': self.advance_payment,
            'remaining_balance': self.remaining_balance,
            'status': self.status,
            'notes': self.notes,
            'tax_amount': self.tax_amount,
            'is_editable': self.is_editable()
        }
    
    def is_editable(self):
        """Check if invoice can be edited (only if no payments made beyond advance)"""
        if self.status == 'Cancelled':
            return False
        # Can edit if only advance payment exists (no additional payments)
        return len(self.payments) <= 1 if self.payments else True


class PaymentTransaction(Base):
    """Payment Transaction model - tracks all payments"""
    __tablename__ = 'payment_transactions'
    
    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey('invoices.id'), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False)  # Cash, Bank Transfer, Cheque, Mobile Wallet
    payment_date = Column(DateTime, default=datetime.now)
    notes = Column(Text, nullable=True)
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    invoice = relationship('Invoice', back_populates='payments')
    customer = relationship('Customer', back_populates='payments')
    
    def to_dict(self):
        return {
            'id': self.id,
            'invoice_id': self.invoice_id,
            'invoice_number': self.invoice.invoice_number if self.invoice else None,
            'customer_id': self.customer_id,
            'customer_name': self.customer.name if self.customer else None,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date.isoformat() if self.payment_date else None,
            'notes': self.notes,
            'created_by': self.created_by
        }


class CompanySettings(Base):
    """Company Settings model"""
    __tablename__ = 'company_settings'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(200), default='Silver Trading Co.')
    logo_path = Column(String(500), nullable=True)
    address = Column(Text, nullable=True)
    phone = Column(String(50), nullable=True)
    email = Column(String(100), nullable=True)
    website = Column(String(200), nullable=True)
    
    # Currency settings
    currency_symbol = Column(String(10), default='PKR')
    currency_code = Column(String(10), default='PKR')
    
    # Unit settings
    weight_unit = Column(String(20), default='kg')
    
    # Tax settings
    tax_enabled = Column(Boolean, default=False)
    tax_rate = Column(Float, default=0.0)
    tax_label = Column(String(50), default='VAT')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'logo_path': self.logo_path,
            'address': self.address,
            'phone': self.phone,
            'email': self.email,
            'website': self.website,
            'currency_symbol': self.currency_symbol,
            'currency_code': self.currency_code,
            'weight_unit': self.weight_unit,
            'tax_enabled': self.tax_enabled,
            'tax_rate': self.tax_rate,
            'tax_label': self.tax_label
        }


class AuditLog(Base):
    """Audit Log model for tracking all actions"""
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    user = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)  # created, updated, deleted, payment_added
    entity_type = Column(String(50), nullable=False)  # invoice, customer, payment
    entity_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    details = Column(Text, nullable=True)  # JSON string with additional details
    
    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'details': self.details
        }


class User(Base):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default='Operator')  # Admin, Operator, Accountant
    email = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'email': self.email,
            'is_active': self.is_active
        }
