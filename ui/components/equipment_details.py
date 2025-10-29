"""Equipment inventory component."""

import streamlit as st
import pandas as pd
from utils.calculations import get_health_status_color, get_severity_color


def render_equipment_inventory(df: pd.DataFrame):
    """Render the equipment inventory page with filters and search."""
    
    st.title("📦 Equipment Inventory")
    st.markdown("---")
    
    # Sidebar filters
    st.sidebar.header("🔍 Filters")
    
    # Status filter
    status_options = ['All'] + sorted(df['status'].unique().tolist())
    selected_status = st.sidebar.selectbox("Status", status_options)
    
    # Site filter
    site_options = ['All'] + sorted(df['site'].unique().tolist())
    selected_site = st.sidebar.selectbox("Site", site_options)
    
    # Vendor filter
    vendor_options = ['All'] + sorted(df['vendor'].unique().tolist())
    selected_vendor = st.sidebar.selectbox("Vendor", vendor_options)
    
    # Equipment type filter
    type_options = ['All'] + sorted(df['type'].unique().tolist())
    selected_type = st.sidebar.selectbox("Equipment Type", type_options)
    
    # Health score filter
    st.sidebar.markdown("**Health Score Range**")
    health_min, health_max = st.sidebar.slider(
        "Select range",
        0.0, 100.0, (0.0, 100.0)
    )
    
    # Search box
    search_query = st.text_input("🔎 Search by Equipment ID or Model", "")
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_status != 'All':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    if selected_site != 'All':
        filtered_df = filtered_df[filtered_df['site'] == selected_site]
    
    if selected_vendor != 'All':
        filtered_df = filtered_df[filtered_df['vendor'] == selected_vendor]
    
    if selected_type != 'All':
        filtered_df = filtered_df[filtered_df['type'] == selected_type]
    
    filtered_df = filtered_df[
        (filtered_df['health_score'] >= health_min) & 
        (filtered_df['health_score'] <= health_max)
    ]
    
    if search_query:
        filtered_df = filtered_df[
            filtered_df['id'].str.contains(search_query, case=False) |
            filtered_df['model'].str.contains(search_query, case=False)
        ]
    
    # Display count
    st.markdown(f"**Showing {len(filtered_df)} of {len(df)} equipment items**")
    
    # Display data table
    if len(filtered_df) > 0:
        # Prepare display columns
        display_df = filtered_df[[
            'id', 'model', 'type', 'vendor', 'site', 'location',
            'status', 'health_score', 'temperature_celsius',
            'cpu_utilization_percent', 'memory_utilization_percent'
        ]].copy()
        
        # Rename columns for display
        display_df.columns = [
            'Equipment ID', 'Model', 'Type', 'Vendor', 'Site', 'Location',
            'Status', 'Health Score', 'Temp (°C)', 'CPU %', 'Memory %'
        ]
        
        # Color code the status column
        def color_status(val):
            colors = {
                'Operational': 'background-color: #d4edda',
                'Degraded': 'background-color: #fff3cd',
                'Down': 'background-color: #f8d7da'
            }
            return colors.get(val, '')
        
        def color_health_score(val):
            if val >= 70:
                return 'background-color: #d4edda'
            elif val >= 40:
                return 'background-color: #fff3cd'
            else:
                return 'background-color: #f8d7da'
        
        # Apply styling
        styled_df = display_df.style.applymap(
            color_status, subset=['Status']
        ).applymap(
            color_health_score, subset=['Health Score']
        ).format({
            'Health Score': '{:.1f}',
            'Temp (°C)': '{:.0f}',
            'CPU %': '{:.0f}',
            'Memory %': '{:.0f}'
        })
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=500
        )
        
        st.markdown("---")
        
        # Equipment details section
        st.subheader("📋 Equipment Details")
        
        # Select equipment for detailed view
        equipment_ids = filtered_df['id'].tolist()
        selected_equipment_id = st.selectbox(
            "Select equipment for detailed view:",
            equipment_ids,
            format_func=lambda x: f"{x} - {filtered_df[filtered_df['id']==x]['model'].iloc[0]}"
        )
        
        if selected_equipment_id:
            equipment = filtered_df[filtered_df['id'] == selected_equipment_id].iloc[0]
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("### Basic Information")
                st.markdown(f"**Equipment ID:** {equipment['id']}")
                st.markdown(f"**Model:** {equipment['model']}")
                st.markdown(f"**Type:** {equipment['type']}")
                st.markdown(f"**Vendor:** {equipment['vendor']}")
                st.markdown(f"**Serial Number:** {equipment['serial_number']}")
                
            with col2:
                st.markdown("### Location & Network")
                st.markdown(f"**Site:** {equipment['site']}")
                st.markdown(f"**Location:** {equipment['location']}")
                st.markdown(f"**IP Address:** {equipment['ip_address']}")
                st.markdown(f"**Firmware:** {equipment['firmware_version']}")
                
            with col3:
                st.markdown("### Status & Health")
                status_color = get_health_status_color(equipment['status'])
                st.markdown(f"**Status:** <span style='color:{status_color};font-weight:bold'>{equipment['status']}</span>", unsafe_allow_html=True)
                st.markdown(f"**Health Score:** {equipment['health_score']:.1f}")
                st.markdown(f"**Temperature:** {equipment['temperature_celsius']}°C")
                st.markdown(f"**CPU Usage:** {equipment['cpu_utilization_percent']}%")
                st.markdown(f"**Memory Usage:** {equipment['memory_utilization_percent']}%")
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Maintenance Information")
                st.markdown(f"**Install Date:** {equipment['install_date']}")
                st.markdown(f"**Last Maintenance:** {equipment['last_maintenance']}")
                st.markdown(f"**Uptime:** {equipment['uptime_days']} days")
                st.markdown(f"**Contract Expiry:** {equipment['maintenance_contract_expiry']}")
                
            with col2:
                st.markdown("### Active Alerts")
                if equipment['alerts'] and len(equipment['alerts']) > 0:
                    for alert in equipment['alerts']:
                        severity_color = get_severity_color(alert['severity'])
                        st.markdown(
                            f"🔔 **{alert['type']}** - "
                            f"<span style='color:{severity_color};font-weight:bold'>{alert['severity'].upper()}</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(f"   *{alert['timestamp']}*")
                else:
                    st.success("✅ No active alerts")
    else:
        st.warning("No equipment found matching the selected filters.")
