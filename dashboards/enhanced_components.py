
"""
Enhanced Dashboard Components
Reusable visualization and insight components for the Supply Chain Analytics Platform
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import textwrap

# Color Palette
COLORS = {
    'primary': '#00d2ff',
    'secondary': '#3a7bd5',
    'success': '#5cb85c',
    'warning': '#f0ad4e',
    'danger': '#ff4b4b',
    'info': '#17a2b8',
    'dark': '#2d2d44',
    'gradient_start': '#00d2ff',
    'gradient_end': '#3a7bd5'
}


def benchmark_card(title, value, benchmark_status, icon="📊", trend=None, col=None):
    """Display a KPI card with benchmark comparison"""
    status_color = benchmark_status.get('color', '#888')
    status_icon = benchmark_status.get('icon', '📊')
    status_text = benchmark_status.get('status', 'N/A')
    
    trend_html = ""
    if trend:
        trend_color = COLORS['success'] if trend > 0 else COLORS['danger']
        trend_arrow = "↑" if trend > 0 else "↓"
        trend_html = f'<span style="color: {trend_color}; font-size: 0.85rem;">{trend_arrow} {abs(trend):.1f}%</span>'
    
    html_content = f"""
    <div style="background: linear-gradient(135deg, rgba(0,210,255,0.1) 0%, rgba(58,123,213,0.1) 100%); backdrop-filter: blur(10px); border-radius: 15px; padding: 1.2rem; border: 1px solid rgba(255,255,255,0.15); margin-bottom: 0.5rem;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="color: #a0a0c0; font-size: 0.85rem;">{title}</span>
            <span style="font-size: 1.2rem;">{icon}</span>
        </div>
        <div style="font-size: 1.7rem; font-weight: 700; margin: 0.4rem 0; color: white;">{value}</div>
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <span style="background: {status_color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.75rem;">{status_icon} {status_text}</span>
            {trend_html}
        </div>
    </div>
    """
    if col:
        col.markdown(html_content, unsafe_allow_html=True)
    else:
        st.markdown(html_content, unsafe_allow_html=True)


def create_gauge_chart(value, title, target=None, max_val=100):
    """Create a modern gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={'reference': target or 95, 'increasing': {'color': COLORS['success']}, 
               'decreasing': {'color': COLORS['danger']}},
        gauge={
            'axis': {'range': [0, max_val], 'tickwidth': 1},
            'bar': {'color': COLORS['primary']},
            'bgcolor': 'rgba(0,0,0,0)',
            'borderwidth': 0,
            'steps': [
                {'range': [0, max_val * 0.6], 'color': 'rgba(255,75,75,0.2)'},
                {'range': [max_val * 0.6, max_val * 0.85], 'color': 'rgba(240,173,78,0.2)'},
                {'range': [max_val * 0.85, max_val], 'color': 'rgba(92,184,92,0.2)'}
            ],
            'threshold': {
                'line': {'color': COLORS['warning'], 'width': 3},
                'thickness': 0.8,
                'value': target or 95
            }
        },
        title={'text': title, 'font': {'size': 14, 'color': '#a0a0c0'}}
    ))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=200,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def create_radar_chart(categories, values, title="Performance Radar"):
    """Create a radar/spider chart for multi-dimensional comparison"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the polygon
        theta=categories + [categories[0]],
        fill='toself',
        fillcolor='rgba(0,210,255,0.2)',
        line=dict(color=COLORS['primary'], width=2),
        name='Current'
    ))
    
    # Add benchmark line
    benchmark = [85] * len(categories) + [85]
    fig.add_trace(go.Scatterpolar(
        r=benchmark,
        theta=categories + [categories[0]],
        line=dict(color=COLORS['warning'], width=2, dash='dash'),
        name='Benchmark'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], showticklabels=True,
                          gridcolor='rgba(255,255,255,0.1)'),
            angularaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        ),
        showlegend=True,
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=350,
        margin=dict(l=60, r=60, t=60, b=40)
    )
    return fig


def create_heatmap(correlation_matrix, title="Correlation Matrix"):
    """Create a correlation heatmap"""
    fig = px.imshow(
        correlation_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        aspect='auto',
        title=title
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig


def create_waterfall_chart(categories, values, title="Impact Analysis"):
    """Create a waterfall chart for breakdown analysis"""
    fig = go.Figure(go.Waterfall(
        name="Impact",
        orientation="v",
        measure=["relative"] * (len(categories) - 1) + ["total"],
        x=categories,
        y=values,
        connector={"line": {"color": "rgba(255,255,255,0.3)"}},
        increasing={"marker": {"color": COLORS['success']}},
        decreasing={"marker": {"color": COLORS['danger']}},
        totals={"marker": {"color": COLORS['primary']}}
    ))
    
    fig.update_layout(
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=350,
        showlegend=False,
        margin=dict(l=20, r=20, t=50, b=40)
    )
    return fig


def create_bullet_chart(actual, target, title, max_val=None):
    """Create a bullet chart for target comparison"""
    max_val = max_val or max(actual, target) * 1.2
    
    fig = go.Figure()
    
    # Background ranges
    fig.add_trace(go.Bar(
        x=[max_val], y=[title], orientation='h',
        marker_color='rgba(45,45,68,0.8)', width=0.5, showlegend=False
    ))
    fig.add_trace(go.Bar(
        x=[max_val * 0.85], y=[title], orientation='h',
        marker_color='rgba(58,123,213,0.3)', width=0.5, showlegend=False
    ))
    fig.add_trace(go.Bar(
        x=[max_val * 0.7], y=[title], orientation='h',
        marker_color='rgba(0,210,255,0.3)', width=0.5, showlegend=False
    ))
    
    # Actual value bar
    fig.add_trace(go.Bar(
        x=[actual], y=[title], orientation='h',
        marker_color=COLORS['primary'], width=0.25,
        name='Actual', showlegend=True
    ))
    
    # Target marker
    fig.add_trace(go.Scatter(
        x=[target], y=[title],
        mode='markers',
        marker=dict(symbol='line-ns', size=20, color=COLORS['danger'], line=dict(width=3)),
        name='Target', showlegend=True
    ))
    
    fig.update_layout(
        barmode='overlay',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        height=120,
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False)
    )
    return fig


def insight_box(text, insight_type="info", show_icon=True):
    """Display an insight callout with styling"""
    styles = {
        "info": {"icon": "💡", "color": "#00d2ff", "bg": "rgba(0,210,255,0.1)"},
        "warning": {"icon": "⚠️", "color": "#f0ad4e", "bg": "rgba(240,173,78,0.1)"},
        "success": {"icon": "✅", "color": "#5cb85c", "bg": "rgba(92,184,92,0.1)"},
        "danger": {"icon": "🚨", "color": "#ff4b4b", "bg": "rgba(255,75,75,0.1)"},
        "trend": {"icon": "📈", "color": "#3a7bd5", "bg": "rgba(58,123,213,0.1)"},
        "action": {"icon": "🎯", "color": "#9b59b6", "bg": "rgba(155,89,182,0.1)"}
    }
    
    style = styles.get(insight_type, styles["info"])
    icon = style["icon"] if show_icon else ""
    
    st.markdown(f"""
