
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from app_utils import setup_page, load_raw_data, render_sidebar, filter_data, get_analytics, glass_card, insight_box, export_data_table

# Page Setup
setup_page(title="Financial Analytics", icon="💰")

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

st.markdown('<div class="premium-header">Financial Performance Analytics</div>', unsafe_allow_html=True)

budget_sum = analytics['financial'].get_budget_variance_summary()

if not budget_sum.empty:
    total_budget = budget_sum['budget_amount'].sum()
    total_actual = budget_sum['actual_amount'].sum()
    total_variance = budget_sum['variance'].sum()
else:
    total_budget = total_actual = total_variance = 0

col1, col2, col3, col4 = st.columns(4)
with col1:
    glass_card("Total Budget", f"₹{total_budget/1e6:.1f}M", "Annual", "💰", col=col1)
with col2:
    glass_card("Actual Spend", f"₹{total_actual/1e6:.1f}M", f"{total_variance/1e6:+.1f}M", "💸", col=col2)
with col3:
    var_pct = (total_variance / total_budget) * 100 if total_budget > 0 else 0
    glass_card("Budget Variance", f"{var_pct:+.1f}%", "Vs Plan", "⚖️", col=col3)
with col4:
    projects = analytics['financial'].get_investment_portfolio()
    avg_roi = projects['roi_pct'].mean() if not projects.empty else 0
    glass_card("Avg Project ROI", f"{avg_roi:.1f}%", "+2.1%", "📈", col=col4)

st.markdown("<br>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Budget Variance", "📦 Inventory Valuation", "💰 Investment ROI"])

with tab1:
    st.subheader("Budget vs Actual Analysis")
    
    if not budget_sum.empty:
        export_data_table(budget_sum, "budget_variance.csv", "Export Budget Data")
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(budget_sum, x='equipment_type', y=['budget_amount', 'actual_amount'],
                        barmode='group', title="Maintenance Spend vs Budget by Asset Class",
                        template="plotly_dark", color_discrete_sequence=['#3a7bd5', '#00d2ff'])
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            fig = px.pie(budget_sum, values='actual_amount', names='equipment_type',
                        title="Spend Distribution", template="plotly_dark", hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No budget data.")
        
    # Cost Category Variance
    st.subheader("Cost Category Breakdown & Variance")
    cost_analysis = analytics['financial'].get_cost_breakdown_analysis()
    if not cost_analysis.empty:
        fig = px.bar(cost_analysis, x='cost_category', y='variance', color='variance_pct',
                    title="Variance by Cost Category", template="plotly_dark",
                    color_continuous_scale='RdYlGn_r')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No cost analysis data.")
    
with tab2:
    st.subheader("Inventory Valuation Comparison (Holding Strategy)")
    valuation_data = analytics['financial'].compare_inventory_valuation_methods()
    
    if not valuation_data.empty:
        export_data_table(valuation_data, "inventory_valuation.csv", "Export Valuation")
        col1, col2 = st.columns([3, 1])
        with col1:
            st.dataframe(valuation_data[['part_name', 'holding_qty', 'fifo_value', 'lifo_value', 'wac_value']].head(20).style.format({
                'fifo_value': '₹{:,.0f}', 'lifo_value': '₹{:,.0f}', 'wac_value': '₹{:,.0f}'
            }), use_container_width=True)
            
        with col2:
            total_fifo = valuation_data['fifo_value'].sum()
            total_lifo = valuation_data['lifo_value'].sum()
            total_wac = valuation_data['wac_value'].sum()
            
            fig = go.Figure(go.Bar(
                x=['FIFO', 'LIFO', 'WAC'],
                y=[total_fifo, total_lifo, total_wac],
                marker_color=['#00d2ff', '#3a7bd5', '#666']
            ))
            fig.update_layout(title="Inventory Portfolio Value", template="plotly_dark", height=300)
            st.plotly_chart(fig, use_container_width=True)
            
        insight_box("**FIFO** (First-In-First-Out) typically results in higher ending inventory value during inflation. **LIFO** (Last-In-First-Out) matches current costs with current revenue.", "info")
    else:
        st.info("No inventory valuation data.")

with tab3:
    st.subheader("Maintenance Investment Project ROI")
    projects = analytics['financial'].get_investment_portfolio()
    
    if not projects.empty:
        export_data_table(projects, "project_roi.csv", "Export Project ROI")
        fig = px.scatter(projects, x='payback_period_years', y='roi_pct', 
                        size='investment_amount', color='status',
                        hover_data=['project_name'], title="Project ROI vs Payback (Size=Investment)",
                        template="plotly_dark")
        fig.add_hline(y=15, line_dash="dash", line_color="#00ff00", annotation_text="Hurdle Rate (15%)")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(projects[['project_name', 'investment_amount', 'annual_savings', 'payback_period_years', 'roi_pct', 'status']], use_container_width=True)
    else:
        st.info("No project data.")
