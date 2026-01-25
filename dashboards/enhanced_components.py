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


def benchmark_card(title, value, benchmark_status, icon="📊", trend=None):
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


def metric_delta_card(title, current, previous, format_str="{:.1f}", suffix="", icon="📊"):
    """Display a metric with delta from previous period"""
    delta = current - previous
    delta_pct = (delta / previous * 100) if previous != 0 else 0
    is_positive = delta >= 0
    
    delta_color = COLORS['success'] if is_positive else COLORS['danger']
    delta_symbol = "▲" if is_positive else "▼"
    
    st.markdown(f"""
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
""", unsafe_allow_html=True)


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

def create_gantt_chart(tasks_df, title="Maintenance Schedule"):
    """
    Create Gantt chart for scheduling
    Expects df with: Task, Start, Finish, Resource
    """
    fig = px.timeline(tasks_df, x_start="start_date", x_end="end_date", y="equipment_name",
                     color="assigned_technician", hover_data=["task_name", "status"],
                     title=title, template="plotly_dark")
    
    fig.update_yaxes(autorange="reversed") # Latest on top
    fig.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig

def create_fishbone_diagram(data):
    """
    Visualize Fishbone (Ishikawa) Diagram using network graph structure
    Input: Dict with keys as Major Categories (Man, Machine, etc) and values as list of causes
    """
    # Nodes and Edges
    labels = ["Problem"] + list(data.keys())
    parents = [""] + ["Problem"] * 6
    values = [10] + [5] * 6 # Size
    
    # Add leaves
    for cat, items in data.items():
        for item in items:
            labels.append(item['name'])
            parents.append(cat)
            values.append(item['value'])
            
    # Visualize as Sunburst or Treemap (better for web than static fishbone)
    # Using Suburst as modern interactive alternative
    fig = go.Figure(go.Sunburst(
        labels=labels,
        parents=parents,
        values=values,
        branchvalues="total",
        marker=dict(colorscale='Blues')
    ))
    
    fig.update_layout(title="Root Cause Analysis (Fishbone Structure)", height=500, template="plotly_dark",
                      paper_bgcolor='rgba(0,0,0,0)')
    return fig

def render_a3_template():
    """Render an A3 Problem Solving Template in Streamlit"""
    html_code = """
    <div style="background-color: white; color: black; padding: 20px; border-radius: 5px;">
        <h2 style="text-align: center; color: #2c3e50;">A3 Problem Solving Report</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>1. Background</h4>
                <p><i>Context of the problem...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>5. Countermeasures</h4>
                <p><i>Proposed solutions...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>2. Current Condition</h4>
                <p><i>Problem statement & data...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>6. Implementation Plan</h4>
                <p><i>Who, When, What...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>3. Goal / Target State</h4>
                <p><i>Specific metric targets...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px;">
                <h4>7. Follow Up</h4>
                <p><i>Check results & standard work...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
            <div style="border: 1px solid #ccc; padding: 10px; grid-column: span 2;">
                <h4>4. Root Cause Analysis</h4>
                <p><i>5 Whys / Fishbone...</i></p>
                <div style="height: 100px; background: #f9f9f9;"></div>
            </div>
        </div>
    </div>
    """
    st.markdown(html_code, unsafe_allow_html=True)