<div style="background: linear-gradient(135deg, {style['bg']} 0%, rgba(45,45,68,0.3) 100%);
            border-left: 4px solid {style['color']}; padding: 12px 16px; 
            border-radius: 8px; margin: 10px 0;">
    <span style="font-size: 1.1rem;">{icon}</span>
    <span style="color: #e0e0e0; font-size: 0.9rem; margin-left: 8px;">{text}</span>
</div>
""", unsafe_allow_html=True)


def metric_delta_card(title, current, previous, format_str="{:.1f}", suffix="", icon="📊", col=None):
    """Display a metric with delta from previous period"""
    delta = current - previous if previous else 0
    delta_pct = (delta / previous * 100) if previous and previous != 0 else 0
    is_positive = delta >= 0
    
    delta_color = COLORS['success'] if is_positive else COLORS['danger']
    delta_symbol = "▲" if is_positive else "▼"
    
    html = f"""
<div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 1rem;
            border: 1px solid rgba(255,255,255,0.1);">
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 0.5rem;">
        <span style="font-size: 1.3rem;">{icon}</span>
        <span style="color: #a0a0c0; font-size: 0.85rem;">{title}</span>
    </div>
    <div style="font-size: 1.8rem; font-weight: 700; color: white;">
        {format_str.format(current)}{suffix}
    </div>
    <div style="color: {delta_color}; font-size: 0.85rem; margin-top: 0.3rem;">
        {delta_symbol} {abs(delta_pct):.1f}% vs previous
    </div>
