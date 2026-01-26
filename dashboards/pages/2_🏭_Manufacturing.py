
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout, var, create_gantt_chart, export_data_table

# Page Setup
setup_page(title="Manufacturing Analytics", icon="🏭")

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

st.markdown('<div class="premium-header">Engineering Analytics</div>', unsafe_allow_html=True)

# Advanced KPIs Row
oee_data = analytics['maintenance'].calculate_oee_metrics()

if not oee_data.empty:
    avg_oee = oee_data['oee_score'].mean()
    avg_avail = oee_data['oee_availability'].mean() * 100
    avg_perf = oee_data['oee_performance'].mean() * 100
    avg_qual = oee_data['oee_quality'].mean() * 100
else:
    avg_oee = avg_avail = avg_perf = avg_qual = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    glass_card("Global OEE", f"{avg_oee:.1f}%", "+1.2%", "🎯", col=col1)
with col2:
    glass_card("Avg Availability", f"{avg_avail:.1f}%", "+0.5%", "⏱️", col=col2)
with col3:
    glass_card("Avg Performance", f"{avg_perf:.1f}%", "-0.2%", "⚡", col=col3)
with col4:
    glass_card("Avg Quality", f"{avg_qual:.1f}%", "+0.1%", "💎", col=col4)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📊 Performance", "🔬 Reliability", "🚨 Risk Analysis", "🛠️ RCM Analysis", "📅 Scheduler", "📡 Condition Monitor"])

with tab1:
    col1, col2 = st.columns([1, 1])
    with col1:
        if not oee_data.empty:
            # OEE Breakdown by Equipment
            fig = px.bar(oee_data.head(15), x='equipment_name', y=['oee_availability', 'oee_performance', 'oee_quality'],
                        title="OEE Component Breakdown (Top 15 Assets)",
                        barmode='group', template="plotly_dark",
                        color_discrete_sequence=['#00d2ff', '#3a7bd5', '#1e1e2f'])
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            insight_callout("**OEE = Availability × Performance × Quality**. World-class OEE is 85%. Assets with low availability need maintenance focus; low performance suggests speed losses; low quality indicates rework/defects.", "info")
        else:
            st.info("No OEE data available.")
    
    with col2:
        # Failure distribution
        fail_patterns = analytics['maintenance'].failure_pattern_analysis()
        if not fail_patterns['by_type'].empty:
            fig = px.treemap(fail_patterns['by_type'], path=['failure_type'], values='failure_count',
                            title="Failure Mode Distribution", template="plotly_dark",
                            color='failure_count', color_continuous_scale='Blues')
            st.plotly_chart(fig, use_container_width=True)
            top_failure = fail_patterns['by_type'].iloc[0]['failure_type']
            top_count = fail_patterns['by_type'].iloc[0]['failure_count']
            insight_callout(f"**'{top_failure}'** is the dominant failure mode ({top_count} events). Investigate root causes—consider implementing targeted preventive maintenance or design improvements.", "action")
        else:
            st.info("No failure data available.")
    
    # Component Pareto Analysis
    st.subheader("Component Failure Pareto (80/20 Rule)")
    if not fail_patterns['by_component'].empty:
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
    else:
        st.info("No component failure data.")

with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        if not oee_data.empty:
            selected_eq = st.selectbox("Select Asset for Reliability Profile", 
                                    oee_data['equipment_name'].unique())
            # Find ID
            eq_row = analytics['raw_data']['equipment'][analytics['raw_data']['equipment']['equipment_name'] == selected_eq]
            if not eq_row.empty:
                eq_id = eq_row['equipment_id'].iloc[0]
                
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
            else:
                st.warning("Equipment ID not found.")
        else:
            st.info("No equipment data.")

    with col2:
        # Interactive MTBF vs MTTR Scatter
        metrics = analytics['maintenance'].calculate_reliability_metrics()
        if not metrics.empty:
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
        else:
            st.info("No reliability metrics.")

