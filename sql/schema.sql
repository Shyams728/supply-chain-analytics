-- Supply Chain Analytics Database Schema
-- Manufacturing → Supply Chain → Logistics → Analytics

-- ========================================
-- MANUFACTURING MODULE
-- ========================================

-- Equipment/Machines Master
CREATE TABLE equipment (
    equipment_id VARCHAR(20) PRIMARY KEY,
    equipment_name VARCHAR(100),
    equipment_type VARCHAR(50),
    manufacturer VARCHAR(50),
    model VARCHAR(50),
    location VARCHAR(50),
    installation_date DATE,
    purchase_cost DECIMAL(12,2),
    status VARCHAR(20) -- Active, Under Maintenance, Decommissioned
);

-- Production Orders
CREATE TABLE production_orders (
    order_id VARCHAR(20) PRIMARY KEY,
    product_id VARCHAR(20),
    quantity INT,
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE,
    actual_end_date DATE,
    equipment_id VARCHAR(20),
    status VARCHAR(20), -- Planned, In Progress, Completed, Delayed
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- Equipment Downtime Log
CREATE TABLE equipment_downtime (
    downtime_id VARCHAR(20) PRIMARY KEY,
    equipment_id VARCHAR(20),
    failure_date TIMESTAMP,
    repair_start_date TIMESTAMP,
    repair_end_date TIMESTAMP,
    downtime_hours DECIMAL(8,2),
    failure_type VARCHAR(50), -- Mechanical, Electrical, Hydraulic, etc.
    failure_component VARCHAR(100),
    root_cause VARCHAR(200),
    maintenance_type VARCHAR(30), -- Reactive, Preventive, Predictive
    repair_cost DECIMAL(10,2),
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
);

-- ========================================
-- SUPPLY CHAIN MODULE
-- ========================================

-- Spare Parts Master
CREATE TABLE spare_parts (
    part_id VARCHAR(20) PRIMARY KEY,
    part_name VARCHAR(100),
    part_category VARCHAR(50), -- Critical, High, Medium, Low
    equipment_compatibility VARCHAR(200),
    unit_cost DECIMAL(10,2),
    reorder_point INT,
    reorder_quantity INT,
    lead_time_days INT,
    supplier_id VARCHAR(20)
);

-- Inventory Transactions
CREATE TABLE inventory_transactions (
    transaction_id VARCHAR(20) PRIMARY KEY,
    part_id VARCHAR(20),
    transaction_date DATE,
    transaction_type VARCHAR(20), -- Receipt, Issue, Adjustment
    quantity INT,
    stock_after_transaction INT,
    warehouse_location VARCHAR(50),
    reference_doc VARCHAR(50), -- PO number, Work Order, etc.
    FOREIGN KEY (part_id) REFERENCES spare_parts(part_id)
);

-- Purchase Orders
CREATE TABLE purchase_orders (
    po_id VARCHAR(20) PRIMARY KEY,
    part_id VARCHAR(20),
    supplier_id VARCHAR(20),
    order_date DATE,
    expected_delivery_date DATE,
    actual_delivery_date DATE,
    quantity_ordered INT,
    quantity_received INT,
    unit_price DECIMAL(10,2),
    total_cost DECIMAL(12,2),
    po_status VARCHAR(20), -- Open, Partial, Received, Cancelled
    FOREIGN KEY (part_id) REFERENCES spare_parts(part_id)
);

-- Suppliers Master
CREATE TABLE suppliers (
    supplier_id VARCHAR(20) PRIMARY KEY,
    supplier_name VARCHAR(100),
    location VARCHAR(100),
    contact_person VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    rating DECIMAL(3,2), -- Supplier performance rating 0-5
    average_lead_time INT
);

-- ========================================
-- LOGISTICS MODULE
-- ========================================

-- Warehouses
CREATE TABLE warehouses (
    warehouse_id VARCHAR(20) PRIMARY KEY,
    warehouse_name VARCHAR(100),
    location VARCHAR(100),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6),
    capacity INT,
    warehouse_type VARCHAR(30) -- Central, Regional, Site
);

-- Delivery Orders
CREATE TABLE delivery_orders (
    delivery_id VARCHAR(20) PRIMARY KEY,
    part_id VARCHAR(20),
    source_warehouse VARCHAR(20),
    destination_site VARCHAR(100),
    destination_lat DECIMAL(10,6),
    destination_lon DECIMAL(10,6),
    order_date DATE,
    planned_delivery_date DATE,
    actual_delivery_date DATE,
    quantity INT,
    transport_mode VARCHAR(20), -- Road, Air, Express
    delivery_cost DECIMAL(10,2),
    delivery_status VARCHAR(20), -- Pending, In Transit, Delivered, Delayed
    distance_km DECIMAL(8,2),
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
    DATEDIFF(CURDATE(), MIN(d.failure_date)) as days_in_operation,
    ROUND(DATEDIFF(CURDATE(), MIN(d.failure_date)) / NULLIF(COUNT(d.downtime_id), 0), 2) as mtbf_days
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
    DATE_FORMAT(actual_delivery_date, '%Y-%m') as delivery_month,
    transport_mode,
    COUNT(*) as total_deliveries,
    SUM(CASE WHEN actual_delivery_date <= planned_delivery_date THEN 1 ELSE 0 END) as on_time_deliveries,
    ROUND(100.0 * SUM(CASE WHEN actual_delivery_date <= planned_delivery_date THEN 1 ELSE 0 END) / COUNT(*), 2) as on_time_percentage,
    AVG(DATEDIFF(actual_delivery_date, order_date)) as avg_delivery_days,
    SUM(delivery_cost) as total_logistics_cost,
    AVG(delivery_cost) as avg_cost_per_delivery
FROM delivery_orders
WHERE actual_delivery_date IS NOT NULL
GROUP BY DATE_FORMAT(actual_delivery_date, '%Y-%m'), transport_mode;

-- Spare Parts Consumption Pattern
CREATE VIEW vw_spare_parts_consumption AS
SELECT 
    sp.part_id,
    sp.part_name,
    sp.part_category,
    DATE_FORMAT(it.transaction_date, '%Y-%m') as consumption_month,
    SUM(CASE WHEN it.transaction_type = 'Issue' THEN it.quantity ELSE 0 END) as quantity_consumed,
    COUNT(CASE WHEN it.transaction_type = 'Issue' THEN 1 END) as issue_frequency,
    sp.unit_cost * SUM(CASE WHEN it.transaction_type = 'Issue' THEN it.quantity ELSE 0 END) as consumption_value
FROM spare_parts sp
JOIN inventory_transactions it ON sp.part_id = it.part_id
GROUP BY sp.part_id, sp.part_name, sp.part_category, DATE_FORMAT(it.transaction_date, '%Y-%m');

-- Supplier Performance
CREATE VIEW vw_supplier_performance AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.location,
    s.rating,
    COUNT(po.po_id) as total_orders,
    SUM(po.total_cost) as total_spend,
    AVG(DATEDIFF(po.actual_delivery_date, po.order_date)) as actual_avg_lead_time,
    SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) as on_time_deliveries,
    ROUND(100.0 * SUM(CASE WHEN po.actual_delivery_date <= po.expected_delivery_date THEN 1 ELSE 0 END) / COUNT(po.po_id), 2) as on_time_percentage
FROM suppliers s
JOIN purchase_orders po ON s.supplier_id = po.supplier_id
WHERE po.actual_delivery_date IS NOT NULL
GROUP BY s.supplier_id, s.supplier_name, s.location, s.rating;