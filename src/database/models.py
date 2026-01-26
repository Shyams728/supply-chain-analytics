from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Equipment(Base):
    __tablename__ = 'equipment'
    
    equipment_id = Column(String(50), primary_key=True)
    equipment_name = Column(String(100))
    equipment_type = Column(String(50))
    location = Column(String(100))
    installation_date = Column(DateTime)
    manufacturer = Column(String(100))
    model = Column(String(100))
    purchase_cost = Column(Float)
    warranty_expiry = Column(DateTime)
    status = Column(String(50))
    
    # Relationships
    downtime_events = relationship("Downtime", back_populates="equipment")

class Downtime(Base):
    __tablename__ = 'downtime'
    
    downtime_id = Column(String(50), primary_key=True)
    equipment_id = Column(String(50), ForeignKey('equipment.equipment_id'))
    start_time = Column(DateTime) # Mapped from failure_date? Using existing schema logic
    end_time = Column(DateTime) # repair_end_date
    downtime_hours = Column(Float)
    failure_type = Column(String(100))
    failure_component = Column(String(100))
    repair_cost = Column(Float)
    maintenance_type = Column(String(50))
    technician_id = Column(String(50))
    
    equipment = relationship("Equipment", back_populates="downtime_events")

class SparePart(Base):
    __tablename__ = 'spare_parts'
    
    part_id = Column(String(50), primary_key=True)
    part_name = Column(String(100))
    part_category = Column(String(50)) # A/B/C or Critical/Low
    unit_cost = Column(Float)
    current_stock = Column(Integer)
    reorder_point = Column(Integer)
    reorder_quantity = Column(Integer)
    lead_time_days = Column(Integer)
    equipment_compatibility = Column(String(100))
    supplier_id = Column(String(50), ForeignKey('suppliers.supplier_id'))
    
    supplier = relationship("Supplier", back_populates="parts")
    transactions = relationship("InventoryTransaction", back_populates="part")

class Supplier(Base):
    __tablename__ = 'suppliers'
    
    supplier_id = Column(String(50), primary_key=True)
    supplier_name = Column(String(100))
    location = Column(String(100))
    email = Column(String(100))
    contact_person = Column(String(100))
    phone = Column(String(50))
    rating = Column(Float)
    average_lead_time = Column(Float)
    
    parts = relationship("SparePart", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

class InventoryTransaction(Base):
    __tablename__ = 'inventory_transactions'
    
    transaction_id = Column(String(50), primary_key=True)
    part_id = Column(String(50), ForeignKey('spare_parts.part_id'))
    transaction_date = Column(DateTime, default=datetime.utcnow)
    transaction_type = Column(String(20)) # Issue/Receipt
    quantity = Column(Integer)
    warehouse_id = Column(String(50))
    reference_doc = Column(String(50))
    stock_after_transaction = Column(Integer)
    
    part = relationship("SparePart", back_populates="transactions")

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    
    po_id = Column(String(50), primary_key=True)
    supplier_id = Column(String(50), ForeignKey('suppliers.supplier_id'))
    part_id = Column(String(50)) 
    quantity_ordered = Column(Integer)
    quantity_received = Column(Integer)
    unit_price = Column(Float)
    order_date = Column(DateTime)
    expected_delivery_date = Column(DateTime)
    actual_delivery_date = Column(DateTime)
    total_cost = Column(Float)
    po_status = Column(String(20))
    
    supplier = relationship("Supplier", back_populates="purchase_orders")

# --- Function to init DB ---
def init_db(connection_string='sqlite:///supply_chain.db'):
    engine = create_engine(connection_string)
    Base.metadata.create_all(engine)
    return engine
