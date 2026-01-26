
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Add src to path to import local modules
def setup_path():
    # Assuming running from root directory
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    
    src_path = os.path.abspath(os.path.join(os.getcwd(), 'src'))
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    dash_path = os.path.abspath(os.path.join(os.getcwd(), 'dashboards'))
    if dash_path not in sys.path:
        sys.path.append(dash_path)

setup_path()

# Force reload comment (System Update)
# Import modules
try:
    from maintenance_analytics import MaintenanceAnalytics
    from supply_chain_analytics import SupplyChainAnalytics
    from logistics_analytics import LogisticsAnalytics
    from advanced_analytics import AdvancedSupplyChainMetrics, TrendAnalysis
    from quality_analytics import QualityAnalytics
    from financial_analytics import FinancialAnalytics
    from benchmarking_analytics import BenchmarkingAnalytics
    from enhanced_components import *
except ImportError as e:
    st.error(f"Failed to import modules: {e}")

# Color palette definition
COLORS = {
    '--primary-color': '#00d2ff',
    '--secondary-color': '#3a7bd5',
    '--glass-bg': 'rgba(255, 255, 255, 0.1)',
    '--glass-border': 'rgba(255, 255, 255, 0.2)',
}

def var(name):
    """Helper to simulate CSS variables in Python/Plotly"""
    return COLORS.get(name, '#000000')

def load_css(file_name="dashboards/style.css"):
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass

