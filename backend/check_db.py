"""
Check database schema
"""
from sqlalchemy import create_engine, inspect
import config

def check_schema():
    engine = create_engine(f'sqlite:///{config.DATABASE_PATH}')
    inspector = inspect(engine)
    
    tables = inspector.get_table_names()
    print(f"Tables: {tables}")
    
    if 'invoices' in tables:
        columns = [col['name'] for col in inspector.get_columns('invoices')]
        print(f"Invoice columns: {columns}")
        
    if 'customers' in tables:
        columns = [col['name'] for col in inspector.get_columns('customers')]
        print(f"Customer columns: {columns}")

if __name__ == '__main__':
    check_schema()
