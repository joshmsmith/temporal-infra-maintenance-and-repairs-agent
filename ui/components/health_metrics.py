"""Health metrics visualization component."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from utils.data_loader import DataLoader


def render_health_metrics(df: pd.DataFrame):
    """Render the health metrics page with time-series charts."""
    
    # Header with refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("📈 Health Metrics & Trends")
    with col2:
        st.button("🔄 Refresh Data", key="refresh_health")
    
    st.markdown("---")
    
    # Equipment selector
    equipment_ids = df['id'].tolist()
    selected_equipment_id = st.selectbox(
        "Select Equipment",
        equipment_ids,
        format_func=lambda x: f"{x} - {df[df['id']==x]['model'].iloc[0]} ({df[df['id']==x]['site'].iloc[0]})"
    )
    
    if selected_equipment_id:
        equipment = df[df['id'] == selected_equipment_id].iloc[0]
        
        # Display equipment summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Current Status",
                value=equipment['status']
            )
        
        with col2:
            st.metric(
                label="Health Score",
                value=f"{equipment['health_score']:.1f}"
            )
        
        with col3:
            st.metric(
                label="CPU Usage",
                value=f"{equipment['cpu_utilization_percent']}%"
            )
        
        with col4:
            st.metric(
                label="Memory Usage",
                value=f"{equipment['memory_utilization_percent']}%"
            )
        
        st.markdown("---")
        
        # Get recent readings
        loader = DataLoader()
        recent_readings = loader.get_recent_readings_for_equipment(selected_equipment_id)
        
        if recent_readings and len(recent_readings) > 0:
            # Convert to DataFrame
            readings_df = pd.DataFrame(recent_readings)
            readings_df['timestamp'] = pd.to_datetime(readings_df['timestamp'])
            readings_df = readings_df.sort_values('timestamp')
            
            # Create time-series charts
            st.subheader("📊 Performance Metrics Over Time (Last 5 Days)")
            
            # CPU and Memory Utilization
            fig1 = make_subplots(
                rows=1, cols=2,
                subplot_titles=("CPU Utilization", "Memory Utilization")
            )
            
            fig1.add_trace(
                go.Scatter(
                    x=readings_df['timestamp'],
                    y=readings_df['cpu_utilization_percent'],
                    mode='lines+markers',
                    name='CPU %',
                    line=dict(color='#007bff', width=2),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            fig1.add_trace(
                go.Scatter(
                    x=readings_df['timestamp'],
                    y=readings_df['memory_utilization_percent'],
                    mode='lines+markers',
                    name='Memory %',
                    line=dict(color='#28a745', width=2),
                    marker=dict(size=8)
                ),
                row=1, col=2
            )
            
            fig1.update_xaxes(title_text="Date", row=1, col=1)
            fig1.update_xaxes(title_text="Date", row=1, col=2)
            fig1.update_yaxes(title_text="Utilization %", row=1, col=1)
            fig1.update_yaxes(title_text="Utilization %", row=1, col=2)
            
            fig1.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Temperature
            st.subheader("🌡️ Temperature Trends")
            fig2 = go.Figure()
            
            fig2.add_trace(
                go.Scatter(
                    x=readings_df['timestamp'],
                    y=readings_df['temperature_celsius'],
                    mode='lines+markers',
                    name='Temperature',
                    line=dict(color='#dc3545', width=2),
                    marker=dict(size=8),
                    fill='tozeroy',
                    fillcolor='rgba(220, 53, 69, 0.1)'
                )
            )
            
            fig2.update_layout(
                height=300,
                xaxis_title="Date",
                yaxis_title="Temperature (°C)",
                showlegend=False
            )
            
            st.plotly_chart(fig2, use_container_width=True)
            
            # Network Metrics
            st.subheader("🌐 Network Performance")
            
            fig3 = make_subplots(
                rows=1, cols=2,
                subplot_titles=("Packet Loss", "Latency")
            )
            
            fig3.add_trace(
                go.Scatter(
                    x=readings_df['timestamp'],
                    y=readings_df['packet_loss_percent'],
                    mode='lines+markers',
                    name='Packet Loss %',
                    line=dict(color='#ffc107', width=2),
                    marker=dict(size=8)
                ),
                row=1, col=1
            )
            
            fig3.add_trace(
                go.Scatter(
                    x=readings_df['timestamp'],
                    y=readings_df['latency_ms'],
                    mode='lines+markers',
                    name='Latency (ms)',
                    line=dict(color='#17a2b8', width=2),
                    marker=dict(size=8)
                ),
                row=1, col=2
            )
            
            fig3.update_xaxes(title_text="Date", row=1, col=1)
            fig3.update_xaxes(title_text="Date", row=1, col=2)
            fig3.update_yaxes(title_text="Packet Loss %", row=1, col=1)
            fig3.update_yaxes(title_text="Latency (ms)", row=1, col=2)
            
            fig3.update_layout(height=350, showlegend=False)
            st.plotly_chart(fig3, use_container_width=True)
            
            # Data table
            st.markdown("---")
            st.subheader("📋 Detailed Readings")
            
            display_df = readings_df.copy()
            display_df['timestamp'] = display_df['timestamp'].dt.strftime('%Y-%m-%d %H:%M')
            display_df.columns = [
                'Timestamp', 'CPU %', 'Memory %', 'Temp (°C)',
                'Packet Loss %', 'Latency (ms)'
            ]
            
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
            
            # Statistics
            st.markdown("---")
            st.subheader("📊 Statistical Summary")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**CPU Utilization**")
                st.markdown(f"Average: {readings_df['cpu_utilization_percent'].mean():.1f}%")
                st.markdown(f"Max: {readings_df['cpu_utilization_percent'].max():.1f}%")
                st.markdown(f"Min: {readings_df['cpu_utilization_percent'].min():.1f}%")
            
            with col2:
                st.markdown("**Memory Utilization**")
                st.markdown(f"Average: {readings_df['memory_utilization_percent'].mean():.1f}%")
                st.markdown(f"Max: {readings_df['memory_utilization_percent'].max():.1f}%")
                st.markdown(f"Min: {readings_df['memory_utilization_percent'].min():.1f}%")
            
            with col3:
                st.markdown("**Temperature**")
                st.markdown(f"Average: {readings_df['temperature_celsius'].mean():.1f}°C")
                st.markdown(f"Max: {readings_df['temperature_celsius'].max():.1f}°C")
                st.markdown(f"Min: {readings_df['temperature_celsius'].min():.1f}°C")
            
        else:
            st.warning("No historical readings available for this equipment.")
    
    # Multi-equipment comparison
    st.markdown("---")
    st.subheader("🔀 Compare Multiple Equipment")
    
    # Multi-select for comparison
    comparison_ids = st.multiselect(
        "Select equipment to compare (up to 5)",
        equipment_ids,
        max_selections=5,
        format_func=lambda x: f"{x} - {df[df['id']==x]['model'].iloc[0]}"
    )
    
    if len(comparison_ids) > 1:
        comparison_data = []
        
        for eq_id in comparison_ids:
            eq_data = df[df['id'] == eq_id].iloc[0]
            comparison_data.append({
                'Equipment': f"{eq_id}",
                'Model': eq_data['model'],
                'Site': eq_data['site'],
                'Health Score': eq_data['health_score'],
                'CPU %': eq_data['cpu_utilization_percent'],
                'Memory %': eq_data['memory_utilization_percent'],
                'Temp (°C)': eq_data['temperature_celsius'],
                'Status': eq_data['status']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Bar chart comparison
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Health Score',
            x=comparison_df['Equipment'],
            y=comparison_df['Health Score'],
            marker_color='#007bff'
        ))
        
        fig.add_trace(go.Bar(
            name='CPU %',
            x=comparison_df['Equipment'],
            y=comparison_df['CPU %'],
            marker_color='#28a745'
        ))
        
        fig.add_trace(go.Bar(
            name='Memory %',
            x=comparison_df['Equipment'],
            y=comparison_df['Memory %'],
            marker_color='#ffc107'
        ))
        
        fig.update_layout(
            height=400,
            barmode='group',
            xaxis_title="Equipment",
            yaxis_title="Value",
            legend_title="Metric"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Comparison table
        st.dataframe(comparison_df, use_container_width=True, hide_index=True)
