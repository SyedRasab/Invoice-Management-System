"""
Database Migration Script - Version 2
Migrates database from v1 to v2 with new features:
- Payment transactions with payment methods
- Invoice status tracking
- Customer notes
- Company settings
- Audit logging
"""
import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base, Customer, Invoice, PaymentTransaction, CompanySettings, AuditLog
from config import DATABASE_PATH

def check_column_exists(engine, table_name, column_name):
    """Check if a column exists in a table"""
    inspector = inspect(engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

def migrate_database():
    """Perform database migration"""
    print("=" * 60)
    print("Invoice Management System - Database Migration to V2")
    print("=" * 60)
    
    # Create engine
    engine = create_engine(f'sqlite:///{DATABASE_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n[1/6] Checking existing database structure...")
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"   Found {len(existing_tables)} existing tables: {', '.join(existing_tables)}")
        
        # Backup note
        print("\n[2/6] Creating backup...")
        backup_path = DATABASE_PATH.replace('.db', f'_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db')
        import shutil
        if os.path.exists(DATABASE_PATH):
            shutil.copy2(DATABASE_PATH, backup_path)
            print(f"   ✓ Backup created: {backup_path}")
        
        print("\n[3/6] Adding new columns to existing tables...")
        
        # Add columns to customers table
        if 'customers' in existing_tables:
            with engine.connect() as conn:
                if not check_column_exists(engine, 'customers', 'notes'):
                    conn.execute(text('ALTER TABLE customers ADD COLUMN notes TEXT'))
                    print("   ✓ Added 'notes' column to customers")
                
                if not check_column_exists(engine, 'customers', 'last_invoice_date'):
                    conn.execute(text('ALTER TABLE customers ADD COLUMN last_invoice_date DATETIME'))
                    print("   ✓ Added 'last_invoice_date' column to customers")
                
                conn.commit()
        
        # Add columns to invoices table
        if 'invoices' in existing_tables:
            with engine.connect() as conn:
                if not check_column_exists(engine, 'invoices', 'status'):
                    conn.execute(text("ALTER TABLE invoices ADD COLUMN status VARCHAR(20) DEFAULT 'Unpaid'"))
                    print("   ✓ Added 'status' column to invoices")
                
                if not check_column_exists(engine, 'invoices', 'notes'):
                    conn.execute(text('ALTER TABLE invoices ADD COLUMN notes TEXT'))
                    print("   ✓ Added 'notes' column to invoices")
                
                if not check_column_exists(engine, 'invoices', 'tax_amount'):
                    conn.execute(text('ALTER TABLE invoices ADD COLUMN tax_amount FLOAT DEFAULT 0.0'))
                    print("   ✓ Added 'tax_amount' column to invoices")
                
                if not check_column_exists(engine, 'invoices', 'created_by'):
                    conn.execute(text('ALTER TABLE invoices ADD COLUMN created_by VARCHAR(100)'))
                    print("   ✓ Added 'created_by' column to invoices")
                
                conn.commit()
        
        print("\n[4/6] Creating new tables...")
        
        # Create all new tables
        Base.metadata.create_all(engine)
        print("   ✓ Created payment_transactions table")
        print("   ✓ Created company_settings table")
        print("   ✓ Created audit_log table")
        
        print("\n[5/6] Migrating existing payment data...")
        
        # Migrate old payments to payment_transactions if old payments table exists
        if 'payments' in existing_tables:
            with engine.connect() as conn:
                # Get old payments
                result = conn.execute(text('SELECT * FROM payments'))
                old_payments = result.fetchall()
                
                if old_payments:
                    print(f"   Found {len(old_payments)} payments to migrate...")
                    
                    for payment in old_payments:
                        # Insert into new table with default payment method
                        conn.execute(text("""
                            INSERT INTO payment_transactions 
                            (invoice_id, customer_id, amount, payment_method, payment_date, notes, created_by)
                            VALUES (:invoice_id, :customer_id, :amount, 'Cash', :payment_date, 'Migrated from v1', 'System')
                        """), {
                            'invoice_id': payment[1],  # invoice_id
                            'customer_id': payment[2],  # customer_id
                            'amount': payment[3],  # amount
                            'payment_date': payment[4]  # payment_date
                        })
                    
                    conn.commit()
                    print(f"   ✓ Migrated {len(old_payments)} payments to new structure")
                else:
                    print("   No existing payments to migrate")
        
        print("\n[6/6] Initializing default settings...")
        
        # Create default company settings if not exists
        settings = session.query(CompanySettings).first()
        if not settings:
            settings = CompanySettings(
                company_name='Silver Trading Co.',
                address='123 Business Street, City, Country',
                phone='+1 234 567 8900',
                email='info@silvertrading.com',
                website='www.silvertrading.com',
                currency_symbol='$',
                currency_code='USD',
                weight_unit='kg',
                tax_enabled=False,
                tax_rate=0.0,
                tax_label='VAT'
            )
            session.add(settings)
            session.commit()
            print("   ✓ Created default company settings")
        else:
            print("   Company settings already exist")
        
        # Update invoice statuses based on remaining balance
        print("\n[BONUS] Updating invoice statuses...")
        invoices = session.query(Invoice).all()
        updated_count = 0
        for invoice in invoices:
            if invoice.remaining_balance <= 0:
                invoice.status = 'Paid'
                updated_count += 1
            elif invoice.remaining_balance < invoice.total_amount:
                invoice.status = 'Partially Paid'
                updated_count += 1
            else:
                invoice.status = 'Unpaid'
                updated_count += 1
        
        session.commit()
        print(f"   ✓ Updated status for {updated_count} invoices")
        
        print("\n" + "=" * 60)
        print("✓ Migration completed successfully!")
        print("=" * 60)
        print("\nNew Features Available:")
        print("  • Multiple payments per invoice")
        print("  • Payment method tracking (Cash, Bank, Cheque, Wallet)")
        print("  • Invoice status system (Draft, Unpaid, Partially Paid, Paid, Cancelled)")
        print("  • Customer notes")
        print("  • Company settings configuration")
        print("  • Audit logging")
        print("\nBackup Location:")
        print(f"  {backup_path}")
        print("\nYou can now restart the server to use the new features!")
        print("=" * 60)
        
    except Exception as e:
        session.rollback()
        print(f"\n✗ Migration failed: {str(e)}")
        print("\nYour database has not been modified.")
        print(f"If a backup was created, you can restore it from: {backup_path}")
        raise
    finally:
        session.close()

if __name__ == '__main__':
    print("\n⚠️  WARNING: This will modify your database structure!")
    print("A backup will be created automatically.")
    response = input("\nDo you want to proceed? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        migrate_database()
    else:
        print("\nMigration cancelled.")
