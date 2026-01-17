"""
Synthetic Supply Chain Data Generator
Manufacturing → Supply Chain → Logistics → Analytics
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# ========================================
# CONFIGURATION
# ========================================

START_DATE = datetime(2023, 1, 1)
END_DATE = datetime(2025, 12, 31)
NUM_EQUIPMENT = 50
NUM_SPARE_PARTS = 200
NUM_SUPPLIERS = 20
NUM_WAREHOUSES = 5

# ========================================
# 1. EQUIPMENT MASTER DATA
# ========================================

def generate_equipment_data():
    equipment_types = ['Excavator', 'Bulldozer', 'Dump Truck', 'Crane', 'Loader', 'Grader']
    manufacturers = ['Caterpillar', 'Komatsu', 'Volvo', 'Hitachi', 'JCB']
    locations = ['Site_A', 'Site_B', 'Site_C', 'Site_D', 'Site_E']
    
    equipment_data = []
    for i in range(1, NUM_EQUIPMENT + 1):
        equip_type = random.choice(equipment_types)
        equipment_data.append({
            'equipment_id': f'EQ{i:04d}',
            'equipment_name': f'{equip_type} {i}',
            'equipment_type': equip_type,
            'manufacturer': random.choice(manufacturers),
            'model': f'Model-{random.randint(100, 999)}',
            'location': random.choice(locations),
            'installation_date': START_DATE + timedelta(days=random.randint(0, 730)),
            'purchase_cost': round(random.uniform(500000, 5000000), 2),
            'status': np.random.choice(['Active', 'Under Maintenance'], p=[0.9, 0.1])
        })
    
    return pd.DataFrame(equipment_data)

# ========================================
# 2. EQUIPMENT DOWNTIME EVENTS
# ========================================

def generate_downtime_data(equipment_df):
    failure_types = ['Mechanical', 'Electrical', 'Hydraulic', 'Engine', 'Structural']
    components = ['Engine', 'Transmission', 'Hydraulic Pump', 'Alternator', 'Brake System', 
                  'Cooling System', 'Fuel System', 'Undercarriage', 'Boom', 'Bucket']
    maintenance_types = ['Reactive', 'Preventive', 'Predictive']
    
    downtime_data = []
    downtime_id = 1
    
    for _, equip in equipment_df.iterrows():
        # Each equipment has 5-20 downtime events over the period
        num_failures = random.randint(5, 20)
        
        for _ in range(num_failures):
            failure_date = START_DATE + timedelta(days=random.randint(0, (END_DATE - START_DATE).days))
            downtime_hours = round(random.uniform(2, 72), 2)  # 2 hours to 3 days
            repair_start = failure_date + timedelta(hours=random.randint(1, 8))
            repair_end = repair_start + timedelta(hours=downtime_hours)
            
            downtime_data.append({
                'downtime_id': f'DT{downtime_id:05d}',
                'equipment_id': equip['equipment_id'],
                'failure_date': failure_date,
                'repair_start_date': repair_start,
                'repair_end_date': repair_end,
                'downtime_hours': downtime_hours,
                'failure_type': random.choice(failure_types),
                'failure_component': random.choice(components),
                'root_cause': f'Root cause analysis: {random.choice(["Wear and tear", "Operator error", "Design flaw", "Material fatigue", "External damage"])}',
                'maintenance_type': np.random.choice(maintenance_types, p=[0.6, 0.3, 0.1]),
                'repair_cost': round(random.uniform(500, 50000), 2)
            })
            downtime_id += 1
    
    return pd.DataFrame(downtime_data)

# ========================================
# 3. SPARE PARTS MASTER
# ========================================

def generate_spare_parts_data():
    part_categories = ['Critical', 'High', 'Medium', 'Low']
    part_types = ['Filter', 'Belt', 'Seal', 'Bearing', 'Gasket', 'Hose', 'Pump', 
                  'Valve', 'Cylinder', 'Sensor', 'Wire', 'Bolt', 'Brake Pad']
    
    spare_parts_data = []
    for i in range(1, NUM_SPARE_PARTS + 1):
        part_type = random.choice(part_types)
        category = random.choice(part_categories)
        
        # Critical parts have higher costs and stricter inventory levels
        if category == 'Critical':
            unit_cost = random.uniform(500, 5000)
            reorder_point = random.randint(10, 30)
            lead_time = random.randint(3, 10)
        elif category == 'High':
            unit_cost = random.uniform(200, 1000)
            reorder_point = random.randint(5, 20)
            lead_time = random.randint(5, 15)
        else:
            unit_cost = random.uniform(50, 500)
            reorder_point = random.randint(3, 10)
            lead_time = random.randint(7, 21)
        
        spare_parts_data.append({
            'part_id': f'SP{i:05d}',
            'part_name': f'{part_type} Type-{i}',
            'part_category': category,
            'equipment_compatibility': f'EQ{random.randint(1, NUM_EQUIPMENT):04d}',
            'unit_cost': round(unit_cost, 2),
            'reorder_point': reorder_point,
            'reorder_quantity': reorder_point * 2,
            'lead_time_days': lead_time,
            'supplier_id': f'SUP{random.randint(1, NUM_SUPPLIERS):03d}'
        })
    
    return pd.DataFrame(spare_parts_data)

# ========================================
# 4. SUPPLIERS
# ========================================

def generate_suppliers_data():
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Pune', 
              'Ahmedabad', 'Hyderabad', 'Jaipur', 'Lucknow']
    
    suppliers_data = []
    for i in range(1, NUM_SUPPLIERS + 1):
        suppliers_data.append({
            'supplier_id': f'SUP{i:03d}',
            'supplier_name': f'Supplier_{i}_Industries',
            'location': random.choice(cities),
            'contact_person': f'Contact_{i}',
            'email': f'contact{i}@supplier{i}.com',
            'phone': f'+91-{random.randint(7000000000, 9999999999)}',
            'rating': round(random.uniform(3.0, 5.0), 2),
            'average_lead_time': random.randint(5, 20)
        })
    
    return pd.DataFrame(suppliers_data)

# ========================================
# 5. INVENTORY TRANSACTIONS
# ========================================

def generate_inventory_transactions(spare_parts_df):
    transactions_data = []
    transaction_id = 1
    
    # Initialize stock levels
    current_stock = {}
    for _, part in spare_parts_df.iterrows():
        current_stock[part['part_id']] = random.randint(part['reorder_point'], part['reorder_point'] * 3)
    
    # Generate transactions over time
    current_date = START_DATE
    while current_date <= END_DATE:
        # Each day, random parts are issued or received
        num_transactions = random.randint(3, 15)
        
        for _ in range(num_transactions):
            part = spare_parts_df.sample(1).iloc[0]
            part_id = part['part_id']
            
            # 70% issues, 30% receipts
            if random.random() < 0.7:
                transaction_type = 'Issue'
                quantity = random.randint(1, 5)
                current_stock[part_id] = max(0, current_stock[part_id] - quantity)
            else:
                transaction_type = 'Receipt'
                quantity = random.randint(5, 20)
                current_stock[part_id] += quantity
            
            transactions_data.append({
                'transaction_id': f'TXN{transaction_id:06d}',
                'part_id': part_id,
                'transaction_date': current_date,
                'transaction_type': transaction_type,
                'quantity': quantity,
                'stock_after_transaction': current_stock[part_id],
                'warehouse_location': f'WH{random.randint(1, NUM_WAREHOUSES):02d}',
                'reference_doc': f'REF{random.randint(1000, 9999)}'
            })
            transaction_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(transactions_data)

# ========================================
# 6. PURCHASE ORDERS
# ========================================

def generate_purchase_orders(spare_parts_df, suppliers_df):
    po_data = []
    po_id = 1
    
    current_date = START_DATE
    while current_date <= END_DATE:
        # Generate 2-5 POs per week
        if random.random() < 0.3:  # 30% chance each day
            num_pos = random.randint(1, 3)
            
            for _ in range(num_pos):
                part = spare_parts_df.sample(1).iloc[0]
                supplier = suppliers_df[suppliers_df['supplier_id'] == part['supplier_id']].iloc[0]
                
                quantity = random.randint(10, 100)
                expected_delivery = current_date + timedelta(days=part['lead_time_days'])
                
                # 80% delivered on time, 20% delayed
                if random.random() < 0.8:
                    actual_delivery = expected_delivery + timedelta(days=random.randint(-2, 2))
                else:
                    actual_delivery = expected_delivery + timedelta(days=random.randint(3, 10))
                
                quantity_received = quantity if random.random() < 0.95 else quantity - random.randint(1, 5)
                
                po_data.append({
                    'po_id': f'PO{po_id:06d}',
                    'part_id': part['part_id'],
                    'supplier_id': supplier['supplier_id'],
                    'order_date': current_date,
                    'expected_delivery_date': expected_delivery,
                    'actual_delivery_date': actual_delivery if actual_delivery <= END_DATE else None,
                    'quantity_ordered': quantity,
                    'quantity_received': quantity_received if actual_delivery <= END_DATE else 0,
                    'unit_price': round(part['unit_cost'] * random.uniform(0.95, 1.05), 2),
                    'total_cost': round(part['unit_cost'] * quantity * random.uniform(0.95, 1.05), 2),
                    'po_status': 'Received' if actual_delivery <= END_DATE else 'Open'
                })
                po_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(po_data)

# ========================================
# 7. WAREHOUSES
# ========================================

def generate_warehouses_data():
    warehouse_locations = [
        {'name': 'Central Hub Mumbai', 'lat': 19.0760, 'lon': 72.8777},
        {'name': 'North Regional Delhi', 'lat': 28.7041, 'lon': 77.1025},
        {'name': 'South Regional Chennai', 'lat': 13.0827, 'lon': 80.2707},
        {'name': 'East Regional Kolkata', 'lat': 22.5726, 'lon': 88.3639},
        {'name': 'West Regional Pune', 'lat': 18.5204, 'lon': 73.8567}
    ]
    
    warehouses_data = []
    for i, loc in enumerate(warehouse_locations, 1):
        warehouses_data.append({
            'warehouse_id': f'WH{i:02d}',
            'warehouse_name': loc['name'],
            'location': loc['name'].split()[-1],
            'latitude': loc['lat'],
            'longitude': loc['lon'],
            'capacity': random.randint(5000, 15000),
            'warehouse_type': 'Central' if i == 1 else 'Regional'
        })
    
    return pd.DataFrame(warehouses_data)

# ========================================
# 8. DELIVERY ORDERS
# ========================================

def generate_delivery_orders(spare_parts_df, warehouses_df):
    transport_modes = ['Road', 'Air', 'Express']
    delivery_data = []
    delivery_id = 1
    
    current_date = START_DATE
    while current_date <= END_DATE:
        # Generate 3-8 deliveries per day
        if random.random() < 0.5:
            num_deliveries = random.randint(1, 5)
            
            for _ in range(num_deliveries):
                part = spare_parts_df.sample(1).iloc[0]
                warehouse = warehouses_df.sample(1).iloc[0]
                transport = random.choice(transport_modes)
                
                # Destination coordinates (near equipment sites)
                dest_lat = warehouse['latitude'] + random.uniform(-2, 2)
                dest_lon = warehouse['longitude'] + random.uniform(-2, 2)
                
                distance = random.uniform(50, 800)
                
                # Lead time based on transport mode
                if transport == 'Express':
                    planned_days = 1
                    cost_per_km = 15
                elif transport == 'Air':
                    planned_days = 2
                    cost_per_km = 12
                else:
                    planned_days = random.randint(3, 7)
                    cost_per_km = 8
                
                planned_delivery = current_date + timedelta(days=planned_days)
                actual_delivery = planned_delivery + timedelta(days=random.randint(-1, 3))
                
                delivery_data.append({
                    'delivery_id': f'DEL{delivery_id:06d}',
                    'part_id': part['part_id'],
                    'source_warehouse': warehouse['warehouse_id'],
                    'destination_site': f'Site_{random.choice(["A", "B", "C", "D", "E"])}',
                    'destination_lat': round(dest_lat, 6),
                    'destination_lon': round(dest_lon, 6),
                    'order_date': current_date,
                    'planned_delivery_date': planned_delivery,
                    'actual_delivery_date': actual_delivery if actual_delivery <= END_DATE else None,
                    'quantity': random.randint(1, 10),
                    'transport_mode': transport,
                    'delivery_cost': round(distance * cost_per_km * random.uniform(0.9, 1.1), 2),
                    'delivery_status': 'Delivered' if actual_delivery <= END_DATE else 'In Transit',
                    'distance_km': round(distance, 2)
                })
                delivery_id += 1
        
        current_date += timedelta(days=1)
    
    return pd.DataFrame(delivery_data)

# ========================================
# MAIN DATA GENERATION
# ========================================

def generate_all_data():
    print("Generating Supply Chain Data...")
    print("=" * 50)
    
    # Generate all datasets
    equipment_df = generate_equipment_data()
    print(f"✓ Equipment Master: {len(equipment_df)} records")
    
    downtime_df = generate_downtime_data(equipment_df)
    print(f"✓ Equipment Downtime: {len(downtime_df)} records")
    
    spare_parts_df = generate_spare_parts_data()
    print(f"✓ Spare Parts Master: {len(spare_parts_df)} records")
    
    suppliers_df = generate_suppliers_data()
    print(f"✓ Suppliers: {len(suppliers_df)} records")
    
    inventory_df = generate_inventory_transactions(spare_parts_df)
    print(f"✓ Inventory Transactions: {len(inventory_df)} records")
    
    po_df = generate_purchase_orders(spare_parts_df, suppliers_df)
    print(f"✓ Purchase Orders: {len(po_df)} records")
    
    warehouses_df = generate_warehouses_data()
    print(f"✓ Warehouses: {len(warehouses_df)} records")
    
    deliveries_df = generate_delivery_orders(spare_parts_df, warehouses_df)
    print(f"✓ Delivery Orders: {len(deliveries_df)} records")
    
    # Save to CSV
    print("\nSaving data to CSV files...")
    equipment_df.to_csv('data/equipment.csv', index=False)
    downtime_df.to_csv('data/equipment_downtime.csv', index=False)
    spare_parts_df.to_csv('data/spare_parts.csv', index=False)
    suppliers_df.to_csv('data/suppliers.csv', index=False)
    inventory_df.to_csv('data/inventory_transactions.csv', index=False)
    po_df.to_csv('data/purchase_orders.csv', index=False)
    warehouses_df.to_csv('data/warehouses.csv', index=False)
    deliveries_df.to_csv('data/delivery_orders.csv', index=False)
    
    print("\n✓ All data generated successfully!")
    print("=" * 50)
    
    return {
        'equipment': equipment_df,
        'downtime': downtime_df,
        'spare_parts': spare_parts_df,
        'suppliers': suppliers_df,
        'inventory': inventory_df,
        'purchase_orders': po_df,
        'warehouses': warehouses_df,
        'deliveries': deliveries_df
    }

if __name__ == "__main__":
    data = generate_all_data()