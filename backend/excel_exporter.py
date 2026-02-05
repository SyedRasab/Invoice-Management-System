"""
Excel Export Functionality
"""
import pandas as pd
from datetime import datetime
import config


def export_to_excel(customers_data, invoices_data, payments_data, output_path):
    """
    Export all data to Excel with multiple sheets
    
    Args:
        customers_data: List of customer dictionaries
        invoices_data: List of invoice dictionaries
        payments_data: List of payment dictionaries
        output_path: Path where Excel file should be saved
    
    Returns:
        Path to generated Excel file
    """
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: Customers
        if customers_data:
            customers_df = pd.DataFrame(customers_data)
            # Reorder columns for better readability
            customer_columns = ['id', 'name', 'contact', 'created_date', 'total_invoices']
            customers_df = customers_df[[col for col in customer_columns if col in customers_df.columns]]
            customers_df.to_excel(writer, sheet_name='Customers', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Customers']
            for idx, col in enumerate(customers_df.columns):
                max_length = max(
                    customers_df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        # Sheet 2: Invoices
        if invoices_data:
            invoices_df = pd.DataFrame(invoices_data)
            # Reorder columns for better readability
            invoice_columns = [
                'id', 'invoice_number', 'customer_name', 'customer_contact', 'date',
                'silver_weight', 'piece_size', 'num_pieces', 'billing_mode', 'rate',
                'total_amount', 'advance_payment', 'remaining_balance'
            ]
            invoices_df = invoices_df[[col for col in invoice_columns if col in invoices_df.columns]]
            invoices_df.to_excel(writer, sheet_name='Invoices', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Invoices']
            for idx, col in enumerate(invoices_df.columns):
                max_length = max(
                    invoices_df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
        
        # Sheet 3: Payments
        if payments_data:
            payments_df = pd.DataFrame(payments_data)
            # Reorder columns for better readability
            payment_columns = ['id', 'invoice_id', 'customer_id', 'amount', 'payment_date']
            payments_df = payments_df[[col for col in payment_columns if col in payments_df.columns]]
            payments_df.to_excel(writer, sheet_name='Payments', index=False)
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Payments']
            for idx, col in enumerate(payments_df.columns):
                max_length = max(
                    payments_df[col].astype(str).apply(len).max(),
                    len(col)
                ) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
    
    return output_path


if __name__ == '__main__':
    # Test Excel export
    test_customers = [
        {'id': 1, 'name': 'Customer 1', 'contact': '1234567890', 'created_date': '2026-01-01', 'total_invoices': 2},
        {'id': 2, 'name': 'Customer 2', 'contact': '0987654321', 'created_date': '2026-01-15', 'total_invoices': 1},
    ]
    
    test_invoices = [
        {
            'id': 1, 'invoice_number': 'INV-001', 'customer_name': 'Customer 1',
            'customer_contact': '1234567890', 'date': '2026-01-05',
            'silver_weight': 10.0, 'piece_size': '1 kg', 'num_pieces': 10.0,
            'billing_mode': 'Ready', 'rate': 75000.00,
            'total_amount': 750000.00, 'advance_payment': 100000.00, 'remaining_balance': 650000.00
        }
    ]
    
    test_payments = [
        {'id': 1, 'invoice_id': 1, 'customer_id': 1, 'amount': 100000.00, 'payment_date': '2026-01-05'}
    ]
    
    export_to_excel(test_customers, test_invoices, test_payments, 'test_export.xlsx')
    print("Test Excel file generated successfully!")
