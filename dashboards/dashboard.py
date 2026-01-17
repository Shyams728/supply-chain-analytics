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
    page_title="Sophisticated Supply Chain Platform",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("dashboards/style.css")
except FileNotFoundError:
    pass # Fallback if CSS not found during initial setup

# Add src to path to import local modules
import os
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'src')))

from maintenance_analytics import MaintenanceAnalytics
from supply_chain_analytics import SupplyChainAnalytics
from logistics_analytics import LogisticsAnalytics

# Color palette matching style.css for use in Plotly/Python
COLORS = {
    '--primary-color': '#00d2ff',
    '--secondary-color': '#3a7bd5',
    '--glass-bg': 'rgba(255, 255, 255, 0.1)',
    '--glass-border': 'rgba(255, 255, 255, 0.2)',
}

def var(name):
    """Helper to simulate CSS variables in Python/Plotly"""
    return COLORS.get(name, '#000000')

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

@st.cache_resource
def initialize_analytics():
    """Initialize all analytics modules"""
    try:
        # Load raw data
        eq = pd.read_csv('data/equipment.csv')
        dt = pd.read_csv('data/equipment_downtime.csv')
        sp = pd.read_csv('data/spare_parts.csv')
        inv = pd.read_csv('data/inventory_transactions.csv')
        sup = pd.read_csv('data/suppliers.csv')
        po = pd.read_csv('data/purchase_orders.csv')
        wh = pd.read_csv('data/warehouses.csv')
        dl = pd.read_csv('data/delivery_orders.csv')
        
        # Initialize modules
        maint = MaintenanceAnalytics(eq, dt)
        sc = SupplyChainAnalytics(sp, inv, po, sup)
        log = LogisticsAnalytics(dl, wh)
        
        return {
            'maintenance': maint,
            'supply_chain': sc,
            'logistics': log,
            'raw_data': {
                'equipment': eq, 'downtime': dt, 'spare_parts': sp,
                'inventory': inv, 'suppliers': sup, 'purchase_orders': po,
                'warehouses': wh, 'deliveries': dl
            }
        }
    except Exception as e:
        st.error(f"Error initializing analytics: {str(e)}")
        return None

analytics = initialize_analytics()

if analytics is None:
    st.error("⚠️ Failed to load data or initialize modules.")
    st.stop()

