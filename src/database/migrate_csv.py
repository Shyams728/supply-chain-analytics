import pandas as pd
import os
import sys
from sqlalchemy.exc import IntegrityError

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.database.models import Base, Equipment, Downtime, SparePart, Supplier, InventoryTransaction, PurchaseOrder
from src.database.connection import DBConnection

def migrate_csv_to_db():
    print("Starting Migration from CSV to Database...")
    
    conn = DBConnection()
    engine = conn.get_engine()
    session = conn.get_session()
    
    # Create tables
    Base.metadata.create_all(engine)
    print("Tables created.")
    
    data_dir = 'data'
    
    # 1. Suppliers (Parent)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'suppliers.csv'))
        records = df.to_dict('records')
        objects = [Supplier(**row) for row in records]
        session.bulk_save_objects(objects)
        print(f"Migrated {len(objects)} Suppliers.")
    except Exception as e:
        print(f"Skipping Suppliers: {e}")

    # 2. Equipment (Parent)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'equipment.csv'))
        # Fix date
        if 'installation_date' in df.columns:
            df['installation_date'] = pd.to_datetime(df['installation_date'])
        records = df.to_dict('records')
        objects = [Equipment(**row) for row in records]
        session.bulk_save_objects(objects)
        print(f"Migrated {len(objects)} Equipment.")
    except Exception as e:
        print(f"Skipping Equipment: {e}")

    # 3. Spare Parts (Depends on Supplier)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'spare_parts.csv'))
        # Fix potential NaN in foreign keys
        records = df.to_dict('records')
        objects = [SparePart(**row) for row in records]
        session.bulk_save_objects(objects)
        print(f"Migrated {len(objects)} Spare Parts.")
    except Exception as e:
        print(f"Skipping Spare Parts: {e}")

    # 4. Downtime (Depends on Equipment)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'equipment_downtime.csv'))
        # Rename cols to match model
        df = df.rename(columns={'failure_date': 'start_time', 'repair_end_date': 'end_time'})
        if 'start_time' in df.columns: df['start_time'] = pd.to_datetime(df['start_time'])
        if 'end_time' in df.columns: df['end_time'] = pd.to_datetime(df['end_time'])
        
        records = df.to_dict('records')
        # Filter fields that exist in model
        valid_keys = Downtime.__table__.columns.keys()
        clean_records = [{k: v for k, v in r.items() if k in valid_keys} for r in records]
        
        objects = [Downtime(**row) for row in clean_records]
        session.bulk_save_objects(objects)
        print(f"Migrated {len(objects)} Downtime events.")
    except Exception as e:
        print(f"Skipping Downtime: {e}")

    # 5. Purchase Orders (Depends on Supplier)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'purchase_orders.csv'))
        # Dates
        for col in ['order_date', 'expected_delivery_date', 'actual_delivery_date']:
            if col in df.columns: df[col] = pd.to_datetime(df[col])
            
        records = df.to_dict('records')
        objects = [PurchaseOrder(**row) for row in records]
        session.bulk_save_objects(objects)
        print(f"Migrated {len(objects)} Purchase Orders.")
    except Exception as e:
        print(f"Skipping Purchase Orders: {e}")

    # 6. Inventory Transactions (Depends on Part)
    try:
        df = pd.read_csv(os.path.join(data_dir, 'inventory_transactions.csv'))
        if 'transaction_date' in df.columns: df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        
        # Rename if needed (warehouse_location -> warehouse_id)
        if 'warehouse_location' in df.columns:
            df = df.rename(columns={'warehouse_location': 'warehouse_id'})
            
        records = df.to_dict('records')
        
        # Batch insert for large table
        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]
                
        count = 0
        for chunk in chunks(records, 1000):
            objects = [InventoryTransaction(**row) for row in chunk]
            session.bulk_save_objects(objects)
            count += len(objects)
            
        print(f"Migrated {count} Inventory Transactions.")
    except Exception as e:
        print(f"Skipping Inventory Transactions: {e}")

    try:
        session.commit()
        print("Migration committed successfully!")
    except Exception as e:
        session.rollback()
        print(f"Migration failed during commit: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    migrate_csv_to_db()