</div>
"""
    if col:
        col.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)


def create_sparkline(data, title="", height=60, color=None):
    """Create a mini sparkline chart"""
    color = color or COLORS['primary']
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(data))),
        y=data,
        mode='lines',
        line=dict(color=color, width=2),
        fill='tozeroy',
        fillcolor=f"rgba{tuple(list(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + [0.1])}"
    ))
    
    # Add min/max markers
    min_idx, max_idx = data.argmin(), data.argmax() if hasattr(data, 'argmin') else (np.argmin(data), np.argmax(data))
    fig.add_trace(go.Scatter(
        x=[min_idx, max_idx],
        y=[data[min_idx], data[max_idx]],
        mode='markers',
        marker=dict(color=[COLORS['danger'], COLORS['success']], size=6),
        showlegend=False
    ))
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=height,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False
    )
    return fig


def section_header(title, subtitle=None, icon="📊"):
    """Display a styled section header"""
    subtitle_html = f'<p style="color: #888; font-size: 0.9rem; margin: 0;">{subtitle}</p>' if subtitle else ""
    st.markdown(f"""
<div style="margin: 1.5rem 0 1rem 0;">
    <h2 style="background: linear-gradient(to right, #00d2ff, #3a7bd5);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;
               font-weight: 700; font-size: 1.8rem; margin: 0;">
        {icon} {title}
    </h2>
    {subtitle_html}
