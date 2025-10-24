"""
Refactored Fraud Detection Dashboard - Main Orchestrator
"""
import streamlit as st
from datetime import datetime

# Import configuration
from config import PAGE_CONFIG, TAB_CONFIG

# Import styling
from styles import apply_styles

# Import data service
from data_service import DataService

# Import components
from components.sidebar import render_sidebar, handle_auto_refresh
from components.metrics import render_key_metrics
from components.alerts import render_alerts_section
from components.transactions import render_transactions_tab
from components.detection_results import render_detection_results_tab
from components.alerts_details import render_alerts_details_tab
from components.analytics import render_analytics_tab
from components.footer import render_footer


def initialize_session_state():
    """Initialize session state variables"""
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()


def configure_page():
    """Configure Streamlit page settings"""
    st.set_page_config(**PAGE_CONFIG)


def render_header():
    """Render dashboard header"""
    st.title("Fraud Detection Dashboard")
    st.markdown("Real-time monitoring of transaction fraud detection")


def render_tabs(dataframes):
    """Render main content tabs"""
    tab_labels = [f"{tab['icon']} {tab['title']}" for tab in TAB_CONFIG]
    tab1, tab2, tab3, tab4 = st.tabs(tab_labels)
    
    with tab1:
        render_transactions_tab(dataframes['df_transactions'])
    
    with tab2:
        render_detection_results_tab(dataframes['df_results'])
    
    with tab3:
        render_alerts_details_tab(dataframes['df_alerts'])
    
    with tab4:
        render_analytics_tab(dataframes['df_transactions'], dataframes['df_alerts'])


def main():
    """Main dashboard application"""
    # Initialize
    initialize_session_state()
    configure_page()
    apply_styles()
    
    # Render header
    render_header()
    
    # Render sidebar and handle controls
    controls = render_sidebar()
    handle_auto_refresh(controls)
    
    # Load data
    try:
        data_service = DataService()
        dataframes = data_service.get_dataframes()
        metrics = data_service.get_key_metrics(dataframes)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()
    
    # Render main content
    render_key_metrics(metrics)
    render_alerts_section(dataframes['df_alerts'])
    render_tabs(dataframes)
    render_footer(dataframes, controls)


if __name__ == "__main__":
    main()
