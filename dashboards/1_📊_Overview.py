
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout, benchmark_card, var

# Page Setup - this must be the first Streamlit command
setup_page(title="Supply Chain Overview", icon="📊")

# 1. Load Raw Data
raw_data = load_raw_data()
if not raw_data:
    st.error("⚠️ Failed to load data.")
    st.stop()

# 2. Render Sidebar & Get Filters
filters = render_sidebar(raw_data)

# 3. Apply Filters
filtered_data = filter_data(raw_data, filters)

# 4. Initialize Analytics with Filtered Data
analytics = get_analytics(filtered_data)
if not analytics:
    st.error("⚠️ Failed to initialize analytics modules.")
    st.stop()

# Main content
st.markdown('<p class="main-header">🏭 Supply Chain Analytics Platform</p>', unsafe_allow_html=True)
st.markdown("**Manufacturing → Supply Chain → Logistics → Analytics**")

st.markdown('<div class="premium-header">Executive Insights</div>', unsafe_allow_html=True)

# KPIs Row
col1, col2, col3, col4 = st.columns(4)

# Calculate global metrics from modules
maint_metrics = analytics['maintenance'].calculate_reliability_metrics()
# Metrics might be empty if filter removes all data
if maint_metrics.empty:
    avg_avail = 0.0
    total_downtime = 0
else:
    avg_avail = maint_metrics['availability_pct'].mean()
    total_downtime = analytics['maintenance'].merged_data['downtime_hours'].sum()

with col1:
    glass_card("Asset Availability", f"{avg_avail:.1f}%", "+2.4%", "🛠️", col=col1)
with col2:
    glass_card("Operational Downtime", f"{total_downtime:,.0f}h", "-15%", "📉", col=col2)
with col3:
    _, sc_summary = analytics['supply_chain'].abc_analysis()
    inv_val = sc_summary['total_value'].sum() / 1e6 if not sc_summary.empty else 0
    glass_card("Inventory Value", f"₹{inv_val:.1f}M", "+5.2%", "📦", col=col3)
with col4:
    log_kpis, _, _ = analytics['logistics'].delivery_performance_analysis()
    on_time = log_kpis['on_time_percentage'] if log_kpis else 0
    glass_card("On-Time Delivery", f"{on_time}%", "+1.8%", "🚚", col=col4)

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
                    fill_rate['benchmark'], "📦", trend=1.5, col=col1)
with col2:
    benchmark_card("Perfect Order Rate", f"{por['perfect_order_rate']}%",
                    por['benchmark'], "✨", trend=0.8, col=col2)
with col3:
    benchmark_card("Inventory Health", f"{inv_health['overall_health_score']:.0f}/100",
                    {'status': inv_health['status'], 
                    'color': '#00d2ff' if inv_health['overall_health_score'] >= 70 else '#f0ad4e',
                    'icon': '🏥'},'🏥', trend= -2.1, col=col3)
with col4:
    avg_oee = oee_data['oee_score'].mean() if not oee_data.empty else 0
    benchmark_card("Avg OEE", f"{avg_oee:.1f}%",
                    {'status': 'World-Class' if avg_oee >= 85 else 'Good' if avg_oee >= 65 else 'Needs Work',
                    'color': '#00d2ff' if avg_oee >= 85 else '#5cb85c' if avg_oee >= 65 else '#f0ad4e',
                    'icon': '🎯'}, "⚙️", trend=+2.3, col=col4)

st.markdown("<br>", unsafe_allow_html=True)

# Main Visuals Row 1
col1, col2 = st.columns([2, 1])

with col1:
    # Monthly Maintenance Cost Trend
    monthly_maint = analytics['maintenance'].maintenance_cost_analysis()['monthly_trend']
    
    if not monthly_maint.empty:
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
    else:
        st.info("No maintenance data for selected period.")

with col2:
    # ABC Distribution
    _, abc_sum = analytics['supply_chain'].abc_analysis()
    if not abc_sum.empty:
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
    else:
        st.info("No inventory data found.")