with tab3:
    st.subheader("🚨 High-Risk Equipment Requiring Attention")
    high_risk = analytics['maintenance'].high_risk_equipment_identification(top_n=15)
    
    if not high_risk.empty:
        export_data_table(high_risk, "high_risk_equipment.csv", "Export High Risk List")
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
    else:
        st.success("No high-risk equipment identified!")

with tab4:
    st.subheader("🛠️ Reliability Centered Maintenance (RCM)")
    rcm_analysis = analytics['maintenance'].rcm_failure_mode_prioritization()
    
    if not rcm_analysis.empty:
        export_data_table(rcm_analysis, "rcm_analysis.csv", "Export RCM Data")
        col1, col2 = st.columns([2, 1])
        with col1:
            # RPN Pareto
            fig = px.bar(rcm_analysis.head(10), x='failure_type', y='rpn', color='recommended_strategy',
                        title="Top Failure Modes by Risk Priority Number (RPN)",
                        color_discrete_map={'Redesign / Process Change': '#ff4b4b', 
                                          'Predictive Maintenance': '#f0ad4e',
                                          'Preventive Maintenance': '#00d2ff',
                                          'Run-to-Failure': '#5cb85c'},
                        template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            strategy_counts = rcm_analysis['recommended_strategy'].value_counts()
            fig = px.pie(values=strategy_counts.values, names=strategy_counts.index, 
                        title="Recommended Maintenance Strategies",
                        template="plotly_dark", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
            
        st.dataframe(rcm_analysis[['failure_type', 'downtime_id', 'downtime_hours', 'repair_cost', 'rpn', 'recommended_strategy']], use_container_width=True)
        insight_callout("Focus resources on failure modes with RPN > 100. Consider redesign for RPN > 200.", "action")
    else:
        st.info("No RCM analysis data.")

with tab5:
    st.subheader("📅 Maintenance Scheduler Optimization")
    
    # Check if schedule data exists
    if hasattr(analytics['maintenance'], 'schedule_data') and analytics['maintenance'].schedule_data is not None:
        schedule_data = analytics['maintenance'].schedule_data
        opt_results = analytics['maintenance'].optimize_pm_schedule(schedule_data)
        
        # Gantt Chart
        start_date, end_date = filters.get('date_range', (None, None))
        fig = create_gantt_chart(
            opt_results['schedule_df'], 
            "Upcoming Maintenance Schedule",
            start_limit=start_date,
            end_limit=end_date
        )
        st.plotly_chart(fig, use_container_width=True)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown("### 👷 Technician Workload")
            fig = px.bar(opt_results['workload'], x='Technician', y='Tasks',
                        title="Tasks per Technician", template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown("### ⚠️ Scheduling Conflicts")
            conflicts = opt_results['conflicts']
            if not conflicts.empty:
                st.error(f"{len(conflicts)} scheduling conflicts detected!")
                st.dataframe(conflicts)
            else:
                st.success("No scheduling conflicts detected.")
    else:
        st.info("No schedule data loaded.")
            
with tab6:
    st.subheader("📡 IO Condition Monitoring")
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Simulation of live data
        triggers = analytics['maintenance'].condition_based_monitoring()
        
        if not triggers.empty:
            for _, alert in triggers.iterrows():
                color = "#ff4b4b" if alert['severity'] == "Critical" else "#f0ad4e" if alert['severity'] == "High" else "#00d2ff"
                st.markdown(f"""
                <div style="background: rgba(45,45,68,0.5); border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px; border-radius: 5px;">
                    <h4 style="margin:0;">{alert['equipment_name']} - {alert['parameter']} Alert</h4>
                    <p style="font-size: 1.2rem; margin: 5px 0;">Reading: <strong>{alert['value']}</strong> (Limit: {alert['threshold']})</p>
                    <span style="background: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 0.8rem;">{alert['severity']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("All systems nominal. No condition-based alerts.")
    
    with col2:
        st.markdown("### Active Sensors")
        st.metric("Vibration Sensors", "142", "Active", delta_color="normal")
        st.metric("Temp Sensors", "98", "Active", delta_color="normal")
        st.metric("Oil Quality Monitors", "45", "Active", delta_color="normal")
