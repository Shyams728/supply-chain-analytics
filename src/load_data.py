import pandas as pd
import sqlite3
import os

def load_data():
    db_path = 'data/supply_chain.db'
    data_dir = 'data'
    
    # Mapping of CSV files to table names
    csv_to_table = {
        'equipment.csv': 'equipment',
        'equipment_downtime.csv': 'equipment_downtime',
        'spare_parts.csv': 'spare_parts',
        'suppliers.csv': 'suppliers',
        'inventory_transactions.csv': 'inventory_transactions',
        'purchase_orders.csv': 'purchase_orders',
        'warehouses.csv': 'warehouses',
        'delivery_orders.csv': 'delivery_orders'
    }
    
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found. Run init_db.py first.")
        return

    conn = sqlite3.connect(db_path)
    
    try:
        for csv_file, table_name in csv_to_table.items():
            csv_path = os.path.join(data_dir, csv_file)
            if os.path.exists(csv_path):
                print(f"Loading {csv_file} into {table_name}...")
                df = pd.read_csv(csv_path)
                
                # Use to_sql to load data. if_exists='append' to add to existing schema
                df.to_sql(table_name, conn, if_exists='append', index=False)
                print(f"v Loaded {len(df)} records into {table_name}")
            else:
                print(f"Warning: {csv_file} not found in {data_dir}")
        
        print("\nAll data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    load_data()