# Row 2: Additional Insights
st.markdown("<br>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    # Failure Trend Mini-Chart
    fail_data = analytics['maintenance'].failure_pattern_analysis()['monthly_trend']
    if not fail_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=fail_data['month'].astype(str), y=fail_data['failure_count'],
                            marker_color='#3a7bd5', name='Failures'))
        fig.update_layout(title="Monthly Failure Events", template="plotly_dark",
                            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            height=250, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        insight_callout("Track failure frequency to identify problematic months. Spikes may indicate seasonal stress or scheduled maintenance gaps.", "info")
    else:
        st.info("No failure data.")

with col2:
    # Delivery Performance Gauge
    log_kpis, _, _ = analytics['logistics'].delivery_performance_analysis()
    if log_kpis:
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
    else:
        st.info("No logistics data.")

with col3:
    # Stock Health Summary
    _, health_sum, _ = analytics['supply_chain'].inventory_health_check()
    if not health_sum.empty:
        fig = px.bar(health_sum, x='stock_status', y='num_parts', color='stock_status',
                    color_discrete_map={'Healthy': '#00d2ff', 'Below Reorder Point': '#f0ad4e', 
                                        'Stock Out': '#ff4b4b', 'Excess Stock': '#9b59b6'},
                    title="Inventory Health Status")
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                            height=250, margin=dict(l=10, r=10, t=40, b=10), showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        stock_out = health_sum[health_sum['stock_status'] == 'Stock Out']['num_parts'].sum() if 'Stock Out' in health_sum['stock_status'].values else 0
        insight_callout(f"**{stock_out}** parts in stock-out. Prioritize replenishment for critical A-class items to prevent production delays.", "warning" if stock_out > 0 else "success")
    else:
        st.info("No inventory health data.")

# ==========================================
# Advanced Analytics Section (Predictive ML)
# ==========================================
st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="premium-header">Advanced Predictive Analytics</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### 🚨 Equipment Failure Risk (ML Model)")
    try:
        # Get predictions
        risk_data = analytics['maintenance'].get_failure_predictions()
        
        if risk_data is not None and not risk_data.empty:
            # Filter for high risk
            high_risk = risk_data[risk_data['risk_score'] > 50].head(10)
            
            if not high_risk.empty:
                # Gauge chart for average risk of top 5
                avg_high_risk = high_risk['risk_score'].mean()
                
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = avg_high_risk,
                    title = {'text': "Avg Risk (Top Critical Equip)"},
                    gauge = {
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "#ff4b4b"},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgreen"},
                            {'range': [50, 75], 'color': "yellow"},
                            {'range': [75, 100], 'color': "orange"}],
                    }))
                fig.update_layout(height=250, margin=dict(l=20, r=20, t=30, b=20),
                                  paper_bgcolor='rgba(0,0,0,0)', font=dict(color='white'))
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                st.dataframe(
                    high_risk[['equipment_id', 'equipment_type', 'risk_score', 'risk_category']],
                    use_container_width=True,
                    hide_index=True
                )
            else:
                st.success("✅ No high-risk equipment detected by ML model.")
        else:
            st.info("Training Predictive Model in background... Refresh shortly.")
    except Exception as e:
        st.warning(f"ML Module not ready: {str(e)}")

with col2:
    st.markdown("##### 📈 Integrated Demand Forecasting (AI)")
    try:
        # Get batch forecasts
        forecasts = analytics['supply_chain'].get_batch_forecasts(top_n=1)
        
        if forecasts:
            # Visualize the first one
            part_id = list(forecasts.keys())[0]
            fc_df = forecasts[part_id]
            
            fig = go.Figure()
            
            # Forecast line
            fig.add_trace(go.Scatter(
                x=fc_df['ds'], y=fc_df['yhat'],
                mode='lines+markers', name='Forecast',
                line=dict(color='#00d2ff', width=3)
            ))
            
            # Confidence Interval
            fig.add_trace(go.Scatter(
                x=pd.concat([fc_df['ds'], fc_df['ds'][::-1]]),
                y=pd.concat([fc_df['yhat_upper'], fc_df['yhat_lower'][::-1]]),
                fill='toself', fillcolor='rgba(0, 210, 255, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo="skip", showlegend=False
            ))
            
            fig.update_layout(
                title=f"Demand Forecast: {part_id}",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=350, margin=dict(l=20, r=20, t=40, b=20),
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            insight_callout(f"Forecast for **{part_id}** indicates a projected usage of **{fc_df['yhat'].iloc[-1]:.0f}** units next month. Ensure stock levels are adequate.", "trend")
        else:
            st.info("Insufficient data for forecasting.")
            
    except Exception as e:
        st.warning(f"Forecasting Module not ready: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d;'>
        <p style="font-size: 0.9rem;">🏭 Supply Chain Analytics Platform | Built with Streamlit & Python</p>
        <p style="font-size: 0.8rem; color: #555;">Data refreshed: Real-time | Powered by advanced analytics modules</p>
    </div>
""", unsafe_allow_html=True)