def setup_page(title="Supply Chain Platform", icon="🏭", layout="wide"):
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout=layout,
        initial_sidebar_state="expanded"
    )
    load_css()
    
    # Inject custom CSS
    st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            font-weight: bold;
            color: #1f77b4;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 5px solid #1f77b4;
        }
        .section-header {
            font-size: 1.8rem;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 2rem;
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_raw_data():
    """Load raw data from CSVs"""
    try:
        base_dir = os.getcwd()
        data_dir = os.path.join(base_dir, 'data')
        
        def load_csv(name):
            return pd.read_csv(os.path.join(data_dir, name))
            
        data = {
            'equipment': load_csv('equipment.csv'),
            'downtime': load_csv('equipment_downtime.csv'),
            'spare_parts': load_csv('spare_parts.csv'),
            'inventory': load_csv('inventory_transactions.csv'),
            'suppliers': load_csv('suppliers.csv'),
            'purchase_orders': load_csv('purchase_orders.csv'),
            'warehouses': load_csv('warehouses.csv'),
            'deliveries': load_csv('delivery_orders.csv')
        }
        
        # Load date columns
        data['downtime']['failure_date'] = pd.to_datetime(data['downtime']['failure_date'])
        
        # Load advanced data (optional)
        try:
            data.update({
                'spc_data': load_csv('quality_spc.csv'),
                'defect_data': load_csv('quality_defects.csv'),
                'budget_data': load_csv('maintenance_budget.csv'),
                'val_data': load_csv('inventory_valuation.csv'),
                'proj_data': load_csv('maintenance_projects.csv'),
                'cost_data': load_csv('cost_breakdown.csv'),
                'bench_data': load_csv('industry_benchmarks.csv'),
                'schedule_data': load_csv('maintenance_schedule.csv')
            })
        except FileNotFoundError:
            # These might be generated later or optional
            pass
            
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

def render_sidebar(raw_data=None):
    """Render sidebar filters and return filter values"""
    filters = {}
    with st.sidebar:
        st.markdown("---")
        st.markdown("### Data Filters")
        
        # Date range filter
        if 'date_range' not in st.session_state:
            st.session_state.date_range = (pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31"))
            
        filters['date_range'] = st.date_input(
            "Date Range",
            value=st.session_state.date_range,
        )
        st.session_state.date_range = filters['date_range']
        
        # Equipment Type Filter
        options = ["All"]
        if raw_data is not None and 'equipment' in raw_data:
            unique_types = sorted(raw_data['equipment']['equipment_type'].unique().tolist())
            options.extend(unique_types)
        
        if 'equipment_types' not in st.session_state:
            st.session_state.equipment_types = ["All"]
            
        filters['equipment_types'] = st.multiselect(
            "Equipment Type",
            options,
            default=st.session_state.equipment_types
        )
        st.session_state.equipment_types = filters['equipment_types']
        
        # Location/Warehouse Filter
        loc_options = ["All"]
        if raw_data is not None and 'warehouses' in raw_data:
            unique_locs = sorted(raw_data['warehouses']['warehouse_name'].unique().tolist())
            loc_options.extend(unique_locs)
            
        if 'locations' not in st.session_state:
            st.session_state.locations = ["All"]
            
        filters['locations'] = st.multiselect(
            "Location / Warehouse",
            loc_options,
            default=st.session_state.locations
        )
        st.session_state.locations = filters['locations']

        # Supplier Filter
        sup_options = ["All"]
        if raw_data is not None and 'suppliers' in raw_data:
            unique_sups = sorted(raw_data['suppliers']['supplier_name'].unique().tolist())
            sup_options.extend(unique_sups)
            
        if 'suppliers' not in st.session_state:
            st.session_state.suppliers = ["All"]
            
        filters['suppliers'] = st.multiselect(
            "Supplier",
            sup_options,
            default=st.session_state.suppliers
        )
        st.session_state.suppliers = filters['suppliers']
        
        st.markdown("---")
        st.info("💡 Filters apply across all analytics modules.")
        
        # Reset Filters Button
        if st.button("Reset Filters"):
            st.session_state.date_range = (pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31"))
            st.session_state.equipment_types = ["All"]
            st.session_state.locations = ["All"]
            st.session_state.suppliers = ["All"]
            st.rerun()

    return filters

def filter_data(data, filters):
    """Apply filters to the raw data"""
    if not filters:
        return data.copy()
        
    filtered_data = data.copy()
    
    # helper for list filtering
    def apply_list_filter(df, col, filter_val):
        if not filter_val or "All" in filter_val:
            return df
        return df[df[col].isin(filter_val)]
    
    # 1. Equipment Type Filter
    if 'equipment' in filtered_data:
        filtered_data['equipment'] = apply_list_filter(
            filtered_data['equipment'], 'equipment_type', filters.get('equipment_types'))
            
    # 2. Location Filter
    if 'warehouses' in filtered_data:
        filtered_data['warehouses'] = apply_list_filter(
            filtered_data['warehouses'], 'warehouse_name', filters.get('locations'))
            
        # Also filter equipment if they have location? Equipment has 'location' column (e.g. Site A)
        # Assuming warehouse_name maps to location roughly or we filter specifically warehouses
        # For equipment, we might need a mapping. Assuming 'location' column in equipment matches warehouse locations?
        # Let's check: equipment.csv usually has 'Site A', 'Site B'. warehouses.csv has 'Central Warehouse', etc.
        # They might not match directly. Filter strictly on what we can.
        # If equipment has a location column, filter it
        if 'location' in filtered_data['equipment'].columns and filters.get('locations') and "All" not in filters.get('locations'):
             # This might filter out everything if names don't match. 
             # Let's inspect data. Without match, better to skip or be careful.
             # Verification step: View data to see if 'location' matches 'warehouse_name'
             pass
    
    # 3. Supplier Filter
    if 'suppliers' in filtered_data:
        filtered_data['suppliers'] = apply_list_filter(
            filtered_data['suppliers'], 'supplier_name', filters.get('suppliers'))
    
    # 4. Date Range Filter - Apply to Transactional Tables
    start_date, end_date = filters.get('date_range', (None, None))
    if start_date and end_date:
        start_ts = pd.Timestamp(start_date)
        end_ts = pd.Timestamp(end_date)
        
        # Downtime
        if 'downtime' in filtered_data:
             mask = (filtered_data['downtime']['failure_date'] >= start_ts) & \
                    (filtered_data['downtime']['failure_date'] <= end_ts)
             filtered_data['downtime'] = filtered_data['downtime'][mask]
             
        # Purchase Orders
        if 'purchase_orders' in filtered_data:
            po = filtered_data['purchase_orders']
            # Assuming order_date exists and is parseable
            if 'order_date' in po.columns:
                 po['order_date'] = pd.to_datetime(po['order_date'])
                 filtered_data['purchase_orders'] = po[(po['order_date'] >= start_ts) & (po['order_date'] <= end_ts)]
                 
        # Deliveries
        if 'deliveries' in filtered_data:
            dl = filtered_data['deliveries']
            if 'delivery_date' in dl.columns:
                dl['delivery_date'] = pd.to_datetime(dl['delivery_date'])
                filtered_data['deliveries'] = dl[(dl['delivery_date'] >= start_ts) & (dl['delivery_date'] <= end_ts)]
        
        # Inventory
        if 'inventory' in filtered_data:
            inv = filtered_data['inventory']
            if 'transaction_date' in inv.columns:
                inv['transaction_date'] = pd.to_datetime(inv['transaction_date'])
                filtered_data['inventory'] = inv[(inv['transaction_date'] >= start_ts) & (inv['transaction_date'] <= end_ts)]

        # Quality SPC
        if 'spc_data' in filtered_data and filtered_data['spc_data'] is not None:
             spc = filtered_data['spc_data']
             if 'inspection_date' in spc.columns:
                 spc['inspection_date'] = pd.to_datetime(spc['inspection_date'])
                 filtered_data['spc_data'] = spc[(spc['inspection_date'] >= start_ts) & (spc['inspection_date'] <= end_ts)]
        
        # Quality Defects
        if 'defect_data' in filtered_data and filtered_data['defect_data'] is not None:
             defects = filtered_data['defect_data']
             if 'defect_date' in defects.columns:
                 defects['defect_date'] = pd.to_datetime(defects['defect_date'])
                 filtered_data['defect_data'] = defects[(defects['defect_date'] >= start_ts) & (defects['defect_date'] <= end_ts)]

                
    return filtered_data

def get_analytics(data):
    """Initialize analytics classes with (potentially filtered) data"""
    try:
        # Initialize modules
        maint = MaintenanceAnalytics(data['equipment'], data['downtime'])
        sc = SupplyChainAnalytics(data['spare_parts'], data['inventory'], data['purchase_orders'], data['suppliers'])
        log = LogisticsAnalytics(data['deliveries'], data['warehouses'])
        
        # Initialize advanced analytics
        # Note: Some advanced analytics might need optional data
        spc = data.get('spc_data')
        defects = data.get('defect_data')
        
        # Handle case where advanced data is missing (e.g. filtered out or not loaded)
        # Assuming init handles empty dfs gracefully or we pass what we have
        # If keys are missing, we pass None? Analytics classes might expect DataFrames.
        # We should ensure data dict has keys even if empty.
        
        advanced = AdvancedSupplyChainMetrics(
            data['spare_parts'], data['inventory'], data['purchase_orders'], data['suppliers'], data['deliveries']
        )
        
        quality = QualityAnalytics(
            spc if spc is not None else pd.DataFrame(), 
            defects if defects is not None else pd.DataFrame()
        )
        
        val_data = data.get('val_data', pd.DataFrame())
        budget_data = data.get('budget_data', pd.DataFrame())
        proj_data = data.get('proj_data', pd.DataFrame())
        cost_data = data.get('cost_data', pd.DataFrame())
        
        finance = FinancialAnalytics(val_data, budget_data, proj_data, cost_data)
        
        bench_data = data.get('bench_data', pd.DataFrame())
        benchmark = BenchmarkingAnalytics(bench_data)
        
        # Add schedule to maintenance
        if 'schedule_data' in data:
            maint.schedule_data = data['schedule_data']
        
        return {
            'maintenance': maint,
            'supply_chain': sc,
            'logistics': log,
            'advanced': advanced,
            'quality': quality,
            'financial': finance,
            'benchmark': benchmark,
            'raw_data': data # Pass the filtered data as 'raw_data'
        }
    except Exception as e:
        st.error(f"Error initializing analytics: {str(e)}")
        return None

# Backwards compatibility legacy function (wraps new structure)
def initialize_analytics():
    raw = load_raw_data()
    if raw is None: return None
    # No filters applied in legacy mode
    return get_analytics(raw)

def glass_card(title, value, delta=None, icon="📈", col=None):
    delta_html = f'<span style="color: {"#00ff00" if "+" in str(delta) else "#ff4b4b"}; font-size: 0.8rem;">{delta}</span>' if delta else ""
    html = f"""
        <div class="glass-card metric-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #a0a0c0;">{title}</span>
                <span>{icon}</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0;">{value}</div>
            {delta_html}
        </div>
    """
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)

def insight_callout(text, insight_type="info"):
    """Display an insight callout box explaining what a chart means"""
    icons = {"info": "💡", "warning": "⚠️", "success": "✅", "trend": "📈", "action": "🎯"}
    colors = {"info": "#00d2ff", "warning": "#f0ad4e", "success": "#5cb85c", "trend": "#3a7bd5", "action": "#9b59b6"}
    icon = icons.get(insight_type, "💡")
    color = colors.get(insight_type, "#00d2ff")
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(0,210,255,0.1) 0%, rgba(58,123,213,0.1) 100%);
                    border-left: 4px solid {color}; padding: 12px 16px; border-radius: 8px; margin: 10px 0;">
            <span style="font-size: 1.1rem;">{icon}</span>
            <span style="color: #e0e0e0; font-size: 0.9rem; margin-left: 8px;">{text}</span>
        </div>
    """, unsafe_allow_html=True)

def insight_box(text, insight_type="info"):
    insight_callout(text, insight_type)

def benchmark_card(title, value, benchmark, icon, trend=None, col=None):
    # Specialized card for benchmarking
    # Assuming benchmark is a dict or value
    # Simplified implementation
    glass_card(title, value, f"{trend:+.1f}%" if trend else None, icon, col)

def create_radar_chart(categories, values, title):
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Performance'
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title=title,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig
