
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from quality_data_generator import QualityDataGenerator
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout, insight_box, create_spc_chart, create_fishbone_diagram, render_a3_template

# Page Setup
setup_page(title="Quality Analytics", icon="💎")

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

st.markdown('<div class="premium-header">Six Sigma & Quality Control</div>', unsafe_allow_html=True)

# Quality KPIs
quality_metrics = analytics['quality'].calculate_six_sigma_metrics()

col1, col2, col3, col4 = st.columns(4)
with col1:
    glass_card("Sigma Level", f"{quality_metrics['sigma_level']:.1f}σ", "Target: 6.0σ", "💎", col=col1)
with col2:
    glass_card("DPMO", f"{quality_metrics['dpmo']:,.0f}", "Defects/Million", "🚨", col=col2)
with col3:
    glass_card("Process Yield", f"{quality_metrics['yield_pct']:.2f}%", "First Pass", "📈", col=col3)
with col4:
    glass_card("Total Defects", f"{quality_metrics['total_defects']:,}", "This Period", "📋", col=col4)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📉 Statistical Process Control", "🔍 Defect Pareto", "🧬 Root Cause Engine"])

with tab1:
    st.subheader("📊 Control Charts (X-bar & R)")
    metric_list = analytics['quality'].get_metrics_list()
    
    if metric_list:
        selected_metric = st.selectbox("Select Process Parameter", metric_list)
        
        spc_data = analytics['quality'].calculate_spc_charts(selected_metric)
        if not spc_data.empty:
            fig = create_spc_chart(spc_data, selected_metric)
            st.plotly_chart(fig, use_container_width=True)
            
            violations = spc_data[spc_data['xbar_violation'] | spc_data['r_violation']]
            if not violations.empty:
                st.warning(f"⚠️ {len(violations)} points out of control limits detected! Review process stability.")
            else:
                st.success("✅ Process is currently in statistical control.")
        else:
            st.info("Not enough data for SPC chart.")
    else:
        st.info("No SPC metrics available for selected period.")
        
with tab2:
    st.subheader("🎯 Defect Pareto Analysis")
    pareto_data = analytics['quality'].defect_pareto_analysis()
    
    if not pareto_data.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=pareto_data['defect_type'], y=pareto_data['count'], name='Defects', marker_color='#3a7bd5'))
        fig.add_trace(go.Scatter(x=pareto_data['defect_type'], y=pareto_data['cumulative_percentage'], 
                                name='Cumulative %', yaxis='y2', line=dict(color='#ff6b6b', width=3)))
        
        fig.update_layout(template="plotly_dark", yaxis2=dict(overlaying='y', side='right', range=[0, 105]),
                         title="Pareto: 80% of defects from top identified causes",
                         paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
        insight_box("Focus on the 'Vital Few' defect types on the left to achieve the greatest quality improvement.", "action")
    else:
        st.info("No defects found in this period.")

    # Defect Trend
    st.subheader("📈 Monthly Defect Trend")
    trend = analytics['quality'].defect_trend_analysis()
    if not trend.empty:
        fig = px.line(trend, x='month', y='defect_count', markers=True, 
                     title="Trend of Quality Issues", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("🧬 Root Cause Analysis Engine")
    
    if not pareto_data.empty:
        col1, col2 = st.columns([1, 2])
        with col1:
            defect_to_analyze = st.selectbox("Analyze Defect Type", pareto_data['defect_type'].unique())
            st.markdown("---")
            st.markdown("### A3 Problem Solving")
            if st.button("Generate A3 Template"):
                # Initialize generator (we can pass empty df as we only need the report method for now, 
                # or better yet, pass the actual data if we wanted to be more precise, but for this method it uses internal logic)
                # Ideally we should instantiate this once or reuse, but for button click it's fine.
                # We need to pass a dataframe to init, let's use the one from analytics or just an empty one if safe.
                # The generator needs equipment_df to init.
                # Let's try to get equipment data from raw_data if available
                equipment_df = raw_data.get('equipment') if raw_data else pd.DataFrame()
                generator = QualityDataGenerator(equipment_df)
                
                a3_data = generator.generate_a3_report(defect_to_analyze)
                render_a3_template(a3_data)
        
        with col2:
            fishbone_data = analytics['quality'].get_fishbone_data(defect_to_analyze)
            fig = create_fishbone_diagram(fishbone_data)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No defect data for Root Cause Analysis.")
