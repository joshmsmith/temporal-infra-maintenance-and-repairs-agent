"""Overview dashboard component."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict


def render_overview(df: pd.DataFrame):
    """Render the overview dashboard page."""
    
    # Header with refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🏢 Infrastructure Overview")
    with col2:
        # Note: The refresh button will trigger a page rerun, 
        # and the parent app handles cache clearing
        st.button("🔄 Refresh Data", key="refresh_overview")
    
    st.markdown("---")
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Equipment",
            value=len(df)
        )
    
    with col2:
        critical_count = len(df[df['status'] == 'Down'])
        st.metric(
            label="Critical Alerts",
            value=critical_count
        )
        if critical_count > 0:
            st.caption(f"🔴 {critical_count} Down")
    
    with col3:
        warning_count = len(df[df['status'] == 'Degraded'])
        st.metric(
            label="Warning Alerts",
            value=warning_count
        )
        if warning_count > 0:
            st.caption(f"⚠️ {warning_count} Degraded")
    
    with col4:
        avg_health = df['health_score'].mean()
        st.metric(
            label="Avg Health Score",
            value=f"{avg_health:.1f}"
        )
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Equipment Status Distribution")
        status_counts = df['status'].value_counts()
        
        colors = {
            'Operational': '#28a745',
            'Degraded': '#ffc107',
            'Down': '#dc3545'
        }
        color_list = [colors.get(status, '#6c757d') for status in status_counts.index]
        
        fig = px.pie(
            values=status_counts.values,
            names=status_counts.index,
            color=status_counts.index,
            color_discrete_map=colors,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📍 Status by Site")
        site_status = df.groupby(['site', 'status']).size().reset_index(name='count')
        
        fig = px.bar(
            site_status,
            x='site',
            y='count',
            color='status',
            color_discrete_map=colors,
            barmode='stack'
        )
        fig.update_layout(
            height=350,
            xaxis_title="Site",
            yaxis_title="Equipment Count",
            legend_title="Status"
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💚 Health Score Distribution")
        fig = px.histogram(
            df,
            x='health_score',
            nbins=20,
            color_discrete_sequence=['#007bff']
        )
        fig.update_layout(
            height=350,
            xaxis_title="Health Score",
            yaxis_title="Equipment Count",
            showlegend=False
        )
        # Add vertical lines for thresholds
        fig.add_vline(x=40, line_dash="dash", line_color="red", annotation_text="Poor")
        fig.add_vline(x=70, line_dash="dash", line_color="orange", annotation_text="Fair")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏭 Equipment by Vendor")
        vendor_counts = df['vendor'].value_counts()
        
        fig = px.bar(
            x=vendor_counts.index,
            y=vendor_counts.values,
            color=vendor_counts.values,
            color_continuous_scale='blues'
        )
        fig.update_layout(
            height=350,
            xaxis_title="Vendor",
            yaxis_title="Equipment Count",
            showlegend=False
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Equipment at Risk
    st.subheader("⚠️ Equipment at Risk (Health Score < 40)")
    at_risk = df[df['health_score'] < 40].sort_values('health_score')
    
    if len(at_risk) > 0:
        display_cols = ['id', 'model', 'type', 'site', 'status', 'health_score']
        st.dataframe(
            at_risk[display_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("✅ No equipment currently at risk!")
    
    # Equipment Type Distribution
    st.markdown("---")
    st.subheader("🔧 Equipment Type Distribution")
    type_counts = df['type'].value_counts()
    
    fig = px.bar(
        x=type_counts.values,
        y=type_counts.index,
        orientation='h',
        color=type_counts.values,
        color_continuous_scale='viridis'
    )
    fig.update_layout(
        height=400,
        xaxis_title="Count",
        yaxis_title="Equipment Type",
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)
