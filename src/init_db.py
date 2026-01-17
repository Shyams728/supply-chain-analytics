import sqlite3
import os

def init_db():
    db_path = 'data/supply_chain.db'
    schema_path = 'sql/sqlite_schema.sql'
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    # Connect to (or create) the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute the schema script
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    
    try:
        cursor.executescript(schema_sql)
        conn.commit()
        print(f"v Database initialized successfully at {db_path}")
    except sqlite3.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
