
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout, export_data_table

# Page Setup
setup_page(title="Supply Chain Analytics", icon="📦")

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

st.markdown('<div class="premium-header">Supply Chain Optimization</div>', unsafe_allow_html=True)

# Optimization Metrics Row
eoq_results = analytics['supply_chain'].calculate_eoq_rop()
total_reorders = len(eoq_results)

col1, col2, col3, col4 = st.columns(4)
with col1:
    glass_card("SKUs Analyzed", f"{total_reorders}", "Active", "🔍", col=col1)
with col2:
    stock_health = analytics['supply_chain'].inventory_health_check()[1]
    if not stock_health.empty and not stock_health[stock_health['stock_status'] == 'Stock Out'].empty:
        stock_out_count = stock_health[stock_health['stock_status'] == 'Stock Out']['num_parts'].iloc[0]
    else:
        stock_out_count = 0
    glass_card("Stock-Out Events", f"{stock_out_count}", "-42%", "🚫", col=col2)
with col3:
    avg_eoq = eoq_results['eoq'].mean() if not eoq_results.empty else 0
    glass_card("Avg Order Qty", f"{avg_eoq:.0f} units", "Optimized", "⚖️", col=col3)
with col4:
    serv_level = 95
    glass_card("Target Service", f"{serv_level}%", "High Confidence", "🛡️", col=col4)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📉 Inventory Health", "🎯 Procurement Strategy", "📊 Demand Analysis"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        # Inventory Health Summary
        health_df, health_sum, _ = analytics['supply_chain'].inventory_health_check()
        if not health_df.empty:
            fig = px.sunburst(health_df, path=['stock_status', 'part_category'], values='current_stock',
                             title="Inventory Health Hierarchy", template="plotly_dark",
                             color='stock_status', 
                             color_discrete_map={'Healthy': '#00d2ff', 'Below Reorder Point': '#3a7bd5', 'Stock Out': '#ff4b4b', 'Excess Stock': '#a0a0c0'})
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("Click segments to drill down. **Critical** parts in 'Stock Out' or 'Below Reorder Point' need immediate attention to prevent production stoppages.", "info")
        else:
            st.info("No inventory data.")
    
    with col2:
        # Safety Stock vs Reorder Point
        if not eoq_results.empty:
            parts_eoq = pd.merge(eoq_results, analytics['raw_data']['spare_parts'][['part_id', 'part_name', 'part_category']], on='part_id')
            fig = px.scatter(parts_eoq.head(30), x='safety_stock', y='reorder_point_opt',
                            size='annual_demand', color='part_category',
                            title="Safety Stock vs Reorder Point (Top 30 SKUs)",
                            template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**Safety Stock** buffers against demand variability. **Reorder Point** = when to place new order. Higher values for critical items reduce stock-out risk but increase holding costs.", "trend")
        else:
            st.info("No EOQ analysis available.")
    
    # Inventory Turnover Analysis
    st.subheader("📦 Inventory Turnover Analysis")
    turnover_data = analytics['supply_chain'].inventory_turnover_analysis()
    if not turnover_data.empty:
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
    else:
        st.info("No turnover data available.")

with tab2:
    # EOQ Visualization
    st.subheader("Economic Order Quantity (EOQ) Analysis")
    insight_callout("**EOQ** minimizes total ordering + holding costs. Order quantity = √(2 × Annual Demand × Order Cost / Holding Cost). Use these optimized values for procurement planning.", "info")
    if not eoq_results.empty:
        # Re-merge parts_eoq if needed
        parts_eoq = pd.merge(eoq_results, analytics['raw_data']['spare_parts'][['part_id', 'part_name', 'part_category']], on='part_id')
        export_data_table(parts_eoq, "eoq_analysis.csv", "Export EOQ Data")
        st.dataframe(parts_eoq[['part_name', 'part_category', 'annual_demand', 'eoq', 'safety_stock', 'reorder_point_opt']].head(15).style.background_gradient(subset=['eoq'], cmap='Blues'), 
                     use_container_width=True)
    
    # Supplier Performance Scatter
    st.subheader("Supplier Performance Matrix")
    sup_perf = analytics['supply_chain'].supplier_performance_analysis()
    if not sup_perf.empty:
        export_data_table(sup_perf, "supplier_performance.csv", "Export Supplier Data")
        fig = px.scatter(sup_perf, x='avg_lead_time', y='on_time_delivery_pct',
                        size='total_spend', color='supplier_category',
                        hover_data=['supplier_name'], title="Supplier Reliability Matrix",
                        template="plotly_dark",
                        color_discrete_map={'Preferred': '#00d2ff', 'Acceptable': '#3a7bd5', 'Review Required': '#ff4b4b'})
        fig.add_hline(y=90, line_dash="dash", line_color="rgba(255,255,255,0.3)", annotation_text="90% OTD Target")
        st.plotly_chart(fig, use_container_width=True)
        
        review_suppliers = len(sup_perf[sup_perf['supplier_category'] == 'Review Required'])
        insight_callout(f"**{review_suppliers}** suppliers require performance review. Bottom-left quadrant = ideal (fast + reliable). Size = spend volume.", "warning" if review_suppliers > 0 else "success")
    else:
        st.info("No supplier performance data.")

with tab3:
    st.subheader("📊 Demand Pattern Analysis")
    monthly_demand, demand_stats = analytics['supply_chain'].demand_pattern_analysis()
    
    if not demand_stats.empty:
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
    else:
        st.info("No demand data available.")
    
    # Stock-Out Impact
    st.subheader("⚠️ Stock-Out Impact Analysis")
    _, stockout_freq, critical_stockouts = analytics['supply_chain'].stockout_impact_analysis()
    if not stockout_freq.empty:
        export_data_table(critical_stockouts, "critical_stockouts.csv", "Export Stock-Outs")
        fig = px.bar(stockout_freq.head(15), x='part_name', y='stockout_count', color='part_category',
                    title="Most Frequent Stock-Out Items", template="plotly_dark")
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        critical_count = len(critical_stockouts)
        insight_callout(f"**{critical_count}** critical parts have experienced stock-outs. Each stock-out can cause production delays costing 10-100x the part value.", "warning" if critical_count > 0 else "success")
