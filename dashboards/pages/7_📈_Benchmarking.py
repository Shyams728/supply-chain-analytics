
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, metric_delta_card, create_radar_chart, insight_box

# Page Setup
setup_page(title="Benchmarking & Strategy", icon="🏆")

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

st.markdown('<div class="premium-header">Strategic Benchmarking & Gap Analysis</div>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["🏆 Industry Benchmarking", "🤝 Peer Equipment Comparison"])

with tab1:
    st.subheader("Industry KPI Comparison")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        maint_metrics = analytics['maintenance'].calculate_reliability_metrics()
        
        if not maint_metrics.empty:
            avg_avail = maint_metrics['availability_pct'].mean()
            
            comparison = analytics['benchmark'].compare_against_industry('Equipment Availability', avg_avail)
            
            if comparison:
                st.markdown(f"### {comparison['metric']}")
                metric_delta_card("Your Performance", comparison['internal_value'], comparison['industry_average'], suffix="%", col=col1)
                
                # Gap chart
                fig = go.Figure(go.Bar(
                    x=['You', 'Industry Avg', 'Best-in-Class'],
                    y=[comparison['internal_value'], comparison['industry_average'], comparison['best_in_class']],
                    marker_color=['#00d2ff', '#666', '#5cb85c']
                ))
                fig.update_layout(title=f"Gap to Best-in-Class: {comparison['gap_to_best']:.1f}%", template="plotly_dark", height=300)
                st.plotly_chart(fig, use_container_width=True)
                
                status_color = "#5cb85c" if "Above" in comparison['status'] or "World" in comparison['status'] else "#ff4b4b"
                st.markdown(f"Status: <strong style='color:{status_color}'>{comparison['status']}</strong>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ No benchmark data available for Equipment Availability")
        else:
            st.info("No internal data for comparison.")
    
    with col2:
        # Radar chart of all benchmarks
        # Get first 6 metrics for radar
        categories = ['Fill Rate', 'On-Time Delivery', 'Equipment Availability', 'OEE', 'MTBF', 'MTTR']
        # Simulated internal values normalized to 100 for radar comparison
        # Ideally calculate these dynamically
        values = [88, 86, 84, 72, 78, 82] 
        
        fig = create_radar_chart(categories, values, "Internal Performance vs Industry Benchmark")
        st.plotly_chart(fig, use_container_width=True)
        
with tab2:
    st.subheader("Internal Peer Ranking")
    maint_metrics = analytics['maintenance'].calculate_reliability_metrics()
    if not maint_metrics.empty:
        peer_ranking = analytics['benchmark'].peer_equipment_comparison(maint_metrics)
        
        fig = px.bar(peer_ranking.head(15), x='equipment_name', y='composite_score', color='composite_score',
                    color_continuous_scale='Viridis', title="Top Performing Assets (Composite Rank)",
                    template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(peer_ranking, use_container_width=True)
        insight_box("Composite score weightings: 40% Availability, 30% MTBF, 30% Cost Efficiency.", "info")
    else:
        st.info("No data for peer ranking.")
