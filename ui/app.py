"""
Temporal Infrastructure Monitoring Dashboard
Main Streamlit application for monitoring network infrastructure equipment.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ui.utils.data_loader import load_all_data
from ui.components.overview import render_overview
from ui.components.equipment_details import render_equipment_inventory
from ui.components.health_metrics import render_health_metrics
from ui.components.lifecycle import render_lifecycle_management
from ui.components.alerts import render_alerts


def render_page_header(page_title: str):
    """Render page header with refresh button."""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(page_title)
    
    with col2:
        if st.button("🔄 Refresh Data", key=f"refresh_{page_title}"):
            st.cache_data.clear()
            st.rerun()


# Page configuration
st.set_page_config(
    page_title="Infrastructure Monitoring Dashboard",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 600;
        color: #1f1f1f;
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600;
        color: #5a5a5a;
        font-size: 14px;
    }
    h1 {
        color: #2c3e50;
        padding-bottom: 10px;
        border-bottom: 3px solid #007bff;
    }
    h2 {
        color: #34495e;
        margin-top: 20px;
    }
    h3 {
        color: #5a6c7d;
    }
    .streamlit-expanderHeader {
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)


@st.cache_data(ttl=60)  # Cache for 60 seconds
def load_data():
    """Load and cache the infrastructure data."""
    return load_all_data()

@st.cache_data
def get_data_file_timestamps():
    """Get timestamps of data files for change detection."""
    from pathlib import Path
    import os
    
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    timestamps = {}
    data_files = [
        "infrastructure_inventory.json",
        "health_metrics.json", 
        "equipment_life_expectancy.json"
    ]
    
    for file_name in data_files:
        file_path = data_dir / file_name
        if file_path.exists():
            timestamps[file_name] = os.path.getmtime(file_path)
        else:
            timestamps[file_name] = 0
    
    return timestamps


def main():
    """Main application function."""
    
    # Sidebar navigation
    st.sidebar.title("🏢 Infrastructure Dashboard")
    st.sidebar.markdown("---")
    
    # Navigation menu
    page = st.sidebar.radio(
        "Navigation",
        [
            "📊 Overview",
            "📦 Equipment Inventory",
            "📈 Health Metrics",
            "⏳ Lifecycle Management",
            "🔔 Alerts & Notifications"
        ]
    )
    
    st.sidebar.markdown("---")
    
    # Data refresh controls
    st.sidebar.markdown("### 🔄 Data Refresh")
    
    # Auto-refresh options
    refresh_interval = st.sidebar.selectbox(
        "Auto-refresh interval",
        ["Off", "30 seconds", "1 minute", "5 minutes"],
        index=0
    )
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.session_state.data_refreshed = True
        st.rerun()
    
    # Clear all cache button
    if st.sidebar.button("🗑️ Clear Cache"):
        st.cache_data.clear()
        st.session_state.data_refreshed = True
        st.rerun()
    
    # Auto-refresh logic
    if refresh_interval != "Off":
        # Set up auto-refresh based on selected interval
        interval_seconds = {
            "30 seconds": 30,
            "1 minute": 60,
            "5 minutes": 300
        }[refresh_interval]
        
        # Use st.empty() to create a placeholder for countdown
        countdown_placeholder = st.sidebar.empty()
        
        # Initialize session state for auto-refresh
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = 0
        
        import time
        current_time = time.time()
        
        # Check if it's time to refresh
        if current_time - st.session_state.last_refresh >= interval_seconds:
            st.session_state.last_refresh = current_time
            st.session_state.data_refreshed = True
            st.cache_data.clear()
            st.rerun()
        else:
            # Show countdown
            remaining = interval_seconds - (current_time - st.session_state.last_refresh)
            countdown_placeholder.markdown(f"⏱️ Next refresh in {int(remaining)}s")
            
            # Schedule a rerun to update the countdown
            time.sleep(1)
            st.rerun()
    
    # Check for file changes
    current_timestamps = get_data_file_timestamps()
    
    # Store previous timestamps in session state
    if 'previous_timestamps' not in st.session_state:
        st.session_state.previous_timestamps = current_timestamps
    
    # Check if any files have changed
    files_changed = False
    for file_name, current_time in current_timestamps.items():
        previous_time = st.session_state.previous_timestamps.get(file_name, 0)
        if current_time > previous_time:
            files_changed = True
            break
    
    # If files changed, show notification and update timestamps
    if files_changed:
        st.sidebar.info("📝 Data files have been updated!")
        if st.sidebar.button("Load Updated Data"):
            st.cache_data.clear()
            st.session_state.previous_timestamps = current_timestamps
            st.session_state.data_refreshed = True
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # About section
    st.sidebar.markdown("### About")
    st.sidebar.info(
        """
        This dashboard monitors infrastructure equipment across multiple data centers.
        
        **Features:**
        - Real-time equipment status
        - Health metrics tracking
        - Lifecycle management
        - Alert notifications
        - Maintenance scheduling
        
        **Powered by Temporal Workflows**
        """
    )
    
    # Load data
    try:
        with st.spinner("Loading infrastructure data..."):
            df = load_data()
        
        # Show data freshness indicator
        import datetime
        current_time = datetime.datetime.now()
        st.sidebar.markdown(f"**Last loaded:** {current_time.strftime('%H:%M:%S')}")
        
        # Show notification if data was just refreshed
        if 'data_refreshed' in st.session_state and st.session_state.data_refreshed:
            st.success("✅ Data refreshed successfully!")
            st.session_state.data_refreshed = False
        
        # Show data file info
        with st.sidebar.expander("📊 Data File Info", expanded=False):
            for file_name, timestamp in current_timestamps.items():
                if timestamp > 0:
                    file_time = datetime.datetime.fromtimestamp(timestamp)
                    st.markdown(f"**{file_name}**")
                    st.markdown(f"Modified: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    st.markdown(f"**{file_name}** - Not found")
        
        # Check for page-level refresh buttons
        refresh_triggered = False
        for key in st.session_state:
            if key.startswith("refresh_") and st.session_state[key]:
                refresh_triggered = True
                break
        
        if refresh_triggered:
            st.cache_data.clear()
            st.session_state.data_refreshed = True
            st.rerun()
        
        # Render selected page
        if page == "📊 Overview":
            render_overview(df)
        elif page == "📦 Equipment Inventory":
            render_equipment_inventory(df)
        elif page == "📈 Health Metrics":
            render_health_metrics(df)
        elif page == "⏳ Lifecycle Management":
            render_lifecycle_management(df)
        elif page == "🔔 Alerts & Notifications":
            render_alerts(df)
    
    except FileNotFoundError as e:
        st.error(
            f"❌ Error loading data: {str(e)}\n\n"
            "Please ensure the data files are in the 'data' directory."
        )
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.exception(e)
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: #6c757d; font-size: 0.8em;'>
        <p>Infrastructure Monitoring Dashboard v1.0</p>
        <p>Temporal Solutions Architecture Demo</p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