# Helper for glass cards
def glass_card(title, value, delta=None, icon="📈"):
    delta_html = f'<span style="color: {"#00ff00" if "+" in str(delta) else "#ff4b4b"}; font-size: 0.8rem;">{delta}</span>' if delta else ""
    st.markdown(f"""
        <div class="glass-card metric-container">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.9rem; color: #a0a0c0;">{title}</span>
                <span>{icon}</span>
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; margin: 0.5rem 0;">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)

# ===========================================
# OVERVIEW DASHBOARD
# ===========================================

if "Overview" in module:
    st.markdown('<div class="premium-header">Executive Insights</div>', unsafe_allow_html=True)
    
    # KPIs Row
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate global metrics from modules
    maint_metrics = analytics['maintenance'].calculate_reliability_metrics()
    avg_avail = maint_metrics['availability_pct'].mean()
    total_downtime = analytics['maintenance'].merged_data['downtime_hours'].sum()
    
    with col1:
        glass_card("Asset Availability", f"{avg_avail:.1f}%", "+2.4%", "🛠️")
    with col2:
        glass_card("Operational Downtime", f"{total_downtime:,.0f}h", "-15%", "📉")
    with col3:
        _, sc_summary = analytics['supply_chain'].abc_analysis()
        inv_val = sc_summary['total_value'].sum() / 1e6
        glass_card("Inventory Value", f"₹{inv_val:.1f}M", "+5.2%", "📦")
    with col4:
        log_kpis, _, _ = analytics['logistics'].delivery_performance_analysis()
        glass_card("On-Time Delivery", f"{log_kpis['on_time_percentage']}%", "+1.8%", "🚚")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Visuals
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Monthly Downtime vs Availability Trend
        monthly_maint = analytics['maintenance'].maintenance_cost_analysis()['monthly_trend']
        monthly_maint['month'] = monthly_maint['month'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_maint['month'], y=monthly_maint['total_cost'],
                                 name='Maintenance Cost', line=dict(color=var('--primary-color'), width=4),
                                 fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.1)'))
        fig.update_layout(title="Maintenance Cost Dynamics", template="plotly_dark",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # ABC Distribution
        _, abc_sum = analytics['supply_chain'].abc_analysis()
        fig = px.pie(abc_sum, values='total_value', names='abc_class',
                    hole=0.6, color='abc_class',
                    color_discrete_map={'A': '#00d2ff', 'B': '#3a7bd5', 'C': '#2d2d44'})
        fig.update_layout(title="Inventory Pareto (ABC)", template="plotly_dark",
                          showlegend=False, paper_bgcolor='rgba(0,0,0,0)',
                          height=400, margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig, use_container_width=True)

# ===========================================
# MANUFACTURING & ENGINEERING MODULE
# ===========================================

elif "Manufacturing" in module:
    st.markdown('<div class="premium-header">Engineering Analytics</div>', unsafe_allow_html=True)
    
    # Advanced KPIs Row
    oee_data = analytics['maintenance'].calculate_oee_metrics()
    avg_oee = oee_data['oee_score'].mean()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        glass_card("Global OEE", f"{avg_oee:.1f}%", "+1.2%", "🎯")
    with col2:
        glass_card("Avg Availability", f"{(oee_data['oee_availability'].mean()*100):.1f}%", "+0.5%", "⏱️")
    with col3:
        glass_card("Avg Performance", f"{(oee_data['oee_performance'].mean()*100):.1f}%", "-0.2%", "⚡")
    with col4:
        glass_card("Avg Quality", f"{(oee_data['oee_quality'].mean()*100):.1f}%", "+0.1%", "💎")

    st.markdown("<br>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["📊 Performance Analysis", "🔬 Reliability Engineering"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            # OEE Breakdown by Equipment
            fig = px.bar(oee_data.head(15), x='equipment_name', y=['oee_availability', 'oee_performance', 'oee_quality'],
                        title="OEE Component Breakdown (Top 15 Assets)",
                        barmode='group', template="plotly_dark",
                        color_discrete_sequence=['#00d2ff', '#3a7bd5', '#1e1e2f'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Failure distribution
            fail_patterns = analytics['maintenance'].failure_pattern_analysis()
            fig = px.treemap(fail_patterns['by_type'], path=['failure_type'], values='failure_count',
                            title="Failure Mode Distribution", template="plotly_dark",
                            color='failure_count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns([1, 2])
        with col1:
            selected_eq = st.selectbox("Select Asset for Reliability Profile", 
                                       oee_data['equipment_name'].unique())
            eq_id = analytics['raw_data']['equipment'][analytics['raw_data']['equipment']['equipment_name'] == selected_eq]['equipment_id'].iloc[0]
            
            beta, eta = analytics['maintenance'].calculate_weibull_parameters(eq_id)
            
            if beta:
                st.markdown(f"### Weibull Parameters")
                st.markdown(f"**Shape (β):** {beta:.2f}")
                st.markdown(f"**Scale (η):** {eta:.1f} days")
                
                if beta < 1:
                    st.warning("⚠️ Infant Mortality Phase (Decreasing failure rate)")
                elif beta > 1.2:
                    st.error("🚨 Wear-out Phase (Increasing failure rate)")
                else:
                    st.success("✅ Useful Life Phase (Constant failure rate)")
            else:
                st.info("Insufficient failure data for Weibull fitting.")

        with col2:
            # Interactive MTBF vs MTTR Scatter
            metrics = analytics['maintenance'].calculate_reliability_metrics()
            fig = px.scatter(metrics, x='mtbf_days', y='mttr_hours', 
                            size='total_repair_cost', color='equipment_type',
                            hover_data=['equipment_name'], title="Equipment Criticality Matrix",
                            template="plotly_dark")
            fig.add_hline(y=metrics['mttr_hours'].median(), line_dash="dash", line_color="rgba(255,255,255,0.3)")
            fig.add_vline(x=metrics['mtbf_days'].median(), line_dash="dash", line_color="rgba(255,255,255,0.3)")
            st.plotly_chart(fig, use_container_width=True)

# ===========================================
# SUPPLY CHAIN & INVENTORY MODULE
# ===========================================

elif "Supply Chain" in module:
    st.markdown('<div class="premium-header">Supply Chain Optimization</div>', unsafe_allow_html=True)
    
    # Optimization Metrics Row
    eoq_results = analytics['supply_chain'].calculate_eoq_rop()
    total_reorders = len(eoq_results)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        glass_card("SKUs Analyzed", f"{total_reorders}", "Active", "🔍")
    with col2:
        stock_health = analytics['supply_chain'].inventory_health_check()[1]
        stock_out_count = stock_health[stock_health['stock_status'] == 'Stock Out']['num_parts'].iloc[0] if not stock_health[stock_health['stock_status'] == 'Stock Out'].empty else 0
        glass_card("Stock-Out Events", f"{stock_out_count}", "-42%", "🚫")
    with col3:
        avg_eoq = eoq_results['eoq'].mean()
        glass_card("Avg Order Qty", f"{avg_eoq:.0f} units", "Optimized", "⚖️")
    with col4:
        serv_level = 95
        glass_card("Target Service", f"{serv_level}%", "High Confidence", "🛡️")

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["📉 Inventory Health", "🎯 Procurement Strategy"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            # Inventory Health Summary
            health_df, health_sum, _ = analytics['supply_chain'].inventory_health_check()
            fig = px.sunburst(health_df, path=['stock_status', 'part_category'], values='current_stock',
                             title="Inventory Health Hierarchy", template="plotly_dark",
                             color='stock_status', 
                             color_discrete_map={'Healthy': '#00d2ff', 'Below Reorder Point': '#3a7bd5', 'Stock Out': '#1e1e2f', 'Excess Stock': '#a0a0c0'})
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Stock-Out Probability vs Safety Stock
            parts_eoq = pd.merge(eoq_results, analytics['raw_data']['spare_parts'][['part_id', 'part_name']], on='part_id')
            fig = px.scatter(parts_eoq.head(30), x='safety_stock', y='reorder_point_opt',
                            size='annual_demand', color='part_name',
                            title="Safety Stock vs Reorder Point (Top 30 SKUs)",
                            template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # EOQ Visualization
        st.subheader("Economic Order Quantity (EOQ) Analysis")
        st.dataframe(parts_eoq[['part_name', 'annual_demand', 'eoq', 'safety_stock', 'reorder_point_opt']].head(15), 
                     use_container_width=True)
        
        # Supplier Performance Scatter
        sup_perf = analytics['supply_chain'].supplier_performance_analysis()
        fig = px.scatter(sup_perf, x='avg_lead_time', y='on_time_delivery_pct',
                        size='total_spend', color='supplier_category',
                        hover_data=['supplier_name'], title="Supplier Reliability Matrix",
                        template="plotly_dark",
                        color_discrete_map={'Preferred': '#00d2ff', 'Acceptable': '#3a7bd5', 'Review Required': '#ff4b4b'})
        st.plotly_chart(fig, use_container_width=True)

# ===========================================
# LOGISTICS & TRANSPORTATION MODULE
# ===========================================

elif "Logistics" in module:
    st.markdown('<div class="premium-header">Logistics Intelligence</div>', unsafe_allow_html=True)
    
    kpis, mode_perf, monthly_perf = analytics['logistics'].delivery_performance_analysis()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        glass_card("Shipments", f"{kpis['total_deliveries']:,}", "Active", "📦")
    with col2:
        glass_card("On-Time", f"{kpis['on_time_percentage']}%", "-2.1%", "🕒")
    with col3:
        glass_card("Avg Lead Time", f"{kpis['avg_lead_time_days']:.1f}d", "-0.5d", "🚀")
    with col4:
        glass_card("Total Cost", f"₹{kpis['total_cost']/1e6:.1f}M", "+3.4%", "💰")

    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    with col1:
        # Mode distribution mapping
        fig = px.pie(mode_perf, values='total_deliveries', names='transport_mode',
                    title="Transport Mode Utilization", template="plotly_dark",
                    color_discrete_sequence=['#00d2ff', '#3a7bd5', '#1e1e2f'])
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Cost Efficiency
        fig = px.bar(mode_perf, x='transport_mode', y='cost_per_km',
                    title="Cost Efficiency by Mode (₹/km)", template="plotly_dark",
                    color='cost_per_km', color_continuous_scale='Blues')
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Route Optimization & Consolidation")
    opps = analytics['logistics'].route_consolidation_opportunities()
    st.dataframe(opps.head(10), use_container_width=True)

# ===========================================
# RECOMMENDATIONS MODULE
# ===========================================

elif "Recommendations" in module:
    st.markdown('<div class="premium-header">Intelligent Recommendations</div>', unsafe_allow_html=True)
    
    # Generate data-driven recommendations
    maint_recs = analytics['maintenance'].generate_maintenance_recommendations()
    sc_recs = analytics['supply_chain'].generate_procurement_recommendations()
    log_recs = analytics['logistics'].generate_logistics_recommendations()
    
    all_recs = pd.concat([
        maint_recs.assign(category='Maintenance'),
        sc_recs.assign(category='Supply Chain'),
        log_recs.assign(category='Logistics')
    ])
    
    st.markdown("### 🤖 Data-Driven Action Plan")
    
    for _, rec in all_recs.iterrows():
        priority = rec.get('priority', 'Medium')
        color = "🔴" if priority == "Critical" else "🟠" if priority == "High" else "🟡"
        
        with st.expander(f"{color} {rec.get('category')}: {rec.get('issue', 'Optimization Opportunity')}", expanded=(priority == "Critical")):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Recommendation:** {rec.get('recommendation')}")
                if 'impact' in rec:
                    st.markdown(f"**Potential Impact:** {rec['impact']}")
            with col2:
                st.info(f"Priority: {priority}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p>Supply Chain Analytics Platform | Built with Streamlit & Python</p>
        <p>Data updated: 2024-12-31 | <a href='#'>View Documentation</a></p>
    </div>
""", unsafe_allow_html=True)