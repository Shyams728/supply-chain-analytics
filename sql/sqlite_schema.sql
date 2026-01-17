-- Supply Chain Analytics Database Schema (SQLite Version)
-- Manufacturing → Supply Chain → Logistics → Analytics

-- ========================================
-- MANUFACTURING MODULE
-- ========================================

-- Equipment/Machines Master
CREATE TABLE equipment (
    equipment_id TEXT PRIMARY KEY,
    equipment_name TEXT,
    equipment_type TEXT,
    manufacturer TEXT,
    model TEXT,
    location TEXT,
    installation_date TEXT,
    purchase_cost REAL,
    status TEXT -- Active, Under Maintenance, Decommissioned
);

-- Production Orders
CREATE TABLE production_orders (
    order_id TEXT PRIMARY KEY,
    product_id TEXT,
    quantity INTEGER,
    planned_start_date TEXT,
    planned_end_date TEXT,
    actual_start_date TEXT,
    actual_end_date TEXT,
    equipment_id TEXT,
    status TEXT, -- Planned, In Progress, Completed, Delayed
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Equipment Downtime Log
CREATE TABLE equipment_downtime (
    downtime_id TEXT PRIMARY KEY,
    equipment_id TEXT,
    failure_date TEXT,
    repair_start_date TEXT,
    repair_end_date TEXT,
    downtime_hours REAL,
    failure_type TEXT, -- Mechanical, Electrical, Hydraulic, etc.
    failure_component TEXT,
    root_cause TEXT,
    maintenance_type TEXT, -- Reactive, Preventive, Predictive
    repair_cost REAL,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- ========================================
-- SUPPLY CHAIN MODULE
-- ========================================

-- Spare Parts Master
CREATE TABLE spare_parts (
    part_id TEXT PRIMARY KEY,
    part_name TEXT,
    part_category TEXT, -- Critical, High, Medium, Low
    equipment_compatibility TEXT,
    unit_cost REAL,
    reorder_point INTEGER,
    reorder_quantity INTEGER,
    lead_time_days INTEGER,
    supplier_id TEXT
);

-- Inventory Transactions
CREATE TABLE inventory_transactions (
    transaction_id TEXT PRIMARY KEY,
    part_id TEXT,
    transaction_date TEXT,
    transaction_type TEXT, -- Receipt, Issue, Adjustment
    quantity INTEGER,
    stock_after_transaction INTEGER,
    warehouse_location TEXT,
    reference_doc TEXT, -- PO number, Work Order, etc.
    FOREIGN KEY (part_id) REFERENCES spare_parts(part_id)
);

-- Purchase Orders
CREATE TABLE purchase_orders (
    po_id TEXT PRIMARY KEY,
    part_id TEXT,
    supplier_id TEXT,
    order_date TEXT,
    expected_delivery_date TEXT,
    actual_delivery_date TEXT,
    quantity_ordered INTEGER,
    quantity_received INTEGER,
    unit_price REAL,
    total_cost REAL,
    po_status TEXT, -- Open, Partial, Received, Cancelled
    FOREIGN KEY (part_id) REFERENCES spare_parts(part_id)
);

-- Suppliers Master
CREATE TABLE suppliers (
    supplier_id TEXT PRIMARY KEY,
    supplier_name TEXT,
    location TEXT,
    contact_person TEXT,
    email TEXT,
    phone TEXT,
    rating REAL, -- Supplier performance rating 0-5
    average_lead_time INTEGER
);

-- ========================================
-- LOGISTICS MODULE
-- ========================================

-- Warehouses
CREATE TABLE warehouses (
    warehouse_id TEXT PRIMARY KEY,
    warehouse_name TEXT,
    location TEXT,
    latitude REAL,
    longitude REAL,
    capacity INTEGER,
    warehouse_type TEXT -- Central, Regional, Site
);

-- Delivery Orders
CREATE TABLE delivery_orders (
    delivery_id TEXT PRIMARY KEY,
    part_id TEXT,
    source_warehouse TEXT,
    destination_site TEXT,
    destination_lat REAL,
    destination_lon REAL,
    order_date TEXT,
    planned_delivery_date TEXT,
    actual_delivery_date TEXT,
    quantity INTEGER,
    transport_mode TEXT, -- Road, Air, Express
    delivery_cost REAL,
    delivery_status TEXT, -- Pending, In Transit, Delivered, Delayed
    distance_km REAL,
    FOREIGN KEY (part_id) REFERENCES spare_parts(part_id),
    FOREIGN KEY (source_warehouse) REFERENCES warehouses(warehouse_id)
);

-- ========================================
-- ANALYTICS VIEWS
-- ========================================

-- Equipment Reliability Metrics
CREATE VIEW vw_equipment_reliability AS
SELECT 
    e.equipment_id,
    e.equipment_name,
    e.equipment_type,
    COUNT(d.downtime_id) as total_failures,
    SUM(d.downtime_hours) as total_downtime_hours,
    AVG(d.downtime_hours) as avg_repair_time_mttr,
    SUM(d.repair_cost) as total_repair_cost,
    CAST(julianday('now') - julianday(MIN(d.failure_date)) AS INTEGER) as days_in_operation,
    ROUND(CAST(julianday('now') - julianday(MIN(d.failure_date)) AS REAL) / NULLIF(COUNT(d.downtime_id), 0), 2) as mtbf_days
FROM equipment e
LEFT JOIN equipment_downtime d ON e.equipment_id = d.equipment_id
GROUP BY e.equipment_id, e.equipment_name, e.equipment_type;

-- Inventory Health Dashboard
CREATE VIEW vw_inventory_health AS
SELECT 
    sp.part_id,
    sp.part_name,
    sp.part_category,
    sp.unit_cost,
    sp.reorder_point,
    sp.lead_time_days,
    (SELECT stock_after_transaction 
     FROM inventory_transactions 
     WHERE part_id = sp.part_id 
     ORDER BY transaction_date DESC 
     LIMIT 1) as current_stock,
    CASE 
        WHEN (SELECT stock_after_transaction FROM inventory_transactions 
              WHERE part_id = sp.part_id ORDER BY transaction_date DESC LIMIT 1) = 0 
        THEN 'Stock Out'
        WHEN (SELECT stock_after_transaction FROM inventory_transactions 
              WHERE part_id = sp.part_id ORDER BY transaction_date DESC LIMIT 1) <= sp.reorder_point 
        THEN 'Below Reorder Point'
        ELSE 'Healthy'
    END as stock_status
FROM spare_parts sp;

-- Logistics Performance
CREATE VIEW vw_logistics_performance AS
SELECT 
    strftime('%Y-%m', actual_delivery_date) as delivery_month,
    transport_mode,
    COUNT(*) as total_deliveries,
    SUM(CASE WHEN actual_delivery_date <= planned_delivery_date THEN 1 ELSE 0 END) as on_time_deliveries,
    ROUND(100.0 * SUM(CASE WHEN actual_delivery_date <= planned_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage,
    AVG(julianday(actual_delivery_date) - julianday(order_date)) as avg_delivery_days,
    SUM(delivery_cost) as total_logistics_cost,
    AVG(delivery_cost) as avg_cost_per_delivery
FROM delivery_orders
WHERE actual_delivery_date IS NOT NULL
GROUP BY delivery_month, transport_mode;

-- Spare Parts Consumption Pattern
CREATE VIEW vw_spare_parts_consumption AS
SELECT 
    sp.part_id,
    sp.part_name,
    sp.part_category,
    strftime('%Y-%m', it.transaction_date) as consumption_month,
    SUM(CASE WHEN it.transaction_type = 'Issue' THEN it.quantity ELSE 0 END) as quantity_consumed,
    COUNT(CASE WHEN it.transaction_type = 'Issue' THEN 1 END) as issue_frequency,
    sp.unit_cost * SUM(CASE WHEN it.transaction_type = 'Issue' THEN it.quantity ELSE 0 END) as consumption_value
FROM spare_parts sp
JOIN inventory_transactions it ON sp.part_id = it.part_id
GROUP BY sp.part_id, sp.part_name, sp.part_category, consumption_month;

-- Supplier Performance
CREATE VIEW vw_supplier_performance AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.location,
    s.rating,
    COUNT(po.po_id) as total_orders,
    SUM(po.total_cost) as total_spend,
    AVG(julianday(po.actual_delivery_date) - julianday(po.order_date)) as actual_avg_lead_time,
    SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) as on_time_deliveries,
    ROUND(100.0 * SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) / COUNT(po.po_id), 2) as on_time_percentage
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
WHERE po.actual_delivery_date IS NOT NULL
GROUP BY s.supplier_id, s.supplier_name, s.location, s.rating;
