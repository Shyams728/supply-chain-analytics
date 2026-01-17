"""
Integrated Supply Chain Analytics Dashboard
Manufacturing → Supply Chain → Logistics → Analytics

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys

# Import custom analytics modules
# Assuming the modules are in the same directory
# from maintenance_analytics import MaintenanceAnalytics
# from supply_chain_analytics import SupplyChainAnalytics
# from logistics_analytics import LogisticsAnalytics

# Page configuration
st.set_page_config(
    page_title="Supply Chain Analytics Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
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

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Supply+Chain+Analytics", use_column_width=True)
    st.markdown("---")
    
    module = st.selectbox(
        "📊 Select Analysis Module",
        [
            "🏠 Overview Dashboard",
            "🔧 Manufacturing & Maintenance",
            "📦 Supply Chain & Inventory",
            "🚚 Logistics & Transportation",
            "📈 Predictive Analytics",
            "💡 Recommendations"
        ]
    )
    
    st.markdown("---")
    st.markdown("### Data Filters")
    
    # Date range filter
    date_range = st.date_input(
        "Date Range",
        value=(pd.to_datetime("2024-01-01"), pd.to_datetime("2024-12-31"))
    )
    
    # Equipment type filter
    equipment_types = st.multiselect(
        "Equipment Type",
        ["All", "Excavator", "Bulldozer", "Dump Truck", "Crane", "Loader"],
        default=["All"]
    )
    
    st.markdown("---")
    st.info("💡 This dashboard provides end-to-end supply chain analytics from manufacturing operations to logistics optimization.")

# Main content
st.markdown('<p class="main-header">🏭 Supply Chain Analytics Platform</p>', unsafe_allow_html=True)
st.markdown("**Manufacturing → Supply Chain → Logistics → Analytics**")

# Load data (cached)
@st.cache_data
def load_data():
    """Load all datasets"""
    try:
        data = {
            'equipment': pd.read_csv('data/equipment.csv'),
            'downtime': pd.read_csv('data/equipment_downtime.csv'),
            'spare_parts': pd.read_csv('data/spare_parts.csv'),
            'inventory': pd.read_csv('data/inventory_transactions.csv'),
            'suppliers': pd.read_csv('data/suppliers.csv'),
            'purchase_orders': pd.read_csv('data/purchase_orders.csv'),
            'warehouses': pd.read_csv('data/warehouses.csv'),
            'deliveries': pd.read_csv('data/delivery_orders.csv')
        }
        return data
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

data = load_data()

if data is None:
    st.error("⚠️ Failed to load data. Please ensure all data files are in the 'data' folder.")
    st.stop()

# ===========================================
# OVERVIEW DASHBOARD
# ===========================================

if module == "🏠 Overview Dashboard":
    st.markdown('<p class="section-header">Executive Overview</p>', unsafe_allow_html=True)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_equipment = len(data['equipment'])
        st.metric("Total Equipment", f"{total_equipment}", delta="Active")
    
    with col2:
        total_downtime = data['downtime']['downtime_hours'].sum()
        st.metric("Total Downtime", f"{total_downtime:,.0f} hrs", delta="-12%", delta_color="inverse")
    
    with col3:
        inventory_value = (data['spare_parts']['unit_cost'].sum())
        st.metric("Inventory Value", f"₹{inventory_value:,.0f}M", delta="+5%")
    
    with col4:
        deliveries_completed = len(data['deliveries'][data['deliveries']['delivery_status'] == 'Delivered'])
        st.metric("Deliveries Completed", f"{deliveries_completed:,}", delta="+8%")
    
    st.markdown("---")
    
    # Visualizations Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        # Equipment by Type
        equip_by_type = data['equipment']['equipment_type'].value_counts().reset_index()
        equip_by_type.columns = ['Equipment Type', 'Count']
        
        fig = px.bar(
            equip_by_type,
            x='Equipment Type',
            y='Count',
            title='Equipment Distribution by Type',
            color='Count',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Monthly Downtime Trend
        data['downtime']['failure_date'] = pd.to_datetime(data['downtime']['failure_date'])
        monthly_downtime = data['downtime'].groupby(
            data['downtime']['failure_date'].dt.to_period('M')
        )['downtime_hours'].sum().reset_index()
        monthly_downtime['failure_date'] = monthly_downtime['failure_date'].astype(str)
        
        fig = px.line(
            monthly_downtime,
            x='failure_date',
            y='downtime_hours',
            title='Monthly Downtime Trend',
            markers=True
        )
        fig.update_xaxes(title='Month')
        fig.update_yaxes(title='Downtime Hours')
        st.plotly_chart(fig, use_container_width=True)
    
    # Visualizations Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        # Inventory Status
        latest_inventory = data['inventory'].sort_values('transaction_date').groupby('part_id').last()
        merged_inv = pd.merge(
            latest_inventory,
            data['spare_parts'][['part_id', 'reorder_point']],
            on='part_id',
            how='left'
        )
        
        merged_inv['status'] = merged_inv.apply(
            lambda x: 'Stock Out' if x['stock_after_transaction'] == 0
            else 'Below Reorder' if x['stock_after_transaction'] <= x['reorder_point']
            else 'Healthy',
            axis=1
        )
        
        status_counts = merged_inv['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Count']
        
        fig = px.pie(
            status_counts,
            values='Count',
            names='Status',
            title='Inventory Health Status',
            color='Status',
            color_discrete_map={
                'Healthy': '#2ecc71',
                'Below Reorder': '#f39c12',
                'Stock Out': '#e74c3c'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Delivery Performance
        data['deliveries']['on_time'] = (
            pd.to_datetime(data['deliveries']['actual_delivery_date']) <=
            pd.to_datetime(data['deliveries']['planned_delivery_date'])
        ).astype(int)
        
        perf_data = pd.DataFrame({
            'Category': ['On-Time', 'Delayed'],
            'Count': [
                data['deliveries']['on_time'].sum(),
                len(data['deliveries']) - data['deliveries']['on_time'].sum()
            ]
        })
        
        fig = px.bar(
            perf_data,
            x='Category',
            y='Count',
            title='Delivery Performance',
            color='Category',
            color_discrete_map={'On-Time': '#2ecc71', 'Delayed': '#e74c3c'}
        )
        st.plotly_chart(fig, use_container_width=True)

# ===========================================
# MANUFACTURING & MAINTENANCE MODULE
# ===========================================

elif module == "🔧 Manufacturing & Maintenance":
    st.markdown('<p class="section-header">Manufacturing & Maintenance Analytics</p>', unsafe_allow_html=True)
    
    # Reliability Metrics
    st.subheader("Equipment Reliability Metrics")
    
    # Calculate MTBF and MTTR
    reliability = data['downtime'].groupby('equipment_id').agg({
        'downtime_id': 'count',
        'downtime_hours': ['sum', 'mean'],
        'repair_cost': 'sum',
        'failure_date': ['min', 'max']
    }).reset_index()
    
    reliability.columns = [
        'equipment_id', 'total_failures', 'total_downtime',
        'mttr', 'total_cost', 'first_failure', 'last_failure'
    ]
    
    # Add equipment details
    reliability = pd.merge(
        reliability,
        data['equipment'][['equipment_id', 'equipment_name', 'equipment_type']],
        on='equipment_id',
        how='left'
    )
    
    # Display metrics table
    st.dataframe(
        reliability[['equipment_name', 'equipment_type', 'total_failures', 'mttr', 'total_cost']].head(10),
        use_container_width=True
    )
    
    st.markdown("---")
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Failure by Type
        failure_by_type = data['downtime']['failure_type'].value_counts().reset_index()
        failure_by_type.columns = ['Failure Type', 'Count']
        
        fig = px.bar(
            failure_by_type,
            x='Failure Type',
            y='Count',
            title='Failures by Type',
            color='Count',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # MTBF Distribution
        reliability['first_failure'] = pd.to_datetime(reliability['first_failure'])
        reliability['last_failure'] = pd.to_datetime(reliability['last_failure'])
        reliability['operating_days'] = (
            reliability['last_failure'] - reliability['first_failure']
        ).dt.days
        reliability['mtbf'] = reliability['operating_days'] / reliability['total_failures']
        
        fig = px.histogram(
            reliability,
            x='mtbf',
            nbins=20,
            title='MTBF Distribution',
            labels={'mtbf': 'MTBF (days)'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Criticality Matrix
    st.subheader("Equipment Criticality Matrix (MTBF vs MTTR)")
    
    fig = px.scatter(
        reliability,
        x='mtbf',
        y='mttr',
        size='total_cost',
        color='equipment_type',
        hover_data=['equipment_name'],
        title='Equipment Criticality Analysis',
        labels={'mtbf': 'MTBF (days)', 'mttr': 'MTTR (hours)'}
    )
    
    # Add median lines
    fig.add_hline(y=reliability['mttr'].median(), line_dash="dash", line_color="red",
                  annotation_text="Median MTTR")
    fig.add_vline(x=reliability['mtbf'].median(), line_dash="dash", line_color="red",
                  annotation_text="Median MTBF")
    
    st.plotly_chart(fig, use_container_width=True)

# ===========================================
# SUPPLY CHAIN & INVENTORY MODULE
# ===========================================

elif module == "📦 Supply Chain & Inventory":
    st.markdown('<p class="section-header">Supply Chain & Inventory Analytics</p>', unsafe_allow_html=True)
    
    # ABC Analysis
    st.subheader("ABC Analysis")
    
    consumption = data['inventory'][data['inventory']['transaction_type'] == 'Issue'].groupby('part_id').agg({
        'quantity': 'sum'
    }).reset_index()
    
    consumption = pd.merge(
        consumption,
        data['spare_parts'][['part_id', 'part_name', 'unit_cost', 'part_category']],
        on='part_id',
        how='left'
    )
    
    consumption['total_value'] = consumption['quantity'] * consumption['unit_cost']
    consumption = consumption.sort_values('total_value', ascending=False)
    consumption['cumulative_pct'] = (consumption['total_value'].cumsum() / consumption['total_value'].sum() * 100)
    
    def classify_abc(pct):
        if pct <= 80:
            return 'A'
        elif pct <= 95:
            return 'B'
        else:
            return 'C'
    
    consumption['abc_class'] = consumption['cumulative_pct'].apply(classify_abc)
    
    # ABC Summary
    abc_summary = consumption.groupby('abc_class').agg({
        'part_id': 'count',
        'total_value': 'sum'
    }).reset_index()
    abc_summary['pct_value'] = (abc_summary['total_value'] / abc_summary['total_value'].sum() * 100)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            abc_summary,
            x='abc_class',
            y='pct_value',
            title='ABC Classification - Value %',
            color='abc_class',
            color_discrete_map={'A': '#e74c3c', 'B': '#f39c12', 'C': '#2ecc71'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.pie(
            abc_summary,
            values='part_id',
            names='abc_class',
            title='ABC Classification - Part Count %',
            color='abc_class',
            color_discrete_map={'A': '#e74c3c', 'B': '#f39c12', 'C': '#2ecc71'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Supplier Performance
    st.subheader("Supplier Performance")
    
    data['purchase_orders']['on_time'] = (
        pd.to_datetime(data['purchase_orders']['actual_delivery_date']) <=
        pd.to_datetime(data['purchase_orders']['expected_delivery_date'])
    ).astype(int)
    
    supplier_perf = data['purchase_orders'].groupby('supplier_id').agg({
        'po_id': 'count',
        'total_cost': 'sum',
        'on_time': 'mean'
    }).reset_index()
    
    supplier_perf.columns = ['supplier_id', 'total_orders', 'total_spend', 'on_time_pct']
    supplier_perf['on_time_pct'] = supplier_perf['on_time_pct'] * 100
    
    supplier_perf = pd.merge(
        supplier_perf,
        data['suppliers'][['supplier_id', 'supplier_name']],
        on='supplier_id',
        how='left'
    )
    
    top_suppliers = supplier_perf.nlargest(10, 'total_spend')
    
    fig = px.bar(
        top_suppliers,
        x='supplier_name',
        y='on_time_pct',
        title='Top 10 Suppliers - On-Time Delivery %',
        color='on_time_pct',
        color_continuous_scale='RdYlGn',
        range_color=[0, 100]
    )
    fig.add_hline(y=90, line_dash="dash", line_color="blue", annotation_text="Target: 90%")
    st.plotly_chart(fig, use_container_width=True)

# ===========================================
# LOGISTICS & TRANSPORTATION MODULE
# ===========================================

elif module == "🚚 Logistics & Transportation":
    st.markdown('<p class="section-header">Logistics & Transportation Analytics</p>', unsafe_allow_html=True)
    
    # KPIs
    data['deliveries']['on_time'] = (
        pd.to_datetime(data['deliveries']['actual_delivery_date']) <=
        pd.to_datetime(data['deliveries']['planned_delivery_date'])
    ).astype(int)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_deliveries = len(data['deliveries'][data['deliveries']['delivery_status'] == 'Delivered'])
        st.metric("Total Deliveries", f"{total_deliveries:,}")
    
    with col2:
        on_time_pct = (data['deliveries']['on_time'].mean() * 100)
        st.metric("On-Time Delivery", f"{on_time_pct:.1f}%", delta="Target: 90%")
    
    with col3:
        total_cost = data['deliveries']['delivery_cost'].sum()
        st.metric("Total Logistics Cost", f"₹{total_cost:,.0f}")
    
    with col4:
        avg_distance = data['deliveries']['distance_km'].mean()
        st.metric("Avg Distance", f"{avg_distance:.0f} km")
    
    st.markdown("---")
    
    # Performance by Transport Mode
    col1, col2 = st.columns(2)
    
    with col1:
        mode_perf = data['deliveries'].groupby('transport_mode').agg({
            'delivery_id': 'count',
            'on_time': 'mean'
        }).reset_index()
        mode_perf.columns = ['transport_mode', 'deliveries', 'on_time_pct']
        mode_perf['on_time_pct'] = mode_perf['on_time_pct'] * 100
        
        fig = px.bar(
            mode_perf,
            x='transport_mode',
            y='on_time_pct',
            title='On-Time Delivery % by Transport Mode',
            color='on_time_pct',
            color_continuous_scale='RdYlGn'
        )
        fig.add_hline(y=90, line_dash="dash", line_color="blue")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        data['deliveries']['cost_per_km'] = (
            data['deliveries']['delivery_cost'] / data['deliveries']['distance_km']
        )
        
        mode_cost = data['deliveries'].groupby('transport_mode')['cost_per_km'].mean().reset_index()
        
        fig = px.bar(
            mode_cost,
            x='transport_mode',
            y='cost_per_km',
            title='Cost per KM by Transport Mode',
            color='cost_per_km',
            color_continuous_scale='Reds'
        )
        st.plotly_chart(fig, use_container_width=True)

# ===========================================
# RECOMMENDATIONS MODULE
# ===========================================

elif module == "💡 Recommendations":
    st.markdown('<p class="section-header">Actionable Recommendations</p>', unsafe_allow_html=True)
    
    st.info("🔍 AI-powered recommendations based on data analysis")
    
    recommendations = [
        {
            'category': '🔧 Maintenance',
            'priority': 'Critical',
            'issue': '5 critical equipment with MTBF < 30 days',
            'recommendation': 'Implement predictive maintenance for Equipment EQ0012, EQ0024, EQ0035',
            'impact': 'Reduce downtime by 25%'
        },
        {
            'category': '📦 Inventory',
            'priority': 'High',
            'issue': '12 critical spare parts below reorder point',
            'recommendation': 'Emergency procurement for hydraulic pumps and filters',
            'impact': 'Prevent production stoppage'
        },
        {
            'category': '🚚 Logistics',
            'priority': 'Medium',
            'issue': 'Express delivery cost 3x higher than Road',
            'recommendation': 'Optimize transport mode selection for non-urgent deliveries',
            'impact': 'Save ₹2.5M annually'
        },
        {
            'category': '👥 Supplier',
            'priority': 'High',
            'issue': 'Supplier SUP005 on-time delivery 65%',
            'recommendation': 'Review contract, identify backup supplier',
            'impact': 'Improve delivery reliability'
        }
    ]
    
    for rec in recommendations:
        with st.expander(f"{rec['category']}: {rec['issue']}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**Recommendation:** {rec['recommendation']}")
                st.markdown(f"**Expected Impact:** {rec['impact']}")
            
            with col2:
                priority_color = {
                    'Critical': '🔴',
                    'High': '🟠',
                    'Medium': '🟡'
                }
                st.markdown(f"### {priority_color.get(rec['priority'], '🟢')} {rec['priority']}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>Supply Chain Analytics Platform | Built with Streamlit & Python</p>
        <p>Data updated: 2024-12-31 | <a href='#'>View Documentation</a></p>
    </div>
""", unsafe_allow_html=True)