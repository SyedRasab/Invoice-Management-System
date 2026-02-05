"""
Verify Payment Flow
1. Create Customer
2. Create Invoice
3. Add Payment (Partial)
4. Verify Status 'Partially Paid'
5. Add Payment (Remaining)
6. Verify Status 'Paid'
7. Verify Customer Outstanding
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000/api'

def print_step(msg):
    print(f"\nExample: {msg}")
    print("-" * 50)

def main():
    try:
        # 1. Create Customer
        print_step("Creating Customer...")
        customer_data = {
            'name': 'Test Client Payments',
            'contact': '555-0199',
            'notes': 'VIP Client'
        }
        res = requests.post(f"{BASE_URL}/customers", json=customer_data)
        if res.status_code != 201:
            print(f"Failed to create customer: {res.text}")
            return
        customer = res.json()
        print(f"Customer Created: {customer['name']} (ID: {customer['id']})")
        
        # 2. Create Invoice
        print_step("Creating Invoice...")
        invoice_data = {
            'customer_name': customer['name'],
            'contact': customer['contact'],
            'silver_weight': 10.0,
            'piece_size': '1 kg',
            'billing_mode': 'Ready',
            'rate': 100.0,
            'advance_payment': 0
        }
        res = requests.post(f"{BASE_URL}/invoices", json=invoice_data)
        if res.status_code != 201:
            print(f"Failed to create invoice: {res.text}")
            return
        invoice = res.json()
        print(f"Invoice Created: {invoice['invoice_number']} (Total: ${invoice['total_amount']})")
        print(f"Initial Status: {invoice['status']}")
        
        # 3. Add Partial Payment
        print_step("Adding Partial Payment ($500)...")
        payment_data = {
            'amount': 500,
            'payment_method': 'Bank Transfer',
            'notes': 'First installment'
        }
        res = requests.post(f"{BASE_URL}/invoices/{invoice['id']}/payments", json=payment_data)
        if res.status_code != 201:
            print(f"Failed to add payment: {res.text}")
            return
        payment = res.json()['payment']
        print(f"Payment Added: ${payment['amount']} via {payment['payment_method']}")
        
        # 4. Check Invoice Status
        print_step("Checking Invoice Status...")
        res = requests.get(f"{BASE_URL}/invoices/{invoice['id']}")
        invoice = res.json()
        print(f"Current Status: {invoice['status']}")
        print(f"Remaining Balance: ${invoice['remaining_balance']}")
        
        if invoice['status'] != 'Partially Paid':
            print("❌ ERROR: Status should be 'Partially Paid'")
        else:
            print("✅ Status Correct")
            
        # 5. Add Remaining Payment
        remaining = invoice['remaining_balance']
        print_step(f"Adding Remaining Payment (${remaining})...")
        payment_data = {
            'amount': remaining,
            'payment_method': 'Cash',
            'notes': 'Final settlement'
        }
        res = requests.post(f"{BASE_URL}/invoices/{invoice['id']}/payments", json=payment_data)
        if res.status_code != 201:
            print(f"Failed to add payment: {res.text}")
            return
            
        # 6. Check Final Status
        print_step("Checking Final Status...")
        res = requests.get(f"{BASE_URL}/invoices/{invoice['id']}")
        invoice = res.json()
        print(f"Final Status: {invoice['status']}")
        
        if invoice['status'] != 'Paid':
            print("❌ ERROR: Status should be 'Paid'")
        else:
            print("✅ Status Correct")
            
        # 7. Check Customer Outstanding
        print_step("Checking Customer Outstanding Balance...")
        res = requests.get(f"{BASE_URL}/customers/{customer['id']}")
        customer_updated = res.json()
        print(f"Total Outstanding: ${customer_updated['total_outstanding']}")
        
        if customer_updated['total_outstanding'] == 0:
            print("✅ Customer Balance Correct")
        else:
            print(f"❌ ERROR: Expected 0, got {customer_updated['total_outstanding']}")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
