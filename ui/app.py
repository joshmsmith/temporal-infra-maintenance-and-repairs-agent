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


@st.cache_data
def load_data():
    """Load and cache the infrastructure data."""
    return load_all_data()


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