</div>
""", unsafe_allow_html=True)

def create_spc_chart(data, metric_name):
    """
    Create dual-axis X-bar and R chart for Statistical Process Control
    """
    # Create subplots
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                        vertical_spacing=0.1, subplot_titles=(f"X-bar Chart: {metric_name}", "R Chart (Range)"))
    
    # X-bar Chart
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['xbar_value'], mode='lines+markers', name='X-bar',
                            line=dict(color='#00d2ff')), row=1, col=1)
    
    # Center Line (CL)
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['xbar_cl'], mode='lines', name='CL',
                            line=dict(color='green', dash='solid')), row=1, col=1)
    
    # Upper/Lower Control Limits
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['xbar_ucl'], mode='lines', name='UCL',
                            line=dict(color='red', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['xbar_lcl'], mode='lines', name='LCL',
                            line=dict(color='red', dash='dash')), row=1, col=1)
    
    # Highlight Violations
    violations = data[data['xbar_violation']]
    if not violations.empty:
        fig.add_trace(go.Scatter(x=violations['inspection_date'], y=violations['xbar_value'], 
                                mode='markers', name='Violation',
                                marker=dict(color='yellow', size=10, symbol='x')), row=1, col=1)
    
    # R Chart
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['r_value'], mode='lines+markers', name='R-value',
                            line=dict(color='#3a7bd5')), row=2, col=1)
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['r_cl'], mode='lines', name='CL',
                            line=dict(color='green', dash='solid')), row=2, col=1)
    fig.add_trace(go.Scatter(x=data['inspection_date'], y=data['r_ucl'], mode='lines', name='UCL',
                            line=dict(color='red', dash='dash')), row=2, col=1)
                            
    fig.update_layout(height=600, template="plotly_dark", showlegend=False,
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_sankey_diagram(source, target, value, label_list, title="Material Flow"):
    """
    Create Sankey diagram for flow visualization
    """
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=label_list,
            color='#3a7bd5'
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color='rgba(0, 210, 255, 0.4)'
        )
    )])
    
    fig.update_layout(title_text=title, font_size=10, height=500, template="plotly_dark",
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_gantt_chart(tasks_df, title="Maintenance Schedule", start_limit=None, end_limit=None):
    """
    Create an advanced Gantt chart for scheduling with focused time window
    Expects df with: task_name, start_date, end_date, assigned_technician, status
    """
    if tasks_df.empty:
        return go.Figure()

    df = tasks_df.copy()
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['end_date'] = pd.to_datetime(df['end_date'])
    
    # Apply filtering if limits provided, otherwise default to a reasonable window
    today = pd.Timestamp.now().normalize()
    if start_limit is None:
        # Show from 7 days ago to 60 days ahead by default if no limit
        start_view = today - pd.Timedelta(days=7)
    else:
        start_view = pd.to_datetime(start_limit)
        
    if end_limit is None:
        end_view = today + pd.Timedelta(days=60)
    else:
        end_view = pd.to_datetime(end_limit)

    # Filter data for the chart to improve performance and readability
    # Keep tasks that overlap with the view window
    mask = (df['start_date'] <= end_view) & (df['end_date'] >= start_view)
    plot_df = df[mask].sort_values('start_date')

    if plot_df.empty:
        # If no tasks in window, show a message or just the window
        fig = go.Figure()
        fig.add_annotation(text="No maintenance tasks scheduled for this period", 
                          showarrow=False, font=dict(size=16, color="#888"))
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
        return fig

    # Create timeline
    fig = px.timeline(
        plot_df, 
        x_start="start_date", 
        x_end="end_date", 
        y="equipment_name",
        color="status",
        hover_data={
            "equipment_name": True,
            "task_name": True,
            "assigned_technician": True,
            "status": True,
            "start_date": "|%b %d, %Y",
            "end_date": "|%b %d, %Y"
        },
        category_orders={"status": ["Completed", "In Progress", "Scheduled"]},
        color_discrete_map={
            "Completed": COLORS['success'],
            "In Progress": COLORS['warning'],
            "Scheduled": COLORS['primary']
        },
        title=title,
        template="plotly_dark"
    )
    
    # Add "Today" vertical line
    fig.add_vline(x=today.timestamp() * 1000, line_width=2, line_dash="dash", line_color="#ff4b4b")
    fig.add_annotation(x=today.timestamp() * 1000, y=0, text="TODAY", showarrow=False, 
                      textangle=-90, yanchor="top", font=dict(color="#ff4b4b", size=10))

    fig.update_yaxes(autorange="reversed", title="Asset")
    fig.update_xaxes(
        title="Timeline",
        range=[start_view, end_view],
        rangeslider_visible=True
    )
    
    fig.update_layout(
        height=500, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig

def create_fishbone_diagram(data):
    """
    Visualize Fishbone (Ishikawa) Diagram as an actual fishbone structure
    Input: Dict with keys as Major Categories (Man, Machine, etc) and values as list of causes
    """
    fig = go.Figure()
    
    # Main spine (horizontal line from left to right)
    spine_y = 0
    spine_start_x = 0
    spine_end_x = 10
    
    # Draw main spine
    fig.add_trace(go.Scatter(
        x=[spine_start_x, spine_end_x],
        y=[spine_y, spine_y],
        mode='lines',
        line=dict(color='#00d2ff', width=3),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Problem head (arrow at the end)
    fig.add_trace(go.Scatter(
        x=[spine_end_x],
        y=[spine_y],
        mode='markers+text',
        marker=dict(size=20, color='#ff4b4b', symbol='triangle-right'),
        text=['PROBLEM'],
        textposition='middle right',
        textfont=dict(size=12, color='white', family='Arial Black'),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Categories and their positions
    categories = list(data.keys())
    num_categories = len(categories)
    
    # Position categories alternating above and below the spine
    positions = []
    for i, category in enumerate(categories):
        x_pos = 2 + (i * (spine_end_x - 2) / num_categories)
        # Alternate above (positive y) and below (negative y)
        y_offset = 2 if i % 2 == 0 else -2
        positions.append((x_pos, y_offset, category))
    
    # Draw bones and causes
    for x_pos, y_offset, category in positions:
        # Draw bone (diagonal line from spine to category)
        fig.add_trace(go.Scatter(
            x=[x_pos, x_pos + 1.5],
            y=[spine_y, y_offset],
            mode='lines',
            line=dict(color='#3a7bd5', width=2),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add category label
        fig.add_trace(go.Scatter(
            x=[x_pos + 1.5],
            y=[y_offset],
            mode='text',
            text=[f'<b>{category}</b>'],
            textposition='top center' if y_offset > 0 else 'bottom center',
            textfont=dict(size=11, color='#00d2ff'),
            showlegend=False,
            hoverinfo='skip'
        ))
        
        # Add causes for this category
        causes = data.get(category, [])
        for j, cause_item in enumerate(causes[:3]):  # Limit to top 3 causes
            cause_name = cause_item.get('name', '')
            cause_value = cause_item.get('value', 0)
            
            # Position causes along the bone
            cause_x = x_pos + 0.5 + (j * 0.3)
            cause_y = y_offset * (0.7 - j * 0.15)
            
            # Draw small line to cause
            fig.add_trace(go.Scatter(
                x=[x_pos + 1.5, cause_x],
                y=[y_offset, cause_y],
                mode='lines',
                line=dict(color='rgba(58,123,213,0.3)', width=1, dash='dot'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Add cause text
            fig.add_trace(go.Scatter(
                x=[cause_x],
                y=[cause_y],
                mode='markers+text',
                marker=dict(size=8, color='#f0ad4e'),
                text=[f'{cause_name}<br>({cause_value})'],
                textposition='top center' if y_offset > 0 else 'bottom center',
                textfont=dict(size=8, color='#e0e0e0'),
                showlegend=False,
                hovertemplate=f'<b>{cause_name}</b><br>Count: {cause_value}<extra></extra>'
            ))
    
    # Update layout
    fig.update_layout(
        title="Root Cause Analysis (Fishbone Diagram)",
        height=500,
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-1, 12]
        ),
        yaxis=dict(
            showgrid=False,
            showticklabels=False,
            zeroline=False,
            range=[-3, 3]
        ),
        margin=dict(l=20, r=100, t=50, b=20)
    )
    
    return fig

def render_a3_template(data=None):
    """Render an A3 Problem Solving Template in Streamlit using native components"""
    
    # Default empty placeholder text if no data provided
    if data is None:
        data = {
            'background': "Context of the problem...",
            'current_condition': "Problem statement & data...",
            'goal': "Specific metric targets...",
            'root_cause': "5 Whys / Fishbone...",
            'countermeasures': "Proposed solutions...",
            'implementation': "Who, When, What...",
            'follow_up': "Check results & standard work..."
        }
    
    # Title
    st.markdown("### 📋 A3 Problem Solving Report")
    st.markdown("---")
    
    # Create two-column layout
    col1, col2 = st.columns(2)
    
    # Left column - sections 1, 2, 3, 4
    with col1:
        # Section 1: Background
        with st.container():
            st.markdown("#### 1. Background")
            st.markdown(data.get('background', ''), unsafe_allow_html=True)
            st.markdown("")
        
        # Section 2: Current Condition
        with st.container():
            st.markdown("#### 2. Current Condition")
            st.markdown(data.get('current_condition', ''), unsafe_allow_html=True)
            st.markdown("")
        
        # Section 3: Goal / Target State
        with st.container():
            st.markdown("#### 3. Goal / Target State")
            st.markdown(data.get('goal', ''), unsafe_allow_html=True)
            st.markdown("")
    
    # Right column - sections 5, 6, 7
    with col2:
        # Section 5: Countermeasures
        with st.container():
            st.markdown("#### 5. Countermeasures")
            st.markdown(data.get('countermeasures', ''), unsafe_allow_html=True)
            st.markdown("")
        
        # Section 6: Implementation Plan
        with st.container():
            st.markdown("#### 6. Implementation Plan")
            st.markdown(data.get('implementation', ''), unsafe_allow_html=True)
            st.markdown("")
        
        # Section 7: Follow Up
        with st.container():
            st.markdown("#### 7. Follow Up")
            st.markdown(data.get('follow_up', ''), unsafe_allow_html=True)
            st.markdown("")
    
    # Section 4: Root Cause Analysis (full width at bottom)
    with st.container():
        st.markdown("#### 4. Root Cause Analysis")
        st.markdown(data.get('root_cause', ''), unsafe_allow_html=True)
        st.markdown("")
    
    st.markdown("---")

def export_data_table(df, filename="data_export.csv", label="Export Data"):
    """
    Create a download button for a dataframe
    """
    try:
        csv = df.to_csv(index=False).encode('utf-8')
    except Exception as e:
        st.error(f"Error encoding export data: {e}")
        return

    st.download_button(
        label=f"📥 {label}",
        data=csv,
        file_name=filename,
        mime='text/csv',
    )
