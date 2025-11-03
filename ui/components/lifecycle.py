"""Equipment lifecycle management component."""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.calculations import (
    calculate_equipment_age,
    calculate_remaining_life,
    calculate_life_percentage,
    get_lifecycle_status,
    get_lifecycle_color,
    calculate_days_until_contract_expiry,
    get_contract_status
)


def render_lifecycle_management(df: pd.DataFrame):
    """Render the lifecycle management page."""
    
    # Header with refresh button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("⏳ Equipment Lifecycle Management")
    with col2:
        st.button("🔄 Refresh Data", key="refresh_lifecycle")
    
    st.markdown("---")
    
    # Calculate lifecycle metrics for all equipment
    lifecycle_data = []
    
    for _, row in df.iterrows():
        age = calculate_equipment_age(row['install_date'])
        expected_life = row['expected_life_years']
        remaining = calculate_remaining_life(age, expected_life)
        life_pct = calculate_life_percentage(age, expected_life)
        status = get_lifecycle_status(life_pct)
        
        days_to_expiry = calculate_days_until_contract_expiry(row['maintenance_contract_expiry'])
        contract_status = get_contract_status(days_to_expiry)
        
        lifecycle_data.append({
            'id': row['id'],
            'model': row['model'],
            'type': row['type'],
            'site': row['site'],
            'age_years': age,
            'expected_life_years': expected_life,
            'remaining_life_years': remaining,
            'life_percentage': life_pct,
            'lifecycle_status': status,
            'install_date': row['install_date'],
            'contract_expiry': row['maintenance_contract_expiry'],
            'days_to_contract_expiry': days_to_expiry,
            'contract_status': contract_status
        })
    
    lifecycle_df = pd.DataFrame(lifecycle_data)
    
    # KPI Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        critical_count = len(lifecycle_df[lifecycle_df['lifecycle_status'] == 'Critical'])
        st.metric(
            label="Critical Equipment",
            value=critical_count
        )
        st.caption("≥90% Life Used")
    
    with col2:
        warning_count = len(lifecycle_df[lifecycle_df['lifecycle_status'] == 'Warning'])
        st.metric(
            label="Warning",
            value=warning_count
        )
        st.caption("75-90% Life Used")
    
    with col3:
        avg_age = lifecycle_df['age_years'].mean()
        st.metric(
            label="Avg Equipment Age",
            value=f"{avg_age:.1f} yrs"
        )
    
    with col4:
        expired_contracts = len(lifecycle_df[lifecycle_df['contract_status'] == 'Expired'])
        st.metric(
            label="Expired Contracts",
            value=expired_contracts
        )
    
    st.markdown("---")
    
    # Age vs Expected Life Scatter Plot
    st.subheader("📊 Equipment Age vs. Expected Life")
    
    fig = px.scatter(
        lifecycle_df,
        x='age_years',
        y='expected_life_years',
        color='lifecycle_status',
        color_discrete_map={
            'Good': '#28a745',
            'Warning': '#ffc107',
            'Critical': '#dc3545'
        },
        hover_data=['id', 'model', 'site'],
        size='life_percentage',
        labels={
            'age_years': 'Current Age (years)',
            'expected_life_years': 'Expected Life (years)',
            'lifecycle_status': 'Status'
        }
    )
    
    # Add diagonal line for reference (age = expected life)
    max_val = max(lifecycle_df['expected_life_years'].max(), lifecycle_df['age_years'].max())
    fig.add_trace(
        go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            line=dict(color='gray', dash='dash'),
            name='Expected Life Line',
            showlegend=True
        )
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Equipment Needing Replacement Soon
    st.subheader("🚨 Equipment Needing Replacement")
    
    tab1, tab2, tab3 = st.tabs(["Critical (≥90%)", "Warning (75-90%)", "All Equipment"])
    
    with tab1:
        critical_equip = lifecycle_df[lifecycle_df['lifecycle_status'] == 'Critical'].sort_values('remaining_life_years')
        if len(critical_equip) > 0:
            st.markdown(f"**{len(critical_equip)} equipment items in critical status:**")
            
            display_cols = [
                'id', 'model', 'type', 'site', 'age_years', 
                'expected_life_years', 'remaining_life_years', 'life_percentage'
            ]
            display_df = critical_equip[display_cols].copy()
            display_df.columns = [
                'Equipment ID', 'Model', 'Type', 'Site', 'Age (yrs)',
                'Expected Life (yrs)', 'Remaining (yrs)', 'Life Used %'
            ]
            
            st.dataframe(
                display_df.style.format({
                    'Age (yrs)': '{:.1f}',
                    'Expected Life (yrs)': '{:.0f}',
                    'Remaining (yrs)': '{:.1f}',
                    'Life Used %': '{:.1f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No equipment in critical status!")
    
    with tab2:
        warning_equip = lifecycle_df[lifecycle_df['lifecycle_status'] == 'Warning'].sort_values('remaining_life_years')
        if len(warning_equip) > 0:
            st.markdown(f"**{len(warning_equip)} equipment items in warning status:**")
            
            display_cols = [
                'id', 'model', 'type', 'site', 'age_years',
                'expected_life_years', 'remaining_life_years', 'life_percentage'
            ]
            display_df = warning_equip[display_cols].copy()
            display_df.columns = [
                'Equipment ID', 'Model', 'Type', 'Site', 'Age (yrs)',
                'Expected Life (yrs)', 'Remaining (yrs)', 'Life Used %'
            ]
            
            st.dataframe(
                display_df.style.format({
                    'Age (yrs)': '{:.1f}',
                    'Expected Life (yrs)': '{:.0f}',
                    'Remaining (yrs)': '{:.1f}',
                    'Life Used %': '{:.1f}'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.success("✅ No equipment in warning status!")
    
    with tab3:
        display_cols = [
            'id', 'model', 'type', 'site', 'age_years',
            'expected_life_years', 'remaining_life_years', 'life_percentage', 'lifecycle_status'
        ]
        display_df = lifecycle_df[display_cols].copy().sort_values('life_percentage', ascending=False)
        display_df.columns = [
            'Equipment ID', 'Model', 'Type', 'Site', 'Age (yrs)',
            'Expected Life (yrs)', 'Remaining (yrs)', 'Life Used %', 'Status'
        ]
        
        st.dataframe(
            display_df.style.format({
                'Age (yrs)': '{:.1f}',
                'Expected Life (yrs)': '{:.0f}',
                'Remaining (yrs)': '{:.1f}',
                'Life Used %': '{:.1f}'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    st.markdown("---")
    
    # Maintenance Contract Status
    st.subheader("📋 Maintenance Contract Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Contract status distribution
        contract_counts = lifecycle_df['contract_status'].value_counts()
        
        colors = {
            'Active': '#28a745',
            'Warning': '#ffc107',
            'Expiring Soon': '#fd7e14',
            'Expired': '#dc3545'
        }
        
        fig = px.pie(
            values=contract_counts.values,
            names=contract_counts.index,
            color=contract_counts.index,
            color_discrete_map=colors,
            title="Contract Status Distribution"
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Contracts expiring soon
        expiring_soon = lifecycle_df[
            (lifecycle_df['days_to_contract_expiry'] >= 0) & 
            (lifecycle_df['days_to_contract_expiry'] <= 90)
        ].sort_values('days_to_contract_expiry')
        
        st.markdown("**⚠️ Contracts Expiring in 90 Days:**")
        if len(expiring_soon) > 0:
            for _, row in expiring_soon.iterrows():
                days = row['days_to_contract_expiry']
                color = '#dc3545' if days < 30 else '#ffc107'
                st.markdown(
                    f"- **{row['id']}** ({row['model']}): "
                    f"<span style='color:{color};font-weight:bold'>{days} days</span>",
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ No contracts expiring soon")
    
    # Lifecycle by Equipment Type
    st.markdown("---")
    st.subheader("📈 Lifecycle Status by Equipment Type")
    
    type_lifecycle = lifecycle_df.groupby(['type', 'lifecycle_status']).size().reset_index(name='count')
    
    fig = px.bar(
        type_lifecycle,
        x='type',
        y='count',
        color='lifecycle_status',
        color_discrete_map={
            'Good': '#28a745',
            'Warning': '#ffc107',
            'Critical': '#dc3545'
        },
        barmode='stack',
        labels={'type': 'Equipment Type', 'count': 'Count', 'lifecycle_status': 'Status'}
    )
    
    fig.update_layout(height=400)
    fig.update_xaxes(tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
