
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout

# Page Setup
setup_page(title="Logistics Analytics", icon="🚚")

# 1. Load Raw Data
raw_data = load_raw_data()
if not raw_data:
    st.stop()

# 2. Render Sidebar & Get Filters
filters = render_sidebar(raw_data)

# 3. Apply Filters
filtered_data = filter_data(raw_data, filters)

# 4. Initialize Analytics
analytics = get_analytics(filtered_data)
if not analytics:
    st.stop()

st.markdown('<div class="premium-header">Logistics Intelligence</div>', unsafe_allow_html=True)

kpis, mode_perf, monthly_perf = analytics['logistics'].delivery_performance_analysis()

# Handle potential empty data
if kpis:
    total_deliveries = kpis['total_deliveries']
    on_time_pct = kpis['on_time_percentage']
    avg_lead_time = kpis['avg_lead_time_days']
    total_cost = kpis['total_cost']
else:
    total_deliveries = on_time_pct = avg_lead_time = total_cost = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    glass_card("Shipments", f"{total_deliveries:,}", "Active", "📦", col=col1)
with col2:
    glass_card("On-Time", f"{on_time_pct}%", "-2.1%", "🕒", col=col2)
with col3:
    glass_card("Avg Lead Time", f"{avg_lead_time:.1f}d", "-0.5d", "🚀", col=col3)
with col4:
    glass_card("Total Cost", f"₹{total_cost/1e6:.1f}M", "+3.4%", "💰", col=col4)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🚚 Delivery Performance", "📍 Warehouse Analysis", "💰 Cost Optimization"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        if not mode_perf.empty:
            # Mode distribution
            fig = px.pie(mode_perf, values='total_deliveries', names='transport_mode',
                        title="Transport Mode Utilization", template="plotly_dark",
                        color_discrete_sequence=['#00d2ff', '#3a7bd5', '#f0ad4e'])
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Mode mix affects cost and speed trade-offs. **Road** = flexible but expensive. **Rail** = cost-effective for bulk. **Air** = fastest but highest cost.", "info")
        else:
            st.info("No mode performance data.")
    
    with col2:
        if not mode_perf.empty:
            # Cost Efficiency by Mode
            fig = px.bar(mode_perf, x='transport_mode', y='cost_per_km',
                        title="Cost Efficiency by Mode (₹/km)", template="plotly_dark",
                        color='cost_per_km', color_continuous_scale='RdYlGn_r')
            st.plotly_chart(fig, use_container_width=True)
            if not mode_perf.empty:
                cheapest_mode = mode_perf.loc[mode_perf['cost_per_km'].idxmin(), 'transport_mode']
                insight_callout(f"**{cheapest_mode}** is most cost-effective per km. Consider shifting eligible shipments to this mode where delivery time permits.", "action")
        else:
            st.info("No cost efficiency data.")
    
    # Monthly Delivery Trend
    st.subheader("📈 Monthly Delivery Performance Trend")
    if not monthly_perf.empty:
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
    else:
        st.info("No monthly trend data.")

with tab2:
    st.subheader("📍 Warehouse Performance Analysis")
    wh_perf = analytics['logistics'].warehouse_performance_analysis()
    
    if not wh_perf.empty:
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
    else:
        st.info("No warehouse data.")

with tab3:
    st.subheader("💰 Cost Optimization Opportunities")
    cost_by_distance, expensive_routes, inefficient = analytics['logistics'].cost_optimization_analysis()
    
    if not cost_by_distance.empty:
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
            if not inefficient.empty:
                fig = px.box(inefficient, x='transport_mode', y='cost_per_km', 
                            title="Cost per KM Outliers by Mode", template="plotly_dark",
                            color='transport_mode', color_discrete_sequence=['#00d2ff', '#3a7bd5', '#f0ad4e'])
                st.plotly_chart(fig, use_container_width=True)
                insight_callout("Outliers in cost/km indicate inefficient routes. Investigate for consolidation or mode-switch opportunities.", "warning")
            else:
                st.info("No inefficient routes detected.")
    
    # Most Expensive Routes
    st.subheader("🔴 Most Expensive Routes (Review Required)")
    if not expensive_routes.empty:
        st.dataframe(expensive_routes.head(10).style.background_gradient(subset=['delivery_cost'], cmap='Reds'), use_container_width=True)
    else:
        st.success("No expensive routes identified.")

    # Route Consolidation Opportunities
    st.subheader("🔗 Route Consolidation Opportunities")
    opps = analytics['logistics'].route_consolidation_opportunities()
    if not opps.empty:
        st.dataframe(opps.head(10), use_container_width=True)
        insight_callout("Routes with multiple deliveries on same day to same destination can be consolidated to reduce trips and costs.", "action")
    else:
        st.info("No consolidation opportunities found.")
