
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_callout, insight_box

# Page Setup
setup_page(title="Recommendations & Advanced Insights", icon="🎯")

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

if not all_recs.empty:
    # Summary Metrics
    col1, col2, col3, col4 = st.columns(4)
    critical_count = len(all_recs[all_recs.get('priority', pd.Series()) == 'Critical']) if 'priority' in all_recs.columns else 0
    high_count = len(all_recs[all_recs.get('priority', pd.Series()) == 'High']) if 'priority' in all_recs.columns else 0
    
    with col1:
        glass_card("Total Recommendations", f"{len(all_recs)}", "Active", "📋", col=col1)
    with col2:
        glass_card("Critical Items", f"{critical_count}", "Immediate", "🔴", col=col2)
    with col3:
        glass_card("High Priority", f"{high_count}", "This Week", "🟠", col=col3)
    with col4:
        glass_card("Categories", "3", "Domains", "📊", col=col4)
    
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
    
    if not filtered_recs.empty:
        for _, rec in filtered_recs.iterrows():
            priority = rec.get('priority', 'Medium')
            color_icon = "🔴" if priority == "Critical" else "🟠" if priority == "High" else "🟡" if priority == "Medium" else "🟢"
            
            with st.expander(f"{color_icon} {rec.get('category')}: {rec.get('issue', 'Optimization Opportunity')}", expanded=(priority == "Critical")):
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
    else:
        st.info("No recommendations match your filters.")
else:
    st.success("No active recommendations. Operations are running smoothly!")
