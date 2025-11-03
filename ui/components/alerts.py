"""Alerts and notifications component."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.calculations import get_severity_color


def render_alerts(df: pd.DataFrame):
    """Render the alerts and notifications page."""
    
    # Header with refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🔔 Alerts & Notifications")
    with col2:
        st.button("🔄 Refresh Data", key="refresh_alerts")
    
    st.markdown("---")
    
    # Collect all alerts
    all_alerts = []
    
    for _, row in df.iterrows():
        if row['alerts'] and len(row['alerts']) > 0:
            for alert in row['alerts']:
                all_alerts.append({
                    'equipment_id': row['id'],
                    'model': row['model'],
                    'type': row['type'],
                    'site': row['site'],
                    'location': row['location'],
                    'status': row['status'],
                    'alert_type': alert['type'],
                    'severity': alert['severity'],
                    'timestamp': alert['timestamp']
                })
    
    alerts_df = pd.DataFrame(all_alerts)
    
    if len(alerts_df) > 0:
        # Convert timestamp to datetime
        alerts_df['timestamp'] = pd.to_datetime(alerts_df['timestamp'])
        alerts_df = alerts_df.sort_values('timestamp', ascending=False)
        
        # KPI Cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Active Alerts",
                value=len(alerts_df)
            )
        
        with col2:
            critical_alerts = len(alerts_df[alerts_df['severity'] == 'critical'])
            st.metric(
                label="Critical Alerts",
                value=critical_alerts
            )
            if critical_alerts > 0:
                st.caption("🔴 Critical")
        
        with col3:
            warning_alerts = len(alerts_df[alerts_df['severity'] == 'warning'])
            st.metric(
                label="Warning Alerts",
                value=warning_alerts
            )
            if warning_alerts > 0:
                st.caption("⚠️ Warning")
        
        with col4:
            affected_equipment = alerts_df['equipment_id'].nunique()
            st.metric(
                label="Affected Equipment",
                value=affected_equipment
            )
        
        st.markdown("---")
        
        # Alert Distribution Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Alerts by Severity")
            severity_counts = alerts_df['severity'].value_counts()
            
            colors = {
                'critical': '#dc3545',
                'warning': '#ffc107',
                'info': '#17a2b8'
            }
            
            fig = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                color=severity_counts.index,
                color_discrete_map=colors,
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("📍 Alerts by Site")
            site_counts = alerts_df['site'].value_counts().head(10)
            
            fig = px.bar(
                x=site_counts.values,
                y=site_counts.index,
                orientation='h',
                color=site_counts.values,
                color_continuous_scale='reds'
            )
            fig.update_layout(
                height=350,
                xaxis_title="Alert Count",
                yaxis_title="Site",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Critical Alerts
        st.subheader("🚨 Critical Alerts")
        critical_alerts_df = alerts_df[alerts_df['severity'] == 'critical']
        
        if len(critical_alerts_df) > 0:
            for _, alert in critical_alerts_df.iterrows():
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.markdown(
                            f"### 🔴 {alert['equipment_id']}\n"
                            f"**{alert['model']}** - {alert['type']}"
                        )
                    
                    with col2:
                        st.markdown(
                            f"**Site:** {alert['site']}\n\n"
                            f"**Location:** {alert['location']}"
                        )
                    
                    with col3:
                        st.markdown(
                            f"**Status:** {alert['status']}\n\n"
                            f"**Time:** {alert['timestamp'].strftime('%Y-%m-%d %H:%M')}"
                        )
                    
                    st.markdown(f"**Alert Type:** {alert['alert_type']}")
                    st.markdown("---")
        else:
            st.success("✅ No critical alerts!")
        
        # Warning Alerts
        st.subheader("⚠️ Warning Alerts")
        warning_alerts_df = alerts_df[alerts_df['severity'] == 'warning']
        
        if len(warning_alerts_df) > 0:
            # Display in expandable sections
            for _, alert in warning_alerts_df.iterrows():
                with st.expander(
                    f"🟡 {alert['equipment_id']} - {alert['model']} ({alert['site']})"
                ):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown(f"**Equipment ID:** {alert['equipment_id']}")
                        st.markdown(f"**Model:** {alert['model']}")
                        st.markdown(f"**Type:** {alert['type']}")
                        st.markdown(f"**Alert Type:** {alert['alert_type']}")
                    
                    with col2:
                        st.markdown(f"**Site:** {alert['site']}")
                        st.markdown(f"**Location:** {alert['location']}")
                        st.markdown(f"**Status:** {alert['status']}")
                        st.markdown(f"**Timestamp:** {alert['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.success("✅ No warning alerts!")
        
        st.markdown("---")
        
        # All Alerts Table
        st.subheader("📋 All Active Alerts")
        
        # Add filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.multiselect(
                "Filter by Severity",
                options=alerts_df['severity'].unique().tolist(),
                default=alerts_df['severity'].unique().tolist()
            )
        
        with col2:
            site_filter = st.multiselect(
                "Filter by Site",
                options=sorted(alerts_df['site'].unique().tolist()),
                default=alerts_df['site'].unique().tolist()
            )
        
        with col3:
            type_filter = st.multiselect(
                "Filter by Alert Type",
                options=alerts_df['alert_type'].unique().tolist(),
                default=alerts_df['alert_type'].unique().tolist()
            )
        
        # Apply filters
        filtered_alerts = alerts_df[
            (alerts_df['severity'].isin(severity_filter)) &
            (alerts_df['site'].isin(site_filter)) &
            (alerts_df['alert_type'].isin(type_filter))
        ]
        
        # Display filtered table
        if len(filtered_alerts) > 0:
            display_df = filtered_alerts.copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            
            display_df = display_df[[
                'equipment_id', 'model', 'site', 'alert_type',
                'severity', 'status', 'timestamp'
            ]]
            
            display_df.columns = [
                'Equipment ID', 'Model', 'Site', 'Alert Type',
                'Severity', 'Equipment Status', 'Timestamp'
            ]
            
            # Color code severity
            def color_severity(val):
                colors = {
                    'critical': 'background-color: #f8d7da',
                    'warning': 'background-color: #fff3cd',
                    'info': 'background-color: #d1ecf1'
                }
                return colors.get(val, '')
            
            styled_df = display_df.style.applymap(
                color_severity, subset=['Severity']
            )
            
            st.dataframe(
                styled_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Export option
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Alerts as CSV",
                data=csv,
                file_name=f"infrastructure_alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No alerts match the selected filters.")
        
        # Alert Timeline
        st.markdown("---")
        st.subheader("📅 Alert Timeline")
        
        # Group by date
        alerts_df['date'] = alerts_df['timestamp'].dt.date
        timeline_data = alerts_df.groupby(['date', 'severity']).size().reset_index(name='count')
        
        fig = px.bar(
            timeline_data,
            x='date',
            y='count',
            color='severity',
            color_discrete_map=colors,
            labels={'date': 'Date', 'count': 'Alert Count', 'severity': 'Severity'}
        )
        
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        
        # Alerts by Equipment Type
        st.markdown("---")
        st.subheader("🔧 Alerts by Equipment Type")
        
        type_severity = alerts_df.groupby(['type', 'severity']).size().reset_index(name='count')
        
        fig = px.bar(
            type_severity,
            x='type',
            y='count',
            color='severity',
            color_discrete_map=colors,
            barmode='stack',
            labels={'type': 'Equipment Type', 'count': 'Alert Count', 'severity': 'Severity'}
        )
        
        fig.update_layout(height=400)
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.success("🎉 No active alerts! All systems are operating normally.")
        st.balloons()
