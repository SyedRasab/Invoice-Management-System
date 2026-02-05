"""
Flask Application - Invoice Management System API
"""
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import os

# Import local modules
import config
from database import init_db, get_session
import audit_log
import reports
import auth  # New Auth module
from models import Customer, Invoice, PaymentTransaction, CompanySettings, AuditLog, User  # Added User
from utils import (
    generate_invoice_number,
    calculate_num_pieces,
    calculate_total_amount,
    calculate_remaining_balance,
    create_customer_folder,
    save_customer_profile,
    get_invoice_pdf_path,
    validate_invoice_data
)
from pdf_generator import generate_invoice_pdf
from excel_exporter import export_to_excel
from payment_manager import (
    add_payment,
    get_payment_history,
    update_invoice_status,
    delete_payment,
    get_customer_outstanding,
    validate_payment,
    PAYMENT_METHODS,
    INVOICE_STATUSES
)

# Initialize Flask app
# Serve static files from frontend directory
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = config.SECRET_KEY
CORS(app, supports_credentials=True)  # Enable CORS with credentials

# Initialize Auth
auth.init_app(app)

# Initialize database
init_db()

@app.route('/')
def serve_index():
    return send_file('../frontend/login.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_file(f'../frontend/{path}')

@app.route('/api/status')
def api_status():
    return jsonify({'status': 'running'})


# ==================== CUSTOMER ENDPOINTS ====================

@app.route('/api/customers', methods=['GET'])
def get_customers():
    """Get all customers"""
    session = get_session()
    try:
        customers = session.query(Customer).all()
        return jsonify([customer.to_dict() for customer in customers])
    finally:
        session.close()


@app.route('/api/customers/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get specific customer by ID"""
    session = get_session()
    try:
        customer = session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer_data = customer.to_dict()
        # Include invoices
        customer_data['invoices'] = [invoice.to_dict() for invoice in customer.invoices]
        
        return jsonify(customer_data)
    finally:
        session.close()


@app.route('/api/customers', methods=['POST'])
def create_customer():
    """Create new customer"""
    data = request.json
    
    if not data.get('name') or not data.get('contact'):
        return jsonify({'error': 'Name and contact are required'}), 400
    
    session = get_session()
    try:
        customer = Customer(
            name=data['name'],
            contact=data['contact']
        )
        session.add(customer)
        session.commit()
        
        # Create customer folder structure
        create_customer_folder(customer.id)
        save_customer_profile(customer.id, customer.to_dict())
        
        return jsonify(customer.to_dict()), 201
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ==================== INVOICE ENDPOINTS ====================

@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    """Get all invoices"""
    session = get_session()
    try:
        invoices = session.query(Invoice).all()
        return jsonify([invoice.to_dict() for invoice in invoices])
    finally:
        session.close()


@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
def get_invoice(invoice_id):
    """Get specific invoice by ID"""
    session = get_session()
    try:
        invoice = session.query(Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        return jsonify(invoice.to_dict())
    finally:
        session.close()


@app.route('/api/invoices', methods=['POST'])
def create_invoice():
    """Create new invoice"""
    data = request.json
    
    # Validate input data
    is_valid, error_msg = validate_invoice_data(data)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    session = get_session()
    try:
        # Check if customer exists or create new one
        customer = None
        if data.get('customer_id'):
            customer = session.query(Customer).filter_by(id=data['customer_id']).first()
        
        if not customer:
            # Create new customer
            customer = Customer(
                name=data['customer_name'],
                contact=data['contact']
            )
            session.add(customer)
            session.flush()  # Get customer ID
            
            # Create customer folder
            create_customer_folder(customer.id)
            save_customer_profile(customer.id, customer.to_dict())
        
        # Calculate values
        silver_weight = float(data['silver_weight'])
        piece_size = data['piece_size']
        billing_mode = data['billing_mode']
        rate = float(data['rate'])
        advance_payment = float(data.get('advance_payment', 0))
        
        num_pieces = calculate_num_pieces(silver_weight, piece_size)
        total_amount = calculate_total_amount(billing_mode, silver_weight, num_pieces, rate)
        remaining_balance = calculate_remaining_balance(total_amount, advance_payment)
        
        # Generate invoice number
        invoice_number = generate_invoice_number()
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=customer.id,
            silver_weight=silver_weight,
            piece_size=piece_size,
            num_pieces=num_pieces,
            billing_mode=billing_mode,
            rate=rate,
            total_amount=total_amount,
            advance_payment=advance_payment,
            remaining_balance=remaining_balance,
            status='Unpaid' if remaining_balance > 0 else 'Paid'
        )
        session.add(invoice)
        session.commit()
        
        # Create payment record if advance payment exists
        if advance_payment > 0:
            payment_method = data.get('payment_method', 'Cash')
            payment = PaymentTransaction(
                invoice_id=invoice.id,
                customer_id=customer.id,
                amount=advance_payment,
                payment_method=payment_method,
                notes='Advance payment'
            )
            session.add(payment)
            session.commit()
        
        # Generate PDF
        invoice_data = invoice.to_dict()
        invoice_data['date'] = invoice.date.strftime('%Y-%m-%d')
        pdf_path = get_invoice_pdf_path(customer.id, invoice_number)
        generate_invoice_pdf(invoice_data, pdf_path)
        
        return jsonify(invoice.to_dict()), 201
        
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/invoices/<int:invoice_id>/pdf', methods=['GET'])
def download_invoice_pdf(invoice_id):
    """Download invoice PDF"""
    session = get_session()
    try:
        invoice = session.query(Invoice).filter_by(id=invoice_id).first()
        if not invoice:
            return jsonify({'error': 'Invoice not found'}), 404
        
        pdf_path = get_invoice_pdf_path(invoice.customer_id, invoice.invoice_number)
        
        if not os.path.exists(pdf_path):
            # Generate PDF if it doesn't exist
            invoice_data = invoice.to_dict()
            invoice_data['date'] = invoice.date.strftime('%Y-%m-%d')
            generate_invoice_pdf(invoice_data, pdf_path)
        
        return send_file(
            pdf_path,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{invoice.invoice_number}.pdf"
        )
    finally:
        session.close()


# ==================== PAYMENT MANAGEMENT ENDPOINTS ====================

@app.route('/api/invoices/<int:invoice_id>/payments', methods=['POST'])
def add_invoice_payment(invoice_id):
    """Add payment to existing invoice"""
    data = request.json
    
    if not data.get('amount') or not data.get('payment_method'):
        return jsonify({'error': 'Amount and payment method are required'}), 400
    
    try:
        amount = float(data['amount'])
        payment_method = data['payment_method']
        notes = data.get('notes', '')
        created_by = data.get('created_by', 'System')
        
        success, message, payment_data = add_payment(
            invoice_id, amount, payment_method, notes, created_by
        )
        
        if success:
            return jsonify({
                'message': message,
                'payment': payment_data
            }), 201
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/invoices/<int:invoice_id>/payments', methods=['GET'])
def get_invoice_payments(invoice_id):
    """Get all payments for an invoice"""
    try:
        payments = get_payment_history(invoice_id)
        return jsonify(payments)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/invoices/<int:invoice_id>/status', methods=['PUT'])
def update_invoice_status_endpoint(invoice_id):
    """Update invoice status"""
    data = request.json
    
    if not data.get('status'):
        return jsonify({'error': 'Status is required'}), 400
    
    new_status = data['status']
    user = data.get('user', 'System')
    
    success, message = update_invoice_status(invoice_id, new_status, user)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400


@app.route('/api/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment_endpoint(payment_id):
    """Delete a payment (admin only)"""
    user = request.args.get('user', 'System')
    
    success, message = delete_payment(payment_id, user)
    
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 400


# ==================== ENHANCED CUSTOMER ENDPOINTS ====================

@app.route('/api/customers/<int:customer_id>/outstanding', methods=['GET'])
def get_customer_outstanding_balance(customer_id):
    """Get total outstanding balance for a customer"""
    try:
        outstanding = get_customer_outstanding(customer_id)
        return jsonify({'outstanding_balance': outstanding})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers/<int:customer_id>/notes', methods=['PUT'])
def update_customer_notes(customer_id):
    """Update customer notes"""
    data = request.json
    
    if 'notes' not in data:
        return jsonify({'error': 'Notes field is required'}), 400
    
    session = get_session()
    try:
        customer = session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        customer.notes = data['notes']
        session.commit()
        
        return jsonify({'message': 'Customer notes updated successfully'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


@app.route('/api/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update customer information"""
    data = request.json
    
    session = get_session()
    try:
        customer = session.query(Customer).filter_by(id=customer_id).first()
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        if 'name' in data:
            customer.name = data['name']
        if 'contact' in data:
            customer.contact = data['contact']
        if 'notes' in data:
            customer.notes = data['notes']
        
        session.commit()
        
        return jsonify({
            'message': 'Customer updated successfully',
            'customer': customer.to_dict()
        })
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()


# ==================== CALCULATION ENDPOINTS ====================

@app.route('/api/calculate/pieces', methods=['POST'])
def calculate_pieces():
    """Calculate number of pieces based on weight and size"""
    data = request.json
    
    try:
        silver_weight = float(data['silver_weight'])
        piece_size = data['piece_size']
        
        num_pieces = calculate_num_pieces(silver_weight, piece_size)
        
        return jsonify({'num_pieces': num_pieces})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/calculate/total', methods=['POST'])
def calculate_total():
    """Calculate total amount based on billing mode"""
    data = request.json
    
    try:
        billing_mode = data['billing_mode']
        silver_weight = float(data['silver_weight'])
        num_pieces = float(data['num_pieces'])
        rate = float(data['rate'])
        advance_payment = float(data.get('advance_payment', 0))
        
        total_amount = calculate_total_amount(billing_mode, silver_weight, num_pieces, rate)
        remaining_balance = calculate_remaining_balance(total_amount, advance_payment)
        
        return jsonify({
            'total_amount': total_amount,
            'remaining_balance': remaining_balance
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# ==================== EXPORT ENDPOINTS ====================

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Export all data to Excel"""
    session = get_session()
    try:
        # Get all data
        customers = session.query(Customer).all()
        invoices = session.query(Invoice).all()
        payments = session.query(PaymentTransaction).all()
        
        customers_data = [customer.to_dict() for customer in customers]
        invoices_data = [invoice.to_dict() for invoice in invoices]
        payments_data = [payment.to_dict() for payment in payments]
        
        # Generate Excel file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = os.path.join(config.DATA_DIR, f'export_{timestamp}.xlsx')
        export_to_excel(customers_data, invoices_data, payments_data, output_path)
        
        return send_file(
            output_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'invoice_data_{timestamp}.xlsx'
        )
    finally:
        session.close()


# ==================== CONFIGURATION ENDPOINTS ====================

@app.route('/api/config/piece-sizes', methods=['GET'])
def get_piece_sizes():
    """Get available piece sizes"""
    return jsonify(list(config.PIECE_SIZES.keys()))


@app.route('/api/config/billing-modes', methods=['GET'])
def get_billing_modes():
    """Get available billing modes"""
    return jsonify(config.BILLING_MODES)


@app.route('/api/config/payment-methods', methods=['GET'])
def get_payment_methods():
    """Get available payment methods"""
    return jsonify(PAYMENT_METHODS)


@app.route('/api/config/invoice-statuses', methods=['GET'])
def get_invoice_statuses():
    """Get available invoice statuses"""
    return jsonify(INVOICE_STATUSES)


if __name__ == '__main__':
    print("=" * 50)
    print("Invoice Management System - Backend Server")
    print("=" * 50)
    print(f"Server running at: http://{config.HOST}:{config.PORT}")
    print("API Documentation:")
    print("  - GET  /api/customers")
    print("  - POST /api/customers")
    print("  - GET  /api/customers/<id>")
    print("  - GET  /api/invoices")
    print("  - POST /api/invoices")
    print("  - GET  /api/invoices/<id>")
    print("  - GET  /api/invoices/<id>/pdf")
    print("  - GET  /api/export/excel")
    print("  - POST /api/calculate/pieces")
    print("  - POST /api/calculate/total")
    print("=" * 50)
    
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
