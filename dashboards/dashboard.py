"""
Integrated Supply Chain Analytics Dashboard
Manufacturing → Supply Chain → Logistics → Analytics

Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
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
from advanced_analytics import AdvancedSupplyChainMetrics, TrendAnalysis

# Import enhanced components
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), 'dashboards')))
from enhanced_components import (
    benchmark_card, create_gauge_chart, create_radar_chart, 
    create_heatmap, create_waterfall_chart, create_bullet_chart,
    insight_box, metric_delta_card, create_sparkline, section_header
)

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
    # st.image("https://via.placeholder.com/150x50?text=Supply+Chain+Analytics", use_column_width=True)
    st.markdown("---")
    
    module = st.selectbox(
        "📊 Select Analysis Module",
        [
            "🏠 Overview Dashboard",
            "🔧 Manufacturing & Maintenance",
            "📦 Supply Chain & Inventory",
            "🚚 Logistics & Transportation",
            "🎯 Advanced KPIs & Insights",
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
        # Load raw data (Cache invalidated)
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
        
        # Initialize advanced analytics
        advanced = AdvancedSupplyChainMetrics(sp, inv, po, sup, dl)
        
        return {
            'maintenance': maint,
            'supply_chain': sc,
            'logistics': log,
            'advanced': advanced,
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

    # Second KPIs Row - Advanced Metrics
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate advanced metrics for overview
    fill_rate = analytics['advanced'].calculate_fill_rate()
    por = analytics['advanced'].calculate_perfect_order_rate()
    inv_health = analytics['advanced'].inventory_health_score()
    oee_data = analytics['maintenance'].calculate_oee_metrics()
    
    with col1:
        benchmark_card("Fill Rate", f"{fill_rate['fill_rate']}%", 
                      fill_rate['benchmark'], "📦", trend=1.5)
    with col2:
        benchmark_card("Perfect Order Rate", f"{por['perfect_order_rate']}%",
                      por['benchmark'], "✨", trend=0.8)
    with col3:
        benchmark_card("Inventory Health", f"{inv_health['overall_health_score']:.0f}/100",
                      {'status': inv_health['status'], 
                       'color': '#00d2ff' if inv_health['overall_health_score'] >= 70 else '#f0ad4e',
                       'icon': '🏥'}, trend= -2.1)
    with col4:
        avg_oee = oee_data['oee_score'].mean()
        benchmark_card("Avg OEE", f"{avg_oee:.1f}%",
                      {'status': 'World-Class' if avg_oee >= 85 else 'Good' if avg_oee >= 65 else 'Needs Work',
                       'color': '#00d2ff' if avg_oee >= 85 else '#5cb85c' if avg_oee >= 65 else '#f0ad4e',
                       'icon': '🎯'}, "⚙️", trend=+2.3)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Main Visuals Row 1
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Monthly Maintenance Cost Trend
        monthly_maint = analytics['maintenance'].maintenance_cost_analysis()['monthly_trend']
        monthly_maint['month'] = monthly_maint['month'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_maint['month'], y=monthly_maint['total_cost'],
                                 name='Maintenance Cost', line=dict(color=var('--primary-color'), width=4),
                                 fill='tozeroy', fillcolor='rgba(0, 210, 255, 0.1)'))
        # Add trend line
        z = np.polyfit(range(len(monthly_maint)), monthly_maint['total_cost'], 1)
        trend_line = np.poly1d(z)(range(len(monthly_maint)))
        fig.add_trace(go.Scatter(x=monthly_maint['month'], y=trend_line, name='Trend',
                                 line=dict(color='#ff6b6b', width=2, dash='dash')))
        fig.update_layout(title="Maintenance Cost Dynamics with Trend", template="plotly_dark",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=400, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig, use_container_width=True)
        
        # Insight for maintenance cost
        trend_direction = "upward ↗️" if z[0] > 0 else "downward ↘️"
        insight_callout(f"Maintenance costs show a **{trend_direction}** trend. The red dashed line indicates the overall direction—use this to forecast future spending and identify seasonal patterns.", "trend")

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
        
        # Insight for ABC analysis
        a_pct = (abc_sum[abc_sum['abc_class'] == 'A']['total_value'].sum() / abc_sum['total_value'].sum() * 100)
        insight_callout(f"**Class A** items represent ~{a_pct:.0f}% of inventory value. Focus procurement efforts here—these are your critical high-value SKUs.", "action")

    # Row 2: Additional Insights
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Failure Trend Mini-Chart
        fail_data = analytics['maintenance'].failure_pattern_analysis()['monthly_trend']
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fail_data['month'].astype(str), y=fail_data['failure_count'],
                            marker_color='#3a7bd5', name='Failures'))
        fig.update_layout(title="Monthly Failure Events", template="plotly_dark",
                          paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=250, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight_callout("Track failure frequency to identify problematic months. Spikes may indicate seasonal stress or scheduled maintenance gaps.", "info")
    
    with col2:
        # Delivery Performance Gauge
        log_kpis, _, _ = analytics['logistics'].delivery_performance_analysis()
        on_time = log_kpis['on_time_percentage']
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=on_time,
            delta={'reference': 95, 'increasing': {'color': '#00ff00'}, 'decreasing': {'color': '#ff4b4b'}},
            gauge={'axis': {'range': [0, 100]},
                   'bar': {'color': '#00d2ff'},
                   'steps': [{'range': [0, 80], 'color': '#2d2d44'},
                            {'range': [80, 95], 'color': '#3a7bd5'},
                            {'range': [95, 100], 'color': 'rgba(0,255,0,0.3)'}],
                   'threshold': {'line': {'color': '#ff6b6b', 'width': 2}, 'thickness': 0.75, 'value': 95}},
            title={'text': "On-Time Delivery %"}))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=250, margin=dict(l=10, r=10, t=60, b=10))
        st.plotly_chart(fig, use_container_width=True)
        insight_callout(f"Target is 95%. Current: {on_time}%. {'🎉 Above target!' if on_time >= 95 else '⚠️ Needs attention—review delayed routes.'}", "success" if on_time >= 95 else "warning")
    
    with col3:
        # Stock Health Summary
        _, health_sum, _ = analytics['supply_chain'].inventory_health_check()
        fig = px.bar(health_sum, x='stock_status', y='num_parts', color='stock_status',
                    color_discrete_map={'Healthy': '#00d2ff', 'Below Reorder Point': '#f0ad4e', 
                                       'Stock Out': '#ff4b4b', 'Excess Stock': '#9b59b6'},
                    title="Inventory Health Status")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          height=250, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        stock_out = health_sum[health_sum['stock_status'] == 'Stock Out']['num_parts'].sum() if 'Stock Out' in health_sum['stock_status'].values else 0
        insight_callout(f"**{stock_out}** parts in stock-out. Prioritize replenishment for critical A-class items to prevent production delays.", "warning" if stock_out > 0 else "success")

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
    
    tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "🔬 Reliability Engineering", "🚨 Risk Assessment"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            # OEE Breakdown by Equipment
            fig = px.bar(oee_data.head(15), x='equipment_name', y=['oee_availability', 'oee_performance', 'oee_quality'],
                        title="OEE Component Breakdown (Top 15 Assets)",
                        barmode='group', template="plotly_dark",
                        color_discrete_sequence=['#00d2ff', '#3a7bd5', '#1e1e2f'])
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**OEE = Availability × Performance × Quality**. World-class OEE is 85%. Assets with low availability need maintenance focus; low performance suggests speed losses; low quality indicates rework/defects.", "info")
        
        with col2:
            # Failure distribution
            fail_patterns = analytics['maintenance'].failure_pattern_analysis()
            fig = px.treemap(fail_patterns['by_type'], path=['failure_type'], values='failure_count',
                            title="Failure Mode Distribution", template="plotly_dark",
                            color='failure_count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
            top_failure = fail_patterns['by_type'].iloc[0]['failure_type']
            top_count = fail_patterns['by_type'].iloc[0]['failure_count']
            insight_callout(f"**'{top_failure}'** is the dominant failure mode ({top_count} events). Investigate root causes—consider implementing targeted preventive maintenance or design improvements.", "action")
        
        # Component Pareto Analysis
        st.subheader("Component Failure Pareto (80/20 Rule)")
        comp_data = fail_patterns['by_component'].head(10)
        fig = go.Figure()
        fig.add_trace(go.Bar(x=comp_data['component'], y=comp_data['failure_count'], name='Failures', marker_color='#3a7bd5'))
        cumsum = comp_data['failure_count'].cumsum() / comp_data['failure_count'].sum() * 100
        fig.add_trace(go.Scatter(x=comp_data['component'], y=cumsum, name='Cumulative %', yaxis='y2', line=dict(color='#ff6b6b', width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          yaxis2=dict(overlaying='y', side='right', range=[0, 105], title='Cumulative %'),
                          legend=dict(orientation='h', y=1.1), height=350)
        st.plotly_chart(fig, use_container_width=True)
        insight_callout("The Pareto chart shows which components cause 80% of failures. Focus maintenance resources on the first few bars to maximize reliability improvement.", "trend")

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
                    insight_callout("β < 1 means early-life failures. Check installation quality, burn-in processes, or manufacturing defects.", "warning")
                elif beta > 1.2:
                    st.error("🚨 Wear-out Phase (Increasing failure rate)")
                    insight_callout("β > 1.2 indicates aging/wear. Plan preventive replacement before reaching characteristic life (η).", "action")
                else:
                    st.success("✅ Useful Life Phase (Constant failure rate)")
                    insight_callout("β ≈ 1 means random failures. Condition-based monitoring is most effective here.", "success")
            else:
                st.info("Insufficient failure data for Weibull fitting.")

        with col2:
            # Interactive MTBF vs MTTR Scatter
            metrics = analytics['maintenance'].calculate_reliability_metrics()
            fig = px.scatter(metrics, x='mtbf_days', y='mttr_hours', 
                            size='total_repair_cost', color='equipment_type',
                            hover_data=['equipment_name'], title="Equipment Criticality Matrix (MTBF vs MTTR)",
                            template="plotly_dark")
            fig.add_hline(y=metrics['mttr_hours'].median(), line_dash="dash", line_color="rgba(255,255,255,0.3)")
            fig.add_vline(x=metrics['mtbf_days'].median(), line_dash="dash", line_color="rgba(255,255,255,0.3)")
            # Add quadrant annotations
            fig.add_annotation(x=metrics['mtbf_days'].max()*0.9, y=metrics['mttr_hours'].min()*1.1, text="LOW RISK", showarrow=False, font=dict(color="#5cb85c", size=12))
            fig.add_annotation(x=metrics['mtbf_days'].min()*1.1, y=metrics['mttr_hours'].max()*0.9, text="CRITICAL", showarrow=False, font=dict(color="#ff4b4b", size=12))
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**Criticality Matrix**: Top-left = CRITICAL (frequent failures, long repairs). Bottom-right = LOW RISK (reliable, quick repairs). Size = repair cost.", "info")
    
    with tab3:
        st.subheader("🚨 High-Risk Equipment Requiring Attention")
        high_risk = analytics['maintenance'].high_risk_equipment_identification(top_n=15)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            # Risk Score Bar Chart
            fig = px.bar(high_risk, x='equipment_name', y='risk_score', color='risk_score',
                        color_continuous_scale='Reds', title="Equipment Risk Score Ranking",
                        template="plotly_dark")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Risk Score = 40% failure frequency + 30% repair cost + 30% unavailability. Higher scores demand immediate action plans.", "action")
        
        with col2:
            # Risk by Equipment Type
            risk_by_type = high_risk.groupby('equipment_type')['risk_score'].mean().reset_index()
            fig = px.pie(risk_by_type, values='risk_score', names='equipment_type', title="Risk Distribution by Type",
                        template="plotly_dark", color_discrete_sequence=['#ff6b6b', '#f0ad4e', '#00d2ff', '#3a7bd5'])
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed Table
        st.dataframe(high_risk[['equipment_name', 'equipment_type', 'total_failures', 'mtbf_days', 'mttr_hours', 'availability_pct', 'risk_score']].style.background_gradient(subset=['risk_score'], cmap='Reds'), use_container_width=True)

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

    tab1, tab2, tab3 = st.tabs(["📉 Inventory Health", "🎯 Procurement Strategy", "📊 Demand Analysis"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            # Inventory Health Summary
            health_df, health_sum, _ = analytics['supply_chain'].inventory_health_check()
            fig = px.sunburst(health_df, path=['stock_status', 'part_category'], values='current_stock',
                             title="Inventory Health Hierarchy", template="plotly_dark",
                             color='stock_status', 
                             color_discrete_map={'Healthy': '#00d2ff', 'Below Reorder Point': '#3a7bd5', 'Stock Out': '#ff4b4b', 'Excess Stock': '#a0a0c0'})
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Click segments to drill down. **Critical** parts in 'Stock Out' or 'Below Reorder Point' need immediate attention to prevent production stoppages.", "info")
        
        with col2:
            # Safety Stock vs Reorder Point
            parts_eoq = pd.merge(eoq_results, analytics['raw_data']['spare_parts'][['part_id', 'part_name', 'part_category']], on='part_id')
            fig = px.scatter(parts_eoq.head(30), x='safety_stock', y='reorder_point_opt',
                            size='annual_demand', color='part_category',
                            title="Safety Stock vs Reorder Point (Top 30 SKUs)",
                            template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**Safety Stock** buffers against demand variability. **Reorder Point** = when to place new order. Higher values for critical items reduce stock-out risk but increase holding costs.", "trend")
        
        # Inventory Turnover Analysis
        st.subheader("📦 Inventory Turnover Analysis")
        turnover_data = analytics['supply_chain'].inventory_turnover_analysis()
        col1, col2 = st.columns([1, 1])
        with col1:
            # Movement Category Distribution
            movement_counts = turnover_data.groupby('movement_category').size().reset_index(name='count')
            fig = px.pie(movement_counts, values='count', names='movement_category', 
                        title="SKU Movement Classification",
                        color='movement_category',
                        color_discrete_map={'Fast Moving': '#00d2ff', 'Medium Moving': '#3a7bd5', 'Slow Moving': '#f0ad4e', 'No Data': '#888'},
                        template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**Fast Moving** (12+ turns/year): Keep readily available. **Slow Moving** (<4 turns): Review for obsolescence or overstocking.", "action")
        
        with col2:
            # Top Slow Movers (potential dead stock)
            slow_movers = turnover_data[turnover_data['movement_category'] == 'Slow Moving'].nlargest(10, 'avg_stock_level')
            if not slow_movers.empty:
                fig = px.bar(slow_movers, x='part_name', y='avg_stock_level', color='turnover_ratio',
                            color_continuous_scale='RdYlGn', title="Top 10 Slow-Moving Items (Potential Dead Stock)",
                            template="plotly_dark")
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)

    with tab2:
        # EOQ Visualization
        st.subheader("Economic Order Quantity (EOQ) Analysis")
        insight_callout("**EOQ** minimizes total ordering + holding costs. Order quantity = √(2 × Annual Demand × Order Cost / Holding Cost). Use these optimized values for procurement planning.", "info")
        st.dataframe(parts_eoq[['part_name', 'part_category', 'annual_demand', 'eoq', 'safety_stock', 'reorder_point_opt']].head(15).style.background_gradient(subset=['eoq'], cmap='Blues'), 
                     use_container_width=True)
        
        # Supplier Performance Scatter
        st.subheader("Supplier Performance Matrix")
        sup_perf = analytics['supply_chain'].supplier_performance_analysis()
        fig = px.scatter(sup_perf, x='avg_lead_time', y='on_time_delivery_pct',
                        size='total_spend', color='supplier_category',
                        hover_data=['supplier_name'], title="Supplier Reliability Matrix",
                        template="plotly_dark",
                        color_discrete_map={'Preferred': '#00d2ff', 'Acceptable': '#3a7bd5', 'Review Required': '#ff4b4b'})
        fig.add_hline(y=90, line_dash="dash", line_color="rgba(255,255,255,0.3)", annotation_text="90% OTD Target")
        st.plotly_chart(fig, use_container_width=True)
        
        review_suppliers = len(sup_perf[sup_perf['supplier_category'] == 'Review Required'])
        insight_callout(f"**{review_suppliers}** suppliers require performance review. Bottom-left quadrant = ideal (fast + reliable). Size = spend volume.", "warning" if review_suppliers > 0 else "success")

    with tab3:
        st.subheader("📊 Demand Pattern Analysis")
        monthly_demand, demand_stats = analytics['supply_chain'].demand_pattern_analysis()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # Demand Pattern Classification
            pattern_counts = demand_stats.groupby('demand_pattern').size().reset_index(name='count')
            fig = px.bar(pattern_counts, x='demand_pattern', y='count', color='demand_pattern',
                        color_discrete_map={'Stable': '#00d2ff', 'Moderate': '#f0ad4e', 'Erratic': '#ff4b4b'},
                        title="Demand Pattern Distribution", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**Stable** demand (CV<0.5): Use simple forecasting. **Erratic** (CV>1): Needs higher safety stock or intermittent demand models.", "trend")
        
        with col2:
            # CV Distribution
            fig = px.histogram(demand_stats, x='demand_cv', nbins=20, title="Demand Variability Distribution (CV)",
                              template="plotly_dark", color_discrete_sequence=['#3a7bd5'])
            fig.add_vline(x=0.5, line_dash="dash", line_color="#00ff00", annotation_text="Stable Threshold")
            fig.add_vline(x=1.0, line_dash="dash", line_color="#ff4b4b", annotation_text="Erratic Threshold")
            st.plotly_chart(fig, use_container_width=True)
        
        # Stock-Out Impact
        st.subheader("⚠️ Stock-Out Impact Analysis")
        _, stockout_freq, critical_stockouts = analytics['supply_chain'].stockout_impact_analysis()
        if not stockout_freq.empty:
            fig = px.bar(stockout_freq.head(15), x='part_name', y='stockout_count', color='part_category',
                        title="Most Frequent Stock-Out Items", template="plotly_dark")
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            critical_count = len(critical_stockouts)
            insight_callout(f"**{critical_count}** critical parts have experienced stock-outs. Each stock-out can cause production delays costing 10-100x the part value.", "warning" if critical_count > 0 else "success")

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
    
    tab1, tab2, tab3 = st.tabs(["🚚 Delivery Performance", "📍 Warehouse Analysis", "💰 Cost Optimization"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        with col1:
            # Mode distribution
            fig = px.pie(mode_perf, values='total_deliveries', names='transport_mode',
                        title="Transport Mode Utilization", template="plotly_dark",
                        color_discrete_sequence=['#00d2ff', '#3a7bd5', '#f0ad4e'])
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Mode mix affects cost and speed trade-offs. **Road** = flexible but expensive. **Rail** = cost-effective for bulk. **Air** = fastest but highest cost.", "info")
        
        with col2:
            # Cost Efficiency by Mode
            fig = px.bar(mode_perf, x='transport_mode', y='cost_per_km',
                        title="Cost Efficiency by Mode (₹/km)", template="plotly_dark",
                        color='cost_per_km', color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)
            cheapest_mode = mode_perf.loc[mode_perf['cost_per_km'].idxmin(), 'transport_mode']
            insight_callout(f"**{cheapest_mode}** is most cost-effective per km. Consider shifting eligible shipments to this mode where delivery time permits.", "action")
        
        # Monthly Delivery Trend
        st.subheader("📈 Monthly Delivery Performance Trend")
        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly_perf['month'].astype(str), y=monthly_perf['deliveries'],
                            name='Deliveries', marker_color='#3a7bd5'))
        fig.add_trace(go.Scatter(x=monthly_perf['month'].astype(str), y=monthly_perf['on_time_pct'],
                                name='On-Time %', yaxis='y2', line=dict(color='#00d2ff', width=3)))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                          yaxis2=dict(overlaying='y', side='right', range=[0, 105], title='On-Time %'),
                          legend=dict(orientation='h', y=1.1), height=350)
        st.plotly_chart(fig, use_container_width=True)
        insight_callout("Correlate delivery volume with on-time performance. Volume spikes often precede OTD drops—plan capacity accordingly.", "trend")

    with tab2:
        st.subheader("📍 Warehouse Performance Analysis")
        wh_perf = analytics['logistics'].warehouse_performance_analysis()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # Warehouse On-Time Performance
            fig = px.bar(wh_perf, x='warehouse_name', y='on_time_pct', color='on_time_pct',
                        color_continuous_scale='RdYlGn', title="On-Time Delivery by Warehouse",
                        template="plotly_dark")
            fig.add_hline(y=90, line_dash="dash", line_color="#ff6b6b", annotation_text="90% Target")
            st.plotly_chart(fig, use_container_width=True)
            below_target = len(wh_perf[wh_perf['on_time_pct'] < 90])
            insight_callout(f"**{below_target}** warehouses below 90% OTD. Focus on process improvements at lagging locations.", "warning" if below_target > 0 else "success")
        
        with col2:
            # Warehouse Shipment Volume
            fig = px.bar(wh_perf, x='warehouse_name', y='total_shipments', color='total_logistics_cost',
                        color_continuous_scale='Blues', title="Shipment Volume & Cost by Warehouse",
                        template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
        
        # Warehouse Comparison Table
        st.dataframe(wh_perf[['warehouse_name', 'location', 'total_shipments', 'on_time_pct', 'avg_delivery_distance', 'total_logistics_cost']].style.background_gradient(subset=['on_time_pct'], cmap='RdYlGn'), use_container_width=True)

    with tab3:
        st.subheader("💰 Cost Optimization Opportunities")
        cost_by_distance, expensive_routes, inefficient = analytics['logistics'].cost_optimization_analysis()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            # Cost by Distance Band
            fig = px.bar(cost_by_distance, x='distance_band', y='avg_cost', color='transport_mode',
                        barmode='group', title="Avg Cost by Distance Band & Mode",
                        template="plotly_dark", color_discrete_sequence=['#00d2ff', '#3a7bd5', '#f0ad4e'])
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Compare modes at each distance. Short hauls favor road; long hauls may benefit from rail. Optimize mode selection by distance.", "action")
        
        with col2:
            # Cost per KM Distribution
            fig = px.box(inefficient, x='transport_mode', y='cost_per_km', 
                        title="Cost per KM Outliers by Mode", template="plotly_dark",
                        color='transport_mode', color_discrete_sequence=['#00d2ff', '#3a7bd5', '#f0ad4e'])
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Outliers in cost/km indicate inefficient routes. Investigate for consolidation or mode-switch opportunities.", "warning")
        
        # Most Expensive Routes
        st.subheader("🔴 Most Expensive Routes (Review Required)")
        st.dataframe(expensive_routes.head(10).style.background_gradient(subset=['delivery_cost'], cmap='Reds'), use_container_width=True)
    
    # Route Consolidation Opportunities
    st.subheader("🔗 Route Consolidation Opportunities")
    opps = analytics['logistics'].route_consolidation_opportunities()
    st.dataframe(opps.head(10), use_container_width=True)
    insight_callout("Routes with multiple deliveries on same day to same destination can be consolidated to reduce trips and costs.", "action")

# ===========================================
# ADVANCED KPIs & INSIGHTS MODULE
# ===========================================

elif "Advanced KPIs" in module:
    section_header("Advanced KPIs & Strategic Insights", "Industry-benchmarked metrics with deep analytics")
    
    # Advanced KPIs Row 1
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate advanced metrics
    fill_rate_data = analytics['advanced'].calculate_fill_rate()
    por_data = analytics['advanced'].calculate_perfect_order_rate()
    c2c_data = analytics['advanced'].calculate_cash_to_cash_cycle()
    inv_health = analytics['advanced'].inventory_health_score()
    
    with col1:
        benchmark_card("Fill Rate", f"{fill_rate_data['fill_rate']}%", 
                      fill_rate_data['benchmark'], "📦", trend=2.1)
    with col2:
        benchmark_card("Perfect Order Rate", f"{por_data['perfect_order_rate']}%",
                      por_data['benchmark'], "✨", trend=-0.5)
    with col3:
        benchmark_card("Cash-to-Cash Cycle", f"{c2c_data['cash_to_cash_days']} days",
                      {'status': 'Good' if c2c_data['cash_to_cash_days'] < 30 else 'Review', 
                       'color': '#5cb85c' if c2c_data['cash_to_cash_days'] < 30 else '#f0ad4e', 'icon': '📊'}, 
                      "💰", trend=-3.2)
    with col4:
        benchmark_card("Inventory Health", f"{inv_health['overall_health_score']}/100",
                      {'status': inv_health['status'], 
                       'color': '#00d2ff' if inv_health['overall_health_score'] >= 70 else '#f0ad4e', 
                       'icon': '🏥'}, trend= -2.1)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Radar", "🎯 Supplier Risk", "📅 Seasonality", "🔬 Deep Analysis"])
    
    with tab1:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Performance Radar Chart
            maint_metrics = analytics['maintenance'].calculate_reliability_metrics()
            log_kpis, _, _ = analytics['logistics'].delivery_performance_analysis()
            
            categories = ['Fill Rate', 'Perfect Order', 'On-Time Delivery', 
                         'Inventory Health', 'Equipment Availability']
            values = [
                fill_rate_data['fill_rate'],
                por_data['perfect_order_rate'],
                log_kpis['on_time_percentage'],
                inv_health['overall_health_score'],
                maint_metrics['availability_pct'].mean()
            ]
            
            fig = create_radar_chart(categories, values, "Supply Chain Performance Radar")
            st.plotly_chart(fig, use_container_width=True)
            insight_box("The radar chart shows your performance across 5 key dimensions vs industry benchmark (dashed line at 85%). Areas inside the benchmark need improvement.", "info")
        
        with col2:
            # Days of Supply Distribution
            dos_df = analytics['advanced'].calculate_days_of_supply()
            dos_status_counts = dos_df['dos_status'].value_counts().reset_index()
            dos_status_counts.columns = ['Status', 'Count']
            
            fig = px.pie(dos_status_counts, values='Count', names='Status', 
                        title="Days of Supply Distribution",
                        color='Status',
                        color_discrete_map={
                            'Critical - Reorder Now': '#ff4b4b',
                            'Low - Monitor Closely': '#f0ad4e',
                            'Optimal': '#00d2ff',
                            'High - Review Needed': '#3a7bd5',
                            'Excess - Reduce': '#888'
                        },
                        hole=0.5,
                        template="plotly_dark")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig, use_container_width=True)
            
            critical_count = len(dos_df[dos_df['dos_status'] == 'Critical - Reorder Now'])
            excess_count = len(dos_df[dos_df['dos_status'] == 'Excess - Reduce'])
            insight_box(f"**{critical_count}** items need immediate reorder. **{excess_count}** items have excess stock tying up working capital.", 
                       "warning" if critical_count > 5 else "success")
        
        # Cash-to-Cash Waterfall
        st.subheader("💰 Cash-to-Cash Cycle Breakdown")
        waterfall_categories = ['Days Inventory', 'Days Sales', 'Days Payable', 'Net C2C Cycle']
        waterfall_values = [c2c_data['days_inventory_outstanding'], 0, 
                           -c2c_data['days_payable_outstanding'], c2c_data['cash_to_cash_days']]
        fig = create_waterfall_chart(waterfall_categories, waterfall_values, "Working Capital Cycle Components")
        st.plotly_chart(fig, use_container_width=True)
        insight_box("Lower Cash-to-Cash cycle = less working capital tied up. Reduce by shortening inventory days or extending payment terms.", "trend")
    
    with tab2:
        st.subheader("🎯 Supplier Risk Assessment")
        
        supplier_risk = analytics['advanced'].calculate_supplier_risk_score()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Supplier Risk Matrix
            fig = px.scatter(supplier_risk, x='on_time_pct', y='lead_time_variability',
                            size='total_spend', color='risk_category',
                            hover_data=['supplier_name', 'total_orders'],
                            title="Supplier Risk Matrix (OTD vs Lead Time Variability)",
                            color_discrete_map={
                                'Low Risk': '#5cb85c',
                                'Medium Risk': '#f0ad4e',
                                'High Risk': '#ff6b6b',
                                'Critical Risk': '#ff4b4b'
                            },
                            template="plotly_dark")
            fig.add_hline(y=supplier_risk['lead_time_variability'].median(), 
                         line_dash="dash", line_color="rgba(255,255,255,0.3)")
            fig.add_vline(x=90, line_dash="dash", line_color="rgba(255,255,255,0.3)",
                         annotation_text="90% OTD Target")
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig, use_container_width=True)
            insight_box("Bottom-right = BEST (high OTD, low variability). Top-left = RISKY. Size = spend volume.", "info")
        
        with col2:
            st.markdown("### Risk Distribution")
            risk_counts = supplier_risk['risk_category'].value_counts()
            for category in ['Low Risk', 'Medium Risk', 'High Risk', 'Critical Risk']:
                count = risk_counts.get(category, 0)
                color = {'Low Risk': '🟢', 'Medium Risk': '🟡', 'High Risk': '🟠', 'Critical Risk': '🔴'}[category]
                st.markdown(f"{color} **{category}**: {count} suppliers")
            
            st.markdown("---")
            st.markdown("### Top Risk Suppliers")
            for _, sup in supplier_risk.head(3).iterrows():
                st.markdown(f"⚠️ **{sup['supplier_name']}**: Risk Score {sup['risk_score']:.0f}")
        
        # Detailed Supplier Table
        st.dataframe(
            supplier_risk[['supplier_name', 'total_orders', 'total_spend', 'on_time_pct', 
                          'lead_time_variability', 'risk_score', 'risk_category']]
            .style.background_gradient(subset=['risk_score'], cmap='Reds'),
            use_container_width=True
        )
    
    with tab3:
        st.subheader("📅 Seasonal Demand Analysis")
        
        seasonal_data = analytics['advanced'].seasonal_demand_analysis()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Monthly Seasonality Chart
            monthly = seasonal_data['monthly_data']
            fig = go.Figure()
            fig.add_trace(go.Bar(x=monthly['month_name'], y=monthly['quantity'],
                                marker_color='#3a7bd5', name='Demand'))
            fig.add_trace(go.Scatter(x=monthly['month_name'], y=[seasonal_data['average_monthly_demand']]*len(monthly),
                                    mode='lines', name='Average', 
                                    line=dict(color='#f0ad4e', width=2, dash='dash')))
            fig.add_trace(go.Scatter(x=monthly['month_name'], y=monthly['seasonality_index'],
                                    mode='lines+markers', name='Seasonality Index', yaxis='y2',
                                    line=dict(color='#00d2ff', width=3)))
            fig.update_layout(
                title="Monthly Demand Pattern & Seasonality Index",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                yaxis2=dict(overlaying='y', side='right', title='Index (100=Avg)'),
                legend=dict(orientation='h', y=1.1),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("### Seasonality Insights")
            st.metric("Peak Month", seasonal_data['peak_month'], f"{seasonal_data['peak_demand']:,.0f} units")
            st.metric("Low Month", seasonal_data['low_month'], f"{seasonal_data['low_demand']:,.0f} units")
            st.metric("Demand Variability", f"{seasonal_data['demand_variability_cv']:.1f}%", 
                     seasonal_data['seasonality_strength'])
            
            insight_box(f"Demand variability is **{seasonal_data['seasonality_strength']}**. Plan inventory buffers for peak months and reduce stock before low periods.", "trend")
    
    with tab4:
        st.subheader("🔬 Deep Analytics")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Correlation Heatmap
            corr_matrix = analytics['advanced'].correlation_analysis()
            fig = create_heatmap(corr_matrix, "Metric Correlation Matrix")
            st.plotly_chart(fig, use_container_width=True)
            insight_box("Strong correlations (close to 1 or -1) suggest linked metrics. Use this to predict one metric from another.", "info")
        
        with col2:
            # Anomaly Detection
            st.markdown("### 🚨 Anomaly Detection")
            anomalies = analytics['advanced'].anomaly_detection()
            
            for anomaly_type, details in anomalies.items():
                with st.expander(f"📊 {anomaly_type.replace('_', ' ').title()} Anomalies ({details['count']} found)"):
                    st.markdown(f"**Interpretation:** {details['interpretation']}")
                    if 'periods' in details and details['periods']:
                        st.markdown(f"**Affected periods:** {', '.join(details['periods'][:5])}")
                    if 'parts' in details and details['parts']:
                        st.markdown(f"**Affected parts:** {', '.join(details['parts'][:5])}")
        
        # What-If Scenario Analysis
        st.markdown("---")
        st.subheader("🔮 What-If Scenario Analysis")
        
        scenario_col1, scenario_col2 = st.columns([1, 2])
        
        with scenario_col1:
            scenario = st.selectbox("Select Scenario", 
                                   ['demand_increase', 'lead_time_increase', 'cost_increase', 'supplier_failure'])
            if scenario != 'supplier_failure':
                change_pct = st.slider("Change %", 5, 50, 20)
            else:
                change_pct = 0
        
        with scenario_col2:
            if scenario == 'supplier_failure':
                result = analytics['advanced'].what_if_analysis(scenario)
            else:
                result = analytics['advanced'].what_if_analysis(scenario, change_pct)
            
            st.markdown(f"### 📋 Scenario: {result.get('scenario', scenario)}")
            
            for key, value in result.items():
                if key not in ['scenario', 'recommendation']:
                    st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
            
            if 'recommendation' in result:
                insight_box(f"**Recommendation:** {result['recommendation']}", "action")

# ===========================================
# PREDICTIVE ANALYTICS MODULE  
# ===========================================

elif "Predictive" in module:
    st.markdown('<div class="premium-header">Predictive Analytics & Forecasting</div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["🔮 Maintenance Forecast", "📈 Demand Prediction", "⚡ Actionable Insights"])
    
    with tab1:
        st.subheader("🔮 Maintenance Cost Forecasting")
        insight_callout("These forecasts use historical trends. For production use, consider implementing ML models (ARIMA, Prophet) for better accuracy.", "info")
        
        # Historical maintenance cost trend with forecast
        monthly_maint = analytics['maintenance'].maintenance_cost_analysis()['monthly_trend']
        monthly_maint['month'] = monthly_maint['month'].astype(str)
        
        # Simple linear projection for next 6 months
        x = np.arange(len(monthly_maint))
        z = np.polyfit(x, monthly_maint['total_cost'], 1)
        
        # Forecast next 6 periods
        future_x = np.arange(len(monthly_maint), len(monthly_maint) + 6)
        forecast_values = np.poly1d(z)(future_x)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure()
            # Historical data
            fig.add_trace(go.Scatter(x=monthly_maint['month'], y=monthly_maint['total_cost'],
                                     name='Historical', line=dict(color='#00d2ff', width=3)))
            # Forecast
            future_months = [f"2025-{i:02d}" for i in range(1, 7)]
            fig.add_trace(go.Scatter(x=future_months, y=forecast_values,
                                     name='Forecast', line=dict(color='#ff6b6b', width=3, dash='dash'),
                                     fill='tozeroy', fillcolor='rgba(255, 107, 107, 0.1)'))
            fig.update_layout(title="Maintenance Cost: Historical + 6-Month Forecast", template="plotly_dark",
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Forecast Summary
            monthly_change = z[0]
            direction = "increasing" if monthly_change > 0 else "decreasing"
            st.metric("Monthly Trend", f"₹{abs(monthly_change):,.0f}", delta=f"{direction}")
            st.metric("6-Month Forecast Total", f"₹{sum(forecast_values):,.0f}")
            st.metric("Avg Forecast Monthly", f"₹{np.mean(forecast_values):,.0f}")
            
            insight_callout(f"Costs are **{direction}** at ₹{abs(monthly_change):,.0f}/month. Plan budget accordingly.", "trend")
        
        # Failure Prediction by Equipment Type
        st.subheader("🛠️ Equipment Failure Risk Projection")
        metrics = analytics['maintenance'].calculate_reliability_metrics()
        high_risk = metrics.nlargest(10, 'total_failures')
        
        fig = px.scatter(high_risk, x='mtbf_days', y='total_failures', size='total_repair_cost',
                        color='equipment_type', hover_data=['equipment_name'],
                        title="Failure Risk Map (Lower MTBF = Higher Risk)",
                        template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        insight_callout("Equipment with low MTBF and high failure count should be prioritized for predictive maintenance programs or replacement.", "action")

    with tab2:
        st.subheader("📈 Inventory Demand Forecasting")
        
        monthly_demand, demand_stats = analytics['supply_chain'].demand_pattern_analysis()
        
        # Show demand for top consumed parts
        top_parts = demand_stats.nlargest(5, 'avg_monthly_demand')
        part_ids = top_parts['part_id'].tolist()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure()
            for pid in part_ids[:3]:  # Show top 3
                part_data = monthly_demand[monthly_demand['part_id'] == pid]
                part_name = part_data['part_name'].iloc[0] if not part_data.empty else f"Part {pid}"
                fig.add_trace(go.Scatter(x=part_data['month'].astype(str), y=part_data['quantity'],
                                        name=part_name, mode='lines+markers'))
            fig.update_layout(title="Top 3 Parts: Monthly Consumption Trend", template="plotly_dark",
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Analyze consumption patterns to set optimal reorder points. Seasonal patterns may require safety stock adjustments.", "trend")
        
        with col2:
            st.markdown("### Demand Variability Alert")
            erratic_parts = demand_stats[demand_stats['demand_pattern'] == 'Erratic']
            st.metric("Erratic Demand Parts", len(erratic_parts))
            if not erratic_parts.empty:
                st.warning(f"⚠️ {len(erratic_parts)} parts have erratic demand (CV > 1.0). Consider intermittent demand models or vendor-managed inventory.")
            else:
                st.success("✅ No parts with critically erratic demand.")

    with tab3:
        st.subheader("⚡ Key Predictive Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Maintenance Insight
            high_risk_eq = analytics['maintenance'].high_risk_equipment_identification(top_n=5)
            st.markdown("### 🔧 Maintenance Alerts")
            for _, eq in high_risk_eq.iterrows():
                risk_level = "🔴" if eq['risk_score'] > 70 else "🟠" if eq['risk_score'] > 50 else "🟡"
                st.markdown(f"{risk_level} **{eq['equipment_name']}**: Risk {eq['risk_score']:.0f}%")
            insight_callout("Schedule preventive maintenance for red/orange items within 30 days.", "action")
        
        with col2:
            # Inventory Insight
            _, stockout_freq, _ = analytics['supply_chain'].stockout_impact_analysis()
            st.markdown("### 📦 Inventory Alerts")
            if not stockout_freq.empty:
                for _, part in stockout_freq.head(5).iterrows():
                    freq_level = "🔴" if part['stockout_count'] > 5 else "🟠" if part['stockout_count'] > 2 else "🟡"
                    st.markdown(f"{freq_level} **{part['part_name']}**: {part['stockout_count']} stock-outs")
            insight_callout("Increase safety stock or negotiate faster lead times for high-frequency stock-out items.", "warning")
        
        with col3:
            # Logistics Insight
            wh_perf = analytics['logistics'].warehouse_performance_analysis()
            st.markdown("### 🚚 Logistics Alerts")
            low_perf_wh = wh_perf[wh_perf['on_time_pct'] < 85]
            if not low_perf_wh.empty:
                for _, wh in low_perf_wh.iterrows():
                    st.markdown(f"🔴 **{wh['warehouse_name']}**: {wh['on_time_pct']:.1f}% OTD")
            else:
                st.success("✅ All warehouses above 85% OTD")
            insight_callout("Low OTD warehouses need process audits—check picking, packing, and carrier performance.", "action")

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
    
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    critical_count = len(all_recs[all_recs.get('priority', pd.Series()) == 'Critical']) if 'priority' in all_recs.columns else 0
    high_count = len(all_recs[all_recs.get('priority', pd.Series()) == 'High']) if 'priority' in all_recs.columns else 0
    
    with col1:
        glass_card("Total Recommendations", f"{len(all_recs)}", "Active", "📋")
    with col2:
        glass_card("Critical Items", f"{critical_count}", "Immediate", "🔴")
    with col3:
        glass_card("High Priority", f"{high_count}", "This Week", "🟠")
    with col4:
        glass_card("Categories", "3", "Domains", "📊")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Priority Distribution Chart
    col1, col2 = st.columns([1, 2])
    with col1:
        if 'priority' in all_recs.columns:
            priority_counts = all_recs['priority'].value_counts().reset_index()
            priority_counts.columns = ['priority', 'count']
            fig = px.pie(priority_counts, values='count', names='priority', 
                        title="Recommendations by Priority",
                        color='priority', 
                        color_discrete_map={'Critical': '#ff4b4b', 'High': '#f0ad4e', 'Medium': '#00d2ff', 'Low': '#5cb85c'},
                        template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Category Filter
        category_filter = st.multiselect("Filter by Category", ['All', 'Maintenance', 'Supply Chain', 'Logistics'], default=['All'])
        priority_filter = st.multiselect("Filter by Priority", ['All', 'Critical', 'High', 'Medium', 'Low'], default=['All'])
    
    st.markdown("### 🤖 Data-Driven Action Plan")
    insight_callout("Recommendations are auto-generated based on data analysis. Critical items require immediate attention; High items within 7 days.", "info")
    
    filtered_recs = all_recs.copy()
    if 'All' not in category_filter:
        filtered_recs = filtered_recs[filtered_recs['category'].isin(category_filter)]
    if 'All' not in priority_filter and 'priority' in filtered_recs.columns:
        filtered_recs = filtered_recs[filtered_recs['priority'].isin(priority_filter)]
    
    for _, rec in filtered_recs.iterrows():
        priority = rec.get('priority', 'Medium')
        color = "🔴" if priority == "Critical" else "🟠" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
        
        with st.expander(f"{color} {rec.get('category')}: {rec.get('issue', 'Optimization Opportunity')}", expanded=(priority == "Critical")):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**Recommendation:** {rec.get('recommendation')}")
                if 'impact' in rec and pd.notna(rec['impact']):
                    st.markdown(f"**Potential Impact:** {rec['impact']}")
            with col2:
                priority_color = "#ff4b4b" if priority == "Critical" else "#f0ad4e" if priority == "High" else "#00d2ff"
                st.markdown(f"""
                    <div style="background: {priority_color}; padding: 10px; border-radius: 8px; text-align: center;">
                        <strong style="color: white;">{priority}</strong>
                    </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p style="font-size: 0.9rem;">🏭 Supply Chain Analytics Platform | Built with Streamlit & Python</p>
        <p style="font-size: 0.8rem; color: #555;">Data refreshed: Real-time | Powered by advanced analytics modules</p>
        <p style="font-size: 0.75rem; margin-top: 10px;">
            💡 <strong>Chart Reading Tips:</strong> Hover for details • Click legends to filter • Use filters for focused analysis
        </p>
    </div>
""", unsafe_allow_html=True)